#! /bin/python3

import os
import time
from datetime import datetime, timedelta

# von python-rpi.gpio
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
except:
	import GPIO as asdf # Dummylib benutzen
	GPIO = asdf.GPIO()

# GPIO-Definitionen
# Zahlen = Pinnummern, GPIO von Rev. 1, in Klammern Rev. 2
adcPins = [3, 5, 7, 8, 10, 11, 12, 13]
bit0 = 3	# GPIO 0 (2)
bit1 = 5	# GPIO 1 (3)
bit2 = 7	# GPIO 4 (4)
bit3 = 8	# GPIO 14 (14)
bit4 = 10	# GPIO 15 (15)
bit5 = 11	# GPIO 17 (17)
bit6 = 12	# GPIO 18 (18)
bit7 = 13	# GPIO 21 (27)
bits = [bit7, bit6, bit5, bit4, bit3, bit2, bit1, bit0]
latch = 15	# GPIO 22 (22)
senke = 16	# GPIO 22 (23)

# Konstanten
strom = 5.0
intervall = 1.0 # in Sekunden
adc = 0.196078431372549 # Volt pro Bit

# Templates
prot = "Messung: {}\n----------------------------\n"+\
	   "Spannungen: Abschaltspannung: {:.3f}V, Vor Messung: {:.3f}V, "+\
	   "Messbeginn: {:.3f}V, Messende: {:.3f}V\n"+\
	   "Akkueigenschaften: Ladung: {:.3f}Ah, Energie: {:.3f}Wh\n"+\
	   "Messdauer: {:.3f}s\n\nMesspunkte: [Zeit in s : Spannung in V]\n"
dat = "{:0>2d}.{:0>2d}.{:0>4d}-{:0>2d}-{:0>2d}-{:0>2d}"
info = "Akkuleistungsmessung v0.45\n--------------------------\n"+\
       "Der Akku wird kontinuierlich mit 5 Ampere bis zur "+\
       "Abschaltspannung entladen, \naktuelle Spannung, Ladung und "+\
       "Energie werden angezeigt.\n"
mess = "Messung läuft!\n---------------\n"+\
       "Zeit: {:0>2.0f}:{:0>2.0f}:{:0>2.0f}, Sekunden: {:.3f}\n"+\
       "Ladung: {:.3f}Ah, Energie: {:.3f}Wh\n"+\
       "Spannung: {:.3f}V, Strom: {:.3f}A"

# Methodendeklarationen
def spannungAuslesen():
	spannung = 0
	for bit in bits: # die Bits einzeln in das Ergebnis schieben
		if(GPIO.input(bit) == GPIO.HIGH):
			spannung += 1
		spannung = spannung << 1
	spannung = spannung >> 1 # einen zu weit geschoben..
	spannung = spannung * adc # die tatsächliche Spannung ausrechnen
	return spannung
	
def stromsenkeEinschalten():
	GPIO.output(senke, GPIO.HIGH)

def stromsenkeAusschalten():
	GPIO.output(senke, GPIO.LOW)
	
def statusAusgabe(messdaten, spannung, strom, energie, messZeit):
	clear()
	
	sekunden = messZeit % 60
	minuten = (messZeit // 60) % 60
	stunden = minuten // 60
	# die Energie zwischen den letzten beiden Messpunkten addieren
	energie += float(messZeit - messdaten[-2][0])/3600 * spannung * strom
	
	# Ausgabe der aktuellen Messung
	print(mess.format(stunden, minuten, sekunden, messZeit, \
	                  strom*(messZeit/3600), energie, spannung, strom))

	return energie # neue Energie zurückgeben

def messdatenSchreiben(datum, messdaten, energie, abschaltspannung, strom):
	# formatiertes Datum (siehe Templates)
	datumForm = dat.format(datum.day, datum.month, datum.year, \
	                       datum.hour, datum.minute, datum.second)
	
	f = open("messung-{}.txt".format(datumForm), 'w')
	
	# Informationen und Daten in Protokoll schreiben
	f.write(prot.format(datumForm, abschaltspannung, \
	                    messdaten[0][1], messdaten[1][1], \
	                    messdaten[-1][1], messdaten[-1][0]/3600*strom, \
	                    energie, messdaten[-1][0]))
	
	# Messpunkte in Protokoll schreiben
	for messpunkt in messdaten:
		f.write("{:.3f}s:{:.3f}V\n".format(messpunkt[0], messpunkt[1]))

	f.close()

def clear():
	# muss an das Betriebssystem angepasst werden
	os.system("clear")

def beenden():
	GPIO.cleanup() # benutzte Pins wieder freigeben
	exit()

# GPIOs initialisieren
GPIO.setmode(GPIO.BOARD)
GPIO.setup(bits, GPIO.IN)
GPIO.setup([senke, latch], GPIO.OUT)

GPIO.output(latch, GPIO.HIGH) # Wandler einschalten
GPIO.output(senke, GPIO.LOW)  # Senke ausschalten


# Hauptschleife
while True:	
	# Variablen initialisieren
	energie = 0.0
	messdaten = list()
	abschaltspannung = int()
	spannungVorMessung = int()
	messZeit = 0.0

	# Hinweise zur Benutzung ausgeben
	print(info)

	# Abschaltspannung erfragen
	abschaltspannung = float(input("Abschaltspannung in Volt? "))
	input("Akku anschließen und Enter drücken") # nur für Enter
	clear() # Bildschirm leeren

	# Spannung vor Messbeginn ist erster Datenpunkt
	messdaten.append([0, spannungAuslesen()]) # erster Datenpunkt
	
	stromsenkeEinschalten()
	messBeginn = datetime.now()

	while True:
		time.sleep(intervall) # eine Sekunde warten
	
		messZeit += intervall
		spannung = spannungAuslesen()
	
		messdaten.append([messZeit, spannung])
		energie = statusAusgabe(messdaten, spannung, strom, energie, messZeit)
		
		if spannung < abschaltspannung:
			senkeAusschalten()
			print("\nAbschaltspannung unterschritten, Messung beendet!")
			break
	
	print("\nMessung beendet!")
	
	eingabe = str()
	while True:
		eingabe = input("[P]rotokoll, Programm [n]eustarten oder Programm [b]eenden? ")
		if(eingabe in ['b', 'B']):
			beenden()
		elif(eingabe in ['n', 'N']):
			os.system("clear")
			break
		elif(eingabe in ['p', 'P']):
			messdatenSchreiben(messBeginn, messdaten, energie, \
			                   abschaltspannung, strom)
			beenden()
