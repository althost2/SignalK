
#Connect by BLEDevice

"""
import asyncio
import platform
import sys

from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError


ADDRESS = (
    "DC:0D:30:70:3C:E0"
    if platform.system() != "Darwin"
    else "B9EA5233-37EF-4DD6-87A8-2A875E821C46"
)


async def main(ble_address):
    device = await BleakScanner.find_device_by_address(ble_address, timeout=20.0)
    if not device:
        raise BleakError(f"A device with address {ble_address} could not be found.")
    async with BleakClient(device) as client:
        svcs = await client.get_services()
        print("Services:")
        for service in svcs:
            print(service)


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) == 2 else ADDRESS))

import sys
import platform
import asyncio
import logging

from bleak import BleakClient

logger = logging.getLogger(__name__)

ADDRESS = (
    "DC:0D:30:70:3C:E0"
    if platform.system() != "Darwin"
    else "B9EA5233-37EF-4DD6-87A8-2A875E821C46"
)


async def main(address):
    async with BleakClient(address) as client:
        logger.info(f"Connected: {client.is_connected}")

        for service in client.services:
            logger.info(f"[Service] {service}")
            for char in service.characteristics:
                if "read" in char.properties:
                    try:
                        value = bytes(await client.read_gatt_char(char.uuid))
                        logger.info(
                            f"\t[Characteristic] {char} ({','.join(char.properties)}), Value: {value}"
                        )
                    except Exception as e:
                        logger.error(
                            f"\t[Characteristic] {char} ({','.join(char.properties)}), Value: {e}"
                        )

                else:
                    value = None
                    logger.info(
                        f"\t[Characteristic] {char} ({','.join(char.properties)}), Value: {value}"
                    )

                for descriptor in char.descriptors:
                    try:
                        value = bytes(
                            await client.read_gatt_descriptor(descriptor.handle)
                        )
                        logger.info(f"\t\t[Descriptor] {descriptor}) | Value: {value}")
                    except Exception as e:
                        logger.error(f"\t\t[Descriptor] {descriptor}) | Value: {e}")
        try:
            device_name = await client.read_gatt_char("0xFFE4")
            print("Device Name: {0}".format("".join(map(chr, device_name))))
        except Exception:
            print("Uh oh")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main(sys.argv[1] if len(sys.argv) == 2 else ADDRESS))
"""

import sys
import asyncio
import platform

from bleak import BleakClient


# you can change these to match your device or override them from the command line
CHARACTERISTIC_UUID = "0000ffe4-0000-1000-8000-00805f9b34fb"
ADDRESS = (
    "DC:0D:30:70:3C:E0"
)


def notification_handler(sender, data):
    """Simple notification handler which prints the data received."""
    print("{0}: {1}".format(sender, data))
    hexadecimal_string = data.hex()
    scale = 16 ## equals to hexadecimal
    num_of_bits = 48

    binary_str=bin(int(hexadecimal_string, scale))[2:].zfill(num_of_bits)
    r1=binary_str[0:8]
    r2=binary_str[8:16]
    r3=binary_str[16:24]
    r4=binary_str[24:32]
    r5=binary_str[32:40]
    r6=binary_str[40:48]
    
    print (r1,r2,r3,r4,r5,r6)
    
    data=r4+r3
    print(data)
    
    dec_data=int(data, 2)
    perc=0
    if (dec_data <2000):
        perc=0
    if( dec_data>4067 ):
        perc=80
    if(dec_data>=2000 and dec_data<=4067):
        perc=0.03881*dec_data-77.6
    print(perc)

async def main(address, char_uuid):
    async with BleakClient(address) as client:
        print(f"Connected: {client.is_connected}")

        await client.start_notify(char_uuid, notification_handler)
        await asyncio.sleep(5.0)
        await client.stop_notify(char_uuid)


if __name__ == "__main__":
    asyncio.run(
        main(
            sys.argv[1] if len(sys.argv) > 1 else ADDRESS,
            sys.argv[2] if len(sys.argv) > 2 else CHARACTERISTIC_UUID,
        )
    )
