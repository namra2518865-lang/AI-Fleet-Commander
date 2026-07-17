class EventGuard:

    def __init__(self):

        self.event_mode = False

    def activate_event_mode(self):

        self.event_mode = True

    def deactivate_event_mode(self):

        self.event_mode = False

    def should_pause_bot(self, bot):

        if self.event_mode:

            if bot["position_open"] is False:

                return True

        return False


if __name__ == "__main__":

    guard = EventGuard()

    bot = {

        "name": "TrendBot",

        "position_open": False
    }

    guard.activate_event_mode()

    print(

        guard.should_pause_bot(bot)

    )