def SendCommandList():
    msg = "My commands are: "
    for cmd in self.commandList.keys():
        msg += (cmd + " ")
    print(msg)
    self.Send(self.channel, msg)

commands = {
            "help": [
                lambda args:
                SendCommandList(), 0]
            }
