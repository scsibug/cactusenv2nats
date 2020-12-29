from tmp102 import TMP102
from hih6130 import HIH6130
from cloudevents.http import CloudEvent, to_structured
import asyncio
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

import time

# TMP102 sensor
tmp = TMP102(units='K', address=0x49, busnum=1)
hih = HIH6130()

def make_hih6130_cloudevent():
    (temp,rh) = hih.readTemperature()
    # make cloudevent
    attributes = {
        "type": "com.wellorder.iot.indoorenv",
        "source": "https://cactus.wellorder.net/iot/tmp102",
        "datacontenttype": "application/json"
    }
    data = {"loc": "office",
            "dt": time.time(),
            "temp": temp,
            "humidity": rh,
            "sensorModel": "HIH6130"}
    event = CloudEvent(attributes, data)
    header, body = to_structured(event)
    return body

def make_tmp102_cloudevent():
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
    return body

async def run(loop):
    nc = NATS()
	
    await nc.connect("nats.wellorder.net:4222", loop=loop)
    while True: 
        await nc.publish("iot.indoorenv", make_tmp102_cloudevent())
        await nc.publish("iot.indoorenv", make_hih6130_cloudevent())
        await asyncio.sleep(1)
    # Terminate connection to NATS.
    await nc.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
    loop.close()
