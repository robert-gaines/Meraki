
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
    file_name = "CI_Meraki_Device_Statuses_"
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

def AssignStatusIndicator(status):
    status_values = {
                        'online':'green',
                        'offline':'red',
                        'alerting':'yellow',
                        'dormant':'gray'
                    }
    try:
        indicator = status_values[status]
    except:
        indicator = 'gray'
    return indicator
    

def GetDeviceStatuses(orgs,key):
    print("[~] Retrieving device statuses by organization...")
    headers = {
                 "X-Cisco-Meraki-API-Key":key
              }
    fileName      = GenFileName()
    workbook      = xlsxwriter.Workbook(fileName)
    header_format = workbook.add_format({'bold': True})
    for org in orgs:
        col_hdr  = []
        print("[~] Processing organization ID: %s " % org)
        url = "https://api.meraki.com/api/v1/organizations/{0}/devices/statuses".format(org)
        req = requests.get(headers=headers,url=url,timeout=15)
        content = req.json()
        if(content):
            for entry in content:
                for key_value in entry.keys():
                    if(key_value not in col_hdr):
                        col_hdr.append(key_value)
            chars    = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
            limit    = len(col_hdr)
            current_iter      = 0
            alpha_iter        = 0
            col_index         = 1
            secondary_index   = 0
            col_hdr_index     = 0
            current_worksheet = workbook.add_worksheet(org)
            while(current_iter < limit-1):
                char_index = 0
                if(current_iter == limit):
                    break
                while(alpha_iter <= 25):
                    if(current_iter == limit):
                        break
                    if(current_iter > 25):
                        write_index = chars[secondary_index]+chars[alpha_iter]+str(col_index)
                        current_worksheet.write(write_index,col_hdr[col_hdr_index],header_format)
                    if(current_iter < 25):
                        write_index = chars[char_index]+str(col_index)
                        current_worksheet.write(write_index,col_hdr[col_hdr_index],header_format)
                    current_iter += 1 ; char_index += 1 ; alpha_iter += 1 ; col_hdr_index += 1
                if(current_iter > 50):
                    secondary_index += 1
                char_index = 0
                alpha_iter = 0
            row_index = 2 
            for entry in content:
                temp_list  = []
                temp_index = 0
                for item in entry.keys():
                    if(item == col_hdr[temp_index]):
                        temp_list.append(entry[item])
                    else:
                        temp_list.append(' ')
                    temp_index += 1
                if(len(temp_list) < len(col_hdr)):
                    while(len(temp_list) <= len(col_hdr)):
                        temp_list.append(' ')
                current_iter      = 0
                alpha_iter        = 0
                secondary_index   = 0
                status            = temp_list[5]
                indicator         = AssignStatusIndicator(status)
                temp_format       = workbook.add_format({'bold': True, 'bg_color': indicator})
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
                            current_worksheet.write(write_index,write_value,temp_format)
                        if(current_iter <= 25):
                            write_index = chars[alpha_iter]+str(row_index)
                            write_value = str(temp_list[current_iter])
                            current_worksheet.write(write_index,write_value,temp_format)
                        current_iter += 1 ; char_index += 1 ; alpha_iter += 1
                    if(current_iter > 50):
                        secondary_index += 1
                    char_index = 0
                    alpha_iter = 0
                current_iter  = 0
                row_index += 1
    workbook.close()
    print("[*] Device status file located at: %s " % fileName)

def main():
    print("[*] Get Meraki device statuses")
    url  = "https://api.meraki.com/api/v1/organizations"
    key  = input("[+] Enter the Meraki API Key-> ")
    ids  = GetOrganizationID(url,key)
    GetDeviceStatuses(ids,key)

if(__name__ == '__main__'):
    main()