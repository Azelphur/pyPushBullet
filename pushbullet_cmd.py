#!/usr/bin/python

import argparse
import sys
import json
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
        print("%s %s %s" % (device["iden"],
                            device["manufacturer"],
                            device["model"]))

def pushNote(args):
    p = PushBullet(args.api_key)
    note = p.pushNote(args.device, args.title, " ".join(args.body))
    if args.json:
        print(json.dumps(note))
        return
    print("Note %s sent to %s" % (note["iden"], note["target_device_iden"]))

def pushAddress(args):
    p = PushBullet(args.api_key)
    address = p.pushAddress(args.device, args.name, " ".join(args.address))
    if args.json:
        print(json.dumps(address))
        return
    print("Address %s sent to %s" % (address["iden"], address["target_device_iden"]))

def pushList(args):
    p = PushBullet(args.api_key)
    lst = p.pushList(args.device, args.title, args.list)
    if args.json:
        print(json.dumps(lst))
        return
    print("List %s sent to %s" % (lst["iden"], lst["target_device_iden"]))

def pushLink(args):
    p = PushBullet(args.api_key)
    link = p.pushLink(args.device, args.title, args.url)
    if args.json:
        print(json.dumps(link))
        return
    print("Link %s sent to %s" % (link["iden"], link["target_device_iden"]))
            
def pushFile(args):
    p = PushBullet(args.api_key)
    file = p.pushFile(args.device, open(args.file, 'rb'))
    if args.json:
        print(json.dumps(file))
        return
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

