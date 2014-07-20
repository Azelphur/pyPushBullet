# -*- coding: utf-8 -*-
import json
import requests
import magic
from requests.auth import HTTPBasicAuth
from websocket import create_connection

HOST = "https://api.pushbullet.com/v2"


class PushBullet():
    def __init__(self, apiKey):
        self.apiKey = apiKey

    def _request(self, method, url, postdata=None, params=None, files=None):
        headers = {"Accept": "application/json",
                   "Content-Type": "application/json",
                   "User-Agent": "pyPushBullet"}

        if postdata:
            postdata = json.dumps(postdata)

        r = requests.request(method,
                             url,
                             data=postdata,
                             params=params,
                             headers=headers,
                             files=files,
                             auth=HTTPBasicAuth(self.apiKey, ""))

        r.raise_for_status()
        return r.json()

    def addDevice(self, device_name):
        """ Push a note
            https://docs.pushbullet.com/v2/pushes

            Arguments:
            device_name -- Human readable name for device
            type -- stream, thats all there is currently

        """

        data = {"nickname": device_name,
                "type": "stream"
                }
        return self._request("POST", HOST + "/devices", data)

    def getDevices(self):
        """ Get devices
            https://docs.pushbullet.com/v2/devices

            Get a list of devices, and data about them.
        """

        return self._request("GET", HOST + "/devices")["devices"]

    def deleteDevice(self, device_iden):
        """ Delete a device
            https://docs.pushbullet.com/v2/devices

            Arguments:
            device_iden -- iden of device to push to
        """

        return self._request("DELETE", HOST + "/devices/" + device_iden)

    def pushNote(self, device_iden, title, body):
        """ Push a note
            https://docs.pushbullet.com/v2/pushes

            Arguments:
            device_iden -- iden of device to push to
            title -- a title for the note
            body -- the body of the note
        """

        data = {"type": "note",
                "device_iden": device_iden,
                "title": title,
                "body": body}
        return self._request("POST", HOST + "/pushes", data)

    def pushAddress(self, device_iden, name, address):
        """ Push an address
            https://docs.pushbullet.com/v2/pushes

            Arguments:
            device_iden -- iden of device to push to
            name -- name for the address, eg "Bobs house"
            address -- address of the address
        """

        data = {"type": "address",
                "device_iden": device_iden,
                "name": name,
                "address": address}
        return self._request("POST", HOST + "/pushes", data)

    def pushList(self, device_iden, title, items):
        """ Push a list
            https://docs.pushbullet.com/v2/pushes

            Arguments:
            device_iden -- iden of device to push to
            title -- a title for the list
            items -- a list of items
        """

        data = {"type": "list",
                "device_iden": device_iden,
                "title": title,
                "items": items}

        return self._request("POST", HOST + "/pushes", data)

    def pushLink(self, device_iden, title, url):
        """ Push a link
            https://docs.pushbullet.com/v2/pushes

            Arguments:
            device_iden -- iden of device to push to
            title -- link title
            url -- link url
        """

        data = {"type": "link",
                "device_iden": device_iden,
                "title": title,
                "url": url}
        return self._request("POST", HOST + "/pushes", data)

    def pushFile(self, device_iden, file_name, body, file, file_type=None):
        """ Push a file
            https://docs.pushbullet.com/v2/pushes
            https://docs.pushbullet.com/v2/upload-request

            Arguments:
            device_iden -- iden of device to push to
            file_name -- name of the file
            file -- a file object
            file_type -- file mimetype, if not set, python-magic will be used
        """

        if not file_type:
            mime = magic.Magic(mime=True)
            file_type = mime.from_buffer(file.read(1024))
            file.seek(0)

        data = {"file_name": file_name,
                "file_type": file_type}

        upload_request = self._request("GET",
                                       HOST + "/upload-request",
                                       None,
                                       data)

        upload = requests.post(upload_request["upload_url"],
                               data=upload_request["data"],
                               files={"file": file},
                               headers={"User-Agent": "pyPushBullet"})

        upload.raise_for_status()

        data = {"type": "file",
                "device_iden": device_iden,
                "file_name": file_name,
                "file_type": file_type,
                "file_url": upload_request["file_url"],
                "body": body}

        return self._request("POST", HOST + "/pushes", data)

    def getPushHistory(self, modified_after=0, cursor=None):
        """ Get Push History
            https://docs.pushbullet.com/v2/pushes

            Returns a list of pushes

            Arguments:
            modified_after -- Request pushes modified after this timestamp
            cursor -- Request another page of pushes (if necessary)
        """
        data = {"modified_after": modified_after}
        if cursor:
            data["cursor"] = cursor
        return self._request("GET", HOST + "/pushes", None, data)["pushes"]

    def deletePush(self, push_iden):
        """ Delete push
            https://docs.pushbullet.com/v2/pushes

            Arguments:
            push_iden -- the iden of the push to delete
        """
        return self._request("DELETE", HOST + "/pushes/" + push_iden)

    def getContacts(self):
        """ Gets your contacts
            https://docs.pushbullet.com/v2/contacts

            returns a list of contacts
        """
        return self._request("GET", HOST + "/contacts")["contacts"]

    def deleteContact(self, contact_iden):
        """ Delete a contact
            https://docs.pushbullet.com/v2/contacts

            Arguments:
            contact_iden -- the iden of the contact to delete
        """
        return self._request("DELETE", HOST + "/contacts/" + contact_iden)

    def getUser(self):
        """ Get this users information
            https://docs.pushbullet.com/v2/users
        """
        return self._request("GET", HOST + "/users/me")

    def realtime(self, callback):
        """ Opens a Realtime Event Stream
            https://docs.pushbullet.com/stream

            callback will be called with one argument, the JSON response
            from the server, nop messages are filtered.

            Arguments:
            callback -- The function to call on activity
        """

        url = "wss://stream.pushbullet.com/websocket/" + self.apiKey
        ws = create_connection(url)
        while 1:
            data = ws.recv()
            data = json.loads(data)
            if data["type"] != "nop":
                callback(data)
