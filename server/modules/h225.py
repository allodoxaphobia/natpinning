#!/usr/bin/env python
#filename=h225.py
from base import *
import socket
import random
import struct
import select

class H225ProtHandler(asyncore.dispatcher_with_send):
	def __init__(self,conn_sock, client_address, server):
		self.server=server
		asyncore.dispatcher_with_send.__init__(self,conn_sock) #Line is required
		self.server.log("Received connection from " + client_address[0] + ' on port ' + str(self.server.sPort),1)
		self.cbport=0
		self.cbaddr=""
	def handle_read(self):
		request = self.recv(1024).strip()
		if len(request)==0:
			self.server.log("H.225 Client disconnected.",1)
			self.close()
		else:
			TPTK_size = struct.unpack(">B", request[3:4])[0]
			if self.isValidPacket(request):
				q931 = request[4:] #strip off TPTK
				call_ref_len = struct.unpack(">B",q931[1:2])[0] #byte1,byte0 is protocol identifier
				q931 = q931[2+call_ref_len:] #strip of call reference
				q931_msg_type = struct.unpack(">B",q931[0:1])[0]
				self.server.log("Q931.Type: " + str(q931_msg_type),3)
				
				infofield1_type = struct.unpack(">B",q931[1:2])[0]
				infofield1_length = struct.unpack(">B",q931[2:3])[0]
				infofield1 = q931[3:3+infofield1_length]
				
				q931 = q931[3+infofield1_length:]#strip of infofield1
				infofield2_type = struct.unpack(">B",q931[0:1])[0]
				ip_port_data = self.getIpAndPort(q931[14:20])
				if infofield2_type==126:
					infofield2_len = struct.unpack(">H",q931[1:3])[0]
					self.server.log("Q931.PDU Length: " + str(infofield2_len),3)
					self.server.callback(ip_port_data[0],ip_port_data[1],"TCP","H225 CONNECT", infofield1)
				else:
					self.server.log("Received invalid TPTK packet (Wrong data), will ignore.",2)
			else:
				self.server.log("Received invalid TPTK packet, will ignore.",2)		
	
	def isValidPacket(self,packet):
		TPTK_size = struct.unpack(">B", packet[3:4])[0]
		if TPTK_size != len(packet):return False			#wrong TPTK size
		if (struct.unpack(">B", packet[4:5])[0]!=8): return False	#not a Q.931 packet
		return True
	
	def getIpAndPort(self,byteString):
		ipblck1 = str(struct.unpack(">B",byteString[0:1])[0])
		ipblck2 = str(struct.unpack(">B",byteString[1:2])[0])
		ipblck3 = str(struct.unpack(">B",byteString[2:3])[0])
		ipblck4 = str(struct.unpack(">B",byteString[3:4])[0])
		portblck = struct.unpack(">H",byteString[4:6])[0]
		return (ipblck1+"."+ipblck2+"."+ipblck3+"."+ipblck4,portblck)
#end class

class Server(Base):
	def __init__(self,serverPort=1720,caller=None):
		self.TYPE = "H225 Server"
		Base.__init__(self,"TCP",serverPort,caller)
		self.log("Started",2)
	#end def
	def protocolhandler(self,conn, addr):
		self.HANDLER = H225ProtHandler(conn,addr,self)
	#end def
#end class
