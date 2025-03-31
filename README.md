# XTERemoteKeyboard
Simple remote keyboard for controlling an X server from a different device.  Originally thrown together so I could use my pi based mechanical keyboard laptop to control my desktop remotely.  Simply ssh to the box you need to work on and type `python rkbd.py` then type as normal. 

It uses the `xte` program to send the keystrokes on the remote en on the remote end, which is generally found as part of the xautomation package with most distributions and curses to capture the keystrokes.

Known issues:

	- Alt does not work
	- Escape key behavior can be a bit weird due to how curses handles the key.  Pressing Escape does not send the escape key until the next key is pressed.  If using rkbd.py and a local keyboard this can cause X11 to interpret all local keypresses as Ctrl-key until a key is pressed through rkbd.py
	- Currently not compatible with wayland
