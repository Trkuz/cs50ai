"""
Tic Tac Toe Player
"""
import icecream
import copy
import math
import numpy as np
import random
# from pympler import muppy
# all_objects = muppy.get_objects()

X = "X"
O = "O"
EMPTY = None

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):

    counter = 0
    for element in board:
        for inner in element:
            if inner is not None:
                counter += 1

    if counter == 0:
        return "X"
    else:
        if counter % 2 != 0:
            return "O"
        return "X"

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    rows = 0
    columns = 0
    possible_actions = []
    for element in board:
        for inner in element:
            if inner == None:
                possible_actions.append((rows,columns))
            columns += 1
        rows += 1
        columns = 0

    possible_actions = set(possible_actions)
    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    current_player = player(board)
    possible_moves = actions(board)
    if action not in possible_moves:
        raise Exception("You can't make that move!")

    copie = copy.deepcopy(board)

    copie[action[0]][action[1]] = current_player

    return copie

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """


    x = copy.deepcopy(board)
    y = copy.deepcopy(board)

    for i in range(0,3):
        for j in range(0,3):
            if x[i][j] != "X":
                x[i][j] = False
            else:
                x[i][j] = True


    for i in range (0,3):
        for j in range (0,3):
            if y[i][j] != "O":
                y[i][j] = False
            else:
                y[i][j] = True

    for element in x:
        if all(element):
            return "X"

    for element in y:
        if all(element):
            return "O"



    if x[0][0] == x[1][1] == x[2][2] or x[0][2] == x[1][1] == x[2][0]:
        if False not in [x[0][0],x[1][1], x[2][2]] or False not in [x[0][2],x[1][1],x[2][0]]:
            return "X"

    if y[0][0] == y[1][1] == y[2][2] or y[0][2] == y[1][1] == y[2][0]:
        if False not in [y[0][0],y[1][1], y[2][2]] or False not in [y[0][2],y[1][1],y[2][0]]:
            return "O"

    x = np.array(x)
    y = np.array(y)

    x = np.transpose(x)
    y = np.transpose(y)

    for element in x:
        if all(element):
            return "X"

    for element in y:
        if all(element):
            return "O"

    return None

def terminal(board):
    if winner(board) == "X" or winner(board) == "O":
        return True

    table = []
    for element in board:
        for inner in element:
           table.append(inner)

    if None not in table:
        return True

    return False


def utility(board):
    if winner(board) == "X":
        return 1
    if winner(board) == "O":
        return -1

    if None not in (board[0], board[1], board[2]):
        return 0


def max_value(board):
    v = -math.inf
    if terminal(board):
        return utility(board)
    for action in actions(board):
        v = max(v, min_value(result(board, action)))
    return v

def min_value(board):
    v = math.inf
    if terminal(board):
        return utility(board)
    for action in actions(board):
        v = min(v, max_value(result(board, action)))
    return v
def minimax(board):

    if terminal(board):
        return None

    if player(board) == "X":
        moves = []

        for action in actions(board):
            moves.append([min_value(result(board, action)), action])

        return sorted(moves, key=lambda x: x[0], reverse=True)[0][1]


    elif player(board) == "O":
        moves = []

        for action in actions(board):
            moves.append([max_value(result(board, action)), action])

        return sorted(moves, key=lambda x: x[0])[0][1]