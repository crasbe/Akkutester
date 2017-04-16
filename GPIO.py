# this is a dummy to simulate the real thing

class GPIO:
	IN = 0
	OUT = 1
	HIGH = 1
	LOW = 0
	BOARD = 0
	
	def __init__(self):
		self.wert = 256
	
	def cleanup(self):
		pass

	def setup(self, liste, io):
		pass

	def setmode(self, mode):
		pass
	
	def output(self, pin, level):
		pass
		
	def input(self, pin):
		if(pin == 3):
			return (self.wert & 0b00000001) >> 0
		elif(pin == 5):
			return (self.wert & 0b00000010) >> 1
		elif(pin == 7):
			return (self.wert & 0b00000100) >> 2
		elif(pin == 8):
			return (self.wert & 0b00001000) >> 3
		elif(pin == 10):
			return (self.wert & 0b00010000) >> 4
		elif(pin == 11):
			return (self.wert & 0b00100000) >> 5
		elif(pin == 12):
			return (self.wert & 0b01000000) >> 6
		elif(pin == 13):
			self.wert -= 1
			return (self.wert & 0b10000000) >> 7
