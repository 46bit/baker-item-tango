import math
import const
import base_player
from random import randint, shuffle

class Player(base_player.BasePlayer):
  def __init__(self):
    base_player.BasePlayer.__init__(self)
    self._playerName = "Baker Item Tango"
    self._playerYear = "2"
    self._version = "1.21"
    self._playerDescription = "46bit's first Blottleship player."

  DESTROYER = [[0, 0], [1, 0]]
  CRUISER = [[0, -1], [0, 0], [0, 1]]
  BATTLESHIP = [[-1, 0], [0, 0], [1, 0], [2, 0]]
  HOVERCRAFT = [[-1, 0], [0, -1], [0, 1], [0, 0], [1, -1], [1, 1]]
  CARRIER = [[0, -1], [-1, -1], [1, -1], [0, 0], [0, 1], [0, 2]]

  # Distribute the fleet onto your board
  def deployFleet(self):
    self._initBoards()

    # Deploy pieces
    self._pieces = [self.DESTROYER, self.CRUISER, self.BATTLESHIP, self.HOVERCRAFT, self.CARRIER]
    shuffle(self._pieces)
    self.deployPieces(self._pieces)

    # Setup values needed for war
    self._playedMoves = [[-1, -1]]
    self._possibleTargets = []
    self._warMode = "hunt"

    # Setup hunting
    self._huntMode = "tiling"
    self._diagonalMoves = []

    # Create hunting moves for diagonals across each 6x6 square.
    for i in range(0, 6):
      # NW square
      self._diagonalMoves.append([i, i])
      self._diagonalMoves.append([5 - i, 5 - i])

      # SW square
      self._diagonalMoves.append([i + 6, i])
      self._diagonalMoves.append([5 - i + 6, 5 - i])

      # SE square
      self._diagonalMoves.append([i + 6, i + 6])
      self._diagonalMoves.append([5 - i + 6, 5 - i + 6])

    # Fill in the gaps between square diagonals a bit, quick improvement.
    self._diagonalMoves.append([5, 3])
    self._diagonalMoves.append([6, 2])
    self._diagonalMoves.append([8, 5])
    self._diagonalMoves.append([9, 6])

    shuffle(self._diagonalMoves)

    return self._playerBoard

  def deployPieces(self, pieces):
    for piece in pieces:
      # Pick positions for piece
      for i in range(0, 1000):
        d = randint(0, 3)
        row = randint(0, 11)
        col = randint(0, 11)
        # Try to find a location with empty neighbours 500 times.
        if self.placePiece(piece, d, row, col, i < 500):
          break

  def placePiece(self, piece, direction, row, col, emptyNeighbours):
    # Work out direction multipliers for offsets of the piece's voxels
    voxelrowm = -1 if direction % 2 == 1 else 1
    voxelcolm = -1 if direction > 1 else 1

    # Determine and verify the offset and rotated position of the piece's voxels.
    piece = [[voxel[0] * voxelrowm + row, voxel[1] * voxelcolm + col] for voxel in piece]
    for voxel in piece:
      # Check each voxel's position is empty, and the neighbours if emptyNeighbours.
      # If not empty we abort, new row/col needed.
      neighbours = self.cellNeighbours(voxel) if emptyNeighbours else []
      neighbours.append(voxel)

      for neighbour in neighbours:
        # cellNeighbours only returns ones on the board so isCell won't block on
        # pieces touching the edge. Since neighbours here includes the current cell,
        # we are stopping pieces being placed outside the board.
        if not self.isCell(const.EMPTY, neighbour):
          return False

    # We've passed our tests of the location, so occupy it.
    for voxel in piece:
      self._playerBoard[voxel[0]][voxel[1]] = const.OCCUPIED

    return True

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

    self._playedMoves.append(move)
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
    is_valid = False
    if entry == const.HIT:
      is_valid = True
      Outcome = const.HIT
      self.planSinkingFire([row, col])
    elif entry == const.MISSED:
      is_valid = True
      Outcome = const.MISSED
    else:
      raise Exception("Invalid input!")
    self._opponenBoard[row][col] = Outcome

    # Set war mode depending on whether we have possible targets.
    if len(self._possibleTargets) == 0:
      self._warMode = "hunt"
    else:
      self._warMode = "sink"

  def planSinkingFire(self, coords):
    row, col = coords

    # See if it's worth hitting points N, E, S, W of hit point.
    neighbours = self.cellNeighbours([row, col])
    for neighbour in neighbours:
      # Add target to list if within bounds, not played and not already on list.
      if self.withinBounds(neighbour) and self.notPlayed(neighbour) and self.notTarget(neighbour):
        self._possibleTargets.append(neighbour)

  def getOpponentMove(self, row, col):
    if self.isCell(const.OCCUPIED, [row, col]) or self.isCell(const.HIT, [row, col]):
      self._playerBoard[row][col] = const.HIT
      result = const.HIT
    else:
      result = const.MISSED

    return result

  def withinBounds(self, coords):
    row, col = coords
    return not (row < 0 or row > 11 or col < 0 or col > 11 or (col > 5 and row < 6))

  def isCell(self, val, coords):
    row, col = coords
    return self.withinBounds(coords) and self._playerBoard[row][col] == val

  # Get the bounded NESW neighbours of a provided coordinate.
  def cellNeighbours(self, coords):
    row, col = coords

    # List NESW neighbours.
    neighbours = []
    neighbours.append([row - 1, col])
    neighbours.append([row, col + 1])
    neighbours.append([row + 1, col])
    neighbours.append([row, col - 1])

    # Only keep neighbours that are on the board.
    neighbours = [neighbour for neighbour in neighbours if self.withinBounds(neighbour)]

    return neighbours

  # Get the bounded squares in a 3x3 centred upon the provided coordinate.
  def cellLocality(self, coords):
    row, col = coords

    neighbours = []
    for i in range(-1, 2):
      for j in range(-1, 2):
        neighbours.append([row + i, col + j])

    # Only keep neighbours that are on the board.
    neighbours = [neighbour for neighbour in neighbours if self.withinBounds(neighbour)]

    return neighbours

  def notPlayed(self, coords):
    return (coords not in self._playedMoves)

  def notTarget(self, coords):
    return (coords not in self._possibleTargets)

def getPlayer():
    """ MUST NOT be changed, used to get a instance of your class."""
    return Player()
