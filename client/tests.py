#!/usr/bin/env python
from modules import irc
from modules import ftp
from optparse import OptionParser
import sys


def main():
    parser = OptionParser(usage = '%prog --proto=PROTOCOL --type=CALLBACK_TYPE')
    parser.add_option('-p', '--proto', dest='proto', type=str, help='Protocol you wish to test: FTP, IRC')
    parser.add_option('-P', '--port', dest='cbport', type=int, help='Port you wish to connect back to')
    parser.add_option('-I', '--ip', dest='cbip', type=str, help='IP you wish to connect back to')
    parser.add_option('-s', '--server', dest='server', type=str, help='Port you wish to connect back to')    
    opts, args = parser.parse_args()
    try:
	if opts.proto.upper()== "FTP":
		x = ftp.Client(opts.server, 21, opts.cbip, int(opts.cbport))
		x.run()
	elif opts.proto.upper()== "IRC":
		x = irc.Client(opts.server, 6667, opts.cbip, int(opts.cbport))	
		x.run()
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
