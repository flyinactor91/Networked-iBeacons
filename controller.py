#!/usr/bin/python3

##--Michael duPont
##--controller.py : Network iBeacon Updater
##--Update networked beacon values from a CSV file
##--2015-08-14

import socket

portNum = 9475
timeout = 5

#Send a formatted itemList to a given ip:port and returns '1' is successful
def sendPacketItems(ip , port , itemList):
	try:
		print(ip)
		with socket.socket() as client:
			client.settimeout(timeout)
			client.connect((ip , port))
			sendBytes = '&'.join(itemList).encode('utf-8')
			client.send(sendBytes)
			ret = client.recv(1)
		return ret.decode('utf-8')
	except: return '-1'

#Returns an list of beacon csv data
def loadCSVData(filename):
	ret = []
	with open(filename , 'r') as fin:
		for line in fin: ret.append(line.strip().split(','))
	return ret

if __name__ == '__main__':
	good = 0
	bad = []
	beaconData = loadCSVData('beacons.csv')
	for beacon in beaconData:
		success = sendPacketItems(beacon[0] , portNum , beacon[1:])
		if success != '1': bad.append(beacon[0])
	print('Report:')
	print('For a total of {0} beacons,'.format(len(beaconData)))
	print('\t{0} updated successfully'.format(len(beaconData) - len(bad)))
	print('\t{0} updates failed'.format(len(bad)))
	if bad:
		print('\nThe following IPs failed:')
		for ip in bad: print(ip)
