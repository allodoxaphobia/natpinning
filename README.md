These are POC scripts to test natpinning on routers.

Eventually these will be bundeled into one tool that you can use to test all possible loaded helper 
modules on a router to determine which ones are loaded.
In a later stage basic tests will be performed to test the security implementation on the loaded modules.:
- e.g. does it trigger port forwarding after a single line
- does it simply ignore invalid statements
- where ip's are specified in the protocol (i.e.: IRC), does it allow portforwarding to a third host
- if it allows forwarding to a third host, does it allow forwarding to itself
- are the helpers security config parameters set correctly

The setup will allways be the same; client modules are loaded on a host on the target (NATted LAN), the server is set up on a remote server.
Once the client and server are communicating and one of them triggers the nat pinning/port forwarding, an automatic connect test to the forwarded port will be made to validate wether the test was 
succesfull.

Credits: original NAT  pinning POC by Samy Kamkar: http://samy.pl/natpin/


Current status:
===============
- a rough first IRC test is created, follows a fully correct irc conversation up to a DCC chat request (DCC send will also be added)
- a ftp server is created that supports natpinning test through PASV command and PORT command


Usage: IRC
============
start up np_server_irc.py on the internet based host
    Usage: np_server_irc.py
then run np_client_irc.py on the host behind the NAT router (-h for help)
    Usage: np_client_irc.py [options]
