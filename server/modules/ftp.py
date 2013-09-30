#!/usr/bin/env python
#filename=ftp.py
from base import *
import socket
import random
import struct
import select


class FTProtoHandler(asyncore.dispatcher_with_send):
	def __init__(self,conn_sock, client_address, server):
		self.server=server
		asyncore.dispatcher_with_send.__init__(self,conn_sock) #Line is required
		self.server.log("Received connection from " + client_address[0] + ' on port ' + str(self.server.sPort))
		self.send("220 NATPinningTest\r\n")
	def handle_read(self):
		request = conn.recv(1024).strip()
		if (request[:4].upper() == "PORT"):
			cbport = self.ftpCalcPort(request)
			cbaddr = self.ftpCalcAddr(request)
			if (cbport > 0 ):
				self.server.log("Callback expected on " + cbaddr + ":" + str(cbport))
			else:
				self.server.log("Failed to calculate port from: " + line)
			self.send("200 Let's do this\n")
		elif (request[:4].upper() == "USER"):
			self.send("331 user ok, need pass\n")
		elif (request[:4].upper() == "PASS"):
			self.send("230 is good\n")
		elif (request[:4].upper() == "LIST"):
			self.send("150 opening data connection\n")
			self.server.log("FTP Received PORT + LIST callback request for " + cbaddr + " on port " + str(cbport))
			self.server.callback("FTP", self.server.CB_TYPE,cbaddr,int(cbport))
			if self.EXIT_ON_CB == 1:
				self.close()			
		elif (request[:4].upper()=="PASV"):
			pass #TODO			
		elif (request[:4].upper()=="QUIT"):
			conn.send("221 byebye\n")
			conn.close()
		elif len(request)<4:
			pass
		else:
			self.send("500 did not understand that.\n")
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
#end class


class Server(Base):
	def __init__(self,serverPort=21,sCallbackType="socket"):
		Base.__init__(self,"TCP",serverPort,sCallbackType)
		self.EXIT_ON_CB = 1
		self.TYPE = "FTP Server"
	#end def
	def protocolhandler(self,conn, addr):
		self.HANDLER = FTPProtoHandler(conn,addr,self)
	#end def
#end class
