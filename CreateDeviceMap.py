#!/usr/bin/env python3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
import datetime
import requests
import folium
import json
import time
import sys
import os

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def GenerateMapFileName():    
    timestamp = time.ctime()
    replace_colons = timestamp.replace(":",'_')
    final_timestamp = replace_colons.replace(" ","_")
    map_file = "CI_Appliance_Map_"+final_timestamp+'.html'
    return map_file

def PlotDevices(devices):
        print("[~] Plotting devices...")
        map_limit = [40,-101]
        m = folium.Map(location=map_limit)
        m.add_child(folium.LatLngPopup())
        for entry in devices:
            time.sleep(1)
            hostname      = ''
            serial        = ''
            mac           = ''
            netid         = ''
            prod_type     = ''
            model         = ''
            address       = ''
            latitude      = ''
            longitude     = ''
            notes         = ''
            tags          = ''
            config_update = ''
            firmware      = ''
            url           = ''
            try:
                hostname      = str(entry['name'])
                serial        = str(entry['serial'])
                mac           = str(entry['mac'])
                netid         = str(entry['networkId'])
                prod_type     = str(entry['productType'])
                model         = str(entry['model'])
                address       = str(entry['address'])
                latitude      = str(entry['lat'])
                longitude     = str(entry['lng'])
                notes         = str(entry['notes']) 
                tags          = str(entry['tags'])
                config_update = str(entry['configurationUpdatedAt'])
                firmware      = str(entry['firmware'])
                url           = str(entry['url'])
                if_val  = "NAME:            %s <br>" % hostname
                if_val += "SERIAL:          %s <br>" % serial
                if_val += "MAC:             %s <br>" % mac
                if_val += "NETID:           %s <br>" % netid
                if_val += "PRODUCT:         %s <br>" % prod_type
                if_val += "MODEL:           %s <br>" % model
                if_val += "ADDRESS:         %s <br>" % address
                if_val += "LATITUDE:        %s <br>" % latitude
                if_val += "LONGITUDE:       %s <br>" % longitude
                if_val += "NOTES:           %s <br>" % notes
                if_val += "TAGS:            %s <br>" % tags 
                if_val += "CONFIG UPDATED:  %s <br>" % config_update
                if_val += "FIRMWARE:        %s <br>" % firmware
                if_val += "URL:             %s <br>" % url
                iframe = folium.IFrame(if_val)
                popup  = folium.Popup(iframe,min_width=500,max_width=500)
                folium.Marker(location=[float(latitude),float(longitude)],popup=popup,icon=folium.Icon(prefix="fa",icon="shield",color="blue")).add_to(m)
            except Exception as e:
                print("[!] Plotting Error: %s " % (e))
                pass
        map_name = GenerateMapFileName()
        print("[*] Device Map may be located at: %s " % map_name)
        m.save(map_name)

def GetOrganizationID(url,key):
    print("[~] Collecting organization IDs")
    headers = {
                 "X-Cisco-Meraki-API-Key":key
              }
    req = requests.get(headers=headers,url=url,timeout=5)
    ids = []
    if(req.status_code == 200):
        content = req.json()
        for item in content:
            for value in item.keys():
                if(value == 'id'):
                    ids.append(item[value])
    return ids

def GetOrganizationDevices(oid,url,key):
    print("[~] Collecting organization's devices")
    headers = {
                "X-Cisco-Meraki-API-Key":key
              }
    #
    devices = []
    #
    for id in oid:
        url = "https://api.meraki.com/api/v1/organizations/{0}/devices".format(id)
        req = requests.get(headers=headers,url=url,timeout=15)
        if(req.status_code == 200):
            content = req.json()
            for item in content:
                devices.append(item)
    return devices
                    
def main():
    print("Create a map of the organization's Devices")
    url  = "https://api.meraki.com/api/v1/organizations"
    key  = input("[+] Enter the Meraki API Key-> ")
    ids  = GetOrganizationID(url,key)
    devs = GetOrganizationDevices(ids,url,key)
    PlotDevices(devs)

if(__name__ == '__main__'):
    main()