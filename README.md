NATpinning
===============
Based on Samy Kamkar's original idea of NATpinning (http://samy.pl/natpin/), this tool allows pentration testers to identify possible security issues with connection trackers on gateway devices. This is achieved by using a custom FLASH script which mimicks the behaviour of protcols that would normally trigger connection tracking to occur on these devices. As the client can be controlled from the server it can be instructed which protocols to mimick, in what order they should be performed and which port or IP they should use in their communications. This gives the tester the ability to test for assigned port (1-1024) exposure or exposure of other LAN based devices.

FLASH was chosen as client component as it is capable of raw socket communications. This removes the overhead of additional HTTP headers when using javascript and HTTP POST requests, as witnessed in Samy's original proof of concept.

For more extended information on how and why this works, check out our wiki: https://github.com/allodoxaphobia/natpinning/wiki


Installation
==============
Tested on xubuntu and backtrack, requires python 2.7

To install:
```
git clone https://github.com/allodoxaphobia/natpinning.git
```


Usage
==============
```
Usage:  sudo ./run.py
	sudo ./run.py --web-port 8080
	sudo ./run.py (-h | --help)

Options:
  -h, --help          show this help message and exit
  --no-web            Do not run the internal web service (port 80).
  --no-flash          Do not run the internal flash policy service (port 843).
  --web-port=WEBPORT  Specify different port for webserver.
  --no-ip             Don' call external URLs to determine ip.
  -v VERBOSE          Verbosity level, default is 0, set to 5 if you like a
                      lot of output.
```
More information on usage and usage examples can be found [here](https://github.com/allodoxaphobia/natpinning/wiki/Usage)

License
==============
This tool was created by Gremwell (http://www.gremwell.com) and released under GNU GPL v3. 
