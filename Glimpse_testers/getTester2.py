import requests
api_url = "https://192.168.2.37:1443/get_servers_info"
x = requests.get(api_url, json={"API_KEY":"glimpse", "request":{"info":"192.168.2.38"}}, verify=False)
print ("\n\nStatus: " + str(x.status_code) + " | Content: " +  str(x.json()))