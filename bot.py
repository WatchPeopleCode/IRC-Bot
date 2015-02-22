'''
Tuck made this thing
'''


import socket
import requests
import os
from time import time
from flask import Flask, render_template
import threading

previousStreamsLink = "http://www.watchpeoplecode.com/past_streams"
apiUrl = "http://www.watchpeoplecode/json"


class Website:
    def __init__(self, bot):
        self.logs = bot.logs

        self.app = Flask(__name__)

        @self.app.route('/')
        def home():
            return render_template("log.html", logs=self.logs)

    def Run(self):
            self.app.run(debug=True)


class Bot:
    logs = ['test', 'test2']

    def __init__(self):
        self.HOST = "irc.freenode.net"
        self.PORT = 6667
        self.username = "TuckBot_Local"
        self.master = "tuckismad"
        self.channel = "#WpcBotTesting"
        self.password = ""
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.connect((self.HOST, self.PORT))
        if os.environ.get('IRC_PASSWORD'):
            self.password = os.environ['IRC_PASSWORD']

        self.irc.send(bytes("NICK " + self.username + "\r\n", "UTF-8"))
        self.irc.send(bytes("USER " + self.username + " " + self.username + " " + self.username + " :PythonBot\r\n", "UTF-8"))
        self.irc.send(bytes("PRIVMSG nickserv :identify " + self.password + "\r\n", "UTF-8"))
        self.irc.send(bytes("JOIN " + self.channel + "\r\n", "UTF-8"))
        self.lastTime = time()
        self.newCacheLiveStreams = self.JSONtoSet(self.GetJSON())
        self.cacheLiveStreams = self.newCacheLiveStreams

    def Send(self, name, message):
        self.irc.send(bytes("PRIVMSG " + name + " :" + message + "\r\n", "UTF-8"))

    def Check(self, data, cmd):
        data = data.lower()
        cmd = cmd.lower()
        if(data.find(cmd) != -1):
            return True
        else:
            return False

    def GetJSON(self, ):
        return requests.get('http://www.watchpeoplecode.com/json').json()

    def JSONtoSet(self, jsonObject):
        li = []
        for obj in jsonObject['live']:
            li.append(obj)
        return li

    def SendLiveStreams(self):
        response = self.GetJSON()
        if response['live'] == []:
            self.Send(self.channel, "No current streams available :(")
        else:
            for obj in response['live']:
                self.Send(self.channel, ('Name: ' + obj['title'] + ' URL: ' + obj['url']))

    def SendUpcomingStreams(self):
        response = self.GetJSON()
        if response['upcoming'] == []:
            self.Send(self.channel, "There are no upcoming streams :(")
        else:
            for obj in response['upcoming']:
                self.Send(self.channel, ('Name: ' + obj['title'] + ' URL: ' + obj['url']))

    def Run(self):
        while True:
            data = self.irc.recv(4096).decode("UTF-8")  # Sometimes i get this error: UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe5 in position 1804: invalid continuation byte
            if(data.find("PING") != -1):
                self.irc.send(bytes("PONG " + data.split()[1] + "\r\n", "UTF-8"))

            if(self.Check(data, self.username)):
                if(self.Check(data, "previous") and self.Check(data, "streams")):
                    self.Send(self.channel, previousStreamsLink)
                if(self.Check(data, "what") and self.Check(data, "commands")):  # make dict of commands and output
                    self.Send(self.channel, "That is for me to know and you to find out when Tuck programs me to tell you ;)")
                if(self.Check(data, "current") and self.Check(data, "streams")):
                    self.SendLiveStreams()
                if(self.Check(data, "upcoming") and self.Check(data, "streams")):
                    self.SendUpcomingStreams()
                if(self.Check(data, "answer") and self.Check(data, "to") and self.Check(data, "life")):
                    self.Send(self.channel, "According to my memory bank, the answer is 42.")
                if(self.Check(data, "eye") and self.Check(data, "on") and self.Check(data, "hcwool")):
                    self.Send(self.channel, "I'll keep an eye on him for you")
                if(self.Check(data, "is") and self.Check(data, "hcwool") and self.Check(data, "takeover")):
                    self.Send(self.channel, "Yes, but his attempts are futile")

            '''
            Attempting to check if there is a new livestream in the list, then notify IRC
            Note: Should probably do something with async
            '''
            if time() >= self.lastTime + 10:
                self.lastTime = time()
                newCacheLiveStreams = self.JSONtoSet(self.GetJSON())
                for obj in newCacheLiveStreams:
                    found = False
                    for obj2 in self.cacheLiveStreams:
                        if obj == obj2:
                            found = True
                    if not found:
                        self.Send(self.channel, '"' + obj['title'] + '" just went live!, check it out here: ' + obj['url'])
                self.cacheLiveStreams = newCacheLiveStreams
            self.logs.append(data)

if __name__ == '__main__':
    bot = Bot()
    p1 = threading.Thread(target=bot.Run)
    p1.start()

    website = Website(bot)
    p2 = threading.Thread(target=website.Run)
    p2.start()
