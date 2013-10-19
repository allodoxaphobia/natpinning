def isPrivateAddress(_ip):
	result = False
	if isIPv4(_ip):
		parts = _ip.split(".")
		if int(parts[0]) == 10: result = True
		elif int(parts[0])==172 and int(parts[1])>=16: result = True
		elif int(parts[0])==192 and int(parts[1])==168: result = True
		#is it loopback?
		if _ip == "127.0.0.1": result = True
	elif isIPv6(_ip):
		#is it local link addr
		parts = _ip.split(":")
		if parts[0].lower() == " fe80": result = True
	else:
		raise Exception("Invalid IP Specified: " + _ip)
	return result
#end def

def isIPv4(_ip):
	result = False
	if not ":" in _ip:
		if len(_ip.split("."))==4: result = True
	return result
#end def

def isIPv6(_ip):
	result = False
	if ":" in _ip:
		if len(_ip.split(":"))==6: result = True
	return result
#end def
