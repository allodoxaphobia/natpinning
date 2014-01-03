NATpinning
===============
This tool is based of the original NAT pinning proof-of-concept by Samy Kamkar: http://samy.pl/natpin/.
Nat handler modules are used by the kernel to keep track of protocols on natted networks that require additional communication channels to be opened for normal operations. These modules might be susceptible to abuse if/when they do not strictly adhere to RFCs. They might for instance allow the exposure of assigned ports, where only random port ranges should be allowed, or allow exposure of ports on a third party.

Samy's original proof-of-concept was javascript based, which brought with it several shortcommings:

	- client-response sequences might be broken due to additional HTTP headers
	- opening some ports might be blocked by browsers (e.g.: 6667 for irc on Firefox)

To overcome these issues I used flash as client side component. This allowed the use of Flash sockets, which don't have the extra overhead of HTTP headers and are not restricted by browser policies. 
I also attempted to extend this proof-of-concept to a more mature state by creating a server side tool which supports several protocols and gives some level of control over the client behavior.


How it works
============
The suite consists of of a server compnent (python) and a client component (web page).

The server is a python script which needs to be run from an Internet based host, with a public IP assigned to it and not firewalled.
Once the script is running it will open dummy services (irc, ftp, sip ), a flash policy server, a web service and a command-and-control service.

The client is the combination of HTML, JavaScript and, most importantly, a AS3 (Actionscript 3) flash file. 
When the victim loads the exploit page, the flash file will connect to the command service and register itself.
At this point it is possible to start testing for possible natpinning issues using the command server by instructing the client to initiate sessions for the different protocols.

When succesfull nat pinning is detected the user controlling the server can drop to shell and initiate a connection back to the newly exposed port using their favorite tool.

Installation
==============
Tested on xubuntu and backtrack, requires python 2.7
to install:
git clone https://github.com/allodoxaphobia/natpinning.git


Usage
==============
on the server: sudo ./run.py

Usage: run.py 

Options:
  -h, --help  show this help message and exit
  --no-web    Do not run the internal web service (port 80).
  --no-flash  Do not run the internal flash policy service (port 843).
  -v VERBOSE  Verbosity level, default is 2, set to 0 if you like a lot of
              output.

License
==============
This tool was created by Gremwell (http://www.gremwell.com) and released under GNU GPL v3. 
