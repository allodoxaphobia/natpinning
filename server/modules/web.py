#!/usr/bin/env python
#filename=web.py
#This module acts as a very simple HTTP webserver and will feed the exploit page.

from base import *
import socket
import random
import struct
import select

class HTTPProtoHandler(asyncore.dispatcher_with_send):
	def __init__(self,conn_sock, client_address, server):
		self.server=server
		asyncore.dispatcher_with_send.__init__(self,conn_sock) #Line is required
		self.server.log("Received connection from " + client_address[0] + ' on port ' + str(self.server.sPort))
	def handle_read(self):
		header="""HTTP/1.1 200 OK
Content-Type: text;html; charset=UTF-8
Server: NatPin Exploit Server
Content-Length: $len$

"""
		request = self.recv(1024).strip()
		if (request == ""): 
			return
		else:
			reqHeaders = request.split("\n")
			page = reqHeaders[0].split(" ")[1]
			self.server.log("Victim requested page: " + page)
			#f = open("../../exploit/
#end class

class Server(Base):
	def __init__(self,serverPort=843,sCallbackType="socket"):
		self.TYPE = "Flash Policy Server"
		self.EXIT_ON_CB = 1
		self.CB_TYPE=sCallbackType
		Base.__init__(self,"TCP",serverPort,sCallbackType)
		self.log("Started")
	#end def
	def protocolhandler(self,conn, addr):
		# FLASH POLICY FILE SUPPORT
		self.HANDLER = HTTPProtoHandler(conn,addr,self)
	#end def
#end class
