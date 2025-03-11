import time
import board
from adafruit_ble import BLERadio
from adafruit_ble.advertising import Advertisement
from adafruit_ble.services.nordic import UARTService

# Set up the BLE radio
ble = BLERadio()

# Create the UART service
uart_service = UARTService()

# Create an advertisement to advertise the device
advertisement = Advertisement()
advertisement.name = "Pico1"  # Change to "Pico2" for the second peripheral

# Start advertising this peripheral
ble.start_advertising(advertisement)

# Wait for connection from the central device
print(f"{advertisement.name} is now advertising...")

while True:
    if ble.connected:
        print(f"{advertisement.name} is connected.")
        # Access UART service for communication
        uart = uart_service

        # Read data from the central device
        if uart.in_waiting:
            data = uart.read(uart.in_waiting)
            print(f"Received: {data.decode()}")

        # Send data to the central device
        uart.write("Data from Peripheral")
        time.sleep(1)
    else:
        print(f"{advertisement.name} is waiting for a connection.")
        time.sleep(1)
