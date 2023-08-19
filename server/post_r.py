import requests

data_payload = {
    "gateway_ID": "bob_gateway", 
    "datetime": "190820230005", 
    "light": [11.0, 10.0, 23.0, 30.0, 40.0], 
    "temperature": [11.0, 10.0, 30.0, 301.0, 20.0], 
    "deflection": [-200.0, 10.0, 110.0, 40.0, 80.0]
}


response = requests.post("https://granlund.protopaja.aalto.fi", 
    json=data_payload,
    headers={"Content-Type": "application/json"},
)

'''

import requests

data_payload = {
    "gateway_ID": "bob_gateway", 
    "datetime": "160820232355", 
    "light": [11.0, 10.0, 23.0, 30.0, 0.0], 
    "temperature": [11.0, 10.0, 30.0, 101.0, 0.0], 
    "deflection": [200.0, 10.0, 30.0, 40.0, 0.0]
}


response = requests.post("https://granlund.protopaja.aalto.fi", 
    json=data_payload,
    headers={"Content-Type": "application/json"},
)

'''