import BaseHTTPServer

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(self):
		req_path = self.path.lstrip("/").split("/")
		if req_path[0].split("?")[0] in ("admin","ADMIN","Admin"):
			resp_data = self.get_file_contents("web/admin.html")
			if resp_data != "":
				resp_data = resp_data.replace("$body$", self.get_file_contents("web/admin_form.html"))
				self.send_response(200)
				self.send_header("Content-type", "text/html")
				self.end_headers()
				self.wfile.write(resp_data)
		elif req_path[0].split("?")[0] in ("tests","TESTS","Tests"):
			params = None
			resp_data = self.get_file_contents("web/tests.html")
			if "?" in req_path[0]:
				params = req_path[0].split("?")[1].split("&")
				for param in params:
					req_data = param.split("=")
					resp_data = resp_data.replace("$" + req_data[0] +"$",req_data[1])
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()
			self.wfile.write(resp_data)
		elif req_path[0].split("?")[0]=="gremwell.png":
			self.send_response(200)
			self.send_header("Content-type", "image/png")
			self.end_headers()					
			self.wfile.write(self.get_file_contents("web/gremwell.png"))
		else:
			self.send_response(404)
			self.end_headers()
			self.wfile.write("Requested page not found.")
	#end def
	def get_file_contents(self,filepath):
		try:
			f = open(filepath,"r")
			data = f.read()
			f.close()
			return data
		except:
			return ""
	def parse_vars(self,data):
		return data #todo
	#end def
#end class

class Victim():
	IP = None
	IS_CONNECTED = False
	def __init__(self,rem_IP):
		global IP, IS_CONNECTED
		IP = rem_IP
		IS_CONNECTED = True
	#end def
#end class

class WebServer():
	SERVER = None
	victims= []
	def __init__(self, iport):
		global SERVER
		server = BaseHTTPServer.HTTPServer(('',60000),MyHandler)
		server.serve_forever()

x = WebServer(60000)
