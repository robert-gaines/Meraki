
import requests

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
                print(value,'->',item[value])
                if(value == 'id'):
                    ids.append(item[value])
    return ids

def main():
    print("Retrieve the organization ID")
    url = "https://api.meraki.com/api/v1/organizations"
    key = input("[+] Enter the Meraki API Key-> ")
    ids = GetOrganizationID(url,key)
    print("[*] Retrieved Organization IDs")
    print(ids)

if(__name__ == '__main__'):
    main()