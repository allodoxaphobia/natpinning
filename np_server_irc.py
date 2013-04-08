#!/usr/bin/env python
from optparse import OptionParser
from threading import Thread
import random
import socket
import struct


s= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
s.bind(("",6667))
s.listen(1)
while 1:
	cSock, cAddr = s.accept()
	cFile = cSock.makefile('rw',0)
	cFile.write("irc.khleuven.be NOTICE AUTH :*** Looking up your hostname...\r\n")
	while 1:
		line = cFile.readline().strip()
		parts = line.split(" ")
		print line
		if parts[0]=="NICK":
			cFile.write(":irc.khleuven.be 376 natpin252 :End of /MOTD command.\r\n")
		elif parts[0] == "PRIVMSG":
			if parts[3] == "CHAT":
				numip = parts[5]
				numport = parts[6].replace("\x01,""")
				print "Make a callback on " + numip + " " + numport

