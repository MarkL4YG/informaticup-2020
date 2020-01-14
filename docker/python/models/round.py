from models.actions import Action


class Round:

    def __init__(self, state, action):
        self.state: str = state
        self.action: Action = action
