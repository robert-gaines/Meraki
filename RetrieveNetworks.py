
import xlsxwriter
import requests
import time
import sys

def GenFileName():
    file_name = "Meraki_VLANs_"
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
    req = requests.get(headers=headers,url=url,timeout=5)
    if(req.status_code == 200):
        content = req.json()
        org_id = content[0]['id']
        print("[*] Located Organization ID: %s " % org_id)
        return org_id
    else:
        sys.exit()

def GetNetworks(url,key):
    headers = {
                 "X-Cisco-Meraki-API-Key":key
              }
    req = requests.get(headers=headers,url=url,timeout=5)
    network_names = []
    network_ids   = []
    net_dict      = {}
    if(req.status_code == 200):
        content  = req.json()
        networks = content
        fileName        = GenFileName()
        workbook        = xlsxwriter.Workbook(fileName)
        for network in networks:
            for entry in network.keys():
                id = network['id']
                name = network['name']
            if(name not in network_names):
                network_names.append(name)
                network_ids.append(id)
                net_dict[id] = name
        for network in net_dict.keys():
            id   = network
            name = net_dict[network]
            if("Modem" in name):
                name = name[0:9]
                name += '-Modem'
            if(len(name) >= 31):
                name = name[0:29]
            current_worksheet = workbook.add_worksheet(name)    
            print("[~] Retrieving VLANs for: %s " % name)
            vlan_url = "https://api.meraki.com/api/v1/networks/{0}/appliance/vlans".format(id)
            req      = requests.get(headers=headers,url=vlan_url,timeout=15)
            if(req.status_code == 200):
                content           = req.json()
                site_data         = content[0]
                col_header_list = []
                chars = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
                for entry in site_data.keys():
                    if(entry not in col_header_list):
                        col_header_list.append(entry)
                limit             = len(col_header_list)
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
                            current_worksheet.write(write_index,col_header_list[col_hdr_index])
                            print("Writing",col_header_list[col_hdr_index])
                        if(current_iter < 25):
                            write_index = chars[char_index]+str(col_index)
                            current_worksheet.write(write_index,col_header_list[col_hdr_index])
                        current_iter += 1 ; char_index += 1 ; alpha_iter += 1 ; col_hdr_index += 1
                    if(current_iter > 50):
                        secondary_index += 1
                    char_index = 0
                    alpha_iter = 0
                row_index = 2
                for item in content:
                    temp_list = []
                    for value in item.keys():
                        temp_list.append(item[value])
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
                time.sleep(5)
            else:
                pass
        workbook.close()
    else:
        sys.exit()

def main():
    print("Retrieve the organization's networks")
    key        = input("[+] Enter the Meraki API Key-> ")
    org_url    = "https://api.meraki.com/api/v1/organizations"
    org_id     = GetOrganizationID(org_url,key)
    net_url    = "https://api.meraki.com/api/v1/organizations/{0}/networks?perPage=100000".format(org_id)
    GetNetworks(net_url,key)
    
if(__name__ == '__main__'):
    main()