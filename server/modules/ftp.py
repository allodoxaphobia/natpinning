#!/usr/bin/env python
#filename=ftp.py
from base import *
import socket
import random
import struct
import select


class FTPProtoHandler(asyncore.dispatcher_with_send):
	def __init__(self,conn_sock, client_address, server):
		self.server=server
		asyncore.dispatcher_with_send.__init__(self,conn_sock) #Line is required
		self.server.log("Received connection from " + client_address[0] + ' on port ' + str(self.server.sPort),1)
		self.send("220 NATPinningTest\r\n")
		self.cbport=0
		self.cbaddr=""
	def handle_read(self):
		try:
			request = self.recv(1024).strip()
			if (request[:4].upper() == "PORT"):
				self.cbport = self.ftpCalcPort(request)
				self.cbaddr = self.ftpCalcAddr(request)
				if (self.cbport > 0 ):
					self.server.log("Callback expected on " + self.cbaddr + ":" + str(self.cbport),2)
				else:
					self.server.log("Failed to calculate port from: " + line,1)
				self.send("200 Let's do this\n")
			elif (request[:4].upper() == "USER"):
				parts = request.split(" ")
				self.server.TESTID = parts[1]
				self.send("331 user ok, need pass\n")
			elif (request[:4].upper() == "PASS"):
				self.send("230 is good\n")
			elif (request[:4].upper() == "LIST"):
				self.send("150 opening data connection\n")
				self.server.log("FTP Received PORT + LIST callback request for " + self.cbaddr + " on port " + str(self.cbport),2)
				self.server.callback(self.cbaddr,int(self.cbport),"TCP","FTP PORT", self.server.TESTID)		
			elif (request[:4].upper()=="PASV"):
				pass #TODO			
			elif (request[:4].upper()=="QUIT"):
				self.send("221 byebye\n")
				self.close()
			elif len(request)<4 and len(request)>0:
				self.send("500 did not understand that.\n")
				self.server.log("Invalid FTP command:" + request,1)
				pass
			elif len(request)==0:
				#client closed connection
				self.server.log("FTP client closed connection.",1)
				self.close()
			else:
				self.server.log("Invalid FTP command:" + request,1)
				self.send("500 did not understand that.\n")
		except Exception,e:
				self.server.log("Error receiving/sending data." ,1)
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
			x = int(parts[4])
			y = int(parts[5])
			return int(parts[4])*256 + int(parts[5])
		except:
			return 0
	#end def
#end class


class Server(Base):
	def __init__(self,serverPort=21,caller=None):
		self.TYPE = "FTP Server"
		Base.__init__(self,"TCP",serverPort,caller)
		self.log("Started",2)
	#end def
	def protocolhandler(self,conn, addr):
		self.HANDLER = FTPProtoHandler(conn,addr,self)
	#end def
#end class
