
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from queue import Queue
import subprocess
import threading
import requests
import smtplib
import email
import time
import sys
import os

def TimeStamp():
    var         = time.ctime()
    sans_colons = var.replace(":","_")
    sans_spaces = sans_colons.replace(" ","_")
    timestamp   = sans_spaces
    return timestamp

def GenFileName():
    file_name = "CI_Meraki_Device_Monitoring_Status_Log_"
    timestamp = TimeStamp()
    file_name += timestamp
    file_name += ".log"
    return file_name

def SendAlert(body):
    message = MIMEMultipart()
    message['From']    = sender
    message['To']      = recipient
    timestamp          = time.ctime()
    message['Subject'] = "Network Alert [{0}]".format(timestamp)
    message.attach(MIMEText(body,"plain"))
    message            = message.as_string()
    server             = smtplib.SMTP(relay,port)
    #server.ehlo()
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, recipient, message)
    server.quit()

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

def Threader(q):
    while(True):
        host = q.get()
        PingHost(host)
        q.task_done()

def PingHost(host):
    if(os.name == 'nt'):
        output = subprocess.Popen(['ping','-n','1','-w','150',str(host)],stdout=subprocess.PIPE).communicate()[0]
    else:
        output = subprocess.Popen(['ping','-c','1','-w','150',str(host)],stdout=subprocess.PIPE).communicate()[0]
    if('Reply' in output.decode('utf-8')):
        host_stauses.append([host,'Up'])
    elif("Destination host unreachable" in output.decode('utf-8')):
        host_stauses.append([host,'down'])
    elif("Request timed out" in output.decode('utf-8')):
        host_stauses.append([host,'down'])
    else:
        host_stauses.append([host,'down']) 

def CheckDeviceStatus(devices):
    print("[~] Testing down devices via ICMP...")
    q = Queue()
    for device in devices:
        q.put(device['publicIp'])
    for i in range(100):
        process = threading.Thread(target=Threader,args=(q,))
        process.daemon = True 
        process.start()
    q.join()
    #
    for host in host_stauses:
        host_ip          = host[0]
        host_icmp_status = host[1]
        for device in devices:
            if(device['publicIp'] == host_ip):
                meraki_status = device['status']
                device_name   = device['name']
                if(meraki_status == 'offline' and host_icmp_status == 'down'):
                    print("[!] Device is down and unresponsive to ICMP-> {0}:{1}".format(device_name,host_ip))
                    SendAlert("[!] Device is down and unresponsive to ICMP-> {0}:{1}".format(device_name,host_ip))
    host_stauses.clear()

def GetDeviceStatuses(orgs,key):
    print("[~] Retrieving device statuses by organization...")
    headers = {
                 "X-Cisco-Meraki-API-Key":key
              }
    appliances = []
    for org in orgs:
        print("[~] Processing organization ID: %s " % org)
        url = "https://api.meraki.com/api/v1/organizations/{0}/devices/statuses".format(org)
        req = requests.get(headers=headers,url=url,timeout=15)
        content = req.json()
        for entry in content:
            if((entry['productType'] == 'appliance') and (entry['status'] == 'offline')):
                appliances.append(entry)
    return appliances

def main():
    print("[*] Monitor Meraki Device Statuses")
    url     = "https://api.meraki.com/api/v1/organizations"
    key     = input("[+] Enter the Meraki API Key-> ")
    ids     = GetOrganizationID(url,key)
    devices = GetDeviceStatuses(ids,key) 
    CheckDeviceStatus(devices)

if(__name__ == '__main__'):
    host_stauses = []
    log_file     = GenFileName()
    sender       = ''
    recipient    = ''
    password     = ''
    relay        = ''
    port         = ''
    main()