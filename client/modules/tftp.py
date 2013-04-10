#!/usr/bin/env python
#filename=tftp.py

#nf_conntrack_tftp allows a callback from the server from a different port. 
#so a test is succesfull if/when it is possible to reply to a tftp message from a different sourceport
#
#tests to include: 
#	- can dangerous ports be used as sourceport for the initial request from client
#	- are spoofed source ip's routed through

