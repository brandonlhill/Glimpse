# Glimpse
Glimpse is a simple python based Linux server auditing platform. Built by a UMBC Student.

## Table of Contents
1. [General Info](#general-info)
2. [Technologies](#technologies)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Configure Firewall](#configurefirewall)
6. [Deployment](#deployment)
7. [Glimpse API's](#glimpse-api's)
8. [Authors](#authors)
9. [Notice](#notice)

## General Info
This project was created to sharpen software developement techniques. I do not recommend using Glimpse in a production environment. Furthermore, if you're just interested in learning about: flask proxy servers, flask threading, flask (cookie) based sessions, Pymongo, PySQL, etc. then this is the project for you.

If deployed in a production environment it's advised to use a reverse proxy server for FLASK. 

Note: Bug fixes and general improvements are encouraged. So please do submit push/merge requests!

## Technologies
A list of technologies used within the project:
* [MongoDB](https://www.mongodb.com/docs/manual/administration/install-on-linux/): Version 6.0
* [Python3](https://www.python.org/download/releases/3.0/): Version 3.10
* [MySQL](https://ubuntu.com/server/docs/databases-mysql): 8.0.31-0ubuntu0.22.04.1 (Ubuntu) (other versions can be used)

## Installation

#### Install SQL-Server (ubuntu)
```bash
$ sudo apt install mysql-server
```
#### Install MongoDB
Offical Installation Guide: https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/
``` bash 
# Import mongodb public key:
$ sudo apt-get install gnupg
$ wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

# Update apt repo-list
$ sudo apt-get update

# Install MongoDB and Mongo Shell (for config)
$ sudo apt instlal mongodb-mongosh mongodb-ord


#Ubuntu 22.04 has upgraded libssl to 3 and does not propose libssl1.1
#You can force the installation of libssl1.1 by adding the ubuntu 20.04 source:
$ echo "deb http://security.ubuntu.com/ubuntu focal-security main" | sudo tee /etc/apt/sources.list.d/focal-security.list
$ sudo apt-get update
$ sudo apt-get install libssl1.1
``` 
#### Install Python Packages
```bash 
# Python3.10 install & required dev packages
$ sudo apt install python3 python3-pip python-pip python-dev libmysqlclient-dev

# Install python packages (for Glimpse Server HOST)
$ python3 -m pip install flask mysql-connector pymongo pyserial colorama requests shutil bson psutil Flask-MySQLdb

# Install python packages (for Glimpse Server Script on Remote HOST)
$ python3 -m pip install shutil
```

## Configuration
### Glimpse Server Script on Remote Host (GSS)
The GSS is a remote server script responsible for sending server data to the Glimpse Host.
This script communciates to the Glimpse Host via a config defined API_KEY.
The Glimpse Server Script requires you to fill out some config options, allowing it to communicate with Glimpse Server.

### Glimpse Host
Follow for more specific instructions here: (cross reference to this documentation to ensure you configure the database correctly)
https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-20-04
#### SQL Server Setup
```bash
$ sudo systemctl start mysql.service
$ sudo mysql
# NOTE! change the default "Gl1MpS3%^Sr" password here and the User_API.py script... 
mysql> ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Gl1MpS3%^Sr';
mysql> exit;
$ mysql -u root -p
mysql> ALTER USER 'root'@'localhost' IDENTIFIED WITH auth_socket;
mysql> exit;
$ sudo mysql_secure_installation
*ommited definition process... ensure password is the same as define above* 
```
Define SQL database 
```bash
$ sudo mysql
$ mysql -u root -p (may be required)
mysql> CREATE DATABASE [IF NOT EXISTS] accounts;
mysql> CREATE TABLE user (username varchar(255), password varchar(255), access int));
mysql> INSERT INTO user VALUES ("admin","password",5);
mysql> exit;
*Bye*
```

The following commands creates a database named "accounts" with a table named "user" having 3 columns (username, password, access).
Some helpful links to read for debugging:
* (SQL Views) https://www.w3schools.com/SQL/sql_view.asp
* (SQL INSERT INTO Statement) https://www.w3schools.com/sql/sql_insert.asp

#### MongoDB Setup
```bash
$ mongosh
*ommited messages*
... > use glimpse
*switched to db glimpse*
... > db.servers_infos
... > db.servers_logs
```
Some helpful links to read for debugging:
* (Mongo Commands List) https://www.mongodb.com/docs/manual/reference/command/
* (Mongo Create a database using the mongosh -- shell) https://www.mongodb.com/basics/create-database

## Configure Firewall
For the Glimpse Host (this is not needed for the Glimpse Server Script Host Machine)
For additional UFW info read: https://ubuntu.com/server/docs/security-firewall
```bash
$ ufw allow 1443/tcp
$ ufw allow 8443/tcp
```

## Deployment
After following the install and setup instructions you can now configure the config files for the GlimpseServerScript and Glimpse Server.
### Running the Glimpse Server Script on Remote Host (linux server)
To edit the script config you will need to edit the python code. Edit the global vars:

```bash 
$ vim GlimpseServerScript.py
--------------------------------------------------
| *ommited*                                      |
| HOST_IP_ADDR = (The Local Server IP Address)   |
| API_HOST = (The Glimpse Server IP)             |
| API_KEY = (The API KEY)                        |
| *ommited*                                      |
--------------------------------------------------
```

To run the GlimpseServerScript, run the following command:
```bash
$ python3 GlimpseServerScript.py
```

### Running Glimpse Server (Linux Machine)
To edit the Glimpse Server config, edit the "config.ini" file
```bash 
$ vim config.ini
--------------------------------------------------
| [MONGODB]                                      |
| host = mongodb://localhost:27017/              |
| database = glimpse                             |
| document_server_info = servers_info            |
| document_server_logs = servers_logs            |
|                                                |
| [SQLDB]                                        |
| host = localhost                               |
| user = root                                    |
| password = Gl1MpS3%%^Sr                        |
| database = accounts                            |
|                                                |
| [API]                                          |
| debug = False                                  |
| api_key = glimpse                              |
| cert_file = certs/cert.pem                     |
| key_file = certs/key.pem                       |
--------------------------------------------------
```

To START and STOP Glimpse run the following command within the local code directory.
```bash
$ python3 glimpse.py
$ screen -r
# You Should see the following output ...
----------------------------------------------------------------------
|  There are screens on:                                             |
|        *****.Data_API  (11/28/2022 08:08:55 AM)        (Detached)  |
|        *****.User_API  (11/28/2022 08:08:55 AM)        (Detached)  |
|  2 Sockets in /run/screen/S-unknown.                               |
----------------------------------------------------------------------
```

### Note that you can run the GlimpseServerScript.py and the glimpse.py as Linux Services to ensure they stay running on reboot.

## Glimpse API's
This section covers POST/GET endpoints that Glimpse opens to the network.
### User_API.py
This API acts very similar to a webserver because it serves web content, as well as responding to POST/GET requests.
Read More about reverse proxies here: https://www.nginx.com/resources/glossary/reverse-proxy-server/. 
#### User_API Request Reference
```http
  GET :8443/
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| NA        |    NA    | Redirects to /login or /home based on auth status|


```http
  GET :8443/login
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| NA        | NA       | Returns login.html                |

```http
  POST :8443/login
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `username`| `string` | Required for Server Side Session generation and auth|
| `password`| `string` | Required for Server Side Session generation and auth|
```http
  GET :8443/home
```
| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `session_id`| `string` | Returns index.html home page if authenticated|


### Data_API.py
The Data_API is where the Glimpse Server Script (GSS) pushes server data for backend processing and storage. This API enforces HTTPS and for every request to contain a API_KEY for security purposes. The API_Key is defined by the Glimpse admin during the configuration steps (api_key in the config.ini file)

#### Data_API Request Reference
```http
  POST :1443/push_servers_info
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `API_KEY` | `string` | Required authentication           |
| `data`    | `string` | Server Data                       |

```http
  POST :1443/push_servers_logs
```
| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `API_KEY` | `string` | Required authentication           |
| `logs`    | `string` | JSON: {"IP":"...", "Timestamp":"...", "log_type":"ERROR,OK,WARN", "msg": "..."}|

```http
  GET :1443/get_servers_info
```
| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `API_KEY` | `string` | Required authentication           |
| `request` | `string` | JSON Types:  {"info", "IP_ADDRESS"} or {"list_servers","all"}|

```http
  GET :1443/get_servers_logs
```
| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `API_KEY` | `string` | Required authentication           |
| `IP`      | `string` | Server IP to get Logs from        |
| `get_logs`| `string` | JSON: {"start":"..."} How many logs to pull start at index 0 to "..."|

You can test out the following items with the included scripts in the Glimpse_testing folder. Note that some modification is required for the scripts to work for your glimpse install. 

## Authors
- [@brandonlhill](https://www.github.com/brandonlhill) 

# Notice
This is a school project designed to mock real developement that may occur in industry. 
This Work is provided "as is". Any express or implied warranties, including but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. In no event shall the students of this project be liable for any direct, indirect, incidental, special, exemplary or consequential damages (including, but not limited to, procurement of substitute goods or services, loss of use, data or profits, or business interruption).
