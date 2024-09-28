import time
import serial

ser = serial.Serial(
	port = "/dev/ttyUSB0",
	baudrate = 115200,
	parity = serial.PARITY_NONE,
	stopbits = serial.STOPBITS_ONE
)

time.sleep(2)
while ser.inWaiting() > 0:
	print(ser.readline())

ser.close()
