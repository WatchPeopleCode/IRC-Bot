commands = {
            "streams": [
                lambda args:
                self.SendStreamList(self.channel, 'live'), 0],
            "upcomingStreams": [
                lambda args:
                self.SendStreamList(self.channel, 'upcoming'), 0],
            "Qstreams": [
                lambda args:
                self.SendStreamList(args[0], 'live'), 0],
            }