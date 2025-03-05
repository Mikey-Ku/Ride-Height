from machine import ADC, Pin
from time import sleep
import bluetooth
import struct

pot = ADC(Pin(26))  

# Initialize Bluetooth
ble = bluetooth.BLE()
ble.active(True)

# Function to encode potentiometer value
def encode_pot_value(value):
    return struct.pack('<H', value)  # Encode as little-endian unsigned short

# Function to advertise potentiometer value
def advertise_pot_value(value):
    payload = encode_pot_value(value)
    ble.gap_advertise(100, adv_data=payload)

sleep(60)

while True:
    # Read potentiometer value (0-6100)
    pot_value = pot.read_u16() - 3536
    
    # Advertise the potentiometer value over Bluetooth
    advertise_pot_value(pot_value)
    
    # Print the value for debugging
    print("Potentiometer Value:", pot_value)
    
    # Delay to avoid flooding
    sleep(1)
