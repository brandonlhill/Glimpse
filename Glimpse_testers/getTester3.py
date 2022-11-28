import requests
api_url = "https://192.168.2.37:1443/get_servers_logs"
x = requests.get(api_url, json={"API_KEY":"glimpse", "IP":"192.168.2.38", "get_logs":{"start":"1"}}, verify=False)
try:
    print ("\n\nStatus: " + str(x.status_code) + " | Content: " +  str(x.json()))
except:
    print ("no response")