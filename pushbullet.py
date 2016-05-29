#!/usr/bin/python
# -*- coding: utf-8 -*-
# The MIT License (MIT)

# Copyright (c) 2016 Alfie "Azelphur" Day
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

import requests
import json
from os.path import basename
from websocket import create_connection

import sys
if sys.version_info > (3, 0):
    from urllib.parse import urlparse
else:
    from urlparse import urljoin

BASE_URL = "https://api.pushbullet.com/v2/"


# Prototype for PushBullet objects such as devices, pushes, etc.
class _Object(object):
    def __init__(self, pb, **kwargs):
        if type(self) == _Object:
            raise NotImplementedError("This is a prototype")

        self.pb = pb
        self.attrs = kwargs

    def __setitem__(self, key, value):
        if key in self.writable_attributes:
            self.attrs[key] = value
        raise KeyError("%s is read only or does not exist" % (key))

    def __getitem__(self, key):
        return self.attrs[key]

    def __contains__(self, key):
        return key in self.attrs


class Device(_Object):
    """
        This class represents a device
        https://docs.pushbullet.com/#device
    """
    writable_attributes = [
        'nickname',
        'model',
        'manufacturer',
        'push_token',
        'app_version',
        'icon',
        'has_sms'
    ]

    def push_note(self, title=None, body=None):
        """
            Push a note
            https://docs.pushbullet.com/v2/pushes

            Arguments:
            title -- a title for the note
            body -- the body of the note
        """
        return self.pb.push_note(
            device_iden=self.attrs['iden'],
            title=title,
            body=body
        )

    def push_link(self, url, title=None, body=None):
        """
            Push a link
            https://docs.pushbullet.com/#create-push

            Arguments:
            url -- The url to open
            title -- The link's title
            body -- A message associated with the link
        """
        return self.pb.push_link(
            device_iden=self.attrs['iden'],
            title=title,
            body=body
        )

    def push_file(self, file, file_name=None, file_type=None, body=None):
        """
            Push a file
            https://docs.pushbullet.com/#create-push

            Arguments:
            file -- The file to push, can either be a file object or a file path (as a string)
            file_name -- The name of the file
            file_type -- The MIME type of the file, if not specified, magic will be used to attempt to guess.
            body -- A message associated to go with the file
        """
        return self.pb.push_file(
            device_iden=self.attrs['iden'],
            file=file,
            file_name=file_name,
            file_type=file_type,
            body=body
        )

    def update(self, nickname=None, model=None, manufacturer=None, push_token=None, app_version=None, icon=None, has_sms=None):
        """
            Update an existing device
            https://docs.pushbullet.com/#update-device

            Arguments:
            nickname -- Name to use when displaying the device
            model -- Model of the device
            manufacturer -- Manufacturer of the device
            push_token -- Platform-specific push token
            app_version -- Version of the Pushbullet application
            icon -- Icon to use for this device
            has_sms -- true if devices has SMS capability
        """
        return self.pb.update_device(
            device_iden=self.attrs['iden'],
            nickname=nickname,
            model=model,
            manufacturer=manufacturer,
            push_token=push_token,
            app_version=app_version,
            icon=icon,
            has_sms=has_sms
        )

    def commit(self):
        """
            Creates device if it does not exist, otherwise updates.
        """
        if 'iden' in self.attrs:
            f = self.update
        else:
            f = self.pb.create_device

        device = f(
            nickname=self.attrs['nickname'] if 'nickname' in self.attrs else None,
            model=self.attrs['model'] if 'model' in self.attrs else None,
            manufacturer=self.attrs['manufacturer'] if 'manufacturer' in self.attrs else None,
            push_token=self.attrs['push_token'] if 'push_token' in self.attrs else None,
            app_version=self.attrs['app_version'] if 'app_version' in self.attrs else None,
            icon=self.attrs['icon'] if 'icon' in self.attrs else None,
            has_sms=self.attrs['has_sms'] if 'has_sms' in self.attrs else None
        )
        self.attrs = dict(device.attrs)
        return device

    def delete(self):
        """
            Delete a device
            https://docs.pushbullet.com/#delete-device
        """
        return self.pb.delete_device(self.attrs['iden'])


class Push(_Object):
    """
        This class represents a push, see https://docs.pushbullet.com/#push
    """
    writable_attributes = ['dismissed']

    def dismiss(self):
        return self.update(dismissed=True)

    def update(self, dismissed):
        return self.pb.update_push(iden=self.attrs['iden'], dismissed=dismissed)

class Ephemeral(_Object):
    """
        This class represents an ephemeral, see https://docs.pushbullet.com/v2/#ephemerals
    """
    def dismiss(self):
        if "notification_tag" in self:
            notification_tag = self["notification_tag"]
        else:
            notification_tag = None

        data = {"push": {"package_name": self["package_name"],
                         "source_user_iden": self["source_user_iden"],
                         "notification_tag": notification_tag,
                         "notification_id": self["notification_id"],
                         "type": "dismissal"},
                "type": "push"}

        return self.pb._request("POST", "ephemerals", data)


