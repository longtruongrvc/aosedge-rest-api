from urllib import request
from time import sleep
import datetime
import json
import random

HTTP_REQUESTS_RECEIVE_URL = "https://webhook.site/ada814c5-6c66-4538-93c6-cfe68d2779f9"
DELAY_TIME = 30

def dummy_sensor():
    sensor_data = random.randint(10,50)
    return sensor_data

def main():
    while True:
        json_data = {
            "Description": "Temperature sensor data monitoring",
            "Timestamp": datetime.datetime.now().isoformat(),
            "Temperature sensor": dummy_sensor()
        }
        params = json.dumps(json_data).encode('utf-8')
        try:
            send_data = request.Request(
                url     = HTTP_REQUESTS_RECEIVE_URL,
                data    = params,
                headers = {
                    'Content-Type': 'application/json'
                }
            )
            request.urlopen(send_data)
        except request.HTTPError as err:
            print(f"Unhandle exception: {err}")
        
        sleep(DELAY_TIME)
    
if __name__ == "__main__":
    main()