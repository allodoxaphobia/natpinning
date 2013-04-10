#!/usr/bin/env python

# TFTP conntrack: when succesfull it allows a callback from the server from another sourceport (same destination port)
# it is not very usefull for exploitation, added as iptables nf_conntrack_tftp  check.
#
# Requires: scapy, must be run as root

from scapy.all import *
import socket

class TFTPClient():
	#wil send out one packet and wait for incomming packet from different source port to identify wether test was succesfull.
	def __init__(self, server, serverport,sourceip,sourceport):
		tftprq = IP(src=sourceip,dst=server)/UDP(sport=int(sourceport),dport=int(serverport))/TFTP()/TFTP_RRQ(filename="natpin.txt")
		send(tftprq)
	#end def
#end class

x = TFTPClient("IP_HERE",69,"192.168.1.2",111) #portmapping for the win

