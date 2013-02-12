pyPushBullet
============

Python library to interface with PushBullet

My friend showed me PushBullet, I liked it. I like Python, combine the two to achieve greatness.

This is currently very new, quickly written, and may or may not actually be functional. If it breaks feel free to file a bug report (bonus points for patches)

You need python (2 or 3) and beautifulsoup4 (you can get it with pip)

How to use:

```python
from pushbullet import PushBullet

p = PushBullet()
p.signIn("user@gmail.com", "secret")
devices = p.getDevices()
data = {'type' : 'note',
        'device_id' : devices[0]["id"],
        'title' : "Hello World!",
        'body' : "It's wonderful to be here!"}
p.pushNotification(data)
```
