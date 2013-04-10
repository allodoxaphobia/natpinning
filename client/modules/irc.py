#!/usr/bin/env python
#filename=irc.py
from base import *
import struct

class Client(Base):
	IRC_NICK = "natpin" + str(random.randint(1, 1000))
	IRC_BOUNCE_NICK="raf"
	
	def __init__(self,serverip, serverport,callbackip,callbackport):
		Base.__init__(self,"TCP",serverip, serverport,callbackip,callbackport)
	#end if

	def protocolhandler(self):
		while 1:		#runs on seperate thread, will be killed when callback results are in
			try:
				indata = self.sSock.recv(1024).split('\r\n')
				for line in indata:
					x = serverMSG(line)
					if x.Ok==1: self.handlemsg(x)
			except:
				pass
	#end if	
	
	def handlemsg(self,servermsg):
		if servermsg.Type== "NOTICE" and servermsg.SubType=="AUTH":
			self.sSock.send("NICK "+self.IRC_NICK+"\r\n")
			self.sSock.send("USER "+self.IRC_NICK+" "+self.IRC_NICK+" "+self.sIp+" :"+self.IRC_NICK+"\r\n")
		elif servermsg.Type=="PING":
			self.sSock.send("PONG " + servermsg.Val + "\r\n")
			print "PING/PONG"
		elif servermsg.Type==("376"):
			#we're connected, try DDC CHAT NATPIN
			self.DCCChat(self.IRC_BOUNCE_NICK,self.cbIp, self.cbPort)
	#end def
	
	def DCCChat(self, nick, IPAddress, port):
		intIP = struct.unpack("!I", socket.inet_aton(IPAddress))[0]
		self.sSock.send("PRIVMSG " +nick + " :"+chr(0x01)+"DCC CHAT chat " + str(intIP) + " " + str(port) + chr(0x01)+"\r\n")
		#print "DCC CHAT SEND, try to connect from remote host to " + IPAddress + ":" + str(port)
	#end def
#end class

class serverMSG():
	def __init__(self, msg):
		self.Ok = 0
		self.Connected = 0
		#print "RAW = " + msg
		parts = msg.split(" ",3)
		if len(parts) == 4 :
			self.Server = parts[0].replace(":","",1)
			self.Type = parts[1]
			self.SubType = parts[2]
			self.Val= parts[3]
			self.Ok =1
		elif parts[0] == "PING":
			self.Server= ""
			self.Type="PING"
			self.SubType=""
			self.Val= parts[1]
			self.Ok=1
	#end def	
#end class
