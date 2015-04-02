# Imports
import socket
import os
from time import time
import re
import requests
import imp
import threading


class Bot:
    def __init__(self):
        self.commandList = {}

        self.config = {
            'muted': False
        }

        self.permissions = {

            "tuckismad": 3,
            "TyrantWarship": 1
        }

        self.timedEvents = {
            'livestreamChecker': [self.CheckLiveStreams, time(), 10],
            'hangoutsAnnoucenment': [
                lambda:
                self.Send(self.channel, "24/7 Hangouts room, check it out here! http://goo.gl/HkFFqg"), time(), 3600]
        }

        self.host = "irc.freenode.net"
        self.port = 6667
        self.channel = os.environ.get('IRC_CHANNEL', '#WpcBotTesting')
        self.username = os.environ.get('BOT_USERNAME', 'TuckBot_Local')
        self.password = os.environ.get('IRC_PASSWORD', '')

        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.irc.connect((self.host, self.port))

        self.cacheLiveStreams = self.JSONtoSet(self.GetJSON(), 'live')

        self.irc.send(bytes("NICK " + self.username + "\r\n", "UTF-8"))
        self.irc.send(bytes("USER " + self.username + " " + self.username + " " + self.username + " :PythonBot\r\n", "UTF-8"))
        self.irc.send(bytes("PRIVMSG nickserv :identify " + self.password + "\r\n", "UTF-8"))
        self.irc.send(bytes("JOIN " + self.channel + "\r\n", "UTF-8"))

        self.AddModules()

    def Send(self, target, message):
        '''
        Send(String target, String message)
        Sends 'message' to 'target'
        '''
        if not self.GetConfig('muted'):
            self.irc.send(bytes("PRIVMSG " + target + " :" + str(message) + "\r\n", "UTF-8"))

    def ParseData(self, data):
        '''
        ParseData(data)
        Returns a dictionary containing the sender, channel and message
        '''
        arguments_pattern = r'(?: )(\w+)+'
        message_pattern = r'(#\w+) :(.*)'
        command_pattern = r'!(\w+)'
        sender_pattern = r'(\w+)!'
        result = {}
        args = []
        sender_match = re.search(sender_pattern, data)
        message_match = re.search(message_pattern, data)
        if sender_match is not None and message_match is not None:
            if(len(sender_match.groups()) == 1 and len(message_match.groups()) == 2):
                command_match = re.search(command_pattern, message_match.group(2).rstrip())
                if command_match is not None:
                    command = command_match.groups(0)[0]
                    if command in self.commandList.keys():
                        arguments_match = re.finditer(arguments_pattern, message_match.group(2).rstrip())
                        for arg in arguments_match:
                            args.append(arg.groups(0)[0])
                        result = {'sender': sender_match.group(1), 'channel': message_match.group(1), 'command': command, 'arguments': args}
        return result

    def GetJSON(self):
        '''
        GetJSON()
        Returns a JsonObject from watchpeoplecode.com/json
        '''
        return requests.get('http://www.watchpeoplecode.com/json').json()

    def JSONtoSet(self, jsonObject, streamType):
        '''
        JSONtoSet(jsonObject, row)
        Returns a list of rows from a jsonObject
        '''
        result = []
        for row in jsonObject[streamType]:
            result.append(row)
        return result

    def SendStreamList(self, name, streamType):
        '''
        SendStreamList(streamType)
        Sends a list of streams of type 'streamType' to 'name'
        '''
        response = self.GetJSON()
        if response[streamType] == []:
            self.Send(name, "There are no " + streamType + " streams :(")
        else:
            for obj in response[streamType]:
                self.Send(name, ('Name: ' + obj['title'] + ' URL: ' + obj['url']))

    def CheckLiveStreams(self):
        self.newCacheLiveStreams = self.JSONtoSet(self.GetJSON(), 'live')
        for newStream in self.newCacheLiveStreams:
            for oldStream in self.cacheLiveStreams:
                if newStream['title'] == oldStream['title']:
                    break
            else:
                self.Send(self.channel, '"' + newStream['title'] + '" just went live!, check it out here: ' + newStream['url'])
        self.cacheLiveStreams = self.newCacheLiveStreams

    def Run(self):
        '''
        Run()
        Main run function
        '''
        while True:
            try:
                data = self.irc.recv(4096).decode("UTF-8", "replace")
            except:
                pass
            if(data.find("PING") != -1):
                self.irc.send(bytes("PONG " + data.split()[1] + "\r\n", "UTF-8"))
            try:
                parsedData = self.ParseData(data)
                if(len(parsedData) == 4):
                    if parsedData['command'] in self.commandList.keys():
                        if(self.HasPermission(parsedData['sender'], parsedData['command'])):
                            self.commandList[parsedData['command']][0]((parsedData['sender'], parsedData['channel'], parsedData['arguments']))
                        else:
                            self.Send(self.channel, "You dont have permission to use that command")
            except Exception as e:
                print("Error: " + e)

    def AddCommands(self, newDict):
        for cmd in newDict.keys():
            self.commandList[cmd] = newDict[cmd]

    def SetConfig(self, var, state):
        self.config[var] = (str(state).lower() == "true")

    def GetConfig(self, var):
        if var in self.config.keys():
            return self.config[var]
        else:
            return "Not Set"

    def AddModules(self):
        modules = os.listdir('modules')
        for filename in modules:
            if '_' not in filename:
                module = imp.load_source(filename, "modules/" + filename)
                module.self = self
                self.AddCommands(module.commands)

    def HasPermission(self, sender, cmd):
        if sender not in self.permissions.keys():
            self.SetPerms(sender, 0)
        senderPerm = self.permissions[sender]
        if senderPerm >= self.commandList[cmd][1]:
            return True
        return False

    def SetPerms(self, user, level):
        self.permissions[user] = int(level)

    def GetPerms(self, user):
            return self.permissions[user]


def TimedEvents(bot):
    while True:
        for event in bot.timedEvents:
            if(time() >= bot.timedEvents[event][1] + bot.timedEvents[event][2]):
                bot.timedEvents[event][1] = time()
                bot.timedEvents[event][0]()

if __name__ == '__main__':
    bot = Bot()
    p1 = threading.Thread(target=bot.Run)
    p1.start()

    timedEvents = TimedEvents(bot)
    p2 = threading.Thread(target=timedEvents)
    p2.start()


# import pdb; pdb.set_trace()

# GCD
# Uptime
# Timer converter
# Regex
# timezones
# try catch email
# remind me command
# tell tuck command
