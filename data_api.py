import pymongo, json, style, re
from ipaddress import ip_address
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from configparser import ConfigParser

# config reader
conf = ConfigParser()
conf.read('config.ini')
API_CONF = conf["API"]
MONGODB = conf["MONGODB"]
API_KEY = API_CONF["api_key"]

# mongodb
mongodb = pymongo.MongoClient(MONGODB["host"])
db = mongodb[MONGODB["database"]]
dbcol_servers_info = db[MONGODB["document_server_info"]]
dbcol_servers_logs = db[MONGODB["document_server_logs"]]

# flask app
app = Flask(__name__)

# helper functions
def check_API_KEY(api_key):
    # no need to build json object, just search item as a string instead
    return api_key == API_KEY

def convert_List2Dict(lst):
	res_dct = {str(lst[i]): lst[i + 1] for i in range(0, len(lst), 2)}
	return res_dct

def is_IP_ADDR(ip_address):
    regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
    if(re.search(regex, ip_address)):
        return 1
    return 0

@app.route('/test', methods=['GET'])
def test():
    return style.STATUS_OK

@app.route('/clearit', methods=['POST'])
def clearit():
    jsondata = request.get_json()
    api_key = jsondata.pop("API_KEY")

    if check_API_KEY(api_key):
        print("[INFO] Valid Request for 'clear'.")
        request_type = jsondata.pop("request")
        clear_item = request_type.pop("clear")
        if clear_item == "logs":
            print("[INFO] Clearing all LOGS")
            dbcol_servers_logs.delete_many({})
            return style.STATUS_OK
        elif clear_item == "servers":
            print("[INFO] Clearing all Servers")
            dbcol_servers_info.delete_many({})
            return style.STATUS_OK
        elif is_IP_ADDR(clear_item):
            print("[INFO] Clearing [" + clear_item + "] Logs and Info." )
            dbcol_servers_logs.delete_many({"IP":str(clear_item)})
            dbcol_servers_info.delete_many({"IP":str(clear_item)})
            return style.STATUS_OK
        return style.STATUS_ERR
    
    print ("[INFO] Invalid Request Attempted.")
    return style.STATUS_NOAUTH

@app.route('/push_servers_info', methods=['POST'])
def push_servers_info():
    # parse request
    data = request.get_json()
    api_key = data.pop("API_KEY")
    ip_address = data.get('IP')
    
    # prevent data manipulation
    if ip_address == None or ip_address == "" or data == {}:
        return style.STATUS_ERR
    
    # check if API key is valid
    if check_API_KEY(api_key): # TODO: add check if ip address doesnt match the connection address
        print ("[INFO] Valid Request for 'push_servers_info'.")
        # check if the ip exists in the database
        check = dbcol_servers_info.find_one({"IP":ip_address})
        # print ("Print Check: " + str(check))
        # print ("Print Data: " + str(data))
        if check:
            print ("[INFO] Server Info Exists... Updating Database Document.")
            # update existing JSON data in database
            dbcol_servers_info.update_one({"IP":ip_address}, {"$set":{"data":data['data']}})
        else:
            # push the json data to the database
            dbcol_servers_info.insert_one(data)
        return style.STATUS_OK
    
    print ("[INFO] Invalid Request Attempted.")
    return style.STATUS_NOAUTH

@app.route('/get_servers_info', methods=['GET'])
def get_servers_info():
    # parse request
    data = request.get_json()
    api_key = data.pop("API_KEY")
    request_type = data.pop("request")
    
    # check if API key is valid
    if check_API_KEY(api_key):
        # NOTE: dict.get('str') returns None type
        if request_type.get('list_servers'):
            print ("[INFO] Valid Request for list servers.")
            
            # return all IP info from the mongodb collections
            servers = []
            counter = 1

            for x in dbcol_servers_info.find({}):
                servers.append(counter)
                servers.append(x.get("IP"))
                counter = counter + 1
                # print(x)
            
            return convert_List2Dict(servers)
        elif request_type.get('info') != None:
            print ("[INFO] Valid Request for Single Server Info.")
            server_id = dbcol_servers_info.find_one({"IP":request_type.get('info')})
            if server_id != None:
                # add IP to json data
                x = server_id.get("data")
                x.update({"IP":request_type.get('info')})
                # print(x)
                return x
            
            return style.STATUS_ERR
        else:
            print ("[INFO][ERR] Unknown Request field in JSON Defined in GET Request.")
            return style.STATUS_UKN
    
    print ("[INFO] Invalid Request Attempted.")
    return style.STATUS_NOAUTH

@app.route('/push_servers_logs', methods=['POST'])
def push_servers_logs():
    # parse request
    jsondata = request.get_json()
    api_key = jsondata.pop("API_KEY")
    ip = jsondata.get('IP')

    # prevent log manipulation or crafted packets from being uploaded to the database
    if ip == None or ip == "" or jsondata == {}:
        return style.STATUS_ERR

    # check if API key is valid
    # TODO: add check if ip address doesnt match the connection address
    if check_API_KEY(api_key):
        print ("[INFO] Valid Request for 'push_servers-logs'.")
        dbcol_servers_logs.insert_one(jsondata)
        return style.STATUS_OK

    print ("[INFO] Invalid Request Attempted.")
    return style.STATUS_NOAUTH

@app.route('/get_servers_logs', methods=['GET'])
def get_servers_logs():
    # parse request
    jsondata = request.get_json()
    api_key = jsondata.pop("API_KEY")

    if check_API_KEY(api_key):
        print ("[INFO] Valid Request for 'get_servers_logs'.")
        log_request = jsondata.pop("get_logs")
        ip_address = jsondata.pop("IP")
        start_pos = int(log_request.get("start")) # TODO:force positive integers
        logs = dbcol_servers_logs.find({"IP":ip_address}).limit(start_pos+10)

        servers = []
        counter = 1

        if logs != None:
            for x in logs:
                # bug "Object of type ObjectId is not JSON serializable"
                # fixed by turning _ID into a string item and reappending to the data 
                servers.append(counter)
                id = str(x.pop("_id"))
                x.update({"_id":id})
                servers.append(x)
                counter = counter + 1

            return convert_List2Dict(servers)
        return style.STATUS_EMPTY

    print ("[INFO] Invalid Request Attempted.")
    return style.STATUS_NOAUTH

if __name__ == '__main__':
    # start application. note the 0.0.0.0 is to ensure the program takes on what IP the server is currently
    app.run(debug=eval(API_CONF["debug"]), threaded=True, host='0.0.0.0', port=1443, ssl_context=(API_CONF["cert_file"], API_CONF["key_file"]))
