import serial
import time

import pygame as pg

# Adjust the COM port and baud rate as needed
COM_PORT = "/dev/ttyUSB0"  # Change this to your actual COM port
BAUD_RATE = 115200

class Parser:
	def __init__(self):
		self.bytes = []

	def find_start(self):
		while len(self.bytes) > 1:
			if self.bytes[0] == 0x00 and self.bytes[1] == 0xff:
				return True
			self.next(1)
		return False

	def next(self, n):
		nexts = self.bytes[0:n]
		self.bytes = self.bytes[n:]
		return nexts

	def expect(self, bytestring):
		for (b1, b2) in zip(bytestring, self.next(len(bytestring))):
			if b1 != b2:
				raise Exception(f"Error: expected {b1}, received {b2}")

	def skip_header(self):
		self.expect(b'\x00\xff')

	def parse_length(self):
		# little endian: read later byte first
		b2, b1 = self.next(2)
		return b1 * 256 + b2

	def parse_other_content(self):
		return self.next(16)

	def parse_image(self):
		return self.next(self.length - 16)

	def parse_check(self):
		# this is supposed to be a check byte, but i could not get it working so assume it's correct
		check = self.next(1)[0]

	def parse(self, bytes):
		self.bytes += list(bytes)
		if not self.find_start(): return
		if len(self.bytes) < 12000: return
		self.skip_header()
		self.length = self.parse_length()
		self.other_content = self.parse_other_content()
		self.image = self.parse_image()
		self.parse_check()
		self.expect(b'\xdd')
		return self.image

def draw_image(image, display):
	print("Drawing image...")
	display.fill((255, 255, 255))
	for x in range(100):
		for y in range(100):
			idx = x + y * 100
			c = image[x * 100 + (99 - y)]
			pg.draw.rect(
				display,
				(c, c, c),
				[x*WIDTH, y*WIDTH, WIDTH, WIDTH])
	pg.display.update()
	time.sleep(0.5)

WIDTH = 4
def main():
	# Initialize serial connection
	ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
	# Wait for the connection to be established
	time.sleep(2)

	# Set output to go through both usb and lcd
	ser.write(b'AT+DISP=3\r')

	pg.init()
	display = pg.display.set_mode((WIDTH*100, WIDTH*100))

	parser = Parser()

	while True:
		time.sleep(0.2)
		print("Reading this many bytes:", ser.in_waiting)
		buf = ser.read(ser.inWaiting())
		try:
			image = parser.parse(buf)
			# the buffer could have not been long enough, causing the parse to return None
			if image:
				draw_image(image, display)
		except Exception as e:
			print("Error parsing image.")
			print(e)

	ser.close()  # Close the serial connection

if __name__ == '__main__':
	main()
