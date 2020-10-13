import scapy.all as scapy
import time
import json
import pymongo
import random
from pymongo import MongoClient
from yeelight import Bulb

client_list = []
identified_bulbs = []
power_status = ''
monitor_bulb = ''

cluster = MongoClient("mongodb+srv://MARCLDG:SIT31153HD@cluster0.f3acr.mongodb.net/Cluster0?retryWrites=true&w=majority")
db = cluster["changestream"]
collection = db["collection"]

arp_packet = scapy.ARP(pdst='192.168.0.1/24')
broadcast_packet = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
arp_broadcast_packet = broadcast_packet/arp_packet
answered_list = scapy.srp(arp_broadcast_packet, timeout=30, verbose=False)[0]


for element in answered_list:
    client_dict = {"ip": element[1].psrc, "mac": element[1].hwsrc}
    client_list.append(client_dict)


for client in client_list:
    if(client["mac"][0:8] == '5c:e5:0c'):
        
        check_status = Bulb(client["ip"])
        power_status = check_status.get_properties()['power']
        
        if power_status == 'on':
            status = True
        elif power_status == 'off':
            status = False
        
        bulbInDatabase = collection.find({"_id": client["ip"]})
        publishOnce = bulbInDatabase.count() > 0
        level = random.randint(1,2)
        
        if (publishOnce == False):
            identified_bulbs = {"_id": client["ip"], "mac_address": client["mac"], "status": status, "level": level}
            collection.insert_one(identified_bulbs)

change_stream = cluster.changestream.collection.watch()

for change in change_stream:
    print(change)
    status = change['updateDescription']['updatedFields']['status']
    if status == True:
        bulb_ip = (str(change['documentKey']['_id']))
        toggle_bulb = Bulb(bulb_ip)
        toggle_bulb.turn_on()
        print("on")
    elif status == False:
        bulb_ip = (str(change['documentKey']['_id']))
        toggle_bulb = Bulb(bulb_ip)
        toggle_bulb.turn_off()
        print("off")