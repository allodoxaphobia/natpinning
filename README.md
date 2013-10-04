NATpinning
===============
This tool is based of the original NAT pinning POC by Samy Kamkar: http://samy.pl/natpin/. 
The original proof-of-concept provided by Samy was just that, a proof-of-concept, and has very little usefulness for penetration testers.
This test suite should overcome this shortcoming as well as provide support for multiple protocols. It should also be more reliable then the original javascript published by Samy as it utilizes Flash sockets and therefor does not send additional, unwanted, data such as HTTP headers.
We identified the need for this during manual testing as we found most connection tracking modules these days don't just look for a single line/command, but rely on several request/response pairs to identify valid traffic.

The test suite is currently still under development, but when finished should aid penetration testers in accuratly assessing the state of nf_conntrack 
modules used by the router.
The most common issues identified with these are:
	- allowing port forwarding to a third host
	- allowing port forwarding to reserved ports.




How it works
============
The suite consists of two different components, server and client. 

The server is a python script which needs to be run from an Internet based host, with a public IP assigned to it and not firewalled. Once the script is running it will open dummy services (irc, ftp) and a flash policy server.

The client is the combination of HTML, JavaScript and a AS3 (Actionscript 3) flash file. The exploit page and flash file are to be hosted on the same server as the server component.
When the victim loads the exploit page, the flash file will connect to one of the exposed dummy services and a communication between them will ensue that should trigger the nf_conntrack modules on the victim's router to expose and forward additional ports, at which point the server component will attempt to connect to these additional exposed ports.



 __________							________________
 |Browser |<------ Victim loads exploit page ----------------- |                |
 |   on   |======= Flash talks to dummy service =============> |EXPLOIT SERVER  |
 | victim |<###### Router forwards additional ports #########> |                |
 |   PC   |<-------Exploit server connects to forwarded port---|________________|
/ -------- \
____________


Usage
=====
on the exploit server
Copy the files exploit/exploit.html and exploit/exploit.swf to your web-root
Then run the following command. Note that this must be run as root.
$sudo server/tests.py


Usage: tests.py --proto=PROTOCOL --type=CALLBACK_TYPE

Options:
  -h, --help            show this help message and exit
  -p PROTO, --proto=PROTO
                        Protocol you wish to test: FTP, IRC, SIP (default is all)
  -t CBTYPE, --type=CBTYPE
                        How do you wish to connect back to the client: socket,
                        ssh, telnet, none

To run tests, naviguate the victim browser to http://exploit_server/rafsstuff/exploit.html?server=exploit_server&ci=192.168.0.156&cp=443&type=irc
whereby
	server: is the ip to which flash should connect
	ci: the ip of the host you are trying to expose
	cp: the port on host ci you are trying to gain access to
	type: the protocol you want to use for the test (irc, ftp or sip, default is all)


Current status:
===============
The server tool currently supports:
- the IRC protocol, nat pinning triggered through a DCC chat message
- the FTP protocol,nat pinning triggered through the PORT command
- the SIP protocol, nat pinning triggered through a REGISTER message (opens UDP port)



