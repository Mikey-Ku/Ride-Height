import time
import board
import busio
import adafruit_ble
from adafruit_ble import BLERadio
from adafruit_ble.advertising import Advertisement
from adafruit_ble.services.nordic import UARTService

# Create a BLE radio object
ble = BLERadio()

# Set up UART services for communication
uart_service = UARTService()


def scan_for_devices():
    print("Scanning for peripherals...")
    for advertisement in ble.start_scan(Advertisement, timeout=5):
        if advertisement.name == "Pico1" or advertisement.name == "Pico2":
            print(f"Found {advertisement.name}")
            return advertisement
    print("No devices found.")
    return None


# Function to connect to a peripheral and communicate
def connect_to_device(device):
    try:
        print(f"Connecting to {device.name}...")
        # Create a connection object
        peripheral = ble.connect(device)
        print(f"Connected to {device.name}")

        # Access the UART service to read/write data
        uart = peripheral[UARTService]

        # Send data to the peripheral
        uart.write("Hello from Central Pico")
        time.sleep(1)

        # Read data from the peripheral
        if uart.in_waiting:
            data = uart.read(uart.in_waiting)
            print(f"Received from {device.name}: {data.decode()}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Disconnect
        ble.disconnect(peripheral)
        print(f"Disconnected from {device.name}")


while True:
    device1 = scan_for_devices()
    if device1:
        connect_to_device(device1)

    device2 = scan_for_devices()
    if device2:
        connect_to_device(device2)

    time.sleep(2)  # Sleep between scans
