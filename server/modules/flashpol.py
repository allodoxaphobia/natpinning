#!/usr/bin/env python
#filename=irc.py
from base import *
import socket
import random
import struct
import select

class FPProtoHandler(asyncore.dispatcher_with_send):
	def __init__(self,conn_sock, client_address, server):
		self.server=server
		asyncore.dispatcher_with_send.__init__(self,conn_sock) #Line is required
		self.server.log("Received connection from " + client_address[0] + ' on port ' + str(self.server.sPort))
	def handle_read(self):
		request = self.recv(1024).strip()
		if (request == ""): return
		if (request[:22]=="<policy-file-request/>"):
			self.server.log("FLASH policy file request")
			self.send("""<?xml version="1.0"?>
	<!DOCTYPE cross-domain-policy SYSTEM "/xml/dtds/cross-domain-policy.dtd">
	<cross-domain-policy> 
			<site-control permitted-cross-domain-policies="master-only"/>
			<allow-access-from domain="*" to-ports="*" />
	</cross-domain-policy>\x00""")
		else:
			self.server.log("Invalid input :" + request)
#end class

class Server(Base):
	def __init__(self,serverPort=843,sCallbackType="socket",verbose=False):
		self.TYPE = "Flash Policy Server"
		self.EXIT_ON_CB = 1
		self.CB_TYPE=sCallbackType
		Base.__init__(self,"TCP",serverPort,sCallbackType,verbose)
		self.log("Started")
	#end def
	def protocolhandler(self,conn, addr):
		# FLASH POLICY FILE SUPPORT
		self.HANDLER = FPProtoHandler(conn,addr,self)
	#end def
#end class
