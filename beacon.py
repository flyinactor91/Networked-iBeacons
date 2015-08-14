#!/usr/bin/python3

##--Michael duPont
##--beacon.py : Network-Connected iBeacon
##--Uses Bluez and sockets to create an iBeacon whose values can be updated remotely
##--2015-08-13

#If on Raspberry Pi or other Linux/Debian distro, make sure Linux-bluetooth and bluez is installed
#https://learn.adafruit.com/pibeacon-ibeacon-with-a-raspberry-pi/setting-up-the-pi

#If on an Intel Edison, make sure you have BLE enabled
#https://software.intel.com/en-us/articles/intel-edison-board-getting-started-with-bluetooth
#You'll also need to remove 'sudo' from each hcitool command

import os

#Default Beacon Values - only used if csv storage could not be found
#Company ID, Area ID, Unit ID, and Power Setting
cid = '1E 02 01 1A 1A FF 4C 00 02 15 E2 0A 39 F4 73 F5 4B C4 A1 2F 17 D1 AD 07 A9 61'
aid = 0  # -> '00 00'
uid = 0  # -> '00 00'
power = -202  # -> 'CA'

#Set so that connections are only recieved from a single IP
#0.0.0.0 = all IPs can connect
listenIP = '0.0.0.0'
portNum = 9475

setbeacon = 'sudo hcitool -i hci0 cmd 0x08 0x0008 {0} {1} {2} {3} 00'
storageFile = 'beaconData.csv'

class iBeacon:
	__companyID = None
	__areaID = None
	__unitID = None
	__power = None
	#Init takes company ID, major, minor, and power
	#Company ID is the hex string while the rest can be the hex string or int value
	def __init__(self , companyID , areaID , unitID , power):
		self.__setClassValues(companyID , areaID , unitID , power)
	
	#Formats and sets the class values into valid hex strings for the BLE packet
	def __setClassValues(self , companyID , areaID , unitID , power):
		self.__companyID = companyID
		if type(areaID) == int: self.__areaID = self.intToFormattedHex(areaID , 2)
		else: self.__areaID = areaID
		if type(unitID) == int: self.__unitID = self.intToFormattedHex(unitID , 2)
		else: self.__unitID = unitID
		if type(power) == int: self.__power = self.intToFormattedHex(power , 1)
		else: self.__power = power
	
	#Starts the iBeacon transmitting. Bluez works asyncronously
	def startBeacon(self):
		os.system('sudo hciconfig hci0 up')
		os.system('sudo hciconfig hci0 leadv')
		os.system('sudo hciconfig hci0 noscan')
		os.system(setbeacon.format(self.__companyID , self.__areaID , self.__unitID , self.__power))
		print('iBeacon up')
	
	#Replace old broadcast packet with one whose minor value is incremented by one
	def changeValues(self , companyID , areaID , unitID , power):
		self.__setClassValues(companyID , areaID , unitID , power)
		os.system(setbeacon.format(self.__companyID , self.__areaID , self.__unitID , self.__power))
		print('iBeacon changed')
	
	#Stop transmission of iBeacon
	def endBeacon(self):
		os.system('sudo hciconfig hci0 noleadv')
		print('iBeacon down')
	
	# int 60 , 2 -> string '00 3C'
	# int 60 , 1 -> string '3C'
	def intToFormattedHex(self , intIn , pairs):
		hexTemp = '{0:x}'.format(abs(intIn)).zfill(pairs*2).upper()
		hexOut = hexTemp[:2]
		for i in range(pairs-1): hexOut += ' ' + hexTemp[2*i+2:2*i+4]
		return hexOut

#Load a storage file and replace the default beacon values before init
def loadBeaconData(filename):
	with open(filename , 'r') as fin:
		data = fin.read().split(',')
		cid = data[0]
		aid = data[1]
		uid = data[2]
		power = data[3]

#Save new beacon values to the storage file
def saveBeaconData(filename , itemList):
	for i in range(len(itemList)): itemList[i] = str(itemList[i])
	with open(filename , 'w') as fout:
		fout.write(','.join(itemList))

if __name__ == '__main__':
	import socket
	
	#Initialize iBeacon
	try: loadBeaconData(storageFile)
	except: pass
	ib = iBeacon(cid , aid , uid , power)
	ib.startBeacon()
	
	#Initialize server and start listening for connections
	server = socket.socket()
	server.bind((listenIP , portNum))
	server.listen(0)
	while True:
		sock , addr = server.accept()
		textIn = sock.recv(128)
		textIn = textIn.decode('utf-8').split('&')
		#Command recieved to update beacon values
		if len(textIn) == 4:
			for i in range(1,4): textIn[i] = int(textIn[i])
			ib.changeValues(textIn[0] , textIn[1] , textIn[2] , textIn[3])
		saveBeaconData(storageFile , textIn)
		sock.send('1'.encode('utf-8'))
		sock.close()
	
	#Under current use, these won't ever fire
	#But they're here in case 'quit' functionality is added later
	server.close()
	ib.endBeacon()
