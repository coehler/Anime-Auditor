# Anime Auditor

A simple Discord bot written in Python 3.6 with discord.py 0.16.12 that uses the OpenCV2 face detector by Nagadomi to check if a Discord user has an Anime profile picture. Middling accuracy, but it gets the job done.

## Installation

This should get Anime Auditor up and running on your machine.

First you need a Discord Bot Token. You can generate one at the Discord Developer Portal. Once you have it, open `animeauditor.py`, find where the token is set, and paste in your own:

```python
TOKEN = 'YourTokenHere!'
``` 

Next you need to install the required python packages. Anime Auditor only works with Python 3.6 and discord.py version 0.16.12.

To install the required version of discord.py use the following terminal command:

```
python3.6 -m pip install discord.py==0.16.12
```

To install OpenCV use the following terminal command:

```
python3.6 -m pip install opencv-python
```

Now you need to download Nagadomi's face detector. It’s an XML file that tells OpenCV2 what an Anime face looks like. Download it [here](https://github.com/nagadomi/lbpcascade_animeface) and place it in the same directory as `animeauditor.py`

Lastly you need to make an empty directory called `servers` in the same directory as `animeauditor.py`

You're all set now. Launch Anime Auditor using the following terminal command:

```
Python3.6 animeauditor.py
```

## Usage

All of Anime Auditor's functionality can be listed using the `aa?help` command.

Anime Auditor also has a blacklist file. Discord user's with their names in `blacklist.txt` will always be reported as having an Anime profile picture. This allows for hosts to correct false negatives.

Names can be added to the blacklist manually or by using the `aa?blacklist` command. The first parameter of this command is the user to blacklist and second parameter is the host key. The host key is a random string that is printed to the host's terminal at startup. It is regenerated every time the blacklist command is called.

## Credits

The organizations and people who helped or facilitated the development of Anime Auditor can be viewed at any time with the `aa?credits` command.

* [lbpcascade_animeface](https://github.com/nagadomi/lbpcascade_animeface) - Cascade file used for face detection
* [OpenCV](https://github.com/nagadomi/lbpcascade_animeface) - Computer vision library
* [discord.py](https://github.com/Rapptz/discord.py) - Discord API