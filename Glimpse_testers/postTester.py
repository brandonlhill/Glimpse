import requests
api_url = "https://192.168.2.37:1443/push_servers-info"
x = requests.post(api_url, json={"API_KEY":"glimpse", "data":{"IP":"192.168.2.37"}}, verify=False)
print ("\n\nStatus: " + str(x.status_code) + " | Content: " +  str(x.json()))
