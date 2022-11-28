# Glimpse
Glimpse is a simple python based Linux server auditing platform. Built by a UMBC Student.

## Table of Contents
1. [General Info](#general-info)
2. [Technologies](#technologies)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Configure Firewall](#configurefirewall)
6. [Glimpse API's](#glimpse-api's)
7. [Deployment](#deployment)
8. [Authors](#authors)
9. [Notice](#notice)

## General Info
This project was developed to learn many critical software developement techniques. Its not recommend to use this software in a production environment. Further more, if youre just interested in learning about: flask proxy servers, flask threading, flask (cookie) based sessions, Pymongo, PySQL, etc. then this is the project you should invest some time in.

Note: Bug fixes, security reports, and general improvements push requests are encouraged. So please do submit push/merge requests!

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
The Glimpse Server Script is a script that is to be installed on a server that you wish to monitor via Glimpse.
This script communciates to the Glimpse Host via a configured API_KEY.
The Glimpse Server Script requires you to fill out some conf options to allow it to communicate to the Host Glimpse Server.

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

The following commands created a database "accounts" with a table "user" define with 3 columns (username, password, access).
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
Read More Here about ubuntu Firewalls: https://ubuntu.com/server/docs/security-firewall
```bash
$ ufw allow 1443/tcp
$ ufw allow 8443/tcp
```

## Glimpse API's
This section covers all the POST/GET endpoints that Glimpse open the network.
### User_API.py
This API handles serves more as a webserver, but its considered an API because it should be behind a webserver "REVERSE PROXY".
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
The Data_API is where the Glimpse Server Script (GSS) pushes server data data for backend processing and storage. Note that all data is 
encrpted using priviate certs and the payload of the data requires a API_KEY for the server to process the data.
The API_Key is defined by the Glimpse admin during configuration into the GSS and into the Data_API config.

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
| `logs`    | `string` | Appended Blob: {"IP":"...", "Timestamp":"...", "log_type":"ERROR,OK,WARN", "msg": "..."}|

```http
  GET :1443/get_servers_info
```
| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `API_KEY` | `string` | Required authentication           |
| `request` | `string` | Request Blob types  {"info", "IP_ADDRESS"} or {"list_servers","all"}|

```http
  GET :1443/get_servers_logs
```
| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `API_KEY` | `string` | Required authentication           |
| `IP`      | `string` | Server IP to get Logs from        |
| `get_logs`| `string` | Appended Blob: {"start":"..."} How many logs to pull start at index 0 to "..."|

You can test out the following items with the included scripts in the Glimpse_testing folder.
Note that you will need to change the internal code a bit to get the scripts running with your configuration.

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

## Authors
- [@brandonlhill](https://www.github.com/brandonlhill) 

# Notice
This is a school project designed to mock real developement that may occur in industry. 
This Work is provided "as is". Any express or implied warranties, including but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed. In no event shall the students of this project be liable for any direct, indirect, incidental, special, exemplary or consequential damages (including, but not limited to, procurement of substitute goods or services, loss of use, data or profits, or business interruption).
