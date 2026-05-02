"""
Loopless Slant Game Tree Search Project

This program implements a small two-player zero-sum Loopless Slant game.
The human player places '/' symbols, while the computer-controlled AI places
'\\' symbols. The AI chooses moves with minimax search and alpha-beta pruning.
"""

import copy
import time
import random


# Positive and negative infinity are used as starting values for minimax.
positiveInfinity = float('inf')
negativeInfinity = float('-inf')


class intersect():
    """
    Represents one intersection point on the board.

    Each intersection may contain a scoring number. A value such as -1 is used
    for intersections that do not award points. Once a player receives points
    from an intersection, that intersection is marked so it cannot be scored
    again later in the game.
    """

    def __init__(self, count):
        # Number of diagonal lines required around this intersection to score.
        self.count = count

        # Tracks whether this intersection has already awarded points.
        self.receivedPoint = False

        # Stores which player received the points: "MIN", "MAX", or None.
        self.pointReceiver = None

    def __str__(self):
        # Used when printing the internal intersection objects for debugging.
        return str("|  ") + str(self.count) + " " + str(self.receivedPoint) + " " + str(self.pointReceiver) + str("  |")


class State():
    """
    Stores a complete snapshot of the current game state.

    A state contains the board grid, the scoring intersections, the move that
    produced the state, the parent state, whose turn produced the state, and
    the number of empty cells remaining.
    """

    def __init__(self, intersects, currentGrid, currenti, currentj, parent_state, turnOf, m) -> None:
        # Current scoring intersections and their already-scored status.
        self.intersects = intersects

        # Current m x m board. Empty cells contain '-', human moves contain '/',
        # and AI moves contain '\\'.
        self.currentGrid = currentGrid

        # Cell coordinates of the move that led to this state.
        self.currenti = currenti
        self.currentj = currentj

        # Link to the previous state, useful for tracing the game tree.
        self.parent_state = parent_state

        # Player that created this state: "MIN" for human, "MAX" for AI.
        self.turnOf = turnOf

        # Board size. The playable grid is m x m and intersections are (m+1) x (m+1).
        self.m = m

        # Calculate newly earned points immediately after the move is applied.
        self.pointsReceived = self.calculatePoints()

        # Count how many empty cells remain so terminal states are easy to detect.
        self.emptyCellCount = 0
        for i in range(0, len(self.currentGrid)):
            for j in range(0, len(self.currentGrid[0])):
                if self.currentGrid[i][j] == "-":
                    self.emptyCellCount += 1

    def print_grid_snapshot(self):
        """Prints only the playable grid, without the intersection numbers."""
        for i in range(0, len(self.currentGrid)):
            for j in range(0, len(self.currentGrid[0])):
                print(self.currentGrid[i][j], end=" ")
            print()

    def calculatePoints(self):
        """
        Checks all intersections and awards points for newly completed circles.

        For each intersection, the method counts how many diagonal lines touch
        it from the four neighboring cells. If the count matches the number on
        the intersection and that intersection has not been scored before, the
        current player receives those points.
        """
        totalPoints = 0

        for i in range(0, len(self.intersects)):
            for j in range(0, len(self.intersects)):
                # Skip intersections that have already awarded points.
                if self.intersects[i][j].receivedPoint == False:
                    currentCount = 0

                    # Check the down-left neighboring cell.
                    # A '/' in that cell touches the current intersection.
                    if i + 1 <= m and j - 1 >= 0:
                        if self.currentGrid[i][j - 1] == "/":
                            currentCount += 1

                    # Check the down-right neighboring cell.
                    # A '\\' in that cell touches the current intersection.
                    if i + 1 <= m and j + 1 <= m:
                        if self.currentGrid[i][j] == "\\":
                            currentCount += 1

                    # Check the up-left neighboring cell.
                    # A '\\' in that cell touches the current intersection.
                    if i - 1 >= 0 and j - 1 >= 0:
                        if self.currentGrid[i - 1][j - 1] == "\\":
                            currentCount += 1

                    # Check the up-right neighboring cell.
                    # A '/' in that cell touches the current intersection.
                    if i - 1 >= 0 and j + 1 <= m:
                        if self.currentGrid[i - 1][j] == "/":
                            currentCount += 1

                    # If the required number of touching diagonals is reached,
                    # award the intersection's points to the current player.
                    if currentCount == self.intersects[i][j].count:
                        totalPoints += currentCount
                        self.intersects[i][j].receivedPoint = True
                        self.intersects[i][j].pointReceiver = self.turnOf

        return totalPoints


