'''
Tuck made this thing
'''

# Imports
import socket
import requests
from time import time

# Vars
HOST = "irc.freenode.net"
PORT = 6667
username = "TuckBot"
master = "tuckismad"
channel = "#WatchPeopleCode"
password = ""
irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((HOST, PORT))

previousStreamsLink = "http://www.watchpeoplecode.com/past_streams"
apiUrl = "http://www.watchpeoplecode/json"


# Functions
def Send(name, message):
    irc.send(bytes("PRIVMSG " + name + " :" + message + "\r\n", "UTF-8"))


def Check(data, cmd):
    data = data.lower()
    cmd = cmd.lower()
    if(data.find(cmd) != -1):
        return True
    else:
        return False


def GetJSON():
    return requests.get('http://www.watchpeoplecode.com/json').json()


def JSONtoSet(jsonObject):
    li = []
    for obj in jsonObject['live']:
        li.append(obj)
    return li


def SendLiveStreams():
    response = GetJSON()
    if response['live'] == []:
        Send(channel, "No current streams available :(")
    else:
        for obj in response['live']:
            Send(channel, ('Name: ' + obj['title'] + ' URL: ' + obj['url']))


def SendUpcomingStreams():
    response = GetJSON()
    if response['upcoming'] == []:
        Send(channel, "There are no upcoming streams :(")
    else:
        for obj in response['upcoming']:
            Send(channel, ('Name: ' + obj['title'] + ' URL: ' + obj['url']))


# Main
irc.send(bytes("NICK " + username + "\r\n", "UTF-8"))
irc.send(bytes("USER " + username + " " + username + " " + username + " :PythonBot\r\n", "UTF-8"))
irc.send(bytes("PRIVMSG nickserv :identify " + password + "\r\n", "UTF-8"))
irc.send(bytes("JOIN " + channel + "\r\n", "UTF-8"))
# irc.send(bytes("PRIVMSG " + master + " :Hello ;), I'm Alive\r\n", "UTF-8"))

lastTime = time()
newCacheLiveStreams = JSONtoSet(GetJSON())
cacheLiveStreams = newCacheLiveStreams

while True:
    data = irc.recv(4096).decode("UTF-8")  # Sometimes i get this error: UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe5 in position 1804: invalid continuation byte
    if(data.find("PING") != -1):
        irc.send(bytes("PONG " + data.split()[1] + "\r\n", "UTF-8"))

    # Commands
    if(Check(data, username)):
        if(Check(data, "previous") and Check(data, "streams")):
            Send(channel, previousStreamsLink)
        if(Check(data, "what") and Check(data, "commands")):  # make dict of commands and output
            Send(channel, "That is for me to know and you to find out when Tuck programs me to tell you ;)")
        if(Check(data, "current") and Check(data, "streams")):
            SendLiveStreams()
        if(Check(data, "upcoming") and Check(data, "streams")):
            SendUpcomingStreams()
        if(Check(data, "answer") and Check(data, "to") and Check(data, "life")):
            Send(channel, "According to my memory bank, the answer is 42.")
        #if(Check(data, "about")):
            #Send(channel, "I'm a IRC Bot programmed for the subreddit /r/WatchPeopleCode")
        if(Check(data, "eye") and Check(data, "on") and Check(data, "hcwool")):
            Send(channel, "I'll keep an eye on him for you ◉_◉")
        if(Check(data, "is") and Check(data, "hcwool") and Check(data, "takeover")):
            Send(channel, "Yes, but his attempts are futile")

    '''
    Attempting to check if there is a new livestream in the list, then notify IRC
    Note: Should probably do something with async
    '''
    if time() >= lastTime + 10:
        lastTime = time()
        newCacheLiveStreams = JSONtoSet(GetJSON())
        for obj in newCacheLiveStreams:
            found = False
            for obj2 in cacheLiveStreams:
                if obj == obj2:
                    found = True
            if not found:
                Send(channel, '"' + obj['title'] + '" just went live!, check it out here: ' + obj['url'])
        cacheLiveStreams = newCacheLiveStreams

# Call Admins
# Uptime
# Notify user when there were talked about
# Timer converter
# Regex
# Log
