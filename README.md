NATpinning
===============
This tool is based of the original NAT pinning proof-of-concept by Samy Kamkar: http://samy.pl/natpin/. 
Samy's original proof-of-concept was javascript based, which brought with it several shortcommings:
	- client-response sequences might be broken due to additional HTTP headers
	- opening some ports might be blocked by browsers (e.g.: 6667 for irc)
To overcome these issues we used flash for our lcient side code. We also attempted to extend this proof-of-concept to a more mature state by creating a server side tool which supports several protocols and gives some level of controle over the client behavior.



How it works
============
The suite consists of two different components, server and client. 

The server is a python script which needs to be run from an Internet based host, with a public IP assigned to it and not firewalled.
Once the script is running it will open dummy services (irc, ftp, sip ) a flash policy server a web service and a command-and-control service.

The client is the combination of HTML, JavaScript and a AS3 (Actionscript 3) flash file. 
When the victim loads the exploit page, the flash file will connect to one of the command sericve and register itself.
At this point it is possible to start testing for possible natpinning issues using the command server. 

Usage
==============
