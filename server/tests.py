#!/usr/bin/env python
from modules import irc
from modules import ftp
from modules import flashpol
from modules import web
from optparse import OptionParser
import sys
import asyncore

def main():
    parser = OptionParser(usage = '%prog --proto=PROTOCOL --type=CALLBACK_TYPE')
    parser.add_option('-p', '--proto', dest='proto', type=str, default="all", help='Protocol you wish to test (default is all): FTP, IRC')
    parser.add_option('-t', '--type', dest='cbtype', type=str, default="socket", help='How do you wish to connect back to the client (default is socket: socket, ssh, telnet')
    parser.add_option('--no-web', action="store_false", dest='runweb', default=True, help='Do not run the internal web service (port 80).')
    parser.add_option('--no-flash', action="store_false", dest='runflash', default=True, help='Do not run the internal flash policy service (port 843).')
    parser.add_option('-q', action="store_false", dest='verbose', default=True, help='Kill verbose output')
    opts, args = parser.parse_args()
    try:
	servers = []
    	if (opts.runflash==True): servers.append(flashpol.Server(sCallbackType=opts.cbtype.lower(),serverPort=843,verbose=opts.verbose))#required: flash policy server
    	if (opts.runweb==True): servers.append(web.Server(sCallbackType=opts.cbtype.lower(),serverPort=80,verbose=opts.verbose))#required: exploit server
	if opts.proto.upper() == "FTP" or opts.proto.upper() == "ALL":
	        servers.append(ftp.Server(sCallbackType=opts.cbtype.lower(),serverPort=21,verbose=opts.verbose))
	elif opts.proto.upper() == "IRC" or opts.proto.upper() == "ALL":
		servers.append(irc.Server(sCallbackType=opts.cbtype.lower(),serverPort=6667,verbose=opts.verbose))
	elif opts.proto.upper() == "SIP" or opts.proto.upper() == "ALL":
		servers.append(sip.Server(sCallbackType=opts.cbtype.lower(),serverPort=5060,verbose=opts.verbose))	
	try:
		print "Services running, press CTRL-C to exit."
		asyncore.loop()
	except KeyboardInterrupt:
		#cleanup
		for server in servers:
			server.stop()	
    except Exception, e:
        print e
        sys.exit(1)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
