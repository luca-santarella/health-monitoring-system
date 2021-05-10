import asyncio
import os
import requests
import time

from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager

EMAIL = os.environ.get('email') or "email"
PASSWORD = os.environ.get('password') or "password"
channel_id = 
temp_field = 2

async def main():
    channel = 0 #heat lamp
    # Setup the HTTP client API from user-password
    http_api_client = await MerossHttpClient.async_from_user_password(email=EMAIL, password=PASSWORD)
    # Setup and start the device manager
    manager = MerossManager(http_client=http_api_client)
    await manager.async_init()
    # Retrieve all the MSS310 devices that are registered on this account
    await manager.async_device_discovery()
    plugs = manager.find_devices(device_name="Lampada Calore Bit")
    if(len(plugs)<1):
        print("No device found..")
    else:
        dev = plugs[channel]

        url = "https://api.thingspeak.com/channels/"+str(channel_id)+"/fields/"+str(temp_field)+"/last.json"
        try:
            while True:
                await dev.async_update()
            
                r = requests.get(url)
                json_resp = r.json()
                temp = json_resp["field2"]
                on_off = dev.is_on()
                if(float(temp) > 30):
                    if on_off:
                        print(f"Turning off {dev.name}")
                        await dev.async_turn_off(channel=channel)
                if(float(temp) < 20):
                    if not on_off:
                        print(f"Turning on {dev.name}...")
                        await dev.async_turn_on(channel=channel)
                await asyncio.sleep(60)
        except Exception as ex:
             print(ex)
             pass
            
            

    # Close the manager and logout from http_api
    manager.close()
    await http_api_client.async_logout()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
