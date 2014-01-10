pyPushBullet
============

Python library to interface with PushBullet

My friend showed me PushBullet, I liked it. I like Python, combine the two to achieve greatness.

You need python (2 or 3), that's it!

You can get your API Key from https://www.pushbullet.com/settings

Using the library:

```python
from pushbullet import PushBullet

apiKey = "YOUR_API_KEY_HERE"
p = PushBullet(apiKey)
# Get a list of devices
devices = p.getDevices()

# Send a note
p.pushNote(devices[0]["id"], 'Hello world', 'Test body')

# Send a map location
p.pushAddress(devices[0]["id"], "Eiffel tower", "Eeiffel tower, france")

# Send a list
p.pushList(devices[0]["id"], "Groceries", ["Apples", "Bread", "Milk"])

# Send a link
p.pushLink(devices[0]["id"], "Google", "http://www.google.com")

# Send a file
p.pushFile(devices[0]["id"], "filename")
```

Using the command line tool:
```
./pushbullet_cmd.py YOUR_API_KEY_HERE getdevices
./pushbullet_cmd.py YOUR_API_KEY_HERE note 12345 "Hello World" "Test Body"
./pushbullet_cmd.py YOUR_API_KEY_HERE address 12345 "Eiffel tower" "Eeiffel tower, france"
./pushbullet_cmd.py YOUR_API_KEY_HERE list 12345 Groceries Apples Bread Milk
./pushbullet_cmd.py YOUR_API_KEY_HERE link 12345 Google http://www.google.com
./pushbullet_cmd.py YOUR_API_KEY_HERE file 12345 test.jpg

```

Questions? Comments?
Feel free to drop me a line on IRC, irc.azelphur.com #azelphur