def lookLikeAiIsWeak():
    """
    Adds a small artificial delay before the AI move is shown.

    This does not affect the search result. It only makes the command-line game
    feel more interactive by printing a thinking animation.
    """
    print("AI HAS NOW STARTED THINKING ABOUT ITS OWN MOVE.")
    totalThinkTime = random.randint(1, 5)
    for i in range(0, totalThinkTime):
        print("STILL THINKING...")
        time.sleep(1)

    print("Finally found it")


def printGrid(currentGrid):
    """Prints a simple 2D grid or list of objects row by row."""
    for i in range(0, len(currentGrid)):
        for j in range(0, len(currentGrid[0])):
            print(currentGrid[i][j], end="")
        print()


def printBoard(intersects, currentGrid):
    """
    Prints the full board with intersection numbers and playable cells.

    Empty cells are displayed with their selectable cell number so the player
    knows which number to type for the next move.
    """
    for i in range(0, len(intersects)):
        # Print one row of intersection values.
        for j in range(0, len(intersects[0])):
            if j != len(intersects[0]) - 1:
                print(intersects[i][j].count, " --- ", end="")
            else:
                print(intersects[i][j].count)

        # Between two intersection rows, print the playable cells.
        if i != len(intersects) - 1:
            for j in range(0, len(intersects[0])):
                if j != len(intersects[0]) - 1:
                    # Show the existing move if the cell is already filled.
                    if currentGrid[i][j] != "-":
                        print("|  ", currentGrid[i][j], "  ", end="")
                    # Otherwise show the cell number the user can choose.
                    else:
                        print("|  ", cellNumbers[(i, j)], "  ", end="")
                else:
                    # Right-side border spacing for the printed board.
                    print("|       ", end="")
            print()


def createIntersects(initialIntersects, m):
    """
    Converts raw intersection numbers into intersect objects.

    The input is a (m+1) x (m+1) matrix of integers. Each integer becomes an
    intersect object so the program can store both the scoring number and
    whether that intersection has already been scored.
    """
    gridIntersects = [[0] * (m + 1) for _ in range((m + 1))]

    for i in range(0, len(initialIntersects)):
        for j in range(0, len(initialIntersects[0])):
            currentCount = initialIntersects[i][j]

            # Prints the loaded intersection values as a setup trace.
            print(currentCount)

            gridIntersects[i][j] = intersect(currentCount)

    return gridIntersects


def calculatePayOff(currentIntersects):
    """
    Calculates the minimax payoff from the scored intersections.

    The AI is the maximizing player, and the human is the minimizing player.
    Therefore, payoff = AI points - human points.
    """
    minPoints = 0
    maxPoints = 0

    for i in range(0, len(currentIntersects)):
        for j in range(0, len(currentIntersects[0])):
            # Only intersections that already awarded points affect the payoff.
            if currentIntersects[i][j].receivedPoint == True:
                # Points received by the AI / maximizing player.
                if currentIntersects[i][j].pointReceiver == "MAX":
                    maxPoints += currentIntersects[i][j].count
                # Points received by the human / minimizing player.
                else:
                    minPoints += currentIntersects[i][j].count

    payOff = maxPoints - minPoints
    return payOff


