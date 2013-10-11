#!/usr/bin/env python
#filename=irc.py
from base import *
import socket
import random
import struct
import select

class Victim():
	VIC_ID = ""
	PUBLIC_IP = ""
	PRIVATE_IP=""
	TESTS = []
	def __init__(self,pub_ip,priv_ip,tests=None):
		global VIC_ID, PUBLIC_IP, PRIVATE_IP, TESTS
		self.PUBLIC_IP = pub_ip.strip()
		self.PRIVATE_IP= priv_ip.strip()
		self.VIC_ID = self.PUBLIC_IP.replace(".","").replace(":","") + self.PRIVATE_IP.replace(".","").replace(":","")
		if tests != None: 
			self.TESTS=tests
		else:
			self.buildTests()
	def buildTests(self):
		global TESTS
		tests = []
		tests.append("FTP " + self.PRIVATE_IP + " 65530") #FTP own ip, high port test, this is basic proto support test
		tests.append("FTP " + self.PRIVATE_IP + " 80") #FTP own ip, low port test
		tests.append("IRC " + self.PRIVATE_IP + " 65530") #IRC own ip, high port test, this is basic proto support test
		tests.append("IRC " + self.PRIVATE_IP + " 80") #IRC own ip, low port test
		tests.append("SIP " + self.PRIVATE_IP + " 65530") #SIP own ip, high port test, this is basic proto support test
		tests.append("SIP " + self.PRIVATE_IP + " 111") #SIP own ip, low port test
		self.TESTS = tests
#end class
class CMDProtoHandler(asyncore.dispatcher_with_send):
	VICTIMS = []
	def __init__(self,conn_sock, client_address, server):
		self.server=server
		asyncore.dispatcher_with_send.__init__(self,conn_sock) #Line is required
		self.server.log("Received connection from " + client_address[0] + ' on port ' + str(self.server.sPort))
	def handle_read(self):
		global VICTIMS
		request = self.recv(1024).strip()
		if (request == ""): return
		parts = request.split(" ")
		if parts[0]=="REG":
			#new client received, grap local ip and return test id
			vic = Victim(self.getpeername()[0], parts[1])
			self.server.log("New client registered as " + vic.VIC_ID)
			self.VICTIMS.append(vic)
			self.send("SET ID " + vic.VIC_ID + "\n")
		elif parts[0]=="POLL":
			self.server.log("POLLING request from " + parts[1])
			test = self.getVicTest(request)
			self.send(test + "\n")
			#client waits for new command
		else:
			self.server.log("Invallid command.")
	def getVicTest(self,cmd):
		global VICTIMS
		test = ""
		pollreq = cmd.split(" ")
		if len(pollreq) != 2:
			self.server.log("Invallid POLL request: " + cmd)
		else:
			for vic in self.VICTIMS:
				if vic.VIC_ID == pollreq[1]:
					if len(vic.TESTS)==0:
						test = "FIN"
					else:
						test = vic.TESTS[0]
						vic.TESTS.remove(test)
						test = "TEST " + test
					break
		return test
	#end def
			
#end class


class Server(Base):
	def __init__(self,serverPort=60006,sCallbackType="socket", verbose=False):
		self.EXIT_ON_CB = 1
		self.CB_TYPE=sCallbackType
		self.TYPE = "COMMAND Server"
		Base.__init__(self,"TCP",serverPort,sCallbackType,verbose)
		self.log("Started")
	#end def
	def protocolhandler(self,conn, addr):
		self.HANDLER = CMDProtoHandler(conn,addr,self)
	#end def
#end class

