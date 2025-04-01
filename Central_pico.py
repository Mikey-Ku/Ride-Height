import aioble
import bluetooth
import asyncio
import struct
from sys import exit
import time

# Define UUIDs for the service and characteristic
_SERVICE_UUID = bluetooth.UUID(0x1848)
_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)

# IAM = "Central" # Change to 'Peripheral' or 'Central'
IAM = "Central"
IAM_SENDING_TO = "RHS"

if IAM not in ['RHS', 'Central']:
    print("IAM must be either Peripheral or Central")
    exit()

# Bluetooth parameters
BLE_NAME = f"{IAM}"  # You can dynamically change this if you want unique names
BLE_SVC_UUID = bluetooth.UUID(0x181A)
BLE_CHARACTERISTIC_UUID = bluetooth.UUID(0x2A6E)
BLE_APPEARANCE = 0x0300
BLE_ADVERTISING_INTERVAL = 2000
BLE_SCAN_LENGTH = 5000
BLE_INTERVAL = 30000
BLE_WINDOW = 30000

# state variables
message_count = 0

def encode_message(message):
    """ Encode a message to bytes """
    return message.encode('utf-8')

def decode_message(message):
    """ Decode a message from bytes """
    return message.decode('utf-8')

async def receive_data_task(characteristic):
    """ Receive data from the connected device """
    global message_count
    while True:
        try:
            data = await characteristic.read()

            if data:
                print(f"{IAM} received: {decode_message(data)}, count: {message_count}")
                await characteristic.write(encode_message("Got it"))
                await asyncio.sleep(0.5)

            message_count += 1
        except asyncio.TimeoutError:
            print(f"Timeout waiting for data in {BLE_NAME}.")
            break
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

async def ble_scan():
    """ Scan for a BLE device with the matching service UUID """
    print(f"Scanning for BLE Beacon named RHS...")
    async with aioble.scan(5000, interval_us=30000, window_us=30000, active=True) as scanner:
        async for result in scanner:
            if result.name() == IAM_SENDING_TO and BLE_SVC_UUID in result.services():
                print(f"found {result.name()} with service uuid {BLE_SVC_UUID}")
                return result
    return None

async def run_central_mode():
    """ Run the central mode """
    # Create a simple timestamp for the filename
    timestamp = str(int(time.time()))
    csv_filename = f"C:\\Users\\mkujr\\Downloads\\{timestamp}.csv"
    
    # Open the CSV file and write the header
    with open(csv_filename, 'w') as f:
        f.write("Timestamp,Data\n")
    
    # Start scanning for a device with the matching service UUID
    while True:
        device = await ble_scan()
        if device is None:
            continue
        print(f"device is: {device}, name is {device.name()}")
        try:
            print(f"Connecting to {device.name()}")
            connection = await device.device.connect()
        except asyncio.TimeoutError:
            print("Timeout during connection")
            continue
        print(f"{IAM} connected to {connection}")
        
        # Discover services
        async with connection:
            try:
                service = await connection.service(BLE_SVC_UUID)
                characteristic = await service.characteristic(BLE_CHARACTERISTIC_UUID)
            except (asyncio.TimeoutError, AttributeError):
                print("Timed out discovering services/characteristics")
                continue
            except Exception as e:
                print(f"Error discovering services {e}")
                await connection.disconnect()
                continue
            
            # Receive data and write to CSV without sending any data back
            async def receive_data_task_with_csv(characteristic):
                global message_count
                while True:
                    try:
                        data = await characteristic.read()
                        current_time = str(int(time.time()))
                        
                        if data:
                            decoded_data = decode_message(data)
                            print(f"{IAM} received: {decoded_data}, count: {message_count}")
                            
                            # Write data to CSV file
                            with open(csv_filename, 'a') as f:
                                f.write(f"{current_time},{decoded_data}\n")
                            
                            message_count += 1
                            await asyncio.sleep(0.5)
                    except asyncio.TimeoutError:
                        print(f"Timeout waiting for data in {BLE_NAME}.")
                        break
                    except Exception as e:
                        print(f"Error receiving data: {e}")
                        break
            
            tasks = [
                asyncio.create_task(receive_data_task_with_csv(characteristic)),
            ]
            await asyncio.gather(*tasks)
            await connection.disconnected()
            print(f"{BLE_NAME} disconnected from {device.name()}")
            break

async def main():
    """ Main function """
    tasks = [
        asyncio.create_task(run_central_mode()),
    ]
    await asyncio.gather(*tasks)

asyncio.run(main())

