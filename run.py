#!/usr/bin/env python
from server import engine
from optparse import OptionParser
from server.tools import ip
import sys
import readline
import socket
from datetime import datetime
from subprocess import call

class Shell():
	ENGINE = None
	CURR_VICTIM = None
	COMMANDS = "HELP", "LIST", "SET", "TEST", "EXPLOIT", "QUIT", "EXIT", "CLEAR" , "RELOAD"
	def __init__(self, engine):
		global ENGINE
		self.ENGINE = engine
		print "Interactive shell, type <help> if you're not sure on how to proceed."
		val = ""
		#readline.parse_and_bind()
		while val.upper() != "QUIT" and val.upper() != "EXIT":
			val = self.getUserInput()
			self.handleCMD(val)
		self.ENGINE.shutdown()
		#end while
	#end def

	def handleCMD_help(self,parts):
		if len(parts)==1:
			call("clear")
			exploit_page = self.ENGINE.getExploitPage()
			print "For extended help check out the wiki \n(https://github.com/allodoxaphobia/natpinning/wiki)."
			print ""
			print "Available Commands:"
			print "   help".ljust(15) + "Prints this message"
			print "   list".ljust(15) + "list items, expects list to display; clients, services, tests"
			print "   test".ljust(15) + "Test natpinning."
			print "   autotest".ljust(15) + "Test all possibilities on given client."
			print "   !".ljust(15) + "Drop to shell"
			print "   clear".ljust(15) + "Clears the screen."
			#disabled until fixed print "   reload".ljust(15) + "Reloads the given clients browser."
			print "   exit|quit".ljust(15) + "Quits the application."
			print ""
			print "Type <help command> to receive more detailed help on any given command."
			print ""
			print
			print "CLI Usage:"
			print "   The cli supports limited command history."
			print "   Use the <up-arrow> key for previous commands."
			print ""
			print "   To connect clients, point their browser to " + exploit_page
			print "   For example, if the client's private IP address is 192.168.0.5"
			print "   " + exploit_page.replace("LAN_IP_Of_Client","192.168.0.5")
			print "   Note that the server IP used is what we believe to be your public IP."
			print "   If you're running this setup in a test environment, alter this IP with the IP"
			print "   of the interface you're clients will be connecting to."
			print ""
		elif len(parts)==2:
			if parts[1].upper()=="CLEAR":
				print ""
				print "Clear: Clears the screen."	
				print ""
				print "Usage: "
				print "   clear"
			elif parts[1].upper() in ["QUIT","EXIT"]:
				print ""
				print parts[1] + ": Exits the application."	
				print ""
				print "Usage: "
				print "   " + parts[1]		
			elif parts[1].upper()=="TEST":
				print ""
				print "Test: The test command is the bread and butter of this tool"
				print "   it instructs a client to perform a natpin test."
				print ""
				print "Usage: "
				print """   test <client_id> (<protocol>|"ALL") (<ip>|"$") <port>"""
				print ""
				print "Notes: "
				print "   Supported protocols: 'FTP, IRC, SIP, H.225', use ALL to test all protocols"
				print "   Ip can be replaced by $ to use client's own private ip."
				print ""
				print "Examples: "
				print "   test 0 FTP 192.168.2.1 65532"
				print "   test 0 ALL $ 65532" 
				print ""
				print ""
			elif parts[1].upper()=="AUTOTEST":
				print ""
				print "Autotest: run all possible tests agains a client."
				print "   All protocols will be tested for ports 22, 3389 and 65500 "
				print "   and this for the client's private IP and another IP."
				print ""
				print "Usage: "
				print "   autotest [client-id]"
				print ""
				print "Note: "
				print "   If client id is ommited, will default to 0"
				print ""
			elif parts[1].upper()=="LIST":
				print ""
				print "List: The list command lists objects currently loaded."
				print "   list clients: lists all clients that connected since the program started."
				print "   list services: lists all services started by the program."
				print "   list tests [id]: lists all tests performed for the given client id"
				print " "
				print "Usage:"
				print "   list clients"
				print "   list services"
				print "   list tests"
				print "   list tests 0"
				print ""
				print "Note: "
				print "   list tests: If client id is ommited, will default to 0"
				print ""
	def handleCmd_test(self, args):
		if len(args) != 5:
			print "Invalid command format, type <help test> for correct syntax."
		else:
			vic_id = args[1]
			proto = args[2].upper()
			ip = args[3].strip()
			port = args[4]
			if self.ENGINE.isValidTestCommand(vic_id,proto,ip,port,True):
				victim = self.ENGINE.getVictimById(int(vic_id))
				if ip == "$":	
					ip = victim.PRIVATE_IP	
				if proto != "ALL":
					victim.addTest(proto, ip, str(port))
				else:
					#run all proto tests
					for xproto in self.ENGINE.PROTOS:
						victim.addTest(xproto, ip, str(port))
	def handleCmd_autotest(self,args):
		vicid = ""
		ports = [22,3389,65500]
		ips = []
		if len(args)==2:
			vicid = args[1].strip()
		else:
			vicid="0"
		victim = self.ENGINE.getVictimById(int(vicid))
		if victim == None:
			print "You specified an unkown client id. Type <help autotest> for more information."
			return 0
		else:
			ips.append(victim.PRIVATE_IP)
			ipparts = victim.PRIVATE_IP.split(".")
			if ipparts[3]!=1:
				tmpipblock = "1"
			else:
				tmpipblock = "2"
			ips.append(ipparts[0]+"."+ipparts[1]+"."+ipparts[2]+"."+tmpipblock)
		#add tests to client
		for ip in ips:
			if ip==victim.PRIVATE_IP:
				for port in ports:
					if self.ENGINE.isValidTestCommand(vicid,"ALL",ip,str(port),False):
						#input is validated
						for xproto in self.ENGINE.PROTOS:
							victim.addTest(xproto, ip, str(port))
			else:
				if self.ENGINE.isValidTestCommand(vicid,"ALL",ip,str(65500),False):
					victim.addTest(xproto, ip, str(65500))
	def handleCmd_list(self, command):
		parts = command.split(" ")
		if len(parts)<2:
			item = None
		else:
			item = parts[1].strip()
			item = item.upper()
		if item=="CLIENTS":
			victims = self.ENGINE.getVictims() # refresh list
			if len(victims) == 0:
				print "No clients connected yet. To make a client connect, let them browse to"
				print self.ENGINE.getExploitPage()
			else:
				call("clear")
				header= "%5s%15s%15s%15s"  % ("ID","Public IP", "Private IP","Last Seen")
				print header
				print self.setTableLine(len(header))				
				x = 0
				for victim in victims:
					lastseen = datetime.now()-victim.LAST_SEEN
					lastseen_formatted = str(lastseen.seconds) +"s"
					print "%5s%15s%15s%15s"  % (str(x),victim.PUBLIC_IP, victim.PRIVATE_IP,lastseen_formatted)
					x=x+1
		elif item=="SERVICES":
			print "Currently running services:"
			x = 0
			for server in self.ENGINE.SERVERS:
				print "\t" + str(x) + ".\t" + server.TYPE
				x=x+1
		elif item=="TESTS":
			victim = None
			if len(self.ENGINE.getVictims())==0:
				msg = "No clients connected. You can connect clients by making them browse to\n" + self.ENGINE.getExploitPage()
				print msg
				return 0
			if len(parts)>=3:
				vicid=parts[2].strip()
			else:
				#no client id specified, defaulting to 0
				self.ENGINE.log("No client ID specified, defaulting to client 0",0)
				vicid="0"
			try:
				victim = self.ENGINE.getVictimById(vicid)
			except Exception,e:
				print e.message
				victim = None
			if victim == None:
				print "Invalid client id specified. Type <help list> for correct syntax."
				return 0
			call("clear")
			print "Client:"
			print "   public ip: " + victim.PUBLIC_IP
			print "   last seen: " + victim.LAST_SEEN.strftime("%H:%M:%S")
			print ""
			header= "%20s%5s%20s%10s%10s"  % ("From"," ","To","TCP/UDP","Result")
			print header
			print self.setTableLine(len(header))
			if len(victim.TESTS)==0:
				print "No tests performed on this client. Type <help test> for help on how to perform tests"
			else:
				for test in victim.TESTS:
						if test.STATUS != "DONE":
							result = test.STATUS
						else:
							if str(test.PUBLIC_PORT)=="0":
								result = "FAILED"
							else:
								result = "SUCCESS"
							public_if = test.PUBLIC_IP + ":" + test.PUBLIC_PORT
							private_if = test.PRIVATE_IP + ":" + test.PRIVATE_PORT
							print "%20s%5s%20s%10s%10s" % (public_if,"=>",private_if,test.TRANSPORT,result)
		else:
			print "Invalid list item specified, allowed values are: clients, services,tests"
	def setTableLine(self,length):
		"""Returns string of - signs of length specified in parmaeters, used by list commands"""
		x = "-"
		while len(x)<length:
			x = x+"-"
		return x
	def getUserInput(self):
		prompt = ""
		user_input = raw_input(prompt).strip()
		return user_input
	def handleCMD(self,val):
		global CURR_VICTIM
		parts = val.split(" ")
		if parts[0].upper()=="LIST":
			self.handleCmd_list(val)
		elif parts[0].upper()=="SET":
			if len(parts)==3:
				if parts[1].upper() == "VIC":
					self.CURR_VICTIM = int(parts[2])
					print "Current victim set to " +  self.ENGINE.getVictimById(self.CURR_VICTIM).VIC_ID
		elif parts[0].upper()=="RELOAD":
			if len(parts)==2:
				client = self.ENGINE.getVictimById(int(parts[1]))
				if client != None:
					client._reload()
				else:
					print "Invalid client id. Type <list clients> for available clients."
		elif parts[0].upper()=="TEST":
			self.handleCmd_test(parts)
		elif parts[0].upper()=="AUTOTEST":
			self.handleCmd_autotest(parts)
		elif parts[0].upper()=="HELP" or parts[0]=="?":
			self.handleCMD_help(parts)
		elif parts[0]=="!":
			call(["bash"])
		elif parts[0].upper()=="CLEAR":
			call(["clear"])
		else:
			print "Invalid command. Type <help> for a list of available commands."
	#end def
