import serial
import time

# Adjust the COM port and baud rate as needed
COM_PORT = "/dev/tty.usbserial-202206_0CBF5B0"  # Change this to your actual COM port
BAUD_RATE = 2000000

def main():
    # Initialize serial connection
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Wait for the connection to be established

    try:
        # Send command to get distance
        distance_cmd = "AT+DISP=3\r"  # Adjust command if necessary
        ser.write(distance_cmd.encode('utf-8'))

        # Allow some time for the device to respond
        time.sleep(5)

        # Read response
        print("Reading this many bytes:", ser.in_waiting)
        response = ser.read(ser.inWaiting())

        print("Distance response:", response)

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