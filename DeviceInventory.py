
import xlsxwriter
import random
import requests
import time
import sys

def TimeStamp():
    var         = time.ctime()
    sans_colons = var.replace(":","_")
    sans_spaces = sans_colons.replace(" ","_")
    timestamp   = sans_spaces
    return timestamp

def GenFileName():
    file_name = "CI_Network_Device_Inventory_"
    timestamp = TimeStamp()
    file_name += timestamp
    file_name += ".xlsx"
    return file_name

def GetOrganizationID(url,key):
    print("[~] Retrieving organization IDs...")
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

def GetDevices(key,ids):
    headers = {
                 "X-Cisco-Meraki-API-Key":key
              }
    devices       = []
    inventory     = []
    types         = []
    appliances    = 0
    cameras       = 0
    switches      = 0
    wireless      = 0
    cell_gateways = 0
    for id in ids:
        try:
            url = "https://api.meraki.com/api/v1/organizations/{0}/devices".format(id)
            req = requests.get(headers=headers,url=url,timeout=30)
            if(req.status_code == 200):
                content = req.json()
                if(content):
                    for item in content:
                        if(item['productType'] == 'appliance'):
                            appliances += 1
                        if(item['productType'] == 'camera'):
                            cameras    += 1
                        if(item['productType'] == 'switch'):
                            switches   += 1
                        if(item['productType'] == 'wireless'):
                            wireless += 1
                        if(item['productType'] == 'cellularGateway'):
                            cell_gateways += 1
                        for element in item.keys():
                            if(item['productType'] not in types):
                                types.append(item['productType'])
                            name   = item['name']
                            serial = item['serial']
                            if(name not in devices):
                                devices.append(name)
                                inventory.append(item)
        except Exception as e:
            print("[!] Exception: %s " % e)
            time.sleep(1)
            pass
    print("[*] Located the following: ")
    print("[*] Appliance Count:        {0}".format(appliances))
    print("[*] Camera Count:           {0}".format(cameras))
    print("[*] Switch Count:           {0}".format(switches))
    print("[*] Wireless AP Count:      {0}".format(wireless))
    print("[*] Cellular Gateway Count: {0}".format(cell_gateways))
    return [types,inventory]

def CreateInventory(inventory):
    chars    = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    types    = inventory[0]
    devices  = inventory[1]
    limit    = len(devices[0])
    fileName = GenFileName()
    workbook = xlsxwriter.Workbook(fileName)
    for device in types:
        current_worksheet = workbook.add_worksheet(device)
        row_index = 1
        time.sleep(1)
        for entry in devices:
            if(entry['productType'] == device):
                temp_list = []
                for item in entry.keys():
                    temp_list.append(entry[item])
                current_iter      = 0
                alpha_iter        = 0
                secondary_index   = 0
                while(current_iter < limit-1):
                    char_index = 0
                    if(current_iter == limit):
                        break
                    while(alpha_iter <= 25):
                        if(current_iter == limit):
                            break
                        if(current_iter > 25):
                            write_index = chars[secondary_index]+chars[alpha_iter]+str(row_index)
                            write_value = str(temp_list[current_iter])
                            current_worksheet.write(write_index,write_value)
                        if(current_iter < 25):
                            write_index = chars[alpha_iter]+str(row_index)
                            write_value = str(temp_list[current_iter])
                            current_worksheet.write(write_index,write_value)
                        current_iter += 1 ; char_index += 1 ; alpha_iter += 1
                    if(current_iter > 50):
                        secondary_index += 1
                    char_index = 0
                    alpha_iter = 0
                current_iter  = 0
                row_index += 1
    workbook.close()
    print("[*] Network device inventory file located at: %s " % fileName)

def main():
    print("[*] Meraki Device Inventory ")
    url      = "https://api.meraki.com/api/v1/organizations"
    key      = input("[+] Enter the Meraki API Key-> ")
    ids      = GetOrganizationID(url,key) 
    devices  = GetDevices(key,ids)
    CreateInventory(devices)

if(__name__ == '__main__'):
    main()