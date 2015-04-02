commands = {
    "mute": [
        lambda args:
        self.SetConfig('muted', True), 1],
    "unmute": [
        lambda args:
        self.SetConfig('muted', False), 1],
    "setConfig": [
        lambda args:
        self.SetConfig(args[2][0], args[2][1]), 3],
    "getConfig": [
        lambda args:
        self.Send(self.channel, self.GetConfig(args[2][0])), 2],
    "setPerms": [
        lambda args:
        self.SetPerms(args[2][0], args[2][1]), 3],
    "getPerms": [
        lambda args:
        self.Send(self.channel, self.GetPerms(args[2][0])), 2]
}
