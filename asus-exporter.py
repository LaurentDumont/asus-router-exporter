from time import sleep
import requests
import base64
import os
import json
from prometheus_client import start_http_server, Gauge


#data total = {
#"memory_usage":"mem_total":"524288","mem_free":"134976","mem_used":"389312"
#}

#{
#"cpu_usage":"cpu1_total":"169547880","cpu1_usage":"979847","cpu2_total":"169551396","cpu2_usage":"1014974","cpu3_total":"169557418","cpu3_usage":"1100618","cpu4_total":"169538192","cpu4_usage":"1294285"
#}

uptime_metric = Gauge('uptime', 'Uptime of the router')
memory_total_metric = Gauge('memory_total', 'Total memory of the router')
memory_free_metric = Gauge('memory_free', 'Free memory of the router')
memory_used_metric = Gauge('memory_used', 'Used memory of the router')


def parse_payload(payload):
    #print(payload)

    if "cpu_usage" in payload:
        sanitized_format_cpu = payload.split(',')

        for data in sanitized_format_cpu:
            if "cpu1_total" in data:
                cpu1_total = data.split(':')[2].strip()
            elif "cpu1_usage" in data:
                cpu1_usage = data.split(':')[1].strip()
            elif "cpu2_total" in data:
                cpu2_total = data.split(':')[1].strip()
            elif "cpu2_usage" in data:
                cpu2_usage = data.split(':')[1].strip()
            elif "cpu3_total" in data:
                cpu3_total = data.split(':')[1].strip()
            elif "cpu3_usage" in data:
                cpu3_usage = data.split(':')[1].strip()
            elif "cpu4_total" in data:
                cpu4_total = data.split(':')[1].strip()
            elif "cpu4_usage" in data:
                cpu4_usage = data.split(':')[1].strip()
       
    if "memory_usage" in payload:
        memory_usage_list = payload.split(',')
        sanitized_format_memory = memory_usage_list
        for data in sanitized_format_memory:
            if "mem_total" in data:
                memory_total = data.split(':')[2].strip('"')
            elif "mem_free" in data:
                memory_free = data.split(':')[1].strip('"')
            elif "mem_used" in data:
                #We use strip to clean up the string return carriages and spaces
                memory_used = data.split(':')[1].replace('}', '').strip().strip('"')
        memory_total_metric.set(float(memory_total))
        memory_free_metric.set(float(memory_free)) 
        memory_used_metric.set(float(memory_used))

    elif "uptime" in payload:
        json_payload = json.loads(payload)
        # Calculate uptime
        if json_payload['uptime']:
            uptime_seconds = json_payload['uptime'].split(' ')[5].split('(')[1]
            #print(uptime_seconds)
            uptime_metric.set(uptime_seconds)

    

def login_router():
    router_username = os.getenv('ASUS_USERNAME')
    router_password = os.getenv('ASUS_PASSWORD')
    asus_ip = os.getenv('ASUS_IP')
    account = f"{router_username}:{router_password}"

    string_bytes = account.encode('ascii')
    base64_bytes = base64.b64encode(string_bytes)
    login = base64_bytes.decode('ascii')

    url = 'http://{}/login.cgi'.format(asus_ip)
    payload = "login_authorization=" + login
    headers = {
        'user-agent': "asusrouter-Android-DUTUtil-1.0.0.245"
    }
    r = requests.post(url=url, data=payload, headers=headers)
    token = r.json()['asus_token']
    #print(token)

    #payload_list = ["uptime()", "memory_usage()", "cpu_usage()", "get_clientlist()", "netdev(appobj)", "wanlink()"]
    payload_list = ["uptime()", "memory_usage()", "cpu_usage()"]

    headers = {
    'user-Agent': "asusrouter-Android-DUTUtil-1.0.0.245",
    'cookie': 'asus_token={}'.format(token),
    }
    for payload in payload_list:
        formated_payload = "hook="+payload+';'
        try:
            r = requests.post(url='http://{}/appGet.cgi'.format(asus_ip), data=formated_payload, headers=headers)
            #print(r.text)
            parse_payload(r.text)
        except Exception as e:
            print(e)
            print('Failed')
        

def main():
    print("Starting Prometheus ASUS Router")
    start_http_server(8000)

    while True:
        login_router()
        sleep(5)


if __name__ == '__main__':
    main()
