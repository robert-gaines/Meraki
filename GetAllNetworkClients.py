import xlsxwriter
import requests
import time
import sys

def GenFileName():
    file_name = "CI_All_Network_Clients_"
    timestamp = time.ctime()
    replace_colons = timestamp.replace(":",'_')
    final_timestamp = replace_colons.replace(" ","_")
    final_timestamp += ".xlsx"
    file_name += final_timestamp
    return file_name

def GetOrganizationID(url,key):
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
    headers = {
                 "X-Cisco-Meraki-API-Key":key
              }
    for id in oids:
        net_url    = "https://api.meraki.com/api/v1/organizations/{0}/networks?perPage=100000".format(id)
        req = requests.get(headers=headers,url=net_url,timeout=5)
        networks = []
        if(req.status_code == 200):
            content  = req.json()
            for network in content:
                network_id   = network['id']
                network_name = network['name']
                if('Modem' in network_name):
                    network_name = network_name[0:9]+"-Modem"
                if(len(network_name) >= 31):
                    network_name = network_name[0:30] 
                networks.append([network_id,network_name])
        return networks

def GetClients(nets,key):
    print("[~] Processing clients at each site")
    headers = {
                 "X-Cisco-Meraki-API-Key":key
              }
    chars    = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
    col_hdr  = ['ID','MAC','Description','IP','IP6','IP6-Local','User','First Seen','Last Seen','Manufacturer','OS','Device Type Prediciton','Recent Device Serial','Recent Device Name','Recent Device MAC','Recent Device Connection','SSID','VLAN','Switchport','Usage','Status','Notes','SMInstalled','Group Policy 802.1X','Adaptive Policy Group']
    limit    = len(col_hdr)
    fileName = GenFileName()
    workbook = xlsxwriter.Workbook(fileName)
    for net in nets:
        network_id   = net[0]
        network_name = net[1]
        print("[~] Processing: {0}".format(network_name))
        current_iter      = 0
        alpha_iter        = 0
        col_index         = 1
        secondary_index   = 0
        col_hdr_index     = 0
        current_worksheet = workbook.add_worksheet(network_name)
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
                    print("Writing",col_hdr[col_hdr_index])
                if(current_iter < 25):
                    write_index = chars[char_index]+str(col_index)
                    current_worksheet.write(write_index,col_hdr[col_hdr_index])
                current_iter += 1 ; char_index += 1 ; alpha_iter += 1 ; col_hdr_index += 1
            if(current_iter > 50):
                secondary_index += 1
            char_index = 0
            alpha_iter = 0
        row_index = 2 
        client_url   = "https://api.meraki.com/api/v1/networks/{0}/clients?perPage=1000".format(network_id)
        req          = requests.get(headers=headers,url=client_url,timeout=15)
        if(req.status_code == 200):
            content  = req.json()
            if(not content):
                pass
            else:
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
        time.sleep(1)
    workbook.close()
    print("[*] Network clients inventory file located at: %s " % fileName)

def main():
    print("Retrieve all network clients")
    key        = input("[+] Enter the Meraki API Key-> ")
    org_url    = "https://api.meraki.com/api/v1/organizations"
    oids       = GetOrganizationID(org_url,key)
    nets       = GetNetworks(oids,key)
    GetClients(nets,key)

if(__name__ == '__main__'):
    main()