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
from requests.exceptions import HTTPError

pb = None

def add_device(args):
    device = pushbullet.Device(pb, nickname=args.nickname)
    device.commit()
    print("Device %s was assigned ID %s" % (device["nickname"],
                                            device["iden"]))

def get_devices(args):
    devices = pb.list_devices()

    for device in devices:
        if "manufacturer" in device:
            print("%s %s %s" % (device["iden"],
                                device["manufacturer"],
                                device["model"]))
        else:
            print(device["iden"])

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


parser = argparse.ArgumentParser()
parser.add_argument("api_key")
subparser = parser.add_subparsers(dest="type")

getdevices = subparser.add_parser("getdevices", help="Get a list of devices")
getdevices.set_defaults(func=get_devices)

adddevice = subparser.add_parser("adddevice", help="Add a new devices to your account")
adddevice.add_argument('nickname')
adddevice.set_defaults(func=add_device)

note = subparser.add_parser("note", help="Send a note")
note.add_argument('device', type=str, help="Device ID")
note.add_argument('title')
note.add_argument('body', nargs=argparse.REMAINDER)
note.set_defaults(func=push_note)

link = subparser.add_parser("link", help="Send a link")
link.add_argument('device', type=str, help="Device ID")
link.add_argument('title')
link.add_argument('url')
link.add_argument('body', nargs=argparse.REMAINDER)
link.set_defaults(func=push_link)

file = subparser.add_parser("file", help="Send a file")
file.add_argument('device', type=str, help="Device ID")
file.add_argument('file')
file.add_argument('body', nargs=argparse.REMAINDER)
file.set_defaults(func=push_file)

args = parser.parse_args()
pb = pushbullet.PushBullet(args.api_key)
args.func(args)
