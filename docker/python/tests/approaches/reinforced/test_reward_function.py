import numpy as np

from approaches.reinforced import reward_function


def test_smooth_sigmoid():
    assert reward_function.smooth_sigmoid(np.infty) == 10
    assert reward_function.smooth_sigmoid(-np.infty) == 0


def test_sigmoid():
    assert reward_function.sigmoid(np.infty) == 1
    assert reward_function.sigmoid(-np.infty) == 0
