from modules import irc
from modules import ftp
from modules import flashpol
from modules import web
from modules import sip
from modules import h225
from modules import cmd

#global imports
import asyncore
import thread
import urllib2

class Engine():
	"""Main class of this application, used as interface between user interaction part and back end sercvices
	which are the bread and buttor of this application
	"""
	PUBLIC_IP = ""
	VERBOSITY = 0				#level of verbosity in output
	LOGTYPE = "screen"			#currently not used
	SERVERS = []				#array which will hold loaded services
	SERVICE_THREAD = None
	RULES = []
	PROTOS=["FTP","IRC","SIP","H225"]	#supported protcols
	def __init__(self, verbosity=0, logType="screen"):
		global VERBOSITY, LOGTYPE, PUBLIC_IP
		self.VERBOSITY = verbosity
		self.PUBLIC_IP = self. getExternalIP()
		LOGTYPE = logType #either "screen" or filename
	#end def
	
	def getVictims(self):
		"""Retrieves Array of Victim objects from command server.
		Yields:
			array: array of victims or empty array when none are found
		"""
		for server in self.SERVERS:
			if server.TYPE=="Command Server":
				if server.HANDLER:
					return server.HANDLER.VICTIMS
				else:
					return []
	def getExternalIP(self):
		"""Calls remote page over HTTP to get external IP address, returns string"""
		try:
			req = urllib2.urlopen('http://checkip.dyndns.com')
			data = req.read().split(" ")
			sip = data[len(data)-1].strip()
			if sip.index("<")<= 1:
				sip = ""
			else:
				sip = sip[:sip.index("<")-1]
		except Exception,e:
			print e
			self.log("Failed to retrieve public IP from: http://checkip.dyndns.com :" + e.message,1)
			sip =""
		if sip=="":
			#backup plan 
			try:
				req = urllib2.urlopen('https://enabledns.com/ip')
				sip = req.read()
			except Exception, e:
				self.log("Failed to retrieve public IP from: https://enabledns.com/ip" + e.message ,1)
				sip =""
		if not self.isValidIPv4(sip):
			self.log("getExternalIP(): Invalid IPv4 specification " + sip, 4)
			sip = ""
		return sip
	def getExploitPage(self):
		"""Generates example URL to use on clients"""
		sport = "80"
		sip = self.PUBLIC_IP
		if sip=="": sip = "External_Ip_Of_This_Host"
		for server in self.SERVERS:
			if server.TYPE=="Web Server":
				sport = str(server.PORT)
		return "http://"+sip+":"+sport+"/exploit.html?ci=LAN_IP_Of_Client"
	def getVictimById(self,id):
		"""Retrieves specific victim from commandserver.victims.
		Args:
			id (int): index nr of victim in commandserver.VICTIMS array
		"""
		victims = self.getVictims()
		if victims != None:
			try:
				result = victims[int(id)]
			except IndexError:
				result = None #invalid list index
		else:	
			result = None
		return result
	def getVictimTest(self,testid):
		"""Retrieves specific test.
		Args:
			testid (string): test.TEST_ID; a unique identifier given to each test as defined in server/modules/cmd.py
		"""
		victims = self.getVictims()
		if victims != None:
			for victim in victims:
				for test in victim.TESTS:
					if test.TEST_ID==testid:
						return test
	def getVictimByTestId(self,testid):
		"""Retrieves victim from loaded victims based on a certain testid.
		Args:
			testid (string): test.TEST_ID; a unique identifier given to each test as defined in server/modules/cmd.py
		"""
		victims = self.getVictims()
		if victims != None:
			for victim in victims:
				for test in victim.TESTS:
					if test.TEST_ID==testid:
						return victim
	def getRemotePeer(self,sock):
		"""Gets remote IP, strips of ipv6 prefix
		Args:
			sock: instance of asyncore.dispatcher
		"""
		tmp = sock.getpeername()[0]
		tmp = tmp.replace("::ffff:","")
		return tmp
	def log(self, value, logLevel):
		if logLevel <= self.VERBOSITY:
			print "\033[1;34m> "+value+"\033[1;m"
		#end if
	#end def
	def isValidIPv4(self,sIP):
		sparts = sIP.split(".")
		#must have for parts
		if len(sparts)<>4:
			return False
		else:
			for part in sparts:
				if not part.isdigit():
					return False
				else:
					if int(part)>255 or int(part)<0:
						return False
		return True
	def isValidTestCommand(self,clientid,proto,ip,port,printError=False):
		"""Checks TEST command for validity. This is in engine class rather then in run.py as it is
		used both by run.py for command line interaction, as well as by the web service.
		"""
		result = False
		if not clientid.isdigit():
			if printError: print "You provided an invalid client id, type 'list clients' for a list of available clients."
			return False
		if self.getVictimById(clientid)==None:
			if printError: print "You provided an invalid client id, type 'list clients' for a list of available clients."
			return False
		if not port.isdigit():
			if printError: print "Invalid port specified. Allowed values: 1-65535"
			return False
		else:
			if int(port)<1 or int(port)>65535:
				if printError: print "Invalid port specified. Allowed values: 1-65535"
				return False
		if ip!="$":
			if len(ip.split("."))!=4:
				if printError: print("Only IPv4 IP addresses allowed at the moment")
				return False
		if not proto.upper() in self.PROTOS and proto.upper()!="ALL":
			if printError: print("You specified an invalid protocol.")
			return False		
		result = True #only gets here if all is well
		return result
	def getServicePort(self,serviceName):
		result = None
		for server in self.SERVERS:
			if server.sType.upper() == serviceName.strip().upper():
				result = server.PORT
		return result
	def runServers(self,runCMD,runWeb, runFlash, web_port,proto="ALL"):
		global SERVERS, SERVICE_THREAD
		if runCMD == True: self.SERVERS.append(cmd.Server(proto="TCP",serverPort=60003,caller=self))
		if (runWeb==True): self.SERVERS.append(web.Server(serverPort=web_port,caller=self))#required: flash policy server
		if (runFlash==True): self.SERVERS.append(flashpol.Server(serverPort=843,caller=self))
		if proto== "FTP" or proto== "ALL":
	        	self.SERVERS.append(ftp.Server(serverPort=21,caller=self))
		if proto== "IRC" or proto== "ALL":
			self.SERVERS.append(irc.Server(serverPort=6667,caller=self))
		if proto ==  "SIP" or proto==  "ALL":
			self.SERVERS.append(sip.Server(serverPort=5060,caller=self))
		if proto ==  "H225" or proto==  "ALL":
			self.SERVERS.append(h225.Server(serverPort=1720,caller=self))
		try:
			self.log("Services running",0)
			self.SERVICE_THREAD = thread.start_new_thread(asyncore.loop,())
		except KeyboardInterrupt:
			self.shutdown()
	#end def
	def shutdown(self):
		global SERVICE_THREAD
		for server in self.SERVERS:
			server.stop()
		self.SERVICE_THREAD = None
	#end def
#end class
