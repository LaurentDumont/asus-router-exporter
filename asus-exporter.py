import requests
import base64
import os


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
    print(token)

    payload_list = ["uptime()", "memory_usage()", "cpu_usage()", "get_clientlist()", "netdev(appobj)", "wanlink()"]
    headers = {
    'user-Agent': "asusrouter-Android-DUTUtil-1.0.0.245",
    'cookie': 'asus_token={}'.format(token),
    }
    for payload in payload_list:
        formated_payload = "hook="+payload+';'
        try:
            r = requests.post(url='http://{}/appGet.cgi'.format(asus_ip), data=formated_payload, headers=headers)
        except:
            print('Failed')
        print(r.text)

def main():
    login_router()


if __name__ == '__main__':
    main()