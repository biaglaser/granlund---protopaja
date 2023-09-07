# THIS CODE IS FOR POPULATING THE DATABASE FOR TESTING PURPOSES. THESE VALUES ARE NOT REAL.
import requests

text_string = "354008 ad:4c:f9:d9:39:43 3ebfd403 354065 55:6f:c6:3a:6c:f8 a4886e83 354082 98:e2:8f:f5:b2:30 abb93723 354098 30:00:66:89:06:92 5883fc3a 354114 9d:7b:f8:69:0d:5a 5f55ee10 354128 bc:0f:a0:44:fb:73 6b424be0 354143 f1:38:20:ba:de:e7 50a92e8a 354158 97:ff:f9:22:d3:a6 9dcb149b 354172 c0:a6:c9:5f:69:df fe5ec831 354187 69:a4:ae:27:c1:5a ef0765a2 354201 1c:8f:6a:11:02:cd 2a009269 354216 fb:a0:ab:e2:e9:f2 f98ff605 354230 59:65:9d:43:4b:c8 aeb7f1b2 354244 fb:2f:9c:f5:14:4f 28668ac3 354258 23:ba:ff:d5:7b:1d 09f1d1d0 354272 77:a9:70:b0:b9:e5 6dacc696 354286 a1:c2:5b:f7:b5:b4 9d5b3722 354300 ba:7a:e8:b6:39:e6 48394527 354314 fe:a4:16:02:fa:9e 344695e7 354328 a7:1b:ef:de:43:ea 4d"
response = requests.post("https://granlund.protopaja.aalto.fi", data=text_string)


# THE FOLLOWING SCRIPTS WERE USED ON THE PREVIOUS ITERATION WHEN POST REQUESTS WERE DONE IN JSON FORMAT
'''import requests

data_payload = {
    "gateway_ID": "bob_gateway", 
    "datetime": "250820230010", 
    "light": [11.0, 0.0, 23.0, 30.0, 0.5], 
    "temperature": [11.0, 10.0, 30.0, 301.0, 20.0], 
    "deflection": [-200.0, 10.0, 110.0, 40.0, 80.0]
}


response = requests.post("https://granlund.protopaja.aalto.fi", 
    json=data_payload,
    headers={"Content-Type": "application/json"},
)'''

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