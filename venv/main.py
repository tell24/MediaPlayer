from flask import Flask, redirect, url_for, render_template, request
import socket
import time

app = Flask(__name__)

host = "192.168.0.47"
Con_port = 8102
AV_port = 2870

power_headers = "CON A8:9F:BA:CB:AA:2D AndroidClient?RGC\r\n{Power} HTTP/1.1\r\n\
Connection: Keep-Alice\r\n\
\r\n"

control_headers = "POST /control/RenderingControl HTTP/1.1\r\n\
SOAPACTION: \"urn:schemas-upnp-org:service:{Rendering}{option}\r\n\
Content-type: text/xml;charset=utf-8\r\n\
Content-Length: {content_length}\r\n\
Host: {host}\r\n\
Connection: Keep-Alice\r\n\
\r\n"

transport_headers = "POST /control/AVTransport HTTP/1.1\r\n\
SOAPACTION: \"urn:schemas-upnp-org:service:{Transport}{option}\r\n\
Content-type: text/xml;charset=utf-8\r\n\
Content-Length: {content_length}\r\n\
Host: {host}\r\n\
Connection: Keep-Alice\r\n\
\r\n"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/", methods=["POST", "GET"])
def login():
   if request.method == "POST":
      user = request.form["nm"]
      if user == "Radio Two":
        rep = "R2"
        setOption(0)
        setOption(1)
        return render_template("index.html", station=rep)
      if user == "Radio 5 Live":
        rep = "R5"
        return render_template("index.html", station=rep)
      if user == "Radio Bristol":
        rep = "RB"
        return render_template("index.html", station=rep)
      if user == "Get Volume":
        rep = getInfo(0)
        return render_template("index.html", station=rep)
      if user == "Set Volume":
        rep = setOption(2)
        return render_template("index.html", station=rep)
      if user == "Set URI":
        rep = setOption(0)
        return render_template("index.html", station=rep)
      if user == "Get URI":
        rep = getInfo(1)
        return render_template("index.html", station=rep)
      if user == "GetPower":
        rep = getPower()
        return render_template("index.html", station=rep)
      if user == "Power On":
        rep = setPower(1)
        return render_template("index.html", station=rep)
      if user == "Power Off":
        rep = setPower(0)
        return render_template("index.html", station=rep)
   else:
      return render_template("login.html")


def setPower(p):
    if p == 1:
        pfunction = "PO"
    else:
        pfunction = "PF"
    header_bytes = power_headers.format(
    Power = pfunction
    ).encode('iso-8859-1')
    payload = header_bytes
    s = socket.socket()
    response = ''
    try:
        s.connect(('192.168.0.47', 8102))
        s.send(payload);
        time.sleep(1)
        response = s.recv(1024).decode()
        print ("N:",response)
        s.close()
    except socket.error as e:
        return e
    return response

def getPower():
    header_bytes = power_headers.format(
    Power = "?P"
    ).encode('iso-8859-1')
    payload = header_bytes
    s = socket.socket()
    response = ''
    try:
        s.connect(('192.168.0.47', 8102))
        s.send(payload);
        time.sleep(2)
        response = s.recv(1024).decode()
        print ("N:",response)
        s.close()
    except socket.error as e:
        return e
    return response

def setOption(option):
    body = ""
    if option == 0:
        body = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\
        <s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\">\
        <s:Body>\
        <u:SetAVTransportURI xmlns:u=\"urn:schemas-upnp-org:service:AVTransport:1\">\
        <InstanceID>0</InstanceID>\
        <CurrentURI>http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio2_mf_p</CurrentURI>\
        <CurrentURIMetaData></CurrentURIMetaData>\
        </u:SetAVTransportURI>\
        </s:Body>\
        </s:Envelope>"
        body_bytes = body.encode('ascii')
        header_bytes = transport_headers.format(
            Transport="AVTransport:1#",
            option="SetAVTransportURI\"",
            content_length=len(body_bytes),
            host=str(host) + ":" + str(AV_port)
        ).encode('iso-8859-1')
    else:
        if option ==1:
            body = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\
            <s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\">\
            <s:Body>\
            <u:Play xmlns:u=\"urn:schemas-upnp-org:service:AVTransport:1\">\
            <InstanceID>0</InstanceID>\
            </u:Play>\
            </s:Body>\
            </s:Envelope>"
            body_bytes = body.encode('ascii')
            header_bytes = control_headers.format(
                Rendering="AVTransport:1#",
                option="Play\"",
                content_length=len(body_bytes),
                host=str(host) + ":" + str(AV_port)
            ).encode('iso-8859-1')
        else:
            if option == 2:
                body = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\
                   <s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\">\
                   <s:Body>\
                   <u:SetVolume xmlns:u=\"urn:schemas-upnp-org:service:RenderingControl:1\">\
                   <InstanceID>0</InstanceID>\
                   <Channel>Master</Channel>\
                   <DesiredVolume>10</DesiredVolume>\
                   </u:SetVolume>\
                   </s:Body>\
                   </s:Envelope>"
                body_bytes = body.encode('ascii')
                header_bytes = control_headers.format(
                Rendering = "RenderingControl:1#",
                option = "SetVolume\"",
                content_length=len(body_bytes),
                host=str(host) + ":" + str(AV_port)
                ).encode('iso-8859-1')
    payload = header_bytes + body_bytes
    response = ''
    s = socket.socket()
    try:
        s.connect(('192.168.0.47', 2870))
        s.send(payload);
        time.sleep(2)
        response = s.recv(1024).decode()
        print("N:", response)
        s.close()
    except socket.error as e:
        return e
    print(response)
    return response


def getInfo(type):
    body = ""
    if type == 0:
        body = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\
            <s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\">\
            <s:Body>\
            <u:GetVolume xmlns:u=\"urn:schemas-upnp-org:service:RenderingControl:1\">\
            <InstanceID>0</InstanceID>\
            <Channel>Master</Channel>\
            </u:GetVolume>\
            </s:Body>\
            </s:Envelope>"
        body_bytes = body.encode('ascii')
        header_bytes = control_headers.format(
            Rendering="RenderingControl:1#",
            option="GetVolume\"",
            content_length=len(body_bytes),
            host=str(host) + ":" + str(AV_port)
        ).encode('iso-8859-1')
        payload = header_bytes + body_bytes
        print(payload)
    else:
        body = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\
            <s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\">\
            <s:Body>\
            <u:SetAVTransportURI xmlns:u=\"urn:schemas-upnp-org:service:AVTransport:1\">\
            <InstanceID>0</InstanceID>\
            <CurrentURI>http://www.vorbis.com/music/Epoq-Lepidoptera.ogg</CurrentURI>\
            </u:SetAVTransportURI>\
            </s:Body>\
            </s:Envelope>"
        body_bytes = body.encode('ascii')
        header_bytes = transport_headers.format(
            Transport="AVTransport:1#",
            option="SetAVTransportURI\"",
            content_length=len(body_bytes),
            host=str(host) + ":" + str(AV_port)
        ).encode('iso-8859-1')
        payload = header_bytes + body_bytes
        print(payload)
    response = ''
    s = socket.socket()
    try:
        s.connect(('192.168.0.47',2870))
        s.send(payload);
        time.sleep(2)
        response = s.recv(1024).decode()
        print("N:", response)
        s.close()
    except socket.error as e:
        return e
    return response

if __name__ == "__main__":
    app.run(debug=True)
