import requests
import json
import configparser
from paepy.ChannelDefinition import CustomSensorResult


def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)


configfile = configparser.ConfigParser()
configfile.read("Ruckus_Wlan_Clients.ini")
result = CustomSensorResult()

# Parameters
cookie = requests.Session()
username = configfile["credentials"]["username"]
password = configfile["credentials"]["password"]
# Disable warnings, needs to be removed if valid certificate is in place.
requests.packages.urllib3.disable_warnings()

# Start Session
para_session = {"username": username, "password": password}
urlsession = "https://vsz.ant.int.infrastay.be:8443/wsg/api/public/v8_2/session"
session = cookie.post(urlsession, json=para_session, verify=False)

# Get session Info
# call = cookie.get(urlsession, verify=False)
# jprint(call.json())

# Get ZoneID
urlzones = "https://vsz.ant.int.infrastay.be:8443/wsg/api/public/v8_2/rkszones"
call = cookie.get(urlzones, verify=False)
for zones in call.json()["list"]:
    if "Default" in zones["name"]:
        defaultzoneid = zones['id']

# Get Wlan Details
wlannames = []
wlanclients = []
para_session = {
    "filters": [
        {
            "type": "DOMAIN",
            "value": "8b2081d5-9662-40d9-a3db-2a3cf4dde3f7"
        }
    ],
    "fullTextSearch": {
        "type": "AND",
        "value": ""
    },
    "attributes": [
        "*"
    ]
}
urlwlans = "https://vsz.ant.int.infrastay.be:8443/wsg/api/public/v8_2/query/wlan"
call = cookie.post(urlwlans, json=para_session, verify=False)
for wlans in call.json()["list"]:
    wlannames.append(wlans["name"])
    wlanclients.append(wlans["clients"])
for name, clients in zip(wlannames, wlanclients):
    result.add_channel(channel_name=name, value=clients, unit="Clients")

result.add_channel(channel_name="Total Clients", value=sum(wlanclients), unit="Clients", primary_channel=True, )

print(result.get_json_result())

# Delete Session
call = requests.delete(urlsession, verify=False)

# print(call.text)
# call = requests.get(urlsession, verify=False)
# print(call.text)
