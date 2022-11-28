import requests
api_url = "https://192.168.2.37:1443/push_servers-logs"
x = requests.post(api_url, json={"API_KEY":"glimpse", "log":{"IP":"192.168.2.37", "Timestamp":"...", "log_type":"ERROR,OK,WARN", "msg": "Stuff Crashed Please Help."}}, verify=False)
print ("\n\nStatus: " + str(x.status_code) + " | Content: " +  str(x.json()))
