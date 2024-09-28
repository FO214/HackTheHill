import serial
import time
import struct

def parse_image_data(data):
    """Parse the image data from the received bytes."""
    # Check if we have enough data for a complete packet
    if len(data) < 6:  # Minimum length for a valid packet
        return []

    # Extract the packet length
    try:
        packet_length = struct.unpack('<H', data[2:4])[0]  # Read the packet length
        total_length = 4 + packet_length + 2  # 4 bytes for header and length + packet length + 2 bytes for checksum/footer
        
        # Ensure we have the full packet
        if len(data) < total_length:
            return []  # Not enough data

        # Extract image data based on length
        image_data = data[4:4+packet_length]  # Extract image data
        
        # Assuming each pixel is represented by a single byte for simplicity
        pixel_values = list(image_data)  # Convert byte data to list of pixel values

    except Exception as e:
        print(f"Error parsing image data: {e}")
        return []

    return pixel_values

def calculate_distance_from_center(serial_port, image_size=100):
    """Continuously read data from the sensor and calculate the distance to the center object."""
    # Configure the serial port
    ser = serial.Serial(serial_port, baudrate=2000000, timeout=1)

    # Send command to start data capture (adjust command as needed)
    ser.write(b'AT+BINN=1\r\n')  # Example command to set binning, adjust as needed
    time.sleep(2)  # Wait for the sensor to respond

    while True:
        # Read a line of data from the sensor
        data = ser.readline().strip()

        # Print the raw data for debugging
        print(f"Raw data received: {data}")

        if data.startswith(b'ERROR') or data.startswith(b'OK'):
            # Ignore non-image data
            continue

        # Parse the image data to get pixel values
        pixel_values = parse_image_data(data)

        if pixel_values:
            # Get the center pixel value
            center_pixel_value = pixel_values[(image_size // 2) * image_size + (image_size // 2)]
            distance = (center_pixel_value / 5.1) ** 2
            print(f"Distance to center object: {distance:.2f} units")
        else:
            print("No valid image data received.")

if __name__ == "__main__":
    # Call the function with your serial port
    calculate_distance_from_center('/dev/tty.usbserial-202206_0CBF5B0')  # Replace with your actual serial port
