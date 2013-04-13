#!/usr/bin/env python
#filename=base.py

from threading import Thread
import random
import socket
import time
import contextlib
import exceptions

class Base(object):
	def __init__(self,sType, serverPort):
		self.sIp = serverIp
		self.sPort = int(serverPort)
		self.cbIp = sCallbackip
		self.cbPort = int(iCallbackPort)
		if sType =="TCP" or sType == "UDP": self.pType = sType
        	try:
	        	self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
	        except AttributeError:
            		# AttributeError catches Python built without IPv6
            		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error:
			# socket.error catches OS with IPv6 disabled
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	
			self.sock.bind(('', port))
			self.sock.listen(5)
	#end def
	
	def run(self):
		try:
			while True:
				thread.start_new_thread(self.accept, self.sock.accept())
		except socket.error, e:
			self.log('Error accepting connection: %s' % (e[1],))
	#end def
	def accept(self,conn, addr):
		with contextlib.closing(conn):
               		protocolhandler(self,conn, addr)
        except socket.error, e:
            self.log('Error handling connection from %s: %s' % (addrstr, e[1]))
        except Exception, e:
            self.log('Error handling connection from %s: %s' % (addrstr, e[1]))
	#end def
	
	def protocolhandler(self,conn, addr):
		pass
		#OVERRIDE THIS FUNCTION
	#end def
	def log(self, str):
        	print >>sys.stderr, str
	#end def
#end class
