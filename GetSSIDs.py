
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
        print("[~] Processing: %s " % network_name)
        url = "https://api.meraki.com/api/v1/networks/{0}/wireless/ssids".format(network_id)
        req = requests.get(headers=headers,url=url,timeout=30)
        print(req.status_code)
        print(req.json())
        print()
        chars    = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        col_hdr  = [
                     'Number','Name','Enabled','Splash Page','SSSID Admin Access','Authentication Mode','IP Assignment Mode',
                     'Adult Content Filtering','DNS Rewrite','Minimum Bit Rate','Band Selection','Per Client Bandwidth Limit Up','Per Client Bandwidth Limit Down',
                     'Per SSID Bandwidth Limit Up','Per SSID Bandwidth Limit Down','Mandatory DHCP Enabled','Visible','Available on all IPs','Availability Tags','Speed Burst'
                   ]
        limit    = len(col_hdr)
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
                if(current_iter < 25):
                    write_index = chars[char_index]+str(col_index)
                    current_worksheet.write(write_index,col_hdr[col_hdr_index])
                current_iter += 1 ; char_index += 1 ; alpha_iter += 1 ; col_hdr_index += 1
            if(current_iter > 50):
                secondary_index += 1
            char_index = 0
            alpha_iter = 0
        row_index = 2 
        if(req.status_code == 200):
            content = req.json()
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
    workbook.close()
    print("[*] SSID inventory file located at: %s " % fileName)

def main():
    print("Retrieve SSIDs from each site ")
    url  = "https://api.meraki.com/api/v1/organizations"
    key  = input("[+] Enter the Meraki API Key-> ")
    ids  = GetOrganizationID(url,key) ; print(ids)
    nets = GetNetworks(ids,key) ; print(nets)
    RetrieveSSIDs(nets,key)

if(__name__ == '__main__'):
    main()