#!/usr/bin/python

import argparse
from pushbullet import PushBullet
import sys

try:
    from urllib.request import URLError, HTTPError
except:
    from urllib2 import URLError, HTTPError

def getDevices(args):
    p = PushBullet(args.api_key)
    try:
        devices = p.getDevices()
    except HTTPError:
        _, e, _ = sys.exc_info()
        print("The server couldn\'t fulfill the request.")
        print("Error code: %s" % (e.code))
    except URLError:
        _, e, _ = sys.exc_info()
        print("We failed to reach a server.")
        print("Reason: %s" % (e.reason))
    else:
        if args.json:
            print(devices)
            return
        for device in devices:
            if "nickname" in device["extras"]:
                print("%s %s" % (device["id"], device["extras"]["nickname"]))
            else:
                print("%s %s %s" % (device["id"], device["extras"]["manufacturer"], device["extras"]["model"]))

def pushNote(args):
    p = PushBullet(args.api_key)
    note = p.pushNote(args.device, args.title, " ".join(args.body))
    if args.json:
        print(note)
        return
    if "created" in note:
        print("OK")
    else:
        print("ERROR %s" % (note))

def pushAddress(args):
    p = PushBullet(args.api_key)
    try:
        address = p.pushAddress(args.device, args.name, " ".join(args.address))
    except HTTPError:
        _, e, _ = sys.exc_info()
        print("The server couldn\'t fulfill the request.")
        print("Error code: %s" % (e.code))
    except URLError:
        _, e, _ = sys.exc_info()
        print("We failed to reach a server.")
        print("Reason: %s" % (e.reason))
    else:
        if args.json:
            print(address)
            return
        if "created" in address:
            print("OK")
        else:
            print("ERROR %s" % (address))

def pushList(args):
    p = PushBullet(args.api_key)
    try:
        lst = p.pushList(args.device, args.title, args.list)
    except HTTPError:
        _, e, _ = sys.exc_info()
        print("The server couldn\'t fulfill the request.")
        print("Error code: %s" % (e.code))
    except URLError:
        _, e, _ = sys.exc_info()
        print("We failed to reach a server.")
        print("Reason: %s" % (e.reason))
    else:
        if args.json:
            print(lst)
            return
        if "created" in lst:
            print("OK")
        else:
            print("ERROR %s" % (lst))

def pushLink(args):
    p = PushBullet(args.api_key)
    try:
        link = p.pushLink(args.device, args.title, args.url)
    except HTTPError:
        _, e, _ = sys.exc_info()
        print("The server couldn\'t fulfill the request.")
        print("Error code: %s" % (e.code))
    except URLError:
        _, e, _ = sys.exc_info()
        print("We failed to reach a server.")
        print("Reason: %s" % (e.reason))
    else:
        if args.json:
            print(link)
            return
        if "created" in link:
            print("OK")
        else:
            print("ERROR %s" % (link))
            
def pushFile(args):
    p = PushBullet(args.api_key)
    try:
        file = p.pushFile(args.device, args.file)
    except HTTPError:
        _, e, _ = sys.exc_info()
        print("The server couldn\'t fulfill the request.")
        print("Error code: %s" % (e.code))
    except URLError:
        _, e, _ = sys.exc_info()
        print("We failed to reach a server.")
        print("Reason: %s" % (e.reason))
    else:
        if args.json:
            print(file)
            return
        if "created" in file:
            print("OK")
        else:
            print("ERROR %s" % (file))


parser = argparse.ArgumentParser()
parser.add_argument("--json", default=False, action="store_const", const=True)
parser.add_argument("api_key")
subparser = parser.add_subparsers(dest="type")

getdevices = subparser.add_parser("getdevices", help="Get a list of devices")
getdevices.set_defaults(func=getDevices)

note = subparser.add_parser("note", help="Send a note")
note.add_argument('device', type=int, help="Device ID")
note.add_argument('title')
note.add_argument('body', nargs=argparse.REMAINDER)
note.set_defaults(func=pushNote)

address = subparser.add_parser("address", help="Send an address")
address.add_argument('device', type=int, help="Device ID")
address.add_argument('name')
address.add_argument('address', nargs=argparse.REMAINDER)
address.set_defaults(func=pushAddress)

lst = subparser.add_parser("list", help="Send a list")
lst.add_argument('device', type=int, help="Device ID")
lst.add_argument('title')
lst.add_argument('list', nargs=argparse.REMAINDER)
lst.set_defaults(func=pushList)

link = subparser.add_parser("link", help="Send a link")
link.add_argument('device', type=int, help="Device ID")
link.add_argument('title')
link.add_argument('url')
link.set_defaults(func=pushLink)

file = subparser.add_parser("file", help="Send a file")
file.add_argument('device', type=int, help="Device ID")
file.add_argument('file')
file.set_defaults(func=pushFile)

args = parser.parse_args()
args.func(args)