class RealTime(object):
    def __init__(self, pb):
        self.pb = pb
        self._push_modified = 0
        self._push_cache = []

    def connect(self):
        url = "wss://stream.pushbullet.com/websocket/"+self.pb.api_key
        push = self.pb.list_pushes(limit=1)
        if push:
            self._push_modified = push[0]['modified']
        self.ws = create_connection(url)

    def _update_push_cache(self, limit=None):
        self._push_cache = self.pb.list_pushes(modified_after=self._push_modified, limit=limit)
        if self._push_cache:
            self._push_modified = self._push_cache[0]['modified']

    def get_event(self):
        if self._push_cache:
            return Push(self.pb, **self._push_cache.pop())
        data = self.ws.recv()
        data = json.loads(data)
        while data['type'] == "nop":
            data = self.ws.recv()
            data = json.loads(data)

        if data['type'] == "tickle" and data['subtype'] == "push":
            if not self._push_cache:
                self._update_push_cache()
            return Push(self.pb, **self._push_cache.pop())

        elif data['type'] == "push" and data['push']['type'] == "mirror":
            return Ephemeral(self.pb, **data['push'])

        return Push(self.pb, **data["push"])


class PushBullet(object):
    def __init__(self, api_key, user_agent="pyPushBullet", base_url=BASE_URL):
        self.api_key = api_key
        self.user_agent = user_agent
        self.base_url = base_url

    def _request(self, method, path, postdata=None, params=None, files=None):
        headers = {
            'Accept': "application/json",
            'Content-Type': "application/json",
            'User-Agent': self.user_agent,
            'Access-Token': self.api_key
        }
        print(method, path, postdata, params, files)
        r = requests.request(
            method,
            self.base_url+path,
            data=json.dumps(postdata) if postdata else None,
            params=params,
            headers=headers,
            files=files,
        )
        r.raise_for_status()
        return r.json()

    def create_device(self, nickname=None, model=None, manufacturer=None, push_token=None, app_version=None, icon=None, has_sms=None):
        """
            Create a new device
            https://docs.pushbullet.com/#create-device

            Arguments:
            nickname -- Name to use when displaying the device
            model -- Model of the device
            manufacturer -- Manufacturer of the device
            push_token -- Platform-specific push token
            app_version -- Version of the Pushbullet application
            icon -- Icon to use for this device
            has_sms -- true if devices has SMS capability
        """
        data = {
            'nickname': nickname,
            'model': model,
            'manufacturer': manufacturer,
            'push_token': push_token,
            'app_version': app_version,
            'icon': icon,
            'has_sms': has_sms
        }
        response = self._request("POST", "devices", data)
        return Device(pb=self, **response)

    def update_device(self, device_iden, nickname=None, model=None, manufacturer=None, push_token=None, app_version=None, icon=None, has_sms=None):
        """
            Update an existing device
            https://docs.pushbullet.com/#update-device

            Arguments:
            device_iden -- The devices identifier
            nickname -- Name to use when displaying the device
            model -- Model of the device
            manufacturer -- Manufacturer of the device
            push_token -- Platform-specific push token
            app_version -- Version of the Pushbullet application
            icon -- Icon to use for this device
            has_sms -- true if devices has SMS capability
        """
        data = {
            'nickname': nickname,
            'model': model,
            'manufacturer': manufacturer,
            'push_token': push_token,
            'app_version': app_version,
            'icon': icon,
            'has_sms': has_sms
        }
        response = self._request("POST", "devices/"+device_iden, data)
        return Device(pb=self, **response)

    def list_devices(self):
        """
            Get a list of devices belonging to the current user.
            https://docs.pushbullet.com/#list-devices
        """
        data = self._request("GET", "devices")
        return [Device(self, **device) for device in data['devices']]

    def delete_device(self, device_iden):
        """
            Delete a device
            https://docs.pushbullet.com/#delete-device

            Arguments:
            device_iden -- The identifier of the device to delete
        """
        self._request("DELETE", "devices/"+device_iden)

    def push_note(self, title=None, body=None, device_iden=None, email=None, channel_tag=None, client_iden=None):
        """
            Push a note
            https://docs.pushbullet.com/#create-push

            Arguments:
            title -- The note's title
            body -- The note's message
            device_iden -- Send the push to a specific device
            email -- Send the push to this email address
            channel_tag -- Send the push to all subscribers to your channel that has this tag
            client_iden -- Send the push to all users who have granted access to your OAuth client that has this iden

            If no target is specified, a push will be sent to all devices, note that only one target can be specified.
        """
        if not (title or body):
            raise ValidationError("You must specify title or body")

        data = {
            'type': "note",
            'title': title,
            'body': body,
            'device_iden': device_iden,
            'email': email,
            'channel_tag': channel_tag,
            'client_iden': client_iden
        }
        response = self._request("POST", "pushes", data)
        return Push(self, **response)

    def push_link(self, url, title=None, body=None, device_iden=None, email=None, channel_tag=None, client_iden=None):
        """
            Push a link
            https://docs.pushbullet.com/#create-push

            Arguments:
            url -- The url to open
            title -- The link's title
            body -- A message associated with the link
            device_iden -- Send the push to a specific device
            email -- Send the push to this email address
            channel_tag -- Send the push to all subscribers to your channel that has this tag
            client_iden -- Send the push to all users who have granted access to your OAuth client that has this iden

            If no target is specified, a push will be sent to all devices, note that only one target can be specified.
        """
        data = {
            'type': "link",
            'url': url,
            'title': title,
            'body': body,
            'device_iden': device_iden,
            'email': email,
            'channel_tag': channel_tag,
            'client_iden': client_iden
        }
        response = self._request("POST", "pushes", data)
        return Push(self, **response)

    def push_file(self, file, file_name=None, file_type=None, body=None, device_iden=None, email=None, channel_tag=None, client_iden=None):
        """
            Push a file
            https://docs.pushbullet.com/#create-push

            Arguments:
            file -- The file to push, can either be a file object or a file path (as a string)
            file_name -- The name of the file
            file_type -- The MIME type of the file, if not specified, magic will be used to attempt to guess.
            body -- A message associated to go with the file
            device_iden -- Send the push to a specific device
            email -- Send the push to this email address
            channel_tag -- Send the push to all subscribers to your channel that has this tag
            client_iden -- Send the push to all users who have granted access to your OAuth client that has this iden

            If no target is specified, a push will be sent to all devices, note that only one target can be specified.
        """
        if isinstance(file, str):
            if not file_name:
                file_name = basename(file)
            file = open(file, 'rb')

        if not file_type:
            try:
                import magic
            except ImportError:
                raise Exception("No file_type given and python-magic isn't installed")

            # Unfortunately there's two libraries called magic, both of which do
            # the exact same thing but have different conventions for doing so
            if hasattr(magic, 'from_buffer'):
                file_type = magic.from_buffer(file.read(1024))
            else:
                _magic = magic.open(magic.MIME_TYPE)
                _magic.compile(None)

                file_type = _magic.file(file_name)

                _magic.close()
            file.seek(0)

        params = {
            'file_name': file_name,
            'file_type': file_type
        }

        upload_request = self._request("GET", "upload-request", params=params)

        upload = requests.post(
            upload_request["upload_url"],
            data=upload_request["data"],
            files={"file": file},
            headers={"User-Agent": self.user_agent}
        )
        upload.raise_for_status()

        data = {
            "type": "file",
            "file_name": file_name,
            "file_type": file_type,
            "file_url": upload_request["file_url"],
            "body": body,
            'device_iden': device_iden,
            'email': email,
            'channel_tag': channel_tag,
            'client_iden': client_iden
        }
        response = self._request("POST", "pushes", data)
        return Push(self, **response)

    def update_push(self, iden, dismissed):
        """
            Update a push
            https://docs.pushbullet.com/#update-push

            Arguments:
            iden -- The iden of the push
            dismissed -- Marks a push as having been dismissed by the user
        """
        response = self._request("POST", "pushes/"+iden, {'dismissed': dismissed})
        return Push(self, **response)

    def list_pushes(self, modified_after=None, active=None, cursor=None, limit=15):
        """
            Request push history
            https://docs.pushbullet.com/#list-pushes
        """
        params = {
            'modified_after': modified_after,
            'active': active,
            'cursor': cursor,
            'limit': limit
        }
        response = self._request("GET", "pushes", params=params)
        pushes = [Push(self, **push) for push in response['pushes']]
        while 'cursor' in response and (not limit or len(pushes) < limit):
            params = {
                'modified_after': modified_after,
                'active': active,
                'cursor': response['cursor'],
                'limit': limit
            }
            response = self._request("GET", "pushes", params=params)
            pushes += [Push(self, **push) for push in response['pushes']]
        return pushes

    def delete_push(self, iden):
        """
            Delete a push
            https://docs.pushbullet.com/#delete-push

            Arguments:
            iden -- The iden of the push
        """
        self._request("DELETE", "pushes/"+device_iden)

    def delete_all_pushes(self):
        """
            Delete all pushes belonging to the current user. This call is ascynrhonous
            the pushes will be deleted after the call returns
            https://docs.pushbullet.com/#delete-all-pushes
        """
        self._request("DELETE", "pushes")
