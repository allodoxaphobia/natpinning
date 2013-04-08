#!/usr/bin/env python
from optparse import OptionParser
import threading

class IRCClient():
	def __init__(self, server, port):
		self.IRCServer = server
		self.IRCPort = port
	def connect(self, server="",port=0):
		if server != "" and port !=0:

		else:
			t =threading.Thread(target=connect, args=(self.IRCServer, self.IRCPort)
			#pushiong htis on a seperate thread
			t.start()

x = new IRCCLient()
x.connect("irc.khleuven.ac.be",6667)
