
import xlsxwriter
import requests
import random
import time

def TimeStamp():
    var         = time.ctime()
    sans_colons = var.replace(":","_")
    sans_spaces = sans_colons.replace(" ","_")
    timestamp   = sans_spaces
    return timestamp

def GenFileName():
    file_name = "Meraki_Inventory_"
    timestamp = TimeStamp()
    file_name += timestamp
    file_name += ".xlsx"
    return file_name

def GetNetworkIDs(url,key):
    network_ids = []
    headers = {
                 "X-Cisco-Meraki-API-Key":key
              }
    req = requests.get(headers=headers,url=url,timeout=5)
    if(req.status_code == 200):
        content = req.json()
        for item in content:
            for value in item.keys():
                #print(value,'->',item[value])
                name_value = item['name']
                network_id = item['id']
                print("Name       -> %s " % name_value)
                print("Network ID -> %s " % network_id)
                if(network_id not in network_ids):
                    network_ids.append(network_id)
    return network_ids
    
def GetDeviceData(key,ids):
    headers = {
                 "X-Cisco-Meraki-API-Key":key
              }
    filename   = GenFileName()
    workbook   = xlsxwriter.Workbook(filename)
    worksheets = []
    for id in ids:
        try:
            url = "https://api.meraki.com/api/v1/networks/{0}/devices".format(id)
            req = requests.get(headers=headers,url=url,timeout=30)
            if(req.status_code == 200):
                content = req.json()
                try:
                    devname = content[0]['serial']
                except:
                    devname = "UnknownDevice-"+str(random.randint(100,999))
                print(devname)
                current_worksheet = workbook.add_worksheet(devname)
                for item in content:
                    row_index         = 1
                    for value in item.keys():
                        print(value,'->',item[value])
                        key_write_index = 'A'+str(row_index)
                        val_write_index = 'B'+str(row_index) 
                        current_worksheet.write(key_write_index,value)
                        current_worksheet.write(val_write_index,str(item[value]))
                        row_index += 1
        except Exception as e:
            print("[!] Exception: %s " % e)
            time.sleep(1)
            pass
    workbook.close()

def main():
    print("Retrieve Device Serials")
    oid     = "249996"
    url     = "https://api.meraki.com/api/v1/organizations/{0}/networks".format(oid)
    key     = input("[+] Enter the Meraki API Key-> ")
    net_ids = GetNetworkIDs(url,key)
    devices = GetDeviceData(key,net_ids)

if(__name__ == '__main__'):
    main()