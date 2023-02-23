
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
    file_name = "CI_SSIDs_"
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

def GetNetworks(oids,key):
    print("[~] Retrieving network identities and names...")
    headers = {
                 "X-Cisco-Meraki-API-Key":key
              }
    for id in oids:
        net_url = "https://api.meraki.com/api/v1/organizations/{0}/networks?perPage=100000".format(id)
        req = requests.get(headers=headers,url=net_url,timeout=15)
        networks = []
        if(req.status_code == 200):
            content  = req.json()
            for network in content:
                network_id   = network['id']
                network_name = network['name']
                if('Modem' not in network_name):
                    if(len(network_name) >= 31):
                        network_name = network_name[0:30]
                        networks.append([network_id,network_name])
                    else:
                        networks.append([network_id,network_name])
    return networks


def RetrieveSSIDs(nets,key):
    print("[~] Retrieving SSIDs from each site...")
    headers = {
                 "X-Cisco-Meraki-API-Key":key
              }
    fileName = GenFileName()
    workbook = xlsxwriter.Workbook(fileName)
    for net in nets:
        network_id   = net[0]
        network_name = net[1]
        if(("RNO" in network_name) or ("CHO" in network_name) or ("DCA" in network_name) or ("DFW" in network_name)):
            print("[~] Processing: %s " % network_name)
            url = "https://api.meraki.com/api/v1/networks/{0}/wireless/ssids".format(network_id)
            req = requests.get(headers=headers,url=url,timeout=30)
            if(req.status_code == 200):
                content = req.json()
                cur_max = 0
                col_hdr = []
                for listitem in range(0,len(content)):
                    if(len(content[listitem].keys()) > cur_max):
                        col_hdr = []
                        for entry in content[listitem].keys():
                            col_hdr.append(entry)
                        cur_max = len(content[listitem].keys())
                chars             = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
                limit             = len(col_hdr)
                current_iter      = 0
                alpha_iter        = 0
                col_index         = 1
                secondary_index   = 0
                col_hdr_index     = 0
                current_worksheet = workbook.add_worksheet(network_name)
                header_format     = workbook.add_format({'bold': True})
                enabled_format    = workbook.add_format({'bold': True, 'bg_color': 'green'})
                disabled_format   = workbook.add_format({'bold': True, 'bg_color': 'red'})
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
                        if(current_iter <= 25):
                            write_index = chars[char_index]+str(col_index)
                            current_worksheet.write(write_index,col_hdr[col_hdr_index],header_format)
                        current_iter += 1 ; char_index += 1 ; alpha_iter += 1 ; col_hdr_index += 1
                    if(current_iter > 50):
                        secondary_index += 1
                    char_index = 0
                    alpha_iter = 0
                row_index = 2 
                content = req.json()
                for entry in content:
                    temp_list    = []
                    temp_ind     = 0
                    for element in entry.keys():
                        if((element in col_hdr) and (temp_ind == col_hdr.index(element))):
                            temp_list.append(entry[element])
                            temp_ind += 1
                        else:
                            temp_list.append('')
                            temp_ind += 1
                    if(len(temp_list) < limit):
                        while(len(temp_list) <= limit):
                            temp_list.append(' ')
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
                                if((write_value == "True") and col_hdr[current_iter] == "lanIsolationEnabled"):
                                    current_worksheet.write(write_index,write_value,enabled_format)
                                elif((write_value == "False") and col_hdr[current_iter] == "lanIsolationEnabled"):
                                    current_worksheet.write(write_index,write_value,disabled_format)
                                else:
                                    current_worksheet.write(write_index,write_value)
                            if(current_iter <= 25):
                                write_index = chars[alpha_iter]+str(row_index)
                                write_value = str(temp_list[current_iter])
                                if((write_value == "True") and col_hdr[current_iter] == "lanIsolationEnabled"):
                                    current_worksheet.write(write_index,write_value,enabled_format)
                                elif((write_value == "False") and col_hdr[current_iter] == "lanIsolationEnabled"):
                                    current_worksheet.write(write_index,write_value,disabled_format)
                                else:
                                    current_worksheet.write(write_index,write_value)
                            current_iter += 1 ; char_index += 1 ; alpha_iter += 1
                        if(current_iter > 50):
                            secondary_index += 1
                        char_index = 0
                        alpha_iter = 0
                    current_iter  = 0
                    row_index += 1
    workbook.close()
    print("[*] SSID L2 Isolation report file located at: %s " % fileName)

def main():
    print("Retrieve SSIDs from each site ")
    url  = "https://api.meraki.com/api/v1/organizations"
    key  = input("[+] Enter the Meraki API Key-> ")
    ids  = GetOrganizationID(url,key) 
    nets = GetNetworks(ids,key) 
    RetrieveSSIDs(nets,key)

if(__name__ == '__main__'):
    main()