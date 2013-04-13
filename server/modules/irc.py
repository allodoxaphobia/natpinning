#!/usr/bin/env python
#filename=irc.py
from Base import *

class Server(Base):
	def __init__(self,serverPort=6667):
		Base.__init__(self,"TCP",serverPort)
	#end def
	def protocolhandler(self,conn, addr):
		pass
		#OVERRIDE THIS FUNCTION
	#end def
#end class
