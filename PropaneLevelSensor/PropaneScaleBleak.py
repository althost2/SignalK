"""
Purpose: Connect BLE from Raspberry PI to YSN-PS1 Smart Propane Scale, and forward the information to SignalK

Author: Althost2
Date: 1/18/2022
History: Based on BLEAK BLE notification example.

"""
import sys
import asyncio
import platform
import time,  socket

from bleak import BleakClient

debug=1
SLEEP_TIME=60
# you can change these to match your device or override them from the command line
CHARACTERISTIC_UUID = "0000ffe4-0000-1000-8000-00805f9b34fb"
ADDRESS = (
    "DC:0D:30:70:3C:E0"
)


def notification_handler(sender, data):

#start converting the data to something readable.
    """Simple notification handler which prints the data received."""
    if(debug):
        print("{0}: {1}".format(sender, data))
    hexadecimal_string = data.hex()
    scale = 16 ## equals to hexadecimal
    num_of_bits = 48
#splitting out the 8-bit words
    binary_str=bin(int(hexadecimal_string, scale))[2:].zfill(num_of_bits)
    r1=binary_str[0:8]
    r2=binary_str[8:16]
    r3=binary_str[16:24]
    r4=binary_str[24:32]
    r5=binary_str[32:40]
    r6=binary_str[40:48]
    if(debug):
        print (r1,r2,r3,r4,r5,r6)
    
    #swapping the byte order
    data=r4+r3
    if(debug):
        print(data)
    
    #apply 20lb calculation for the tank
    dec_data=int(data, 2)
    perc=0.0
    if (dec_data <2000):
        perc=0
    if( dec_data>4067 ):
        perc=80
    if(dec_data>=2000 and dec_data<=4067):
        perc=0.03881*dec_data-77.6
    if(debug):
        print(perc)
        
    tperc=perc*100/100
        
#Connect and send data to SignalK
    #try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # socket.AF_INET is  Internet
    # socket.SOCK_DGRAM) is  UDP
    # SignalK_UPD_PORT=55557
    SignalK_UPD_PORT=20220

    SignalK='{"updates": [{"$source": "OrangePi","values":[ {"path":"tanks.lpg.0.currentLevel","value":'+format(tperc,'5.3f')+'}]}]}'
    print(SignalK)

    sock.sendto(SignalK.encode(), ('192.168.1.168', SignalK_UPD_PORT))
    sock.close
    #except:
       # print ("Signal K update failed: lpg tank level: ",perc)

async def main(address, char_uuid):
    i=1
    while (i==1):
        err=0;
        try:
            async with BleakClient(address) as client:
                print(f"Connected: {client.is_connected}")

                await client.start_notify(char_uuid, notification_handler)
                await asyncio.sleep(5.0)
                await client.stop_notify(char_uuid)
                err=0
        except:
            print("Connection Failed")
            err=1
          #  
        if(err==0):
            time.sleep (SLEEP_TIME)


if __name__ == "__main__":
    asyncio.run(
        main(
            sys.argv[1] if len(sys.argv) > 1 else ADDRESS,
            sys.argv[2] if len(sys.argv) > 2 else CHARACTERISTIC_UUID,
        )
    )
