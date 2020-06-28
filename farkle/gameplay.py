class State:
    # public game state
    current_round
    scores
    can_roll
    rolled_dice
    turn_sum

    # internal state
    _n_players

    def __init__(self, n_players):
        pass

    def current_player(self) -> int:
        pass

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
        pass

    def roll(self):
        """
        Determines which dice can be rolled and rolls the dice

        Returns
        -------
        out : State
            A new copy of the state where dice have been rolled
        """
        pass

    def play_dice(self, action):
        """
        Plays the action indicated by the players

        1. Adds value of the action
        2. Sets aside any dice that were used
        3. Determines how many dice the player can use for next turn
        """
        pass

    def enumerate_options(self, rolled_dice=None):
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
        pass
