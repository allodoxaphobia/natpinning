#!/usr/bin/env python
from modules import irc
from modules import ftp

x = irc.Client("62.213.198.42", 6667,"192.168.1.2",9997)
x.run()
if x.Result == 1: print "nf_conntrack_irc is loaded: natpin through DCC succesfull"
else: print "nf_conntrack_irc is not loaded"

x = ftp.Client("62.213.198.42", 21,"192.168.1.2",9998)
x.run()
if x.Result == 1: print "nf_conntrack_ftp is loaded: natpin through PASV succesfull"
else: print "nf_conntrack_ftp is not loaded"
