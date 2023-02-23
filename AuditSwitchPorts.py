
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
    file_name = "CI_Switch_Ports_"
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
    devices   = []
    inventory = []
    for id in ids:
        try:
            url = "https://api.meraki.com/api/v1/organizations/{0}/devices".format(id)
            req = requests.get(headers=headers,url=url,timeout=30)
            if(req.status_code == 200):
                content = req.json()
                if(content):
                    for item in content:
                        for element in item.keys():
                            if(item['productType'] == 'switch'):
                                name   = item['name']
                                serial = item['serial']
                                if(name not in devices):
                                    devices.append(name)
                                    inventory.append([name,serial])
        except Exception as e:
            print("[!] Exception: %s " % e)
            time.sleep(1)
            pass
    return inventory

def AuditSwitchPorts(key,inventory):
    headers = {
                 "X-Cisco-Meraki-API-Key":key
              }
    chars    = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    col_hdr  = ['Port ID','Device Name','Tags','Port Enabled','PoE Enabled','Type','VLAN','Voice VLANs','Isolation Enabled','RTSP Enabled','STP Guard','Link Negotiation','Port Schedule ID','Unidirection Link Detection','Link Negotiation Capabilities','Access Policy Type']
    limit    = len(col_hdr)
    fileName = GenFileName()
    workbook = xlsxwriter.Workbook(fileName)
    for device in inventory:
        name              = device[0]
        serial            = device[1]
        current_worksheet = workbook.add_worksheet(name)
        current_iter      = 0
        alpha_iter        = 0
        col_index         = 1
        secondary_index   = 0
        col_hdr_index     = 0
        while(current_iter < limit-1):
            char_index = 0
            if(current_iter == limit):
                break
            while(alpha_iter <= 25):
                if(current_iter == limit):
                    break
                if(current_iter > 25):
                    write_index = chars[secondary_index]+chars[alpha_iter]+str(col_index)
                    current_worksheet.write(write_index,col_hdr[col_hdr_index])
                if(current_iter < 25):
                    write_index = chars[char_index]+str(col_index)
                    current_worksheet.write(write_index,col_hdr[col_hdr_index])
                current_iter += 1 ; char_index += 1 ; alpha_iter += 1 ; col_hdr_index += 1
            if(current_iter > 50):
                secondary_index += 1
            char_index = 0
            alpha_iter = 0
        row_index = 2
        print("[~] Processing: %s " % name)
        time.sleep(1)
        url = "https://api.meraki.com/api/v1/devices/{0}/switch/ports".format(serial)
        req = requests.get(headers=headers,url=url,timeout=15)
        if(req.status_code == 200):
            content = req.json()
            for entry in content:
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
    print("[*] Switchport inventory file located at: %s " % fileName)

def main():
    print("[*] Audit Switch Ports ")
    url      = "https://api.meraki.com/api/v1/organizations"
    key      = input("[+] Enter the Meraki API Key-> ")
    ids      = GetOrganizationID(url,key) 
    switches = GetDevices(key,ids)
    AuditSwitchPorts(key,switches)

if(__name__ == '__main__'):
    main()