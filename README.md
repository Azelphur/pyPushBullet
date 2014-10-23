pyPushBullet
============

Python library to interface with PushBullet

My friend showed me PushBullet, I liked it. I like Python, combine the two to achieve greatness.

You will need...
- Python (2 or 3 should be fine)
- websocket-client - ```pip install websocket-client```
- requests - ```pip install requests```
- python-magic - ```brew install libmagic``` & ```pip install python-magic```

All of which are available from pip.

You can get your API Key from https://www.pushbullet.com/account

Using the library:

```python
from pushbullet import PushBullet

apiKey = "YOUR_API_KEY_HERE"
p = PushBullet(apiKey)
# Get a list of devices
devices = p.getDevices()

# Send a note
p.pushNote(devices[0]["iden"], 'Hello world', 'Test body')

# Send a map location
p.pushAddress(devices[0]["iden"], "Eiffel tower", "Eeiffel tower, france")

# Send a list
p.pushList(devices[0]["iden"], "Groceries", ["Apples", "Bread", "Milk"])

# Send a link
p.pushLink(devices[0]["iden"], "Google", "http://www.google.com")

# Send a file
p.pushFile(devices[0]["iden"], "file.txt", "This is a text file", open("file.txt", "rb"))
```

Using the command line tool:
```
pushbullet_cmd.py YOUR_API_KEY_HERE getdevices
./pushbullet_cmd.py YOUR_API_KEY_HERE note udeCmddJpl "Hello World" "Test Body"
./pushbullet_cmd.py YOUR_API_KEY_HERE address udeCmddJpl "Eiffel tower" "Eeiffel tower, france"
./pushbullet_cmd.py YOUR_API_KEY_HERE list udeCmddJpl Groceries Apples Bread Milk
./pushbullet_cmd.py YOUR_API_KEY_HERE link udeCmddJpl Google http://www.google.com
./pushbullet_cmd.py YOUR_API_KEY_HERE file udeCmddJpl test.jpg

```

Questions? Comments?
Feel free to drop me a line on IRC, irc.azelphur.com #azelphur
