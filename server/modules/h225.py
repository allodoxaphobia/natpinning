#!/usr/bin/env python
#filename=h225.py
from base import *
import socket
import random
import struct
import select

class H225ProtHandler(asyncore.dispatcher_with_send):
	def __init__(self,conn_sock, client_address, server):
		self.server=server
		asyncore.dispatcher_with_send.__init__(self,conn_sock) #Line is required
		self.server.log("Received connection from " + client_address[0] + ' on port ' + str(self.server.sPort),1)
		self.cbport=0
		self.cbaddr=""
	def handle_read(self):
		request = self.recv(1024).strip()
		print request #XXX TODO
		#self.server.callback(self.cbaddr,int(self.cbport),"TCP","H225 CONNECT", self.server.TESTID)		
#end class

class Server(Base):
	def __init__(self,serverPort=1720,caller=None):
		self.TYPE = "H225 Server"
		Base.__init__(self,"TCP",serverPort,caller)
		self.log("Started",0)
	#end def
	def protocolhandler(self,conn, addr):
		self.HANDLER = H225ProtHandler(conn,addr,self)
	#end def
#end class
