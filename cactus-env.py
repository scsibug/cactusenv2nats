from tmp102 import TMP102
from cloudevents.http import CloudEvent, to_structured
import asyncio
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

import time

# TMP102 sensor
tmp = TMP102(units='K', address=0x49, busnum=1)

async def run(loop):
    nc = NATS()
	
    await nc.connect("nats.wellorder.net:4222", loop=loop)
    while True: 
        # Read temp 
        temp = tmp.readTemperature()
        # make cloudevent
        attributes = {
            "type": "com.wellorder.iot.indoorenv",
            "source": "https://cactus.wellorder.net/iot/tmp102",
            "datacontenttype": "application/json"
        }
        data = {"loc": "office",
                "dt": time.time(),
                "temp": temp,
                "sensorModel": "TMP102"}
        event = CloudEvent(attributes, data)
        header, body = to_structured(event)
        await nc.publish("iot.indoorenv", body)
        await asyncio.sleep(1)
    # Terminate connection to NATS.
    await nc.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.close()
