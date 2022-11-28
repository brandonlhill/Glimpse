import subprocess
from time import sleep

class Services:
    proc_data_api = None
    proc_user_api = None    

    def start_data_API(self):
        print ("[INFO] Lanuching Data-API Service...")
        self.proc_data_api = subprocess.Popen(['python3','data_api.py'], stdout=subprocess.PIPE)

    def start_user_API(self):
        print ("[INFO] Lanuching User-API Service...")
        self.proc_user_api = subprocess.Popen(['python3','user_api.py'], stdout=subprocess.PIPE)
    
    def start(self):
        #start processes
        self.start_data_API()
        self.start_user_API()

        #check if processes are online
        self.check()

    def shutdown(self):
        print ("[INFO] Terminating Glimpse Processes...")
        # process protections
        if self.proc_user_api is not None:
            self.proc_user_api.kill()
            self.proc_user_api.wait()
            print ("[OK] Terminated User_API Process sucessfully.")
        
        if self.proc_data_api is not None:
            self.proc_data_api.kill()
            self.proc_data_api.wait()
            print ("[OK] Terminated Data_API Process sucessfully.")

        self.proc_user_api = None
        self.proc_data_api = None

    def check(self, stdout=0):
        # check if processes are online
        # NOTE:  ".poll()" returning a None value indicates that the process hasn’t terminated yet. 
        if (self.proc_user_api.poll() != None) or (self.proc_data_api.poll() != None):
            self.shutdown()
            return [-1, "User-API: " + str(self.proc_user_api.poll() + " Data-API: " + self.proc_data_api.poll())] # failure status
        if stdout == 1:
            return [1, "USER-API-CONSOLE\n" + str(self.proc_user_api.communicate()[0]) + "DATA-API-CONSOLE\n" +str(self.proc_data_api.communicate()[0])] # ok status
        return [1,"OK"]

if __name__ == "__main__":
    # start msg
    print ("[GLIMPSE SERVER STARTUP]")
    service = Services()
    service.start()

    #NOTE: add checks for MongoDB and SQL server
    try:
        # idle watchdog
        print("[INFO] Entering Idle State.")
        while 1:
            report = service.check()
            if report[0] == -1:
                print ("[ERROR] Failure Occured in Service")
                print ("[MSG] " + report[1])
            sleep(3)
    except KeyboardInterrupt:
        print("[INFO] Keyboard Interrupt Detected.")
    finally:
        service.shutdown()
        print ("[OK] Goodbye.")