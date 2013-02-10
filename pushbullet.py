#!/usr/bin/python3

# -*- coding: utf-8 -*-
import http.cookiejar
import urllib.request
import json
from bs4 import BeautifulSoup

HOST = 'https://www.pushbullet.com';

def extract_form_fields(soup):
    "Turn a BeautifulSoup form in to a dict of fields and default values"
    fields = {}
    for input in soup.findAll('input'):
        try:
            fields[input['name']] = input['value']
        except KeyError:
            pass
    return fields

class PushBullet():
    def __init__(self):
        self.cj = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cj))

    def signIn(self, email, password):
        request = urllib.request.Request(HOST + "/signin")
        f = self.opener.open(request)
        response = f.read()
        response = response.decode('utf-8')
        soup = BeautifulSoup(response)
        form = soup.find(id="gaia_loginform")
        fields = extract_form_fields(form)
        fields['Email'] = email
        fields['Passwd'] = password
        postdata = urllib.parse.urlencode(fields)
        postdata = postdata.encode('utf-8')
        request = urllib.request.Request(form['action'])
        f = self.opener.open(request, postdata)
        response = f.read()
        response = response.decode('utf-8')

    def getDevices(self):
        request = urllib.request.Request(HOST + "/devices")
        request.add_header("Accept", "application/json")
        f = self.opener.open(request)
        response = f.read()
        response = response.decode('utf-8')
        j = json.loads(response)
        self.csrf = j['csrf']
        return j['devices']

    def pushNotification(self, data):
        request = urllib.request.Request(HOST + "/push/" + data['type'])
        request.add_header("Content-type","application/json");
        request.add_header("Accept", "application/json")

        data['_csrf'] = self.csrf
        data = json.dumps(data)
        data = data.encode('utf-8')

        f = self.opener.open(request, data)
        response = f.read()
        response = response.decode('utf-8')
        return response
