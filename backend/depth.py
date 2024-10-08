import serial
import time

# Adjust the COM port and baud rate as needed
COM_PORT = "/dev/ttyUSB0"  # Change this to your actual COM port
BAUD_RATE = 115200

dist = 0
def set_dist(d):
	global dist
	dist = d

def get_pen_state() -> str:
	if dist <= 70:
		return 'down'
	if 70 < dist < 90:
		return 'hover'
	else:
		return 'up'

def get_dist():
	return dist

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
		# wait for the next "heading" if this heading is a false alarm
		# also re-calibrates the beginning of frames if somehow it's out of sync
		if self.bytes[2 + 16 + 10000 + 1] != 0xdd: return
		self.length = self.parse_length()
		self.other_content = self.parse_other_content()
		self.image = self.parse_image()
		self.parse_check()
		self.expect(b'\xdd')
		set_dist(self.image[5050])
		return self.image

WIDTH = 4
def start_depth_sensor():
	# Initialize serial connection
	ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
	# Wait for the connection to be established
	time.sleep(0.5)

	# tell it to record unit in millimetres
	ser.write(b'AT+UNIT=1\r')
	time.sleep(0.5)
	ser.read(ser.inWaiting()) # read a response, otherwise it throws a tantrum and refuses to work

	# Set output to go through both usb and lcd
	ser.write(b'AT+DISP=3\r')

	parser = Parser()

	while True:
		# print("Reading this many bytes:", ser.in_waiting)
		buf = ser.read(ser.inWaiting())
		try:
			parser.parse(buf)
		except Exception as e:
			print("Error parsing image.")
			print(e)

	ser.close()  # Close the serial connection

if __name__ == '__main__':
	start_depth_sensor()
