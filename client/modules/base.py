#!/usr/bin/env python
#filename=base.py

from threading import Thread
import random
import socket
import time

class Base():
	#class handles callbacks and initial connection setup
	sIp =""			#server IP
	sPort = 0 		#server port
	sSock = None		#socket to connect to server
	cbIp = ""		#callback IP
	cbPort = 0		#callback Port
	cbTimeOut=10
	cbSock = None		#callback socket
	pType = "TCP"		#TCP or UDP
	Result =""
	def __init__(self,sType,serverIp, serverPort, sCallbackip,iCallbackPort):
		self.sIp = serverIp
		self.sPort = int(serverPort)
		self.cbIp = sCallbackip
		self.cbPort = int(iCallbackPort)
		if sType =="TCP" or sType == "UDP": self.pType = sType
	#end def
	
	def _callback(self):
		#sets up callback port on seperate threat
		if self.pType =="TCP":
			self.callbackThread = Thread(target=self.callbackTCP)
			self.callbackThread.start()
			self.timeThread = Thread(target=self.timeout)
			self.timeThread.start()
	#end def
	
	def timeout(self):
		#kills callback sock thread after n seconds
		#if that thread is done before this, this threrad will be terminated
		time.sleep(self.cbTimeOut)
		if self.callbackThread.isAlive():
			self.callbackThread._Thread__stop()
			self.Result="ERROR:TIMEOUT"
	#end def
	def callbackTCP(self):
		#sets up TCP callback port
		#when connection is received, updates self.Result
		s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
		s.bind(("",self.cbPort))
		print "Callback service listening on " + self.cbIp + ":" + str(self.cbPort)
		s.listen(0)
		cSock, cAddr = s.accept()
		s.close()
		result = 1
		self.Result = result
		#cleanup timeoutThread
		if self.timeThread.isAlive(): self.timeThread._Thread__stop()
	#end def
	def connectTCP(self,sServer,iPort):
		if sServer != "" and iPort !=0:
			try:
				self.sSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)		
				self.sSock.connect((sServer,iPort))
			except:	
				self.sSock = None
		return self.sSock
	#end def
	
	def run(self):
		if self.pType=="TCP":
			if self.connectTCP(self.sIp,self.sPort) is not None: #set to none on error
				self._callback() #sets up callback socket
				self.protocolThread = Thread(target=self.protocolhandler)
				self.protocolThread.start()
				while self.Result == "": pass	#wait for testresults
				self.destroy()
			else:
				print "Failed to connect to " + self.sIp + " on port " + str(self.sPort)
	#end def
	
	def protocolhandler(self):
		print "You MUST ovverride this function in your inheriting class, this is your bread and butter"
	#end def
	def destroy(self):
		if self.sSock is not None:self.sSock.close()
		if self.cbSock is not None:self.cSock.close()
		if self.callbackThread.isAlive():self.callbackThread._Thread__stop()
		if self.timeThread.isAlive():self.timeThread._Thread__stop()
		if self.protocolThread.isAlive():self.protocolThread._Thread__stop()
	#end def
#end class
