#!/usr/bin/env python3

import xlsxwriter
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
    file_name = "Meraki_Organization_Inventory_"
    timestamp = TimeStamp()
    file_name += timestamp
    file_name += ".xlsx"
    return file_name

def GetOrganizationID(url,key):
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
    headers = {
                "X-Cisco-Meraki-API-Key":key
              }
    chars    = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    col_hdr  = ['Name','Serial','MAC','Network ID','Product Type','Model','Address','Latitude','Longitude','Notes','Tags','LAN IP','Configuration Last Updated','Firmware','URL']
    limit    = len(col_hdr)
    fileName = GenFileName()
    workbook = xlsxwriter.Workbook(fileName)
    current_worksheet = workbook.add_worksheet('Device Inventory')
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
    for id in oid:
        url = "https://api.meraki.com/api/v1/organizations/{0}/devices".format(id)
        req = requests.get(headers=headers,url=url,timeout=5)
        if(req.status_code == 200):
            content = req.json()
            for item in content:
                temp_list = []
                for value in item.keys():
                    print(value,'->',item[value])
                    temp_list.append(item[value])
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
    print("[*] Organization device inventory file located at: %s " % fileName)

def main():
    print("Retrieve the Organization's Devices")
    url = "https://api.meraki.com/api/v1/organizations"
    key = input("[+] Enter the Meraki API Key-> ")
    ids = GetOrganizationID(url,key)
    GetOrganizationDevices(ids,url,key)

if(__name__ == '__main__'):
    main()