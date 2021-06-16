#import lib 
import sys
import mysql.connector
import json
from ws4py.client.threadedclient import WebSocketClient
import time 
import requests


#url ip esp
esp8266host = "ws://192.168.1.65:81/"


#connect host esp
class DummyClient(WebSocketClient):
	def opened(self):
		print("Websocket open")
	def closed(self, code, reason=None):
		print ("Connexion closed down", code, reason)
	def received_message(self, m):
		print (m)
ws = DummyClient(esp8266host)
ws.connect()


#connect database
conn = mysql.connector.connect(user="sql6415334", password="jBHWEx5upn", host="sql6.freemysqlhosting.net", database="sql6415334")
print(conn)
if conn:
	print("DA KET NOI")
else:
	PRINT("KET NOI THAT BAI")


#creatdict
class create_dict(dict):

	# __init__ function 
    def __init__(self): 
        self = dict() 

    # Function to add key:value 
    def add(self, key, value): 
        self[key] = value


#check bien so trong database
def api1():
	global status
	global plateID

	#bien so da duoc truyen vao
	if (plateID != None):

		#cau lenh lay thong tin tu database
		select_all = """SELECT * FROM Plate""" 

		#thuc thi cau lenh
		cursor = conn.cursor() 
		cursor.execute(select_all) 

		#hien thi table bang cac hang (rows)
		result = cursor.fetchall() 
		for row in result:
			x = {
			    "ID": row[0],
			    "plateID": row[1],
			    "RFID": row[2],
			    "checkin": row[3],
			    "checkout": row[5]
			}


	#truong hop bien so da co trong dtb:
	if ((row[1] == plateID) and (row[3] == 1) and (row[5] == 0)):
		#bien so da co trong dtb

		status = 1 
		x = {
		    "ID": row[0],
		    "plateID": plateID,
		    "RFID": row[2],
		    "status": status
		}

		#dua ve dang json
		data_json = json.dumps(x)
		payload = {'json_payload': data_json}

		#post len server esp
		r = requests.post(esp8266host, payload)
       
		#reset bien so ve "chua duoc truyen vao"
		plateID = None

		#gui tin hieu da co trong dtb toi esp bang api1 -> checkout
		#-> tien hanh quet RFID , so sanh voi rfid trong api1 
		#-> quay servo -> update checkout = 1 vao json 
		#-> dump json ->  luu all len database + quay servo


	#truong hop bien so chua co trong dtb:
	elif ((row[1] != plateID) or ((row[1] == plateID) and (row[3] == 1) and (row[5] == 1))):

		#bien so chua co trong dtb
		status = 0 
		x = {
			"ID": None,
		    "plateID": plateID,
		    "RFID": None,
		    "status": status
		}

		#dua ve dang json
		data_json = json.dumps(x)
		payload = {'json_payload': data_json}

		#post len server esp
		r = requests.post(esp8266host, payload)
       
		#reset bien so ve "chua duoc truyen vao"
		plateID = None

		#gui tin hieu chua co trong dtb toi esp bang api1 
		#-> checkin tien hanh quet RFID + quay servo 
		#-> dumps lai vao json -> gui api2 ve lap -> luu all len database 


#get server		
def api2():

	global condition

	#get va read json tu server api 
	json_url = urlopen(esp8266host)
	x = json.loads(json_url.read())
	for row in x:
		y = {
			"ID": row[0],
		    "plateID": row[1],
		    "RFID": row[2],
		    "checkin": row[3],
		    "checkinTime": row[4],			
		    "checkout": row[5],
		    "checkoutTime": row[6]
		}


	#thoa dieu kien call api2
	if (condition == 1):

		#neu checkin = 1 va checkout = 1 -> vua` check out xong
		if (row[3] == 1) and (row[5]  == 1): 
			print("checkout thanh cong, tien hanh update database")

			#cau lenh update checkout=1 va thoi gian checkout len dtb
			update = """UPDATE Plate SET checkout=row[5],checkoutTime=row[6] WHERE ID=row[0]""" 
			
			#thuc thi cau lenh
			cursor = conn.cursor() 
			cursor.execute(update) 
			print("update database thanh cong")

			#reset dieu kien ve "chua thoa"
			condition = None

		#neu checkin = 1 va checkout = 0 -> vua checkin xong
		if (row[3 == 1]) and (row[5]  == 0): 
			print("checkin thanh cong, tien hanh update database")

			#cau lenh update bien so, rfid, checkin = 1, thoi gian checkin len dtb
			update = """INSERT INTO Plate(plateID, RFID, checkin, checkinTime) 
			VALUES (row[1],row[2],row[3],row[4]""" 

			#thuc thi cau lenh
			cursor = conn.cursor()
			cursor.execute(update) 
			print("update database thanh cong")

			#reset dieu kien ve "chua thoa"
			condition = None


#vong lap thuc thi khi co bien so truyen vao tu camera
while True:

	#truyen bien so vua nhan duoc tu camera vao day voi kieu du lieu string, tam thoi nhap tay
	print("nhap bien so")
	plateID = input()
	api1()

	#dieu kien de chay api2, tam thoi nhap tay
	print("nhap so 1 de call api2")
	condition = input() 
	api2()