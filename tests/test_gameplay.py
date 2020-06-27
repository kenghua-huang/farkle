from farkle import Farkle, State, Action, Farkle, Dice
from pytest import fixture


@fixture
def two_player_state():
    s = State(2)
    s.turn_sum = 200
    s.can_roll = 2
    s.rolled_dice = [Dice(5)] * 4
    return s


@fixture
def two_player_just_rolled():
    s = State(2)
    s.turn_sum = 0
    s.can_roll = 0
    s.rolled_dice = [Dice(i) for i in range(1, 6)] + [Dice(5)]
    return s


@fixture
def two_player_scored_1():
    s = State(2)
    s.can_roll = 5
    s.rolled_dice = [Dice(i) for i in range(2, 6)] + [Dice(5)]
    s.turn_sum = 100
    return s


@fixture
def two_player_scored_1_5_5():
    s = State(2)
    s.can_roll = 3
    s.rolled_dice = [Dice(i) for i in range(2, 5)]
    s.turn_sum = 200
    return s


@fixture
def two_player_can_score_all():
    s = State(2)
    s.can_roll = 5
    s.rolled_dice = [Dice(1)]
    s.turn_sum = 300
    return s


@fixture
def two_player_played_all():
    s = State(2)
    s.can_roll = 6
    s.rolled_dice = []
    s.turn_sum = 400
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

    def test_roll(self):
        s = State(2)
        new_state = s.roll()

        # make sure state wasn't changed
        assert is_same_state(s, State(2))

        # check what was updated in new state
        assert new_state.can_roll == 0
        assert len(new_state.rolled_dice) == 6

    def test_play_dice_just_rolled_score_1(
        self, two_player_just_rolled, two_player_scored_1
    ):
        s = two_player_just_rolled
        # say we want to play one of the 5's
        act = Action({1: 1}, "1", 100)
        new_state = s.play_dice(act)

        assert is_same_state(two_player_scored_1, new_state)

    def test_play_dice_scored_1_score_5_5(
        self, two_player_scored_1, two_player_scored_1_5_5
    ):
        s = two_player_scored_1
        act = Action({5: 2}, "Two 5's", 100)
        new_state = s.play_dice(act)

        assert is_same_state(s, two_player_scored_1)
        assert is_same_state(new_state, two_player_scored_1_5_5)

    def test_play_dice_can_pick_up_all(
        self, two_player_can_score_all, two_player_played_all
    ):
        s = two_player_can_score_all
        act = Action({1: 1}, "1", 100)
        new_state = s.play_dice(act)

        assert is_same_state(new_state, two_player_played_all)
        assert is_same_state(s, two_player_can_score_all)

    def test_enumerate_options_just_rolled(self, two_player_just_rolled):
        actions = two_player_just_rolled.enumerate_options()
        want = [Action({5: 1}, "5", 50), Action({1: 1}, "1", 100)]

        assert len(actions) == len(want)
        assert all(a in want for a in actions)

    def test_enumerate_options_scored_1(self, two_player_scored_1):
        actions = two_player_scored_1.enumerate_options()
        want = [Action({5: 1}, "5", 50), Action({}, "roll", 0), Action({}, "stop", 0)]
        assert len(actions) == len(want)
        assert all(a in want for a in actions)

    def test_enumerate_options_can_pick_up_all(self, two_player_played_all):
        actions = two_player_played_all.enumerate_options()
        want = [Action({}, "roll", 0), Action({}, "stop", 0)]
        assert len(actions) == len(want)
        assert all(a in want for a in actions)

    def test_enumerate_finds_three_pairs(self):
        s = State(2)
        s.rolled_dice = [Dice(2), Dice(2), Dice(3), Dice(3), Dice(4), Dice(4)]
        s.can_roll = 0
        actions = s.enumerate_options()

        want = [Action({2: 2, 3: 2, 4: 2}, "Three pairs", 1500)]
        assert len(actions) == len(want)
        assert all(a in want for a in actions)

    def test_enumerate_finds_three_singles(self):
        s = State(2)
        s.can_rol = 0

        for num in range(1, 7):
            other = 2 if num != 2 else 3
            s.rolled_dice = [Dice(num)] * 3 + [Dice(other)] * 3
            actions = s.enumerate_options()
            points = 1000 if num == 1 else num * 100
            want = Action({num: 3}, f"Three {num}'s", points)
            assert want in actions

    def test_enumerate_finds_four_five_six_kind(self):
        s = State(2)
        s.can_roll = 0
        for num in range(1, 7):
            for n in range(4, 7):
                other = 2 if num != 2 else 3
                s.rolled_dice = [Dice(num)] * n + [Dice(other)] * (6 - n)
                actions = s.enumerate_options()
                name = {4: "Four", 5: "Five", 6: "Six"}[n]
                points = {4: 1000, 5: 2000, 6: 3000}[n]
                want = Action({num: n}, f"{name} {num}'s", points)
                assert want in actions

    def test_enumerate_finds_straight(self):
        s = State(2)
        s.can_roll
        s.rolled_dice = [Dice(i) for i in range(1, 7)]
        actions = s.enumerate_options()
        want = Action({i: 1 for i in range(1, 7)}, "1-2-3-4-5-6", 3000)
        assert want in actions

    def test_enumerate_options_bankrupt(self):
        # simulate having only one die left and rolling a 3
        s = State(2)
        s.rolled_dice = [Dice(3)]
        s.can_roll = 0

        assert s.enumerate_options() == []

    def test_enumerate_roll_and_stop(self):
        # the condition for having roll and stop is if we've scored
        # any dice with the current roll
        s = State(2).roll()  # don't care what roll is, just that it sets can_roll to 0
        assert s.can_roll == 0

        actions = s.enumerate_options()
        roll = Action({}, "roll", 0)
        stop = Action({}, "stop", 0)
        assert roll not in actions
        assert stop not in actions

        # now change can_roll
        s.can_roll = 1
        actions2 = s.enumerate_options()
        assert roll in actions2
        assert stop in actions2
