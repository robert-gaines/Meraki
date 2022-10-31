
import requests

def GetNetworkID(url,key):
    headers = {
                 "X-Cisco-Meraki-API-Key":key
              }
    req = requests.get(headers=headers,url=url,timeout=5)
    if(req.status_code == 200):
        content = req.json()
        for item in content:
            for value in item.keys():
                print(value,'->',item[value])

def main():
    print("Retrieve the Network ID(s)")
    oid = input("[+] Enter the organization ID-> ")
    url = "https://api.meraki.com/api/v1/organizations/{0}/networks".format(oid)
    key = input("[+] Enter the Meraki API Key-> ")
    GetNetworkID(url,key)

if(__name__ == '__main__'):
    main()