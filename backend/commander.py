class Commander:

    def __init__(self):

        self.state = "RUNNING"

    def make_decision(

        self,

        market_safe,

        event_mode,

        kill_switch

    ):

        if kill_switch:

            return "FREEZE_FLEET"

        if event_mode:

            return "EVENT_MODE"

        if not market_safe:

            return "DEFENSIVE_MODE"

        return "NORMAL_MODE"


if __name__ == "__main__":

    commander = Commander()

    result = commander.make_decision(

        market_safe=True,

        event_mode=False,

        kill_switch=False

    )

    print(result)