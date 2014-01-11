import math
import const
import base_player
from random import randint, shuffle

class Player(base_player.BasePlayer):
  def __init__(self):
    base_player.BasePlayer.__init__(self)
    self._playerName = "Bit"  # Can be whatever you want as long as it is a sensible one.
                                                # No more than 25 characters
    self._playerYear = "2" # indicate your year of study here should range from 1 to 4
    self._version = "1.0"  # enter the version of your solution if you have more than one
    self._playerDescription = "46bit prototype player."

  DESTROYER = [[0, 0], [1, 0]]
  CRUISER = [[0, -1], [0, 0], [0, 1]]
  BATTLESHIP = [[-1, 0], [0, 0], [1, 0], [2, 0]]
  HOVERCRAFT = [[-1, 0], [0, -1], [0, 1], [0, 0], [1, -1], [1, 1]]
  CARRIER = [[0, -1], [-1, -1], [1, -1], [0, 0], [0, 1], [0, 2]]

  def placePiece(self, piece, direction, row, col):
    voxelrowm = 1
    voxelcolm = 1
    if direction % 2 == 1:
      voxelrowm = -1
    if direction > 1:
      voxelcolm = -1

    for voxel in piece:
      vrow = voxel[0] * voxelrowm + row
      vcol = voxel[1] * voxelcolm + col
      if (vrow < 0 or vrow > 11) or (vcol > 5 and vrow < 6) or (vcol < 0 or vcol > 11) or (self._playerBoard[vrow][vcol] != const.EMPTY):
        return False

    for voxel in piece:
      vrow = voxel[0] * voxelrowm + row
      vcol = voxel[1] * voxelcolm + col
      self._playerBoard[vrow][vcol] = const.OCCUPIED

    return True

  def deployPieces(self, pieces):
    for piece in pieces:
      # print "%d segment piece" % len(piece)
      while True:
        d = randint(0, 3)
        row = randint(0, 11)
        col = randint(0, 11)
        # print "(%d %d %d)" % (d, row, col)
        if self.placePiece(piece, d, row, col):
          break

  # Distribute the fleet onto your board
  def deployFleet(self):
    """
    Decide where you want your fleet to be deployed, then return your board.
    The attribute to be modified is _playerBoard. You can see how it is defined
    in the _initBoards method in the file base_player.py
    """
    self._initBoards()

    pieces = [self.DESTROYER, self.CRUISER, self.BATTLESHIP, self.HOVERCRAFT, self.CARRIER]
    shuffle(pieces)
    self.deployPieces(pieces)

    self._playedMoves = [[-1, -1]]
    self._possibleTargets = []
    self._warMode = "hunt"

    self._huntMode = "tiling"
    self._diagonalMoves = []

    # Create hunting moves for diagonals across each 6x6 square.
    for i in range(0, 6):
      self._diagonalMoves.append([i, i])
      self._diagonalMoves.append([5 - i, 5 - i])

      self._diagonalMoves.append([i + 6, i])
      self._diagonalMoves.append([5 - i + 6, 5 - i])

      self._diagonalMoves.append([i + 6, i + 6])
      self._diagonalMoves.append([5 - i + 6, 5 - i + 6])

    # Fill in the gaps between square diagonals a bit, quick improvement.
    self._diagonalMoves.append([5, 3])
    self._diagonalMoves.append([6, 2])
    self._diagonalMoves.append([8, 5])
    self._diagonalMoves.append([9, 6])

    shuffle(self._diagonalMoves)

    return self._playerBoard

  # Decide what move to make based on current state of opponent's board and print it out
  def chooseMove(self):
    """
    Decide what move to make based on current state of opponent's board and return it
    # Completely random strategy
    # Knowledge about opponent's board is completely ignored
    """

    if self._warMode == "hunt":
      move = self.chooseHuntMove()
    elif self._warMode == "sink":
      move = self.chooseSinkMove()

    # print move
    self._playedMoves.append(move)

    # Display move in row (letter) + col (number) grid reference
    # e.g. A3 is represented as 0,2
    return move[0], move[1]

  def chooseHuntMove(self):
    move = [-1, -1]

    if self._huntMode == "diagonal":
      while move in self._playedMoves:
        if len(self._diagonalMoves) == 0:
          self._huntMode = "tiling"
          break
        move = self._diagonalMoves.pop()

    if self._huntMode == "tiling":
      while move in self._playedMoves:
        move[0] = randint(0, 11)
        if move[0] < 6:
          move[1] = randint(0, 2) * 2
        else:
          move[1] = randint(0, 5) * 2
        if move[0] % 2 == 1:
          move[1] = move[1] + 1

    return move

  def chooseSinkMove(self):
    move = self._possibleTargets.pop(0)
    return move

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