#end class

def main():
	usg_msg=""" sudo ./run.py
	sudo ./run.py --web-port 8080
	sudo ./run.py (-h | --help)"""
	parser = OptionParser(usage = usg_msg)
	parser.add_option('--no-web', action="store_false", dest='runweb', default=True, help='Do not run the internal web service (port 80).')
	parser.add_option('--no-flash', action="store_false", dest='runflash', default=True, help='Do not run the internal flash policy service (port 843).')
	parser.add_option('--web-port', dest='webport', default=80, help='Specify different port for webserver.')
	parser.add_option('--no-clear', action="store_false", dest='no_clear', default=True, help="Don't clear screen when program starts.")
	parser.add_option('-v', dest='verbose', default=0, help='Verbosity level, default is 0, set to 5 if you like a lot of output.')
	opts, args = parser.parse_args()
	print ""
	print "Loading... please wait."
	x = engine.Engine(int(opts.verbose),"screen")
	x.runServers(True,opts.runweb,opts.runflash,opts.webport,"ALL")
	if opts.no_clear:
		call(["clear"])
	print "Natpinning test tool - http://github.com/allodoxaphobia/natpinning/"
	if x.PUBLIC_IP=="":
		x.log("Automatic detecting of external IP failed.",0)
		x.PUBLIC_IP = "SERVER_PUBLIC_IP"
		
	s = Shell(x)

#end def
if __name__ == '__main__':
    main()

