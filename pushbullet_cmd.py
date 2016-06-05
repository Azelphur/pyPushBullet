#!/usr/bin/python
# The MIT License (MIT)

# Copyright (c) 2016 Alfie "Azelphur" Day
# Copyright (c) 2016 Lyude Paul <thatslyude@gmail.com>
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

import argparse
import sys
import json
import os
import pushbullet
from pprint import pprint
from requests.exceptions import HTTPError

pb = None

def add_device(args):
    device = pushbullet.Device(pb, nickname=args.name,
                               model=args.model if 'model' in args else None,
                               type=args.type if 'type' in args else None)
    device.commit()

    print("Device created:")
    pprint(device.attrs)

def update_device(args):
    device = pushbullet.Device.get(pb, args.iden)

    if 'name' in args:
        device['nickname'] = args.name
    if 'model' in args:
        device['model'] = args.model
    if 'manufacturer' in args:
        device['manufacturer'] = args.manufacturer
    if 'icon' in args:
        device['icon'] = args.icon

    device.commit()
    print("Device updated:")
    pprint(device.attrs)

def get_device(args):
    try:
        pprint(pushbullet.Device.get(pb, args.iden).attrs)
    except pushbullet.PushBullet.ObjectNotFoundError as e:
        print(e)
        sys.exit(1)

def list_devices(args):
    for device in pb.list_devices():
        pprint(device.attrs)

def delete_device(args):
    try:
        pushbullet.Device(pb, iden=args.iden).delete()
    except pushbullet.PushBullet.ObjectNotFoundError as e:
        print(e)
        sys.exit(1)

    print("Deleted device with iden %s" % args.iden)

def push_note(args):
    response = pb.push_note(args.title, " ".join(args.body), args.device)

    if args.device and args.device[0] == '#':
        print("Note broadcast to channel %s" % (args.device))
    elif not args.device:
        print("Note %s sent to all devices" % (response["iden"]))
    else:
        print("Note %s sent to %s" % (response["iden"],
                                      response["target_device_iden"]))

def push_link(args):
    response = pb.push_link(args.url, args.title,
                            " ".join(args.body), args.device)

    if args.device and args.device[0] == '#':
        print("Link broadcast to channel %s" % (args.device))
    elif not args.device:
        print("Link %s sent to all devices" % (response["iden"]))
    else:
        print("Link %s sent to %s" % (response["iden"],
                                      response["target_device_iden"]))

def push_file(args):
    response = pb.push_file(file=args.file, body=" ".join(args.body),
                            device_iden=args.device)

    if args.device and args.device[0] == '#':
        print("File broadcast to channel %s" % (args.device))
    elif not args.device:
        print("File %s sent to all devices" % (response["iden"]))
    else:
        print("File %s sent to %s" % (response["iden"],
                                      response["target_device_iden"]))

def get_user(args):
    pprint(pushbullet.User.get(pb).attrs)


parser = argparse.ArgumentParser()
parser.add_argument("api_key")
subparser = parser.add_subparsers(dest="type")

device = subparser.add_parser('device', help='Manage devices')
device_subparser = device.add_subparsers(dest='action')

device_add = device_subparser.add_parser('add', help='Create a new device')
device_add.add_argument('name',           metavar=None, type=str, help='The name of the device')
device_add.add_argument('--manufacturer', metavar='m',  type=str, help='The manufacturer of the device')
device_add.add_argument('--icon',         metavar='i',  type=str, help='The icon to use for the device')
device_add.set_defaults(func=add_device)

device_get = device_subparser.add_parser('get', help='Get information on a device')
device_get.add_argument('iden', type=str, help='The iden of the device')
device_get.set_defaults(func=get_device)

device_list = device_subparser.add_parser('list', help='List the available devices')
device_list.set_defaults(func=list_devices)

device_update = device_subparser.add_parser('update', help='Update the device\'s attributes')
device_update.add_argument('iden',           metavar=None, type=str, help='The name of the device')
device_update.add_argument('--name',         metavar='n',  type=str, help='The nickname for the device')
device_update.add_argument('--manufacturer', metavar='m',  type=str, help='The manufacturer of the device')
device_update.add_argument('--icon',         metavar='i',  type=str, help='The icon to use for the device')
device_update.set_defaults(func=update_device)

device_delete = device_subparser.add_parser('delete', help='Delete a device')
device_delete.add_argument('iden', type=str, help='The iden of the device')
device_delete.set_defaults(func=delete_device)

note = subparser.add_parser("note", help="Send a note", add_help=True)
note.add_argument('device', type=str, help="The device ID")
note.add_argument('title',  type=str, help="The title of the note")
note.add_argument('body',   type=str, help="The contents of the note", nargs=argparse.REMAINDER)
note.set_defaults(func=push_note)

link = subparser.add_parser("link", help="Send a link", add_help=True)
link.add_argument('device', type=str, help="The device ID")
link.add_argument('title',  type=str, help="The name of the link")
link.add_argument('url',    type=str, help="The link")
link.add_argument('body',   type=str, help="A message to include with the link", nargs=argparse.REMAINDER)
link.set_defaults(func=push_link)

file = subparser.add_parser("file", help="Send a file", add_help=True)
file.add_argument('device', type=str, help="The device ID")
file.add_argument('file',   type=str, help="The path to the file")
file.add_argument('body',   type=str, help="A message to include with the file", nargs=argparse.REMAINDER)
file.set_defaults(func=push_file)

user = subparser.add_parser('get-user', help='Get info on the current user', add_help=True)
user.set_defaults(func=get_user)

args = parser.parse_args()
pb = pushbullet.PushBullet(args.api_key)
args.func(args)
