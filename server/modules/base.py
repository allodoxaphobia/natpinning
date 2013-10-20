#!/usr/bin/env python
#filename=base.py

from __future__ import with_statement
from threading import Thread
import random
import socket
import time
import contextlib
import exceptions
import subprocess
import asyncore
import sys

class Base(asyncore.dispatcher):
	VICTIMID = ""
	CALLER = None
	HANDLER = None
	PTYPE = ""
	def __init__(self,sType, serverPort,caller):
		#caller is the calling object, this has to be of a class that supports the following methods
		#log(string, loglevel)
		#callback(host,port, proto) whereby proto is TCP or UDP
		global CALLER, PTYPE
		self.CALLER = caller
		asyncore.dispatcher.__init__(self)
		self.sPort = int(serverPort)
		if sType =="TCP" or sType == "UDP": self.PTYPE = sType
        	try:
	        	self.create_socket(socket.AF_INET6, socket.SOCK_STREAM)
			self.set_reuse_addr()
	        except AttributeError:
            		# AttributeError catches Python built without IPv6
            		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error:
			# socket.error catches OS with IPv6 disabled
			self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		try:		
			self.bind(('', self.sPort))
			self.listen(5)
		except socket.error, e:
			if e.errno == 98:#address alrady in use
				print self.TYPE + " couldn't start, is something else using port " + str(serverPort) + "?"
				sys.exit(-1)
			elif e.errno == 13:#not sufficient permissions
				print "You don't have sufficient permissons to start a service on port " + str(serverPort) +", are you root?"
				sys.exit(-1)
			else:
				raise e
	#end def
	
	def handle_accept(self):
		pair = self.accept()
		if pair is not None:
			conn, addr = pair
			self.protocolhandler(conn,addr)
			
	#end def
	def protocolhandler(self,conn, addr):
		pass
	#end def
	def stop(self):
		self.close()
	#end def
	def log(self,value,logLevel):
		self.CALLER.log(self.TYPE + " : " + value,logLevel)
	#end def
#end class
