#import lib 
import sys
import mysql.connector
import json
import time 
import websocket
import datetime

#url ip esp
esp8266host = "ws://192.168.1.100:81/"

#khai bao host esp
ws = websocket.WebSocket()

#connect database
print("dang cho ket noi database")
conn = mysql.connector.connect(user="sql6418350", password="hDLhCBJjKs", host="sql6.freemysqlhosting.net", database="sql6418350")
#print(conn)
if conn:
	print("DA KET NOI DATABASE")
else:
	PRINT("KET NOI THAT BAI")

#check bien so trong database
def api1():
	global status
	global plateID
	#connect server esp
	print("dang cho ket noi esp")
	ws.connect(esp8266host)
	print("DA KET NOI ESP")
	#truyen bien so la 1 STRING cac ki tu tui em lay duoc tu camera
	print("nhap bien so (sau nay se truyen bien so tu camera vao)")
	plateID = input()

	#bien so da duoc truyen vao
	if (plateID != None):

		#cau lenh lay thong tin tu database
		select_all = '''SELECT * FROM Plate WHERE plateID = %s'''
		#thuc thi cau lenh
		cursor = conn.cursor()
		cursor.execute(select_all,(plateID,))

		#hien thi table bang cac hang (rows)
		result = cursor.fetchall()

		#ep kieu string
		string = str(result)
		
		for row in result:
			x = {
			    "ID": row[0],
			    "plateID": row[1],
			    "RFID": row[2],
			    "checkin": row[3],
			    "checkout": row[5]
			}


	#truong hop bien so chua co trong dtb:
	if string == "[]" or ((row[1] == plateID) and (row[3] == 1) and (row[5] == 1)):

		#bien so chua co trong dtb
		print("chua co bien so trong database, tien hanh checkin")
		status = 0 
		x = {
			"ID": None,
		    "plateID": plateID,
		    "RFID": None,
		    "status": status
		}

		#dua ve dang json
		data_json = json.dumps(x)
		
		#post len server esp
		print("tien hanh gui json toi esp")
		ws.send(data_json)
		print("gui thanh cong")
		
		#reset bien so ve "chua duoc truyen vao"
		plateID = None

		#call api2
		api2()
			
                
                
	#truong hop bien so da co trong dtb:
	elif string != "[]":
		if ((row[1] == plateID) and (row[3] == 1) and (row[5] == None)):

			#bien so da co trong dtb
			print("da co bien so trong database, tien hanh checkout")
			status = 1 
			x = {
				"ID": row[0],
				"plateID": plateID,
				"RFID": row[2],
				"status": status
			}

            #dua ve dang json
			data_json = json.dumps(x)
        
            #post len server esp
			print("tien hanh gui json toi esp")
			ws.send(data_json)
			print("gui thanh cong")

            #reset bien so ve "chua duoc truyen vao"
			plateID = None

            #call api2
			api2()


def api2():

	#nhan json tu server
	y = ws.recv()
	ws.close()
	
	print(y)
	#lay cac gia tri trong api2 ra
	x = y.split("|")
	ID = x[0]
	plateID = x[1]
	RFID = x[2]
	checkinout = x[3]
	
    #neu checkin = 1 va checkout = 1 -> vua` check out xong
	if (checkinout == "1"): 
		print("checkout thanh cong, tien hanh update database")
		checkoutTimeTemp = str(datetime.datetime.now())
		checkoutTime = checkoutTimeTemp[0:19]

        #cau lenh update checkout=1 va thoi gian checkout len dtb
		update = """UPDATE Plate SET checkout=%s,checkoutTime=%s WHERE ID=%s""" 
        
        #thuc thi cau lenh
		cursor = conn.cursor() 
		cursor.execute(update,(checkinout, checkoutTime, ID))
		conn.commit()
		print("update database thanh cong")
		
		
    #neu checkin = 1 va checkout = 0 -> vua checkin xong
	if (checkinout == "0"): 
		print("checkin thanh cong, tien hanh update database")
		checkinTimeTemp = str(datetime.datetime.now())
		checkinTime = checkinTimeTemp[0:19]
		checkin = '1'
		#cau lenh update bien so, rfid, checkin = 1, thoi gian checkin len dtb
		update = """INSERT INTO Plate(plateID, RFID, checkin, checkinTime) 
		VALUES (%s,%s,%s,%s)""" 

        #thuc thi cau lenh
		cursor = conn.cursor()
		cursor.execute(update, (plateID, RFID, checkin, checkinTime)) 
		conn.commit()
		print("update database thanh cong")

		#ngat ket noi esp8266
		#ws.close()
	if (checkinout == "2"):
		print("checkout khong thanh cong, sai the RFID, tien hanh checkout lai")
		#ws.close()
        
       
#vong lap thuc thi khi co bien so truyen vao tu camera
while True:
	api1()