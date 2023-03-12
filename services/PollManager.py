from models.PollResponse import PollResponse
from services.TeamPoll import TeamPoll
from services.WigglePoll import WigglePoll


class PollManager:
    def __init__(self):
        self.previous_poll = None
        self.current_poll = None
        self.wiggle_poll = WigglePoll()
        self.team_poll = TeamPoll()
        self.poll_active = False

    def again(self):
        if self.poll_active:
            return PollResponse(text="S;trsfu joyyomh", ephemeral=True)
        if not self.previous_poll:
            return PollResponse(color=0x0F0000, text="Can't do a hit if there was no hit")
        else:
            return self.previous_poll.again()

    def start(self, new_poll_type, context):
        if new_poll_type == "wiggle":
            self.current_poll = self.wiggle_poll
        elif new_poll_type == "team_scramble":
            self.current_poll = self.team_poll
        else:
            return PollResponse(text="Too slow", ephemeral=True)
        return self.current_poll.start(context)

    def user_button_press(self, button_name, context):
        if not self.current_poll:
            return PollResponse(color=0x0F0000, text="The fuck did you just do?")
        else:
            self.current_poll.register_button(button_name, context)

    def timeout(self):
        pass
