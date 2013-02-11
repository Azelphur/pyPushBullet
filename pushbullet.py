# -*- coding: utf-8 -*-
try:
    from http.cookiejar import CookieJar
except ImportError:
    from cookielib import CookieJar
try:
    from urllib.request import build_opener, HTTPCookieProcessor
except ImportError:
    from urllib2 import build_opener, HTTPCookieProcessor
try:
    from urllib.request import Request
except:
    from urllib2 import Request
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from bs4 import BeautifulSoup
import json

HOST = 'https://www.pushbullet.com';

def extract_form_fields(soup):
    "Turn a BeautifulSoup form in to a dict of fields and default values"
    fields = {}
    for input in soup.findAll('input'):
        try:
            fields[input['name']] = input['value'].encode('utf-8')
        except KeyError:
            pass
    return fields

class PushBullet():
    def __init__(self):
        self.cj = CookieJar()
        self.opener = build_opener(HTTPCookieProcessor(self.cj))

    def signIn(self, email, password):
        request = Request(HOST + "/signin")
        f = self.opener.open(request)
        response = f.read()
        response = response.decode('utf-8')
        soup = BeautifulSoup(response)
        form = soup.find(id="gaia_loginform")
        fields = extract_form_fields(form)
        fields['Email'] = email
        fields['Passwd'] = password
        postdata = urlencode(fields)
        postdata = postdata.encode('utf-8')
        request = Request(form['action'])
        f = self.opener.open(request, postdata)
        response = f.read()
        response = response.decode('utf-8')

    def getDevices(self):
        request = Request(HOST + "/devices")
        request.add_header("Accept", "application/json")
        f = self.opener.open(request)
        response = f.read()
        response = response.decode('utf-8')
        j = json.loads(response)
        self.csrf = j['csrf']
        return j['devices']

    def pushNotification(self, data):
        request = Request(HOST + "/push/" + data['type'])
        request.add_header("Content-type","application/json");
        request.add_header("Accept", "application/json")

        data['_csrf'] = self.csrf
        data = json.dumps(data)
        data = data.encode('utf-8')

        f = self.opener.open(request, data)
        response = f.read()
        response = response.decode('utf-8')
        return response
