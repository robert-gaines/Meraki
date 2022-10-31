#!/usr/bin/env python3

import xlsxwriter
import requests
import time
import sys

def GetOrganizationID(url,key):
    headers = {
                 "X-Cisco-Meraki-API-Key":key
              }
    ids = []
    req = requests.get(headers=headers,url=url,timeout=5)
    if(req.status_code == 200):
        content = req.json()
        for item in content:
            for value in item.keys():
                id = item['id']
                if(id not in ids):
                    ids.append(id)
                print(item['id'],'->',item['name'])
    print("[*] Located the following unique id values: ")
    for id in ids:
        print(id)
    return ids

def GetOrganizationDevices(ids,url,key):
    headers = {
                "X-Cisco-Meraki-API-Key":key
              }
    for id in ids:
        url = "https://api.meraki.com/api/v1/organizations/{0}/devices".format(id)
        req = requests.get(headers=headers,url=url,timeout=15)
        print(req.status_code)
        if(req.status_code == 200):
            content = req.json()
            for item in content:
                for value in item.keys():
                    print(value,'->',item[value])
        time.sleep(3)

def main():
    print("Retrieve the Network ID(s)")
    oid = "249996"
    url = "https://api.meraki.com/api/v1/organizations/{0}/networks".format(oid)
    key = input("[+] Enter the Meraki API Key-> ")
    ids = GetOrganizationID(url,key)
    GetOrganizationDevices(ids,url,key)

if(__name__ == '__main__'):
    main()