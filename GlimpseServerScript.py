import time, platform, psutil, threading, tempfile, subprocess, requests, datetime, shutil, json
from bson import ObjectId
from serial.tools import list_ports

# Global Variables
HOST_IP_ADDR = '192.168.2.38'
API_HOST = '192.168.2.37'
API_KEY = 'glimpse'
API_SERVERS_INFO = 'https://{}:1443/push_servers_info'.format(API_HOST)
API_SERVERS_LOGS = 'https://{}:1443/push_servers_logs'.format(API_HOST)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

class Server_Logs:
    def __init__(self, api_key, ip_addr):
        self.api_key = api_key
        self.log_file = tempfile.TemporaryFile()
        self.boot_devices = self.getDeviceList()
        self.boot_RAM = psutil.virtual_memory().total
        self.ip = ip_addr
        self.check()

    def getDeviceList(self):
        return subprocess.check_output('lsusb', shell=True).strip().decode('utf-8').replace('\r', '').split('\n')

    def check(self):
        # check if devices were plugged into COMs (USBS)
        s = set(self.getDeviceList())
        if len(s) > len(self.boot_devices):
            diff_boot_devices = [x for x in self.boot_devices if x not in s] 
            self.boot_devices = diff_boot_devices
            self.generateReport({'timestamp':str(datetime.datetime.now()),  'log_type':'Alert', 'msg':'USB Devices Connected to Server: {}'.format(str(self.boot_devices))})
        
        # check if CPU
        p_cpu = psutil.cpu_percent(0.5)
        
        if p_cpu > 40: # polls cpu for 0.5
            self.generateReport({'timestamp':str(datetime.datetime.now()), 'log_type':'Alert', 'msg':'Total CPU Cores at {}.'.format(p_cpu)})

        # check if RAM is maxed ([WARN] if RAM >= 50% capacity, [ALERT] if RAM >= 80% capacity)
        svmem = psutil.virtual_memory()
        if svmem.used > svmem.total * 0.8:
            self.generateReport({'timestamp':str(datetime.datetime.now()), 'log_type':'Alert', 'msg':'Memory consumption is {} of {}. '.format(svmem.used, svmem.total)})
        elif svmem.used > svmem.total * 0.5:
            self.generateReport({'timestamp':str(datetime.datetime.now()), 'log_type':'Warning', 'msg':'Memory consumption is {} of {}. '.format(svmem.used, svmem.total)})

    def generateReport(self, json_log):
        # call back to API
        print( {'API_KEY':self.api_key, 'log':json_log})
        try:
            requests.post(API_SERVERS_LOGS, json={'API_KEY':self.api_key, 'IP':self.ip, 'log':json_log}, verify=False)
        except Exception as inst:
            print (inst)
            print ('[ERROR] API_DOWN... Dropping JSON Packet.')

class Server_Info:
    def __init__(self, api_key, ip_addr):
        # api key
        self.api_key = api_key

        # computed once variables
        self.ip = ip_addr
        self.hostname = platform.uname()[1]
        self.uptime = time.time() - psutil.boot_time()
        self.cpufreq = psutil.cpu_freq()
        self.specs = {
            'system':platform.uname().system,
            'release':platform.uname().release,
            'version':platform.uname().version,
            'machine':platform.uname().machine,
            'processor':platform.uname().processor,
        }

        # define defaults
        self.cpu_info = ''
        self.mem_info = ''
        self.swap_info = ''
        self.network = ''
        self.disk = ''
        
        # update field values
        self.updateServerInfo()

    def get_size(self, bytes):
        for unit in ['', 'K', 'M', 'G', 'T', 'P']:
            if bytes < 1024:
                return f'{bytes:.2f}{unit}B'
            bytes /= 1024

    def getServerInfo(self):
        data = {
            'hostname':self.hostname,
            'cpu':self.cpu_info,
            'mem':self.mem_info,
            'swap':self.swap_info,
            'uptime':self.uptime,
            'specs':self.specs,
            'network':self.network,
            'disk':self.disk,
        }
        return data

    def updateServerInfo(self):
        svmem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        io_2 = psutil.net_io_counters()
        dk_total, dk_used, dk_free = shutil.disk_usage('/')
        self.cpu_info = {
            'usage':psutil.cpu_percent(0.5),
            'p_cores': psutil.cpu_count(logical=False),
            't_cores': psutil.cpu_count(logical=True),
            'max_freq': str(self.cpufreq.max),
            'cur_freq': str(self.cpufreq.current),
        }
        self.mem_info = {
            'total':svmem.total,
            'used':svmem.used,
        }
        self.swap_info = {
            'total':swap.total,
            'used':swap.used,
        }
        self.uptime = time.time() - psutil.boot_time()
        self.network = {
            'sent':self.get_size(io_2.bytes_sent),
            'recv':self.get_size(io_2.bytes_recv),
        }
        self.disk = {
            'total':self.get_size(dk_total),
            'used':self.get_size(dk_used),
            'free':self.get_size(dk_free),
        }

    def generateReport(self):
        # call back to API
        print({'API_KEY':self.api_key, 'IP':self.ip, 'data':self.getServerInfo()})
        try:
            data = {'API_KEY':self.api_key, 'IP':self.ip, 'data':self.getServerInfo()}

            requests.post(API_SERVERS_INFO, json=data, verify=False)
        except Exception as inst:
            import traceback
            traceback.print_exc()
            print ('[ERROR] API_DOWN... Dropping JSON Packet.')

# threaded task that update values in Server classes over time to queueing preformance purposes
def dataManager(s_info, s_logs, stopevent, timeout=1):
    t_start = time.time() + 5 
    while not stopevent.is_set():
        # update logs
        print('[UPDATED] UPDATED LOGS.')
        s_info.updateServerInfo()

        # check every minute update database fields and or upload logs
        if time.time() > t_start:
            t_start = time.time() + 5
            print ('[INFO] Generating INFO Report')
            s_info.generateReport()
            print ('[INFO] Checking for Logging Upload')
            s_logs.check()

        # timeout
        time.sleep(timeout)

# main
if __name__ == '__main__':
    # define static global vars
    thread_dataManager = None
    thread_event = threading.Event()
    thread_event.clear()

    # define server classes
    s_info = Server_Info(API_KEY, HOST_IP_ADDR)
    s_logs = Server_Logs(API_KEY, HOST_IP_ADDR)
    
    # control loop
    try:
        # spawn data manager thread
        thread_dataManager = threading.Thread(target=dataManager, args=(s_info, s_logs, thread_event, 2))
        thread_dataManager.start()
    except Exception:
        print ('[ERROR] Threading Failed to Spawn.')
    
    # main thread - run networking low level flask API
    while 1:
        # DEBUG: print(thread_dataManager.is_alive())
        time.sleep(1)
        pass

    # stop threaded processes
    thread_event.set()
    thread_dataManager.join()