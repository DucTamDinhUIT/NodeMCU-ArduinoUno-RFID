import mysql.connector
import datetime
conn = mysql.connector.connect(user="sql6415334", password="jBHWEx5upn", host="sql6.freemysqlhosting.net", database="sql6415334")
#print(conn)
if conn:
	print("DA KET NOI DATABASE")
else:
	PRINT("KET NOI THAT BAI")
	
checkoutTimeTemp = str(datetime.datetime.now())
checkoutTime = checkoutTimeTemp[0:19]
print(checkoutTime)
checkout = '1'
ID = '9'
update = '''UPDATE Plate SET checkout = %s,checkoutTime = %s WHERE ID= %s'''
#thuc thi cau lenh
cursor = conn.cursor() 
 
cursor.execute(update,(checkout, checkoutTime, ID))
conn.commit()
print("update database thanh cong")