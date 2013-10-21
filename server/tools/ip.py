def isPrivateAddress(_ip):
	result = False
	if isIPv4(_ip):
		parts = _ip.split(".")
		if int(parts[0]) == 10: result = True
		elif int(parts[0])==172 and int(parts[1])>=16: result = True
		elif int(parts[0])==192 and int(parts[1])==168: result = True
		#is it loopback?
		if _ip == "127.0.0.1": result = True
		if result == False:
			result = isIPv4BroadCastOrMulticast(_ip)
	elif isIPv6(_ip):
		#is it local link addr
		parts = _ip.split(":")
		if parts[0].lower() == " fe80": result = True
		if result == False: result = isIPv6BroadCastOrMulticast(_ip)
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
def isIPv4BroadCastOrMulticast(_ip):
	result = False
	parts = _ip.split(".")
	if len(parts)!=4:
		return result
	else:
		if str(parts[0])=="224" and str(parts[1]) in ("0","1","2","3","4","5"): #multicast
			result = True
		elif str(parts[0])=="225" and str(parts[1]) =="0": #multicast
			result = True
		elif str(parts[0]) in ("232","233","234","235","239") and str(parts[1])=="0":#multicast
			result = True
		elif str(parts[0])=="233" and str(parts[1])=="252":#multicast
			result = True
		elif str(parts[1]) =="255" and str(parts[2])=="255":#broadcast TODO, this is just too ugly
			result = True
	return result
#end def
def isIPv6BroadCastOrMulticast(_ip):
	result = False
	parts = _ip.split(":")
	if str(parts[0]).upper() in ("FF02","FF05","FF08","FF0E","FF01"):
		result = True
	return result
#end def
def isIPv6(_ip):
	result = False
	if ":" in _ip:
		if len(_ip.split(":"))==6: result = True
	return result
#end def
