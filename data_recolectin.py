import serial
import csv
import struct

def main():
    port = 'COM5'   # Change this to match your system
    baudrate = 115200

    ser = serial.Serial(port, baudrate, timeout=1)

    print("Waiting for start byte (0x00)...")
    while True:
        byte = ser.read(1)
        if byte == b'\x00':
            print("Start byte received. Beginning data capture.")
            break

    with open('analog_readings.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['AnalogValue'])  # No timestamp, just value

        try:
            while True:
                chunk = ser.read(200)  # Read 100 samples at a time (2 bytes each)
                for i in range(0, len(chunk), 2):
                    if i + 2 <= len(chunk):
                        sample = struct.unpack('<H', chunk[i:i+2])[0]
                        writer.writerow([sample])
        except KeyboardInterrupt:
            print("Stopped by user.")
        finally:
            ser.close()

if __name__ == '__main__':
    main()
