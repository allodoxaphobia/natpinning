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
from server.tools import ip

class Base(asyncore.dispatcher):
	VICTIMID = ""
	TESTID = ""
	CALLER = None
	HANDLER = None
	PTYPE = ""
	def __init__(self,sType, serverPort,caller):
		""" Base Class initialization
		
		Args:
			sType (string): either TCP or UDP
			serverPort (int): defzault port number the service will listen on (1-65535)
			caller (object): Instance of Engine class.
		"""
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
		"""Event, triggered when the socket receives a new connection.
		Grabs connection and address information from the socket and sets the protocolhandler.
		"""
		pair = self.accept()
		if pair is not None:
			conn, addr = pair
			self.protocolhandler(conn,addr)
			
	#end def
	def protocolhandler(self,conn, addr):
		""" Class object used to handle protcol data. Will be overwritten by inheriting class."""
		pass
	#end def
	def stop(self):
		self.close()
	#end def
	def log(self,value,logLevel):
		"""Calls Engine.log"""
		self.CALLER.log(self.TYPE + " : " + value,logLevel)
	#end def	
	def callback(self, host, port, transport, proto, testid=None):
		"""Callback is the function to call from any inheriting class when test are concluded
		Args:
			host (string): remote ip as returned by the test packet
			port (string): remote port as returned by the test packet
			transport (string):"TCP" or "UDP" 
			protcol (string): protocol used during testing ,set this to the value of the inheriting's classes TYPE var.
		"""
		if testid != None:
			test = self.CALLER.getVictimTest(testid)
			victim = self.CALLER.getVictimByTestId(testid)
			test.STATUS="DONE"
			test.PUBLIC_IP = victim.PUBLIC_IP
			test.TRANSPORT = transport
			if not host in victim.PUBLIC_IP:
				test.RESULT=False
				test.PUBLIC_PORT= "0"
				self.log("Test " + test.TEST_ID + " FAILED",0)
			else:
				test.RESULT=True
				test.PUBLIC_PORT= str(port)
				self.log("Test " + test.TEST_ID + " SUCCESS",0)
	#end def
	############################################################################
#end class
