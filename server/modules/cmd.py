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
			self.send(test + "\n")
			if len(parts)==2:
				for vic in self.VICTIMS:
					if vic.VIC_ID == parts[1]:
						if test <> "NONE": self.server.log(vic.VIC_ID + " : send " + test,0)
						vic.LAST_SEEN = datetime.now()
						break
		elif parts[0]=="ERROR":
			self.server.log("Flash client generated an error" + request)
		else:
			self.server.log("Invallid command.",0)
	def getVicTest(self,cmd):
		global VICTIMS
		test = ""
		pollreq = cmd.split(" ")
		if len(pollreq) != 2:
			self.server.log("Invallid POLL request: " + cmd, 0)
		else:
			for vic in self.VICTIMS:
				if vic.VIC_ID == pollreq[1]:
					if len(vic.TESTS)==0:
						test = "NONE"
					else:
						test = vic.TESTS[0]
						vic.TESTS = vic.TESTS[1:]
						if test<> "RELOAD":
							test = "TEST " + test
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

