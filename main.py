import serial
import time

# Adjust the COM port and baud rate as needed
COM_PORT = "/dev/ttyUSB0"  # Change this to your actual COM port
BAUD_RATE = 115200

def look_for_beginning(bytes):
	for i, b in enumerate(bytes):
		if b == 0x00 and i < len(bytes) and bytes[i+1] == 0xff:
			Parser(bytes[i:]).parse()

class Parser:
	def __init__(self, bytes):
		self.bytes = list(bytes)

	def next(self, n):
		nexts = self.bytes[0:n]
		self.bytes = self.bytes[n:]
		return nexts

	def expect(self, bytestring):
		for (b1, b2) in zip(bytestring, self.next(len(bytestring))):
			if b1 != b2:
				print(f"Error: expected {b1}, received {b2}")
				exit()

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
		check = self.next(1)[0]
		# this is supposed to be a check byte, but i could not get it working so assume it's correct

	def parse(self):
		self.skip_header()
		self.length = self.parse_length()
		self.other_content = self.parse_other_content()
		self.image = self.parse_image()
		self.parse_check()
		self.expect(b'\xdd')
		print("Image:", self.image)
		exit()


def main():
	# Initialize serial connection
	ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
	time.sleep(2)  # Wait for the connection to be established

	try:
		# Send command to get distance
		distance_cmd = "AT+DISP=3\r"  # Adjust command if necessary
		ser.write(distance_cmd.encode('utf-8'))

		# Allow some time for the device to respond

		# Read response
		buf = b''
		for _ in range(5):
			time.sleep(0.5)
			print("Reading this many bytes:", ser.in_waiting)
			response = ser.read(ser.inWaiting())
			buf += response
		look_for_beginning(buf)


		# time.sleep(1)
		# print(ser.readline())

	except KeyboardInterrupt:
		print("Program interrupted.")

	except Exception as e:
		print("Error:", e)

	finally:
		ser.close()  # Close the serial connection

if __name__ == '__main__':
	main()
