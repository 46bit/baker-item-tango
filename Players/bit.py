import math
import const
import base_player
from random import randint

class Player(base_player.BasePlayer):
  def __init__(self):
    base_player.BasePlayer.__init__(self)
    self._playerName = "Bit"  # Can be whatever you want as long as it is a sensible one.
                                                # No more than 25 characters
    self._playerYear = "2" # indicate your year of study here should range from 1 to 4
    self._version = "1.0"  # enter the version of your solution if you have more than one
    self._playerDescription = "46bit prototype player."

  # Distribute the fleet onto your board
  def deployFleet(self):
    """
    Decide where you want your fleet to be deployed, then return your board.
    The attribute to be modified is _playerBoard. You can see how it is defined
    in the _initBoards method in the file base_player.py
    """
    self._initBoards()

    # Simple example which always positions the ships in the same place
    # This is a very bad idea! You will want to do something random
    # Destroyer (2 squares)
    self._playerBoard[4][5]=const.OCCUPIED
    self._playerBoard[5][5]=const.OCCUPIED
    # Cruiser (3 squares)
    self._playerBoard[1][1:4]=[const.OCCUPIED]*3
    # Battleship (4 squares)
    self._playerBoard[6][11]=const.OCCUPIED
    self._playerBoard[7][11]=const.OCCUPIED
    self._playerBoard[8][11]=const.OCCUPIED
    self._playerBoard[9][11]=const.OCCUPIED
    # Hovercraft (6 squares)
    self._playerBoard[4][2]=const.OCCUPIED
    self._playerBoard[5][1:4]=[const.OCCUPIED]*3
    self._playerBoard[6][1:4:2]=[const.OCCUPIED]*2
    # Aircraft carrier (6 squares)
    self._playerBoard[9][5:9]=[const.OCCUPIED]*4
    self._playerBoard[8][5]=const.OCCUPIED
    self._playerBoard[10][5]=const.OCCUPIED

    self._playedMoves = [[-1, -1]]
    self._warMode = "hunt"
    self._possibleTargets = []

    return self._playerBoard

  # Decide what move to make based on current state of opponent's board and print it out
  def chooseMove(self):
    """
    Decide what move to make based on current state of opponent's board and return it
    # Completely random strategy
    # Knowledge about opponent's board is completely ignored
    """

    if self._warMode == "hunt":
      move = [-1, -1]
      while move in self._playedMoves:
        move[0] = randint(0, 11)

        if move[0] < 6:
          move[1] = randint(0, 2) * 2
        else:
          move[1] = randint(0, 5) * 2
        if move[0] % 2 == 1:
          move[1] = move[1] + 1

      self._playedMoves.append(move)
    elif self._warMode == "sink":
      move = self._possibleTargets.pop(0)
      print move
      self._playedMoves.append(move)

    # Display move in row (letter) + col (number) grid reference
    # e.g. A3 is represented as 0,2
    return move[0], move[1]

  def setOutcome(self, entry, row, col):
    """
    entry: the outcome of the shot from the opponent,
        expected value is const.HIT for hit and const.MISSED for missed.
    row: (int) the board row number (e.g. row A is 0)
    col: (int) the board column (e.g. col 2 is represented by  value 3) so A3 case is (0,2)
    """

    is_valid = False
    if entry == const.HIT:
      is_valid = True
      Outcome = const.HIT

      self._warMode = "sink"

      for dx in range(-1, 2):
        for dy in range(-1, 2):
          if dx == dy or dx == -dy:
            continue
          possible_target = [row + dx, col + dy]
          if possible_target[0] < 0 or possible_target[0] > 11:
            continue
          if possible_target[1] < 0 or possible_target[1] > 11:
            continue
          if possible_target[1] > 5 and possible_target[0] < 6:
            continue

          if (possible_target not in self._playedMoves) and (possible_target not in self._possibleTargets):
            self._possibleTargets.append(possible_target)
    elif entry == const.MISSED:
      is_valid = True
      Outcome = const.MISSED
    else:
      raise Exception("Invalid input!")
    self._opponenBoard[row][col]=Outcome

    if len(self._possibleTargets) == 0:
      self._warMode = "hunt"

  def getOpponentMove(self, row, col):
    """ You might like to keep track of where your opponent
    has missed, but here we just acknowledge it. Note case A3 is
    represented as row = 0, col = 2.
    """
    if ((self._playerBoard[row][col]==const.OCCUPIED) or (self._playerBoard[row][col]==const.HIT)):
        # They may (stupidly) hit the same square twice so we check for occupied or hit
        self._playerBoard[row][col]=const.HIT
        result =const.HIT
    else:
        # You might like to keep track of where your opponent has missed, but here we just acknowledge it
        result = const.MISSED
    return result

def getPlayer():
    """ MUST NOT be changed, used to get a instance of your class."""
    return Player()
