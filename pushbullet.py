# -*- coding: utf-8 -*-
try:
    from urllib.request import Request, urlopen
except:
    from urllib2 import Request, urlopen

from base64 import encodestring, b64encode
import json

HOST = "https://www.pushbullet.com/api";

class PushBulletError():
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

class PushBullet():
    def __init__(self, apiKey):
        self.apiKey = apiKey

    def _request(self, url, postdata=None):
        request = Request(url)
        request.add_header("Accept", "application/json")
        request.add_header("Content-type","application/json");
        auth = "%s:" % (self.apiKey)
        auth = auth.encode('ascii')
        auth = b64encode(auth)
        auth = b"Basic "+auth
        request.add_header("Authorization", auth)
        request.add_header("User-Agent", "pyPushBullet")
        if postdata:
            postdata = json.dumps(postdata)
            postdata = postdata.encode('utf-8')
        response = urlopen(request, postdata)
        data = response.read()
        data = data.decode("utf-8")
        j = json.loads(data)
        return j

    def getDevices(self):
        return self._request(HOST + "/devices")["devices"]

    def pushNote(self, device, title, body):
        data = {'type'      : 'note',
                'device_id' : device,
                'title'     : title,
                'body'      : body}
        return self._request(HOST + "/pushes", data)

    def pushAddress(self, device, name, address):
        data = {'type'      : 'address',
                'device_id' : device,
                'name'      : name,
                'address'   : address}
        return self._request(HOST + "/pushes", data)

    def pushList(self, device, title, items):
        data = {'type'      : 'list',
                'device_id' : device,
                'title'     : title,
                'items'     : items}
        return self._request(HOST + "/pushes", data)


    def pushLink(self, device, title, url):
        data = {'type'      : 'link',
                'device_id' : device,
                'title'     : title,
                'url'     : url}
        return self._request(HOST + "/pushes", data)

