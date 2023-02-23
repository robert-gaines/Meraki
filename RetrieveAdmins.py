
import xlsxwriter
import requests
import time
import sys

def GenFileName():
    file_name = "CI_Meraki_Admins_"
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
    ids = []
    if(req.status_code == 200):
        content = req.json()
        for item in content:
            for value in item.keys():
                if(value == 'id'):
                    ids.append(item[value])
    return ids

def GetAdministrators(org_ids,key):
    headers = {
                 "X-Cisco-Meraki-API-Key":key
              }
    fileName        = GenFileName()
    #workbook        = xlsxwriter.Workbook(fileName)
    for id in org_ids:
        net_url = "https://api.meraki.com/api/v1/organizations/{0}/admins".format(id)
        req     = requests.get(headers=headers,url=net_url,timeout=5)
        if(req.status_code == 200):
            content        = req.json()
            administrators = content
            for admin in administrators:
                print(admin)
                print()
        #     current_worksheet = workbook.add_worksheet('CI Meraki Admins')    
        #     col_header_list = []
        #     chars = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        #     for entry in site_data.keys():
        #         if(entry not in col_header_list):
        #             col_header_list.append(entry)
        #     limit             = len(col_header_list)
        #     current_iter      = 0
        #     alpha_iter        = 0
        #     col_index         = 1
        #     secondary_index   = 0
        #     col_hdr_index     = 0
        #     while(current_iter < limit-1):
        #         char_index = 0
        #         if(current_iter == limit):
        #             break
        #         while(alpha_iter <= 25):
        #             if(current_iter == limit):
        #                 break
        #             if(current_iter > 25):
        #                 write_index = chars[secondary_index]+chars[alpha_iter]+str(col_index)
        #                 current_worksheet.write(write_index,col_header_list[col_hdr_index])
        #             if(current_iter < 25):
        #                 write_index = chars[char_index]+str(col_index)
        #                 current_worksheet.write(write_index,col_header_list[col_hdr_index])
        #             current_iter += 1 ; char_index += 1 ; alpha_iter += 1 ; col_hdr_index += 1
        #         if(current_iter > 50):
        #             secondary_index += 1
        #         char_index = 0
        #         alpha_iter = 0
        #     row_index = 2
        #     for item in content:
        #         temp_list = []
        #         for value in item.keys():
        #             temp_list.append(item[value])
        #         current_iter      = 0
        #         alpha_iter        = 0
        #         secondary_index   = 0
        #         while(current_iter < limit-1):
        #             char_index = 0
        #             if(current_iter == limit):
        #                 break
        #             while(alpha_iter <= 25):
        #                 if(current_iter == limit):
        #                     break
        #                 if(current_iter > 25):
        #                     write_index = chars[secondary_index]+chars[alpha_iter]+str(row_index)
        #                     write_value = str(temp_list[current_iter])
        #                     current_worksheet.write(write_index,write_value)
        #                 if(current_iter < 25):
        #                     write_index = chars[alpha_iter]+str(row_index)
        #                     write_value = str(temp_list[current_iter])
        #                     current_worksheet.write(write_index,write_value)
        #                 current_iter += 1 ; char_index += 1 ; alpha_iter += 1
        #             if(current_iter > 50):
        #                 secondary_index += 1
        #             char_index = 0
        #             alpha_iter = 0
        #         current_iter  = 0
        #         row_index += 1
        # else:
        #     pass
        # workbook.close()
    else:
        sys.exit()

def main():
    print("Retrieve the organization's administrators ")
    key        = input("[+] Enter the Meraki API Key-> ")
    org_url    = "https://api.meraki.com/api/v1/organizations"
    org_ids     = GetOrganizationID(org_url,key)
    GetAdministrators(org_ids,key)
    
if(__name__ == '__main__'):
    main()