'''
Tuck made this thing
'''

# Imports
import select
import socket
import requests
import os
from time import time
from flask import Flask, render_template
import threading
import re

# Global Variables
previousStreamsLink = "http://www.watchpeoplecode.com/past_streams"
apiUrl = "http://www.watchpeoplecode/json"


# Website Part
class Website:
    def __init__(self, bot):
        self.logs = bot.logs
        self.app = Flask(__name__)
        self.port = int(os.environ.get('PORT', 5000))

        @self.app.route('/')
        def home():
            return render_template("log.html", logs=self.logs)

    def Run(self):
            self.app.run(host='0.0.0.0', port=self.port)


class Bot:
    logs = []  # Logs to pass to the website

    def __init__(self):
        self.HOST = "irc.freenode.net"  # IRC Server
        self.PORT = 6667  # IRC Server Port
        self.username = os.environ.get('BOT_USERNAME', 'TuckBot_Local')  # Bot Username
        self.master = "tuckismad"
        self.channel = os.environ.get('IRC_CHANNEL', '#WpcBotTesting')  # IRC Channel
        self.password = os.environ.get('IRC_PASSWORD', '')  # Bot Password
        self.lastLivestreamCheck = time()  # Livestream Check Timer
        self.lastWakeUp = time()  # Wakeup Timer
        self.newCacheLiveStreams = self.JSONtoSet(self.GetJSON(), 'live')  # Cache of new liveStreams
        self.cacheLiveStreams = self.newCacheLiveStreams  # Cache of old liveStreams
        self.shouldCheckForLivestreams = True
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creating a socket for IRC
        self.irc.connect((self.HOST, self.PORT))  # Use the socket to connect to IRC

        self.irc.send(bytes("NICK " + self.username + "\r\n", "UTF-8"))  # Sends nick to IRC
        self.irc.send(bytes("USER " + self.username + " " + self.username + " " + self.username + " :PythonBot\r\n", "UTF-8"))  # Sends user data to IRC
        self.irc.send(bytes("PRIVMSG nickserv :identify " + self.password + "\r\n", "UTF-8"))  # Sends password to IRC
        self.irc.send(bytes("JOIN " + self.channel + "\r\n", "UTF-8"))  # Join channel

    '''
    Send(String target, String message)
    Sends 'message' to 'target'
    '''
    def Send(self, name, message):
        self.irc.send(bytes("PRIVMSG " + name + " :" + message + "\r\n", "UTF-8"))

    '''
    Check(data, cmd)
    Checks if the 'cmd' is in 'data'
    '''
    def Check(self, data, cmd):
        data = data.lower()
        cmd = cmd.lower()
        if(data.find(cmd) != -1):
            return True
        else:
            return False

    '''
    GetJSON()
    Returns a JsonObject from watchpeoplecode.com/json
    '''
    def GetJSON(self, ):
        return requests.get('http://www.watchpeoplecode.com/json').json()

    '''
    JSONtoSet(jsonObject, row)
    Returns a list of rows from a jsonObject
    '''
    def JSONtoSet(self, jsonObject, streamType):
        result = []
        for row in jsonObject[streamType]:
            result.append(row)
        return result

    '''
    SendStreamList(streamType)
    Sends a list of streams of type 'streamType' to IRC
    '''
    def SendStreamList(self, streamType):
        response = self.GetJSON()
        if response[streamType] == []:
            self.Send(self.channel, "There are no " + streamType + " streams :(")
        else:
            for obj in response[streamType]:
                self.Send(self.channel, ('Name: ' + obj['title'] + ' URL: ' + obj['url']))

    '''
    ParseData(data)
    Returns a list of tuples of parsed data
    '''
    def ParseData(self, data):
        result = []
        sender_pattern = r'^:(.*)!'
        message_pattern = r'PRIVMSG #?\S* :(.*)'
        sender_match = re.search(sender_pattern, data)
        message_match = re.search(message_pattern, data)
        if sender_match is not None and message_match is not None:
            result.append({'sender': sender_match.group(1), 'message': message_match.group(1)})
        return result

    def WakeUp(self):
        return requests.get('http://tuckbot.herokuapp.com')  # put in the url that wakes the bot
        print("Wake Up")

    '''
    Run()
    Main run function
    '''
    def Run(self):
        while True:
            try:  # Try to decode the incoming data from IRC
                #if select.select([self.irc], [], [], 10)[0]:  # non_blocking check if there is data to read
                data = self.irc.recv(4096).decode("UTF-8")
                #else:
                #    self.WakeUp()  # if no data avaliable after 5 mins send wakeup sig
                #    continue
            except Exception as e:
                print(e)
            if(data.find("PING") != -1):  # replies to pings from IRC
                self.irc.send(bytes("PONG " + data.split()[1] + "\r\n", "UTF-8"))

            if(self.Check(data, self.username)):  # Check if Bot is being talked to
                if(self.Check(data, "previous") and self.Check(data, "streams")):
                    self.Send(self.channel, previousStreamsLink)
                if(self.Check(data, "what") and self.Check(data, "commands")):
                    self.Send(self.channel, "That is for me to know and you to find out when Tuck programs me to tell you ;)")
                if(self.Check(data, "current") and self.Check(data, "streams")):
                    self.SendStreamList('live')
                if(self.Check(data, "upcoming") and self.Check(data, "streams")):
                    self.SendStreamList('upcoming')
                if(self.Check(data, "answer") and self.Check(data, "to") and self.Check(data, "life")):
                    self.Send(self.channel, "According to my memory bank, the answer is 42.")
                if(self.Check(data, "eye") and self.Check(data, "on") and self.Check(data, "hcwool")):
                    self.Send(self.channel, "I'll keep an eye on him for you")
                if(self.Check(data, "is") and self.Check(data, "hcwool") and self.Check(data, "takeover")):
                    self.Send(self.channel, "Yes, but his attempts are futile")
                if(self.Check(data, "livestreamchecker") and self.Check(data, "on")):
                    self.shouldCheckForLivestreams = True
                    self.Send(self.channel, "LivestreamChecker set to: True")
                if(self.Check(data, "livestreamchecker") and self.Check(data, "off")):
                    self.shouldCheckForLivestreams = False
                    self.Send(self.channel, "LivestreamChecker set to: False")
                if(self.Check(data, "mute")):
                    self.channel = ""
                if(self.Check(data, "unmute")):
                    self.channel = os.environ.get('IRC_CHANNEL', '#WpcBotTesting')

            if time() >= self.lastLivestreamCheck + 10:  # Checks for new livestreams every 10 seconds
                self.lastLivestreamCheck = time()
                if self.shouldCheckForLivestreams:
                    self.newCacheLiveStreams = self.JSONtoSet(self.GetJSON(), 'live')
                    for newStream in self.newCacheLiveStreams:
                        for oldStream in self.cacheLiveStreams:
                            if newStream['title'] == oldStream['title'] and newStream['url'] == oldStream['url']:
                                break
                        else:
                            self.Send(self.channel, '"' + newStream['title'] + '" just went live!, check it out here: ' + newStream['url'])
                    self.cacheLiveStreams = self.newCacheLiveStreams

            if time() >= self.lastWakeUp + 300:
                self.lastWakeUp = time()
                self.WakeUp()

            parsedData = self.ParseData(data)  # Used for logging to the flask website
            if parsedData:
                for msg in parsedData:
                    self.logs.append(msg['sender'] + ": " + msg['message'])

if __name__ == '__main__':
    bot = Bot()
    p1 = threading.Thread(target=bot.Run)
    p1.start()

    website = Website(bot)
    p2 = threading.Thread(target=website.Run)
    p2.start()

# break messages with string delimiter for logging
# GCD
# Call Admins
# Uptime
# Timer converter
# Regex
# timezones