def findMove(currentState: State, alpha, beta, maximizingPlayer: bool, depth):
    """
    Runs minimax search with alpha-beta pruning to choose the next move.

    Parameters:
    - currentState: current game state to expand
    - alpha: best guaranteed value for MAX found so far
    - beta: best guaranteed value for MIN found so far
    - maximizingPlayer: True when the AI is choosing a '\\' move
    - depth: maximum remaining search depth

    Returns:
    - evaluated payoff
    - selected successor grid
    - row index of the selected move
    - column index of the selected move
    """

    # Stop searching when the depth limit is reached or the board is full.
    if depth == 0 or currentState.emptyCellCount == 0:
        currentPayOff = calculatePayOff(currentState.intersects)
        return currentPayOff, currentState, -1, -1

    # MAX player: the AI places '\\' and tries to maximize the payoff.
    if maximizingPlayer:
        maxEva = negativeInfinity
        currentMovei = -1
        currentMovej = -1

        # Try every available empty cell as the AI's next move.
        for i in range(0, len(currentState.currentGrid)):
            for j in range(0, len(currentState.currentGrid[0])):
                if currentState.currentGrid[i][j] == "-":
                    currentMovei = i
                    currentMovej = j

                    # Copy the board so the simulated move does not affect
                    # sibling branches in the game tree.
                    newGrid = copy.deepcopy(currentState.currentGrid)
                    newGrid[i][j] = "\\"

                    # Copy the intersections because calculatePoints mutates
                    # their scored/not-scored state.
                    intersectCopy = copy.deepcopy(currentState.intersects)

                    # Create the successor state after the AI move.
                    newSuccesor = State(
                        intersectCopy,
                        newGrid,
                        currentMovei,
                        currentMovej,
                        currentState,
                        "MAX",
                        currentState.m
                    )

                    # After MAX moves, MIN gets the next turn.
                    eva, currentMove, _, _ = findMove(newSuccesor, alpha, beta, False, depth - 1)

                    # Keep the move that gives MAX the best evaluation.
                    previousMax = maxEva
                    maxEva = max(maxEva, eva)
                    if previousMax != maxEva:
                        maxGrid = copy.deepcopy(newGrid)
                        maxI = currentMovei
                        maxJ = currentMovej

                    # Update alpha with the best value MAX can force so far.
                    alpha = max(alpha, maxEva)

                    # Prune the rest of this branch when MIN already has a
                    # better option elsewhere.
                    if beta <= alpha:
                        break

        return maxEva, maxGrid, maxI, maxJ

    # MIN player: the human places '/' and tries to minimize the payoff.
    else:
        minEva = positiveInfinity
        currentMovei = -1
        currentMovej = -1

        # Try every available empty cell as the human's next move.
        for i in range(0, len(currentState.currentGrid)):
            for j in range(0, len(currentState.currentGrid[0])):
                if currentState.currentGrid[i][j] == "-":
                    currentMovei = i
                    currentMovej = j

                    # Copy the board before applying the simulated human move.
                    newGrid = copy.deepcopy(currentState.currentGrid)
                    newGrid[i][j] = "/"

                    # Copy intersections so scoring changes stay local to this branch.
                    intersectCopy = copy.deepcopy(currentState.intersects)

                    # Create the successor state after the human move.
                    newSuccesor = State(
                        intersectCopy,
                        newGrid,
                        currentMovei,
                        currentMovej,
                        currentState,
                        "MIN",
                        currentState.m
                    )

                    # After MIN moves, MAX gets the next turn.
                    eva, currentMove, _, _ = findMove(newSuccesor, alpha, beta, True, depth - 1)

                    # Keep the move that gives MIN the lowest evaluation.
                    previousMin = minEva
                    minEva = min(minEva, eva)
                    if previousMin != minEva:
                        minGrid = copy.deepcopy(newGrid)
                        minI = currentMovei
                        minJ = currentMovej

                    # Update beta with the best value MIN can force so far.
                    beta = min(beta, eva)

                    # Prune the rest of this branch when MAX already has a
                    # better option elsewhere.
                    if beta <= alpha:
                        break

        return minEva, minGrid, minI, minJ


# Board size. The playable board is m x m, while intersections are (m+1) x (m+1).
m = 2

# Intersection scoring layout for the 2 x 2 sample board.
# -1 represents an intersection with no scoring circle.
currentIntersects = [
    [1, -1, 1],
    [-1, 2, -1],
    [-1, -1, 1]
]

# Start with an empty playable grid.
initialGrid = [["-"] * (m) for _ in range((m))]

# Convert raw intersection numbers into objects that can track scoring state.
gridIntersects = createIntersects(currentIntersects, m)

# Create user-facing cell numbers for the command-line interface.
cellNumbers = {}
count = 1
for i in range(0, m):
    for j in range(0, m):
        cellNumbers[(i, j)] = count
        count += 1

# Print initial internal setup information and the starting board.
printGrid(gridIntersects)
printGrid(initialGrid)
printBoard(gridIntersects, initialGrid)

# Rebuild the cell number mapping used to convert user input into coordinates.
cellNumbers = {}
count = 1
for i in range(0, m):
    for j in range(0, m):
        cellNumbers[(i, j)] = count
        count += 1

