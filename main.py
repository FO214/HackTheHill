import serial
import time

# Adjust the COM port and baud rate as needed
COM_PORT = "/dev/ttyUSB0"  # Change this to your actual COM port
BAUD_RATE = 115200

def look_for_beginning(bytes):
	for i, b in enumerate(bytes):
		if b == 0x00 and i < len(bytes) and bytes[i+1] == 0xff:
			length = bytes[i+2] * 256 + bytes[i+3]
			print("Starting found! length:", length)
			print("Total length", len(bytes))
			print("Starting index:", i)
			print("Ending byte:", bytes[i+length-20:i+length+20])
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
