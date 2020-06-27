import abc
import copy
from collections import Counter
import random
import time
from typing import Dict, List, Tuple, NamedTuple, Optional


class Action(NamedTuple):
    used: Dict[int, int]
    name: str
    value: int

    def __str__(self):
        if self.name.lower() in ["roll", "stop"]:
            return self.name
        else:
            return f"Play {self.name} to score {self.value}"


class Dice(object):
    """
    A 6-sided dice object that can be used in dice games implemented
    in Python

    The dice can take the values 1, 2, 3, 4, 5, 6

    The dice keeps track of the most recently rolled value in the
    `value` property. This value is `None` until the dice is rolled.

    Methods
    -------
    roll :
        Rolls the dice and gives a random integer
    """

    def __init__(self, value: Optional[int] = None):
        self.value = value
        self.unicode_dice = {
            1: "\u2680",
            2: "\u2681",
            3: "\u2682",
            4: "\u2683",
            5: "\u2684",
            6: "\u2685",
        }
        if value is None:
            self.roll()

    def __eq__(self, other: "Dice"):
        return self.value == other.value

    def __repr__(self):
        if self.value is None:
            msg = "The dice has not been rolled"
        else:
            msg = f"{self.unicode_dice[self.value]}"

        return msg

    def roll(self):
        """
        Rolls the dice and reset the current value

        Returns
        -------
        value : int
            The number rolled by the dice
        """
        value = random.randint(1, 6)
        self.value = value

        return value


class State:
    # public game state
    current_round: int
    scores: Dict[int, int]
    can_roll: int
    rolled_dice: List[Dice]
    turn_sum: int

    # internal state
    _n_players: int

    def __init__(self, n_players):
        self._n_players = n_players
        self.current_round = 0
        self.scores = {i: 0 for i in range(self._n_players)}
        self.can_roll = 6
        self.rolled_dice = []
        self.turn_sum = 0

    def __dir__(self):
        return [
            "current_round",
            "scores",
            "can_roll",
            "rolled_dice",
            "turn_sum",
        ]

    @property
    def __dict__(self) -> dict:
        return {k: getattr(self, k) for k in dir(self)}

    @__dict__.setter
    def __dict__(self, val: dict):
        for (k, v) in val.items():
            setattr(self, k, copy.deepcopy(v))

    def __copy__(self) -> "State":
        out = State(self._n_players)
        out.__dict__ = self.__dict__
        return out

    @property
    def current_player(self) -> int:
        return self.current_round % self._n_players

    def end_turn(self, forced: bool = False) -> "State":
        """
        End the turn for the current player

        If the player was not forced to end, the `turn_sum` is added to their score

        Parameters
        ----------
        forced: bool, default=False
            A boolean indicating if the player was forced to end his/her turn. If true,
            the player does not get any points for this turn.

        Returns
        -------
        new_state: State
            A new instance of the state is returned recording updated score,
            refreshed dice, and reset current sum
        """

        out = State(self._n_players)
        out.current_round = self.current_round + 1
        out.scores = copy.deepcopy(self.scores)

        if not forced:
            out.scores[self.current_player] += self.turn_sum
        return out

    def roll(self) -> "State":
        out = copy.copy(self)
        out.rolled_dice = [Dice() for _ in range(self.can_roll)]
        out.can_roll = 0  # mark that only actions are to consider scores
        return out

    def play_dice(self, action: Action) -> "State":
        # TODO: validate that the chosen dice exist
        out = copy.copy(self)

        # add value to the current sum
        out.turn_sum += action.value

        n_played = sum(action.used.values())

        # update number of dice that can be rolled
        out.can_roll = len(self.rolled_dice) - n_played
        if out.can_roll == 0:
            # can pick them all up!
            out.can_roll = 6

        # update dice that are set aside
        used_dice = []
        for k, v in action.used.items():
            for _ in range(v):
                used_dice.append(Dice(k))
                out.rolled_dice.remove(Dice(k))

        return out

    def enumerate_options(
            self, rolled_dice: Optional[List[Dice]] = None
    ) -> List[Action]:
        """
        Given a list of dice, it computes all of the possible ways
        that one can score

        Parameters
        ----------
        rolled_dice: Optional[List[Dice]]
            A list of dice for which to enumerate options. If None are passed
            then `self.rolled_dice` is used

        Returns
        -------
        opportunities : List[Action]
            A list of valid actions for a player
        """
        rolled: List[Dice] = self.rolled_dice
        if rolled_dice is not None:
            rolled = rolled_dice

        dice_counts = Counter([d.value for d in rolled])
        opportunities: List[Action] = []

        # Single dice opportunities
        if dice_counts[1] > 0:
            opportunities.append(Action({1: 1}, "1", 100))

        if dice_counts[5] > 0:
            opportunities.append(Action({5: 1}, "5", 50))

        # Three pairs
        pairs = []
        for i in range(1, 7):
            if dice_counts[i] >= 2:
                pairs.append(i)
        if len(pairs) == 3:
            opportunities.append(Action({i: 2 for i in pairs}, f"Three pairs", 1500))

        # Three of a kind
        if dice_counts[1] >= 3:
            opportunities.append(Action({1: 3}, "Three 1's", 1000))
        for i in range(2, 7):
            if dice_counts[i] >= 3:
                opportunities.append(Action({i: 3}, f"Three {i}'s", i * 100))

        for i in range(1, 7):
            # Four of a kind
            if dice_counts[i] >= 4:
                opportunities.append(Action({i: 4}, f"Four {i}'s", 1000))

            # Five of a kind
            if dice_counts[i] >= 5:
                opportunities.append(Action({i: 5}, f"Five {i}'s", 2000))

            # Six of a kind
            if dice_counts[i] == 6:
                opportunities.append(Action({i: 6}, f"Six {i}'s", 3000))

        # Straight
        if all([dice_counts[i] > 0 for i in range(1, 7)]):
            opportunities.append(
                Action({i: 1 for i in range(1, 7)}, "1-2-3-4-5-6", 3000)
            )

        # can_roll is zero iff I just rolled. If there are no opportunities, we
        # must be bankrupt for this round
        if len(opportunities) == 0 and self.can_roll == 0:
            # oops
            return []

        if self.can_roll > 0:
            opportunities.append((Action({}, "roll", 0)))
            opportunities.append(Action({}, "stop", 0))

        return opportunities


class FarklePlayer(abc.ABC):
    name: str

    @abc.abstractmethod
    def act(self, state: State, choices: List[Action]) -> Action:
        pass

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class RandomFarklePlayer(FarklePlayer):
    name = "random_robot"

    def act(self, state: State, choices: List[Action]) -> Action:
        return random.choice(choices)


class HumanFarklePlayer(FarklePlayer):
    def __init__(self, name: str):
        self.name = name

    def act(self, state: State, choices: List[Action]) -> Action:
        # get an action from the user
        print("You have rolled: ", state.rolled_dice)
        print("The current total you have at stake is:", state.turn_sum)
        print("Your scoring options are as follows:")
        for num, act in enumerate(choices):
            print(f"\t{num}: {str(act)}")

        while True:
            msg = "Choose an integer to select a scoring option: "
            try:
                choice = int(input(msg))
                return choices[choice]
            except ValueError:
                print("Input not understood, try again!")


class Farkle(object):
    """
    The Farkle game is executed from this class
    """

    def __init__(self, players, points_to_win=10_000, verbose: bool = False):
        self.points_to_win = points_to_win
        self.players = players
        self._have_human = any(map(
            lambda x: isinstance(x, HumanFarklePlayer),
            players
        ))
        self.verbose = verbose or self._have_human
        self.n_players = len(players)
        self._state = State(self.n_players)
        self._history: List[Tuple[State, Action]] = []

    @property
    def state(self) -> State:
        return self._state

    def set_state(self, action: Action, new_state: State):
        self._history.append((self.state, action))
        self._state = new_state

    def reset(self):
        self._state = State(self.n_players)
        self._history = []

    def step(self, action: Action) -> State:
        used, name, value = action
        if name.lower() == "stop":
            new_state = self.state.end_turn(forced=False)
        elif name.lower() == "roll":
            new_state = self.state.roll()
        elif name.lower() == "bankrupt":
            new_state = self.state.end_turn(forced=True)
        else:
            # otherwise the player used some dice
            new_state = self.state.play_dice(action)

        self.set_state(action, new_state)
        return new_state

    def player_turn(self, choices: Optional[List[Action]] = None):
        """
        Lets each player play a turn and then prints the updated
        scores at the end of the turn
        """
        current_player_num = self.state.current_player
        current_player = self.players[current_player_num]

        if choices is None:
            choices = self.state.enumerate_options()
        action = current_player.act(self.state, choices)
        self.step(action)

        # check if player chose to stop
        if current_player_num != self.state.current_player:
            return

        # check if player has no actions
        next_choices = self.state.enumerate_options()
        if len(next_choices) == 0:
            self.step(Action({}, "bankrupt", 0))
            return

        # otherwise, let the player continue the turn
        self.player_turn(next_choices)

        return None

    def _print_score(self):
        for i in range(self.n_players):
            print(f"  - {self.players[i].name}: {self.state.scores[i]}")

    def play(self):
        """Play a game of Farkle"""
        while True:
            # check end_game
            winners = {
                k: v >= self.points_to_win
                for k, v in self.state.scores.items()
            }

            if any(winners.values()):
                print("Game over! Final score is:")
                self._print_score()
                return winners

            # otherwise the game is on!
            if self.verbose:
                print(f"Starting of turn {self.state.current_round}")
                print("Current score:")
                self._print_score()
                time.sleep(0.1)

            for _ in range(self.n_players):
                if self.verbose:
                    current_player = self.players[self.state.current_player]
                    print(f"It is {current_player}'s turn")
                self.step(Action({}, "roll", 0))
                self.player_turn()


if __name__ == "__main__":
    p1 = HumanFarklePlayer("Spencer")
    # p2 = HumanFarklePlayer("Chase")
    p2 = RandomFarklePlayer()
    f = Farkle([p1, p2])
    f.play()