# Example coordinate lookup. These variables are not needed later, but show how
# a selected cell number maps to a row-column position.
cellPos = list(cellNumbers.values()).index(2)
cell = list(cellNumbers.keys())[cellPos]

# Create the initial game state before any player has moved.
initialState = State(gridIntersects, initialGrid, None, None, None, None, m)
currentGameState = initialState

# Turn flags used by the main game loop.
aiTurn = False
playerTurn = True

# Running scores shown to the user after each move.
player1Points = 0
player2Points = 0

print("WELCOME TO THE GAME")
print("YOU WILL HAVE / TO FILL THE BOARD")
print("THE GAME WILL NOW START")
time.sleep(1)

# Continue until every cell in the board has been filled.
while currentGameState.emptyCellCount != 0:
    # Human turn: the human is the MIN player and places '/'.
    if playerTurn:
        print("Here is the current game board")
        printBoard(currentGameState.intersects, currentGameState.currentGrid)

        # Read the selected cell number from the command line.
        selectedCell = input("Please select a cell to fill: ")

        # Convert the chosen cell number into row-column coordinates.
        cellPos = list(cellNumbers.values()).index(int(selectedCell))
        cell = list(cellNumbers.keys())[cellPos]
        playerMovei = cell[0]
        playerMovej = cell[1]

        # Apply the human move to a copied grid.
        newGrid = copy.deepcopy(currentGameState.currentGrid)
        newGrid[playerMovei][playerMovej] = "/"

        # Create the new game state and calculate any points earned this turn.
        currentGameState = State(
            currentGameState.intersects,
            newGrid,
            playerMovei,
            playerMovej,
            currentGameState,
            "MIN",
            m
        )

        # In this zero-sum game, points gained by one player are subtracted
        # from the opponent.
        player1Points += currentGameState.pointsReceived
        player2Points -= currentGameState.pointsReceived

        # Show the result of the human move.
        if currentGameState.pointsReceived == 0:
            print("No one has received points this round")
        else:
            print("You have received ", currentGameState.pointsReceived, " points\n",
                  "AI has lost ", currentGameState.pointsReceived, " points")

        print("Total points\n", "You: ", player1Points, "\n", "Ai: ", player2Points)
        print("Here is the resulting game board")
        printBoard(currentGameState.intersects, currentGameState.currentGrid)

        # Switch to the AI turn.
        aiTurn = True
        playerTurn = False
        print("\n\n")
        time.sleep(3)

    # AI turn: the AI is the MAX player and places '\\'.
    else:
        # Search on a deep copy so simulated future states do not alter the
        # real game state before the selected move is applied.
        copyOfGameState = copy.deepcopy(currentGameState)

        # Choose the AI move using minimax with alpha-beta pruning.
        point, move, aiMovei, aiMovej = findMove(
            copyOfGameState,
            negativeInfinity,
            positiveInfinity,
            True,
            6
        )

        # Apply the selected AI move to the real game state.
        currentGameState = State(
            currentGameState.intersects,
            move,
            aiMovei,
            aiMovej,
            currentGameState,
            "MAX",
            m
        )

        lookLikeAiIsWeak()

        # Update zero-sum scores after the AI move.
        player2Points += currentGameState.pointsReceived
        player1Points -= currentGameState.pointsReceived

        print("AI has filled the cell ", str(cellNumbers[(aiMovei, aiMovej)]), " with \\")
        if currentGameState.pointsReceived == 0:
            print("No one has received points this round")
        else:
            print("AI has received ", currentGameState.pointsReceived, " points\n",
                  "You have lost ", currentGameState.pointsReceived, " points")

        print("Total points\n", "You: ", player1Points, "\n", "Ai: ", player2Points)
        print("Here is the resulting game board")
        printBoard(currentGameState.intersects, currentGameState.currentGrid)

        # Switch back to the human turn.
        aiTurn = False
        playerTurn = True
        print("\n\n")


# Game-over summary.
print("\n\n")
print("The game has finished")
print("Here are the final points")
print("Total points\n", "You: ", player1Points, "\n", "Ai: ", player2Points)

if player1Points > player2Points:
    print("You have won the game")
elif player2Points > player1Points:
    print("Ai has won the game")
else:
    print("The game has resulted in draw")
