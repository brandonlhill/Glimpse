import subprocess

is_UserAPI_Running = subprocess.call(["screen", "-S", "User_API", "-Q", "select", ".", ";", "echo", "$?"])
is_DataAPI_Running = subprocess.call(["screen", "-S", "Data_API", "-Q", "select", ".", ";", "echo", "$?"])

#screen data api
if is_UserAPI_Running == 1 and is_DataAPI_Running == 1:
    print ("[INFO] Starting Glimpse Services.")
    subprocess.call(["screen", "-dmS", "User_API", "python3", "user_api.py"])
    subprocess.call(["screen", "-dmS", "Data_API", "python3", "data_api.py"])
    subprocess.call(["screen", "-r"])
else:
    print ("[INFO] Stopping Glimpse Services.")
    subprocess.call(["screen", "-S", "User_API", "-X", "quit"])
    subprocess.call(["screen", "-S", "Data_API", "-X", "quit"])