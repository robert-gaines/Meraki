
import xlsxwriter
import requests
import json
import time
import sys

def TimeStamp():
    var         = time.ctime()
    sans_colons = var.replace(":","_")
    sans_spaces = sans_colons.replace(" ","_")
    timestamp   = sans_spaces
    return timestamp

def GenFileName():
    file_name = "CI_Appliance_VPN_Firewall_Policy_Data_"
    timestamp = TimeStamp()
    file_name += timestamp
    file_name += ".xlsx"
    return file_name

def GetOrganizationID(url,key):
    print("[~] Retrieving organization IDs...")
    headers = {
                 "X-Cisco-Meraki-API-Key":key
              }
    req = requests.get(headers=headers,url=url,timeout=15)
    ids = []
    if(req.status_code == 200):
        content = req.json()
        for item in content:
            for value in item.keys():
                if(value == 'id'):
                    ids.append(item[value])
    return ids

def RetrieveVPNPolicies(oids,key):
    print("[~] Retrieving site to site VPN data from each organization...")
    headers = {
                 "X-Cisco-Meraki-API-Key":key
              }
    fileName = GenFileName()
    workbook = xlsxwriter.Workbook(fileName)
    for id in oids:
        print("[~] Processing: %s " % id)
        sheetname = "VPN Firewall Policies - {0}".format(id)
        url = "https://api.meraki.com/api/v1/organizations/{0}/appliance/vpn/vpnFirewallRules".format(id)
        req = requests.get(headers=headers,url=url,timeout=30)
        if(req.status_code == 200):
            content  = req.json()
            content  = content['rules']
            chars    = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
            col_hdr  = ['Comment','Policy','Protocol','Source Port','Source CIDR','Destination Port','Destination CIDR','Syslog Enabled']
            limit    = len(col_hdr)
            current_iter      = 0
            alpha_iter        = 0
            col_index         = 1
            secondary_index   = 0
            col_hdr_index     = 0
            current_worksheet = workbook.add_worksheet(sheetname)
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
            if(not content):
                pass
            else:
                for entry in content:
                    temp_list = []
                    for value in entry.keys():
                        print(entry[value])
                        temp_list.append(entry[value])
                    if(len(temp_list) < limit):
                        while(len(temp_list) < limit):
                            temp_list.append('')
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
    print("[*] VPN Policy data file located at: %s " % fileName)

def main():
    print("Retrieve S2S VPN data from each appliance ")
    url  = "https://api.meraki.com/api/v1/organizations"
    key  = input("[+] Enter the Meraki API Key-> ")
    ids  = GetOrganizationID(url,key)
    RetrieveVPNPolicies(ids,key)

if(__name__ == '__main__'):
    main()