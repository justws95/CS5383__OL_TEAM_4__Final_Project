import asyncio
from bleak import BleakScanner, BleakClient, BleakError

address = "C0:35:EB:5B:29:D2"

async def main(address):
    async with BleakClient(address) as client:
        print("Services:")
        for service in client.services:
            print(service)

        print("Characteristics:")
        for characteristic in client.services.characteristics:
            print(characteristic)
            char_s = client.services.get_characteristic(characteristic)
            print(f" --> {char_s}")
            try:
                str_rep = await client.read_gatt_char(characteristic)
                str_rep = str_rep.decode('utf-8')
                print(f" --> {str_rep}")
            except:
                pass
            

        print("Descriptors:")
        for descriptor in client.services.descriptors:
            print(descriptor)



asyncio.run(main(address=address))

print("Done here...")

