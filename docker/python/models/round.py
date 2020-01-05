class Round:
    def __init__(self, state, action):
        self._state = state
        self._action = action

    def get_state(self):
        return self._state

    def get_action(self):
        return self._action
