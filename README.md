NATpinning
===============
This tool is based of the original NAT pinning proof-of-concept by Samy Kamkar: http://samy.pl/natpin/. 
Samy's original proof-of-concept was javascript based, which brought with it several shortcommings:
	- client-response sequences might be broken due to additional HTTP headers
	- opening some ports might be blocked by browsers (e.g.: 6667 for irc)
To overcome these issues we used flash for our client side component. 
We also attempted to extend this proof-of-concept to a more mature state by creating a server side tool which supports several protocols and gives some level of controle over the client behavior.



How it works
============
The suite consists of two different components, server and client. 

The server is a python script which needs to be run from an Internet based host, with a public IP assigned to it and not firewalled.
Once the script is running it will open dummy services (irc, ftp, sip ) a flash policy server a web service and a command-and-control service.

The client is the combination of HTML, JavaScript and, most importantly, a AS3 (Actionscript 3) flash file. 
When the victim loads the exploit page, the flash file will connect to the command service and register itself.
At this point it is possible to start testing for possible natpinning issues using the command server by instructing the client to initiate sessions for the different protocols.

When succesfull nat pinning is detected the user controlling the server can drop to shell and initiate a connection back to the newly exposed port using their favorite tool.

Usage
==============
sudo ./run.py

Usage: run.py 

Options:
  -h, --help  show this help message and exit
  --no-web    Do not run the internal web service (port 80).
  --no-flash  Do not run the internal flash policy service (port 843).
  -v VERBOSE  Verbosity level, default is 2, set to 0 if you like a lot of
              output.
