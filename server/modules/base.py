#!/usr/bin/env python
#filename=base.py

from __future__ import with_statement
from threading import Thread
import random
import socket
import time
import contextlib
import exceptions

class Base(object):
	def __init__(self,sType, serverPort,sCallbackType):
		self.sPort = int(serverPort)
		self.CB_TYPE=sCallbackType #socket, ssh, telnet TODO
		if sType =="TCP" or sType == "UDP": self.pType = sType
        	try:
	        	self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
	        except AttributeError:
            		# AttributeError catches Python built without IPv6
            		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error:
			# socket.error catches OS with IPv6 disabled
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind(('', self.sPort))
		self.sock.listen(5)
	#end def
	
	def run(self):
		#try:
			while True:
				t = Thread(target=self.handler,args=(self.sock.accept()))
				t.start()
		#except socket.error, e:
		#	self.log('Error accepting connection: %s' % (e[1],))
	#end def
	def handler(self,conn, addr):
		with contextlib.closing(conn):
			self.log("Received connection from " + addr[0])
        	       	self.protocolhandler(conn, addr)
	#end def
	
	def protocolhandler(self,conn, addr):
		pass
		#OVERRIDE THIS FUNCTION
	#end def
	def callback(self,sProto,sType,sIP,iPort):
		if sType == "socket":
			try:
				cbsock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
				cbsock.connect((sIP,iPort))
				self.log(sProto + ": Callback success on): " + sIP + " port " +str(iPort))
				cbsock.close()
			except socket.error:
				self.log(sProto + ": Callback failed on): " + sIP + " port " +str(iPort))
	#end def
	def log(self, str):
        	print str
	#end def
#end class
