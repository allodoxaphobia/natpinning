#!/usr/bin/env python
from modules import irc
from modules import ftp
from optparse import OptionParser
import sys


def main():
    parser = OptionParser(usage = '%prog --proto=PROTOCOL --type=CALLBACK_TYPE')
    parser.add_option('-p', '--proto', dest='proto', type=str, default="all", help='Protocol you wish to test: FTP, IRC')
    parser.add_option('-t', '--type', dest='cbtype', type=str, help='How do you wish to connect back to the client: socket, ssh, telnet')
    opts, args = parser.parse_args()
    try:
	servers = []
    	if not opts.proto or not opts.cbtype:
    		print "Protocol and type are mandatory arguments"
    	else:
		if opts.proto.upper() == "FTP":
	        	servers.append(ftp.Server(sCallbackType=opts.cbtype.lower()))
	        elif opts.proto.upper() == "IRC":
	        	servers.append(irc.Server(sCallbackType=opts.cbtype.lower()))
		else:#run all
	        	servers.append(ftp.Server(sCallbackType=opts.cbtype.lower()))
	        	servers.append(irc.Server(sCallbackType=opts.cbtype.lower()))
		while True:
			for server in servers:
				server.run()
    except Exception, e:
        print e
        sys.exit(1)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
