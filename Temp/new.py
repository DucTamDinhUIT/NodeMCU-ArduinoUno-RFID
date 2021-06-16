#import lib 
import sys
import mysql.connector
import json
import time 
import websocket


#url ip esp
esp8266host = "ws://192.168.1.100:81/"

#khai bao host esp
ws = websocket.WebSocket()



#connect database
print("dang cho ket noi database")
conn = mysql.connector.connect(user="sql6415334", password="jBHWEx5upn", host="sql6.freemysqlhosting.net", database="sql6415334")
print(conn)
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
	print("da ket noi host")
	print("nhap bien so")
	plateID = input()
	#bien so da duoc truyen vao
	if (plateID != None):

		#cau lenh lay thong tin tu database
		select_all = """SELECT * FROM Plate WHERE plateID = %s"""
		
		#thuc thi cau lenh
		cursor = conn.cursor()
		cursor.execute(select_all,(plateID,))
		#print (cursor)
		#print (type(cursor))

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
		print("chua co bien so trong dtb")
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
		ws.send(data_json)
		print("gui thanh cong")
		
		#reset bien so ve "chua duoc truyen vao"
		plateID = None


		api2()
			
                
                
	#truong hop bien so da co trong dtb:
	elif string != "[]":
		if ((row[1] == plateID) and (row[3] == 1) and (row[5] == 0)):
			#bien so da co trong dtb
			print("da co bien so trong dtb")
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
			ws.send(data_json)
			print("gui thanh cong")

            #reset bien so ve "chua duoc truyen vao"
			plateID = None
			time.sleep(3)

			
			
            #call api2
			api2()


def api2():

	#nhan json tu server
	y = ws.recv()
	print(y)
	ws.close()
	x = y.split("|")
	ID = x[0]
	plateID = x[1]
	RFID = x[2]
	checkout = x[3]
	
	api1()
	#jsonstring -> python string
	#z = str(json.loads(y))

	#ID = z[8:9]
	#print(ID)
	#plateID = z[]
	#x = z.fetchall()
#for row in x:
    #y = {
     #   "ID": row[0],
    #"plateID": row[1],
    #"RFID": row[2],
    #"checkin": row[3],
    #"checkinTime": row[4],			
    #"checkout": row[5],
    #"checkoutTime": row[6]
    #}



    #neu checkin = 1 va checkout = 1 -> vua` check out xong
'''	if (checkout == 1): 
		   print("checkout thanh cong, tien hanh update database")

        #cau lenh update checkout=1 va thoi gian checkout len dtb
		update = """UPDATE Plate SET checkout=1,checkoutTime=row[6] WHERE ID=row[0]""" 
        
        #thuc thi cau lenh
		cursor = conn.cursor() 
		cursor.execute(update) 
		print("update database thanh cong")

        #reset dieu kien ve "chua thoa"
		condition = None
        
		api1()

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

		api1()

        '''

#vong lap thuc thi khi co bien so truyen vao tu camera
while True:
	#truyen bien so vua nhan duoc tu camera vao day voi kieu du lieu string, tam thoi nhap tay
    api1()