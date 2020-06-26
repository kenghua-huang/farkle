import random
import time


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
    def __init__(self):
        self.value = None
        self.unicode_dice = {
            1: "\u2680", 2: "\u2681", 3: "\u2682",
            4: "\u2683", 5: "\u2684", 6: "\u2685"
        }

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


def scoring_options(dice_counts, scoredone=False):
    """
    Given a list of dice, it computes all of the possible ways
    that one can score

    Parameters
    ----------
    dice : dict{int -> int}
        A dictionary that expresses how many of each dice were rolled

    Returns
    -------
    opportunities : list(tuple(dict(int->int), str, int))
        A list of scoring opportunities with the number of a
        particular dice number required, the scoring type name, and
        the number of points that opportunity is worth
    """
    if scoredone:
        opportunities = [({}, "no dice", 0)]
    else:
        opportunities = []

    # Single dice opportunities
    if dice_counts[1] > 0:
        opportunities.append(({1: 1}, "1", 100))

    if dice_counts[5] > 0:
        opportunities.append(({5: 1}, "5", 50))

    # Three pairs
    pairs = []
    for i in range(2, 7):
        if dice_counts[i] >= 2:
            pairs.append(i)
    if len(pairs) == 3:
        opportunities.append(
            ({i: 2 for i in pairs}, f"Three pairs", 1500)
        )

    # Three of a kind
    if dice_counts[1] >= 3:
        opportunities.append(({1: 3}, "Three 1's", 1000))
    for i in range(2, 7):
        if dice_counts[i] >= 3:
            opportunities.append(({i: 3}, f"Three {i}'s", i*100))

    # Four of a kind
    for i in range(2, 7):
        if dice_counts[i] >= 4:
            opportunities.append(({i: 4}, f"Four {i}'s", 1000))

    # Five of a kind
    for i in range(2, 7):
        if dice_counts[i] >= 5:
            opportunities.append(({i: 5}, f"Five {i}'s", 2000))

    # Six of a kind
    for i in range(2, 7):
        if dice_counts[i] == 6:
            opportunities.append(({i: 6}, f"Six {i}'s", 3000))

    # Straight
    if all([dice_counts[i] > 0 for i in range(1, 7)]):
        opportunities.append(
            ({i: 1 for i in range(1, 7)}, "1-2-3-4-5-6", 3000)
        )

    return opportunities


class FarklePlayer(object):
    """
    An object that represents a player for the Farkle game

    The player can play their turn using the `playturn` method which
    will roll their dice and offer scoring options to the player. This
    implementation requires human interaction to choose which scores
    to accept

    Parameters
    ----------
    name : str
        The name of the player
    ndice : int, default=6
        The number of dice to play Farkle with. Defaults to 6.

    Methods
    -------
    scoreroll(dice_values) :
        Walks through the scoring phase of a player's turn
    playturn() :
        Walks through a player's turn

    """
    def __init__(self, name, ndice=6):
        self.ndice = ndice
        self.dice = [Dice() for i in range(ndice)]

    def _count_dice(self, dice_counts):
        return sum(dice_counts.values())

    def _count_values(self, dice, value):
        return sum([d.value==value for d in dice])

    def get_dice_counts(self, dice):
        return {i: self._count_values(dice, i) for i in range(1, 7)}

    def scoreroll(self, dice):
        """
        Takes a given roll of dice and gives the player choices for
        how to score their roll

        Parameters
        ----------
        dice : list(Dice)
             The dice rolled

        Returns
        -------
        score : int
            The score the player earns from this roll
        _ : bool
            Whether the player had any score options in the roll
        _ : int
            The number of dice remaining in the player's ''hand''
        """
        # Initialize score and get dice_counts
        score = 0
        dice_counts = self.get_dice_counts(dice)

        # Determine all of the scoring options a player has
        _options = dict(
            enumerate(scoring_options(dice_counts))
        )

        # If you have no scoring options at beginning of the scoring
        # sequence then return 0 points and True for no score dice
        choices_remain = len(_options) > 0
        if not choices_remain:
            return 0, True, self._count_dice(dice_counts)

        while choices_remain:
            # Print all of the scoring options and have player choose
            print("Your scoring options are as follows:")
            for (k, (_cost, _name, _pts)) in _options.items():
                print(f"\t{k}: Play {_name} to score {_pts}")
            msg = "Choose one of the integers that correspond to a scoring "
            msg += "option: "
            choice = int(input(msg))
            _cost, _name, _pts = _options[choice]

            # Add the score of their choice and detract cost from their dice_counts
            if _name == "no dice":
                choices_remain = False
                break
            score += _pts
            for (k, c) in _cost.items():
                dice_counts[k] = dice_counts[k] - c

            # Compute which scoring opportunities remain
            _options = dict(
                enumerate(scoring_options(dice_counts, scoredone=True))
            )
            choices_remain = len(_options) > 1

        return score, False, self._count_dice(dice_counts)

    def playturn(self):
        """
        Walks through each step of a player's turn and allows them
        to make decisions and get a score

        Return
        ------
        score : int
            The score from this player's turn
        """
        # Variables for the turn
        potential_score = 0
        continue_rolling = True
        ndice_remaining = self.ndice
        while continue_rolling:
            # Only work with number of dice remaining
            current_dice = self.dice[:ndice_remaining]

            # Roll all active dice
            print("\nRolling the dice")
            for d in current_dice:
                d.roll()
            print(*current_dice, "\n")

            # Decide which dice to score
            print("Time to score: Please select which scoring options that")
            print("you would like to keep by entering the corresponding")
            print("number\n")
            out = self.scoreroll(current_dice)
            _score, no_scoring_dice, ndice_remaining = out
            potential_score += _score
            if _score == 0:
                print("\nFarkle! Your current round's score is set to 0")
                time.sleep(1.0)
                return 0

            # Hot Dice: If no remaining dice then all dice active again
            if ndice_remaining == 0:
                ndice_remaining = self.ndice

            # Decide whether to reroll or not
            print(f"\nYou currently have scored: {potential_score} points")
            print(f"with {ndice_remaining} dice left")
            _continue = input(
                "\n\tWould you like to roll remaining dice? (y/n): "
            ).lower()
            continue_rolling = "y" in _continue

        return potential_score


class Farkle(object):
    """
    The Farkle game is executed from this class
    """
    def __init__(self, playernames, points_to_win=10_000):
        self.points_to_win = points_to_win
        self.playernames = playernames
        self.players = {name: FarklePlayer(name) for name in playernames}
        self.scores = {name: 0 for name in playernames}

    def did_player_win(self, name):
        return self.scores[name] > self.points_to_win

    def turn(self):
        """
        Lets each player play a turn and then prints the updated
        scores at the end of the turn
        """
        for name in self.playernames:
            print(f"\n\nIt is {name}'s turn")
            _score = self.players[name].playturn()
            self.scores[name] += _score


        return None

    def play(self):
        "Play a game of Farkle"
        nowinner = True
        while nowinner:
            self.turn()
            print("\n\nAt the end of this turn:")
            for name in self.playernames:
                print(f"\t{name} has {self.scores[name]} points")
            time.sleep(1)
            wbool = list(map(self.did_player_win, self.playernames))
            if sum(wbool) > 0:
                nowinner = False

        winner = [n for (i, n) in enumerate(self.playernames) if wbool[i]]
        return winner

