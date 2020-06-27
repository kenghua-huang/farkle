from farkle import Farkle, State, Action, Farkle, Dice
from pytest import fixture


@fixture
def two_player_state():
    s = State(2)
    s.turn_sum = 200
    s.can_roll = 2
    s.rolled_dice = [Dice(5)] * 4
    return s


def is_same_state(s1, s2):
    for attr in dir(s1):
        if getattr(s1, attr) != getattr(s2, attr):
            return False

    return True


class TestState:

    def test_current_player(self):
        # two player game
        s = State(2)
        s.current_round = 0
        assert s.current_player == 0
        s.current_round = 1
        assert s.current_player == 1
        s.current_round = 2
        assert s.current_player == 0

        # three player game
        s = State(3)
        s.current_round = 0
        assert s.current_player == 0
        s.current_round = 1
        assert s.current_player == 1
        s.current_round = 2
        assert s.current_player == 2
        s.current_round = 3
        assert s.current_player == 0

    def test_end_turn_not_forced(self, two_player_state):
        s = two_player_state
        new_state = s.end_turn(forced=False)

        # check that new_state is updated
        assert new_state.current_round == 1
        assert new_state.scores[0] == 200
        assert new_state.rolled_dice == []
        assert new_state.can_roll == 6
        assert new_state.turn_sum == 0

        assert is_same_state(s, two_player_state)

    def test_end_turn_forced(self, two_player_state):
        s = two_player_state
        s.turn_sum = 200
        s.can_roll = 2
        s.rolled_dice = [Dice(5)] * 4

        new_state = s.end_turn(forced=True)

        # check that new_state is updated
        assert new_state.current_round == 1
        assert new_state.scores[0] == 0
        assert new_state.rolled_dice == []
        assert new_state.can_roll == 6
        assert new_state.turn_sum == 0

        # check that is is not updated
        assert is_same_state(s, two_player_state)
