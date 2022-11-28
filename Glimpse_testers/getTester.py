import requests
api_url = "https://192.168.2.37:1443/get_servers_info"
x = requests.get(api_url, json={"API_KEY":"glimpse", "request":{"list_servers":"all"}}, verify=False)
try:
    print ("\n\nStatus: " + str(x.status_code) + " | Content: " +  str(x.json()))
except:
    print ("no response")
