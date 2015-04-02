commands = {
            "shoot": [
                lambda args:
                self.Send(self.channel, "\001ACTION shoots " + args[2][0] + " \001"), 0]
            }
