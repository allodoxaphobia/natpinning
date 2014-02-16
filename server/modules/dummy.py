#!/usr/bin/env python
#filename=dummy.py
#
#
# Copyright Gremwell,2013
# Author: Raf Somers
# License: GNU General Public License, version 3
#
#	This file conains a barebone service that you can use to create new services.

class MyProtoHandler(asyncore.dispatcher_with_send):
	"""Barebone protocol handler, use this a template when adding a new protocol
	
	Note:
		class inherits asyncore.dispatcher_with_send, http://docs.python.org/2/library/asyncore.html	
	
	"""
	def __init__(self,conn_sock, client_address, server):
		self.server=server
		asyncore.dispatcher_with_send.__init__(self,conn_sock) #Line is required
		#required init.
		self.server.log("Received connection from " + client_address[0] + ' on port ' + str(self.server.sPort),1)

class Server(Base):
	"""Server class, inherits the Base server calls to interface with application engine"""
	def __init__(self,serverPort=8888,caller=None):
		"""main initialisation
		
		Args:
			serverPort (int): port the service will listen on
			caller (Engine): this is the Engine class as defined in run.py
		"""
		#set serverport default to default port used by your protocl
		self.TYPE = "MyService Server"
		#set type to Protocol  name: e.g.: "FTP Server"
		Base.__init__(self,"TCP",serverPort,caller)
		#must implement Base.__init__
		self.log("Started",2)
	#end def
	def protocolhandler(self,conn, addr):
		"""Override for protcolhandler in Base class (base.py)
		sets the classes HANDLER an instance of to the MyProtocolHandler
		
		Args:
			conn : (socket connection)  passed on in Base class when socket accepts new connection
			addr : (socket address) passed on in Base class when socket accepts new connection
		"""
		self.HANDLER = MyProtoHandler(conn,addr,self)
	#end def
#end class
