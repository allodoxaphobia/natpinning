#!/usr/bin/env python
#filename=flashpol.py
#
# Copyright Gremwell,2013
# Author: Raf Somers
# License: GNU General Public License, version 3
#
#	Flash policy server
#	Creates a listening socket on port 843 and generates a very permisive flash policy file

from base import *

class FPProtoHandler(asyncore.dispatcher_with_send):
	def __init__(self,conn_sock, client_address, server):
		self.server=server
		asyncore.dispatcher_with_send.__init__(self,conn_sock) #Line is required
		self.server.log("Received connection from " + client_address[0] + ' on port ' + str(self.server.sPort),1)
	def handle_read(self):
		request = self.recv(1024).strip()
		if (request == ""): return
		if (request[:22]=="<policy-file-request/>"):
			self.server.log("FLASH policy file request",1)
			self.send("""<?xml version="1.0"?>
	<!DOCTYPE cross-domain-policy SYSTEM "/xml/dtds/cross-domain-policy.dtd">
	<cross-domain-policy> 
			<site-control permitted-cross-domain-policies="master-only"/>
			<allow-access-from domain="*" to-ports="*" />
	</cross-domain-policy>\x00""")
		else:
			self.server.log("Invalid input :" + request,0)
#end class

class Server(Base):
	def __init__(self,serverPort=843,caller=None):
		self.TYPE = "Flash Policy Server"
		Base.__init__(self,"TCP",serverPort,caller)
		self.log("Started",2)
	#end def
	def protocolhandler(self,conn, addr):
		# FLASH POLICY FILE SUPPORT
		self.HANDLER = FPProtoHandler(conn,addr,self)
	#end def
#end class
