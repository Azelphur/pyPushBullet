#!/usr/bin/python
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
import argparse
import sys
import json
import os
from pushbullet import PushBullet
from requests.exceptions import HTTPError

def addDevice(args):
    p = PushBullet(args.api_key)
    devices = p.addDevice(args.nickname)
    if args.json:
        print(json.dumps(devices))
        return
    print("Device %s was assigned ID %s" % (devices["nickname"],
                                            devices["iden"]))

def getDevices(args):
    p = PushBullet(args.api_key)
    devices = p.getDevices()
    if args.json:
        print(json.dumps(devices))
        return
    for device in devices:
        if "manufacturer" in device:
            print("%s %s %s" % (device["iden"],
                            device["manufacturer"],
                            device["model"]))
        else:
            print(device["iden"])

def pushNote(args):
    p = PushBullet(args.api_key)
    note = p.pushNote(args.device, args.title, " ".join(args.body))
    if args.json:
        print(json.dumps(note))
        return
    if args.device and args.device[0] == '#':
        print("Note broadcast to channel %s" % (args.device))
    elif not args.device:
        print("Note %s sent to all devices" % (note["iden"]))
    else:
        print("Note %s sent to %s" % (note["iden"], note["target_device_iden"]))

def pushAddress(args):
    p = PushBullet(args.api_key)
    address = p.pushAddress(args.device, args.name, " ".join(args.address))
    if args.json:
        print(json.dumps(address))
        return
    if args.device and args.device[0] == '#':
        print("Address broadcast to channel %s" % (args.device))
    elif not args.device:
        print("Address %s sent to all devices" % (address["iden"]))
    else:
        print("Address %s sent to %s" % (address["iden"], address["target_device_iden"]))

def pushList(args):
    p = PushBullet(args.api_key)
    lst = p.pushList(args.device, args.title, args.list)
    if args.json:
        print(json.dumps(lst))
        return
    if args.device and args.device[0] == '#':
        print("List broadcast to channel %s" % (args.device))
    elif not args.device:
        print("List %s sent to all devices" % (lst["iden"]))
    else:
        print("List %s sent to %s" % (lst["iden"], lst["target_device_iden"]))

def pushLink(args):
    p = PushBullet(args.api_key)
    link = p.pushLink(args.device, args.title, args.url)
    if args.json:
        print(json.dumps(link))
        return
    if args.device and args.device[0] == '#':
        print("Link broadcast to channel %s" % (args.device))
    elif not args.device:
        print("Link %s sent to all devices" % (link["iden"]))
    else:
        print("Link %s sent to %s" % (link["iden"], link["target_device_iden"]))

def pushFile(args):
    p = PushBullet(args.api_key)
    file = p.pushFile(args.device, os.path.basename(args.file), "", open(args.file, 'rb'))
    if args.json:
        print(json.dumps(file))
        return
    if args.device and args.device[0] == '#':
        print("File broadcast to channel %s" % (args.device))
    elif not args.device:
        print("File %s sent to all devices" % (file["iden"]))
    else:
        print("File %s sent to %s" % (file["iden"], file["target_device_iden"]))


parser = argparse.ArgumentParser()
parser.add_argument("--json", default=False, action="store_const", const=True)
parser.add_argument("api_key")
subparser = parser.add_subparsers(dest="type")

getdevices = subparser.add_parser("getdevices", help="Get a list of devices")
getdevices.set_defaults(func=getDevices)

adddevice = subparser.add_parser("adddevice", help="Add a new devices to your account")
adddevice.add_argument('nickname')
adddevice.set_defaults(func=addDevice)

note = subparser.add_parser("note", help="Send a note")
note.add_argument('device', type=str, help="Device ID")
note.add_argument('title')
note.add_argument('body', nargs=argparse.REMAINDER)
note.set_defaults(func=pushNote)

address = subparser.add_parser("address", help="Send an address")
address.add_argument('device', type=str, help="Device ID")
address.add_argument('name')
address.add_argument('address', nargs=argparse.REMAINDER)
address.set_defaults(func=pushAddress)

lst = subparser.add_parser("list", help="Send a list")
lst.add_argument('device', type=str, help="Device ID")
lst.add_argument('title')
lst.add_argument('list', nargs=argparse.REMAINDER)
lst.set_defaults(func=pushList)

link = subparser.add_parser("link", help="Send a link")
link.add_argument('device', type=str, help="Device ID")
link.add_argument('title')
link.add_argument('url')
link.set_defaults(func=pushLink)

file = subparser.add_parser("file", help="Send a file")
file.add_argument('device', type=str, help="Device ID")
file.add_argument('file')
file.set_defaults(func=pushFile)

args = parser.parse_args()
args.func(args)
