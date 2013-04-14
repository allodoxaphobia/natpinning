#!/usr/bin/env python
#filename=ftp.py
from base import *
import socket
import random
import struct

class Server(Base):
	def __init__(self,serverPort=21,sCallbackType="socket"):
		Base.__init__(self,"TCP",serverPort,sCallbackType)
		self.EXIT_ON_CB = 1
	#end def
	def protocolhandler(self,conn, addr):
		#we just received a new connection at this point
		#send initial FTP server data
		conn.send("220 NATPinningTest\n")
		while True:
			request = conn.recv(1024).strip()
			if (request[:4].upper() == "PORT"):
				cbport = self.ftpCalcPort(request)
				cbaddr = self.ftpCalcAddr(request)
				if (cbport > 0 ):
					print "Callback expected on " + cbaddr + ":" + str(cbport)
				else:
					print "Failed to calculate port from: " + line
			elif (request[:4].upper() == "USER"):
				conn.send("331 user ok, need pass\n")
			elif (request[:4].upper() == "PASS"):
				conn.send("230 is good\n")
			elif (request[:4].upper() == "LIST"):
				conn.send("150 opening data connection\n")
				self.log("FTP Received PORT + LIST callback request for " + cbaddr + " on port " + str(cbport))
				self.callback("FTP", self.CB_TYPE,cbaddr,int(cbport))
				if self.EXIT_ON_CB == 1:
					break				
			elif (request[:4].upper()=="PASV"):
				pass #TODO			
			elif (request[:4].upper()=="QUIT"):
				conn.send("221 byebye\n")
				conn.close()
				break	
			elif len(request)<4:
				pass
			else:
				conn.send("500 did not understand that.\n")
	#end def
	def ftpCalcAddr(self,lsPortCommand):
		try:
			ls = lsPortCommand.split(" ")
			parts = ls[1].split(",")
			return parts[0] + "." + parts[1] + "." + parts[2] + "." + parts[3]
		except:
			return ""
	def ftpCalcPort(self,lsPortCommand):
		try:
			ls = lsPortCommand
			ls = ls.upper()
			ls = ls.replace("PORT","")
			ls = ls.strip()
			parts = ls.split(",")
			return int(parts[4])*256 + int(parts[5])
		except:
			return 0
	#end def
#end def
#end class
