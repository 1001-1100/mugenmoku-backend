import time
# import psutil as ps
# from scipy import stats

import argparse
import csv
import subprocess

import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
# import seaborn as sns
import multiprocessing
import random

# Settings
x = 3
y = 3
length = 3
withpruning = 0 
# Gomoku Board
black = 1
blackTurn = True
white = -1
whiteTurn = False
blank = 0
depth = 0

if(depth <= 0):
    depth = float('inf')

times = []

class Board:

    def __init__(self, board, x, y, length):
        self.board = board
        self.length = length 
        self.height = y
        self.width = x 
    
    def get_board(self):
        return self.board

    def get_position(self, x, y):
        return self.board[x][y]

    def set_position(self, x, y, z):
        self.board[x][y] = z

    def get_column(self, y, x, length):
        line = np.empty(length)
        for i in range(length):
            line[i] = self.board[y+i,x]
        return line, [(y+i,x) for i in range(length)]

    def get_row(self, y, x, length):
        line = np.empty(length)
        for i in range(length):
            line[i] = self.board[y,x+i]
        return line, [(y,x+i) for i in range(length)]

    def get_diagonal_upleft_to_lowright(self, y, x, length):
        line = np.empty(length)
        for i in range(length):
            line[i] = self.board[y+i,x+i]
        return line, [(y+i,x+i) for i in range(length)]

    def get_diagonal_lowleft_to_upright(self, y, x, length):
        line = np.empty(length)
        if y < length - 1:
            raise IndexError
        for i in range(length):
            line[i] = self.board[y-i,x+i]
        return line, [(y-i,x+i) for i in range(length)]

    def check_win(self):
        for i in range(self.height):
            for j in range(self.width):
                for getter_function in (self.get_row, self.get_column, self.get_diagonal_lowleft_to_upright, self.get_diagonal_upleft_to_lowright):
                    try:
                        line, positions = getter_function(i,j,self.length)
                    except IndexError:
                        continue
                    if abs(line.sum()) == self.length:
                        return True
        return False

    def check_who_win(self):
        for i in range(self.height):
            for j in range(self.width):
                for getter_function in (self.get_row, self.get_column, self.get_diagonal_lowleft_to_upright, self.get_diagonal_upleft_to_lowright):
                    try:
                        line, positions = getter_function(i,j,self.length)
                    except IndexError:
                        continue
                    if abs(line.sum()) == self.length:
                        return line[0]

    def check_end(self):
        possibilities = np.where(self.board == 0)
        px = possibilities[0]
        py = possibilities[1]
        possibilities = np.concatenate((px,py)).reshape(-1,2,order='F')
        return len(possibilities) == 0

    def check_consecutive(self):
        sums = []
        consecutives = []
        for i in range(self.height):
            for j in range(self.width):
                for getter_function in (self.get_row, self.get_column, self.get_diagonal_lowleft_to_upright, self.get_diagonal_upleft_to_lowright):
                    try:
                        line, positions = getter_function(i,j,self.length)
                    except IndexError:
                        continue
                    if abs(line.sum()) > 0:
                        sums.append(line.sum())
                        consecutives.append([self.board[p[0]][p[1]] for p in positions])
        # return (np.array(sums), consecutives)
        return consecutives
    
    def get_possibilities(self):
        possibilities = np.where(self.board == 0)
        px = possibilities[0]
        py = possibilities[1]
        return np.concatenate((px,py)).reshape(-1,2,order='F')

def evaluate(board):
    consecutives = board.check_consecutive()
    minMaxScore = 0
    for line in consecutives:
        for i in range(1, board.length-1):
            for j in range(0, i+1):
                if([float(black)] * (i+1) == line[j:j+i+1]):
                    minMaxScore += i 
                if([float(white)] * (i+1) == line[j:j+i+1]):
                    minMaxScore -= i 
    return minMaxScore

def minimaxNoPruning(state, turn, depth):
    board = Board(state, x, y, length)

    if(turn == blackTurn):
        minMaxScore = float('-inf')
    elif(turn == whiteTurn):
        minMaxScore = float('inf')

    minMaxMove = None

    if(depth > 0 and not board.check_win() and not board.check_end()):
        moves = board.get_possibilities()
        depth -= 1
        for move in moves:
            player = black if turn else white
            state[move[0]][move[1]] = player
            score = minimaxNoPruning(np.copy(state), not turn, depth)[1]
            if(turn == blackTurn):
                if(minMaxScore <= score):
                    minMaxScore = score
                    minMaxMove = move
            elif(turn == whiteTurn):
                if(minMaxScore >= score):
                    minMaxScore = score
                    minMaxMove = move
            state[move[0]][move[1]] = blank
    else:
        if(board.check_win()):
            winner = int(board.check_who_win())
            if(winner == black):
                minMaxScore = float('inf')
            elif(winner == white):
                minMaxScore = float('-inf')
        else:
            minMaxScore = evaluate(board)
    
    return (minMaxMove, minMaxScore)

def minimax(state, turn, alpha, beta, depth):
    board = Board(state, x, y, length)

    if(turn == blackTurn):
        minMaxScore = float('-inf')
    elif(turn == whiteTurn):
        minMaxScore = float('inf')

    minMaxMove = None

    if(depth > 0 and not board.check_win() and not board.check_end()):
        moves = board.get_possibilities()
        depth -= 1
        for move in moves:
            player = black if turn else white
            state[move[0]][move[1]] = player
            score = minimax(np.copy(state), not turn, alpha, beta, depth)[1]
            if(turn == blackTurn):
                if(minMaxScore <= score):
                    minMaxScore = score
                    minMaxMove = move
                if(alpha <= score):
                    alpha = score
            elif(turn == whiteTurn):
                if(minMaxScore >= score):
                    minMaxScore = score
                    minMaxMove = move
                if(beta >= score):
                    beta = score
            state[move[0]][move[1]] = blank
            if(beta <= alpha):
                break
    else:
        if(board.check_win()):
            winner = int(board.check_who_win())
            if(winner == black):
                minMaxScore = float('inf')
            elif(winner == white):
                minMaxScore = float('-inf')
        else:
            minMaxScore = evaluate(board)
    
    return (minMaxMove, minMaxScore)

def parallelA(state, turn, depth):
    class workerThread(multiprocessing.Process):
        def __init__(self, state, move, q):
            multiprocessing.Process.__init__(self)
            self.state = state
            self.move = move
            self.q = q

        def run(self):
            state = self.state
            move = self.move
            q = self.q
            state[move[0]][move[1]] = black if turn else white 
            if(withpruning == 1):
                score = minimax(state, not turn, float('-inf'), float('inf'), depth)[1]
            if(withpruning == 0):
                score = minimaxNoPruning(state, not turn, depth)[1]
            minMaxScore = score
            minMaxMove = move 
            # Put move and score in the queue for parsing later
            q.put((minMaxScore, minMaxMove))

    board = Board(state, x, y, length)

    workers = []
    count = 0
    # Queue for keeping track of move scores
    q = multiprocessing.Queue()
    # Get possible moves (branches)
    moves = board.get_possibilities()
    for move in moves:
        # For each branch, create a process that traverses
        worker = workerThread(np.copy(state), move, q)
        count += 1
        worker.start()
        workers.append(worker)

    # Wait for all workers to be done before proceeding
    while len(workers) > 0:
        workers = [worker for worker in workers if worker.is_alive()]

    if(turn == blackTurn):
        minMaxScore = float('-inf')
    elif(turn == whiteTurn):
        minMaxScore = float('inf')
    
    minMaxMove = None
    
    # Go through the queue, determine which move has the highest score
    while(not q.empty()):
        item = q.get()
        score = item[0]
        move = item[1]
        print(score,move)
        if(turn == blackTurn):
            if(minMaxScore <= score):
                minMaxScore = score
                minMaxMove = move
        elif(turn == whiteTurn):
            if(minMaxScore >= score):
                minMaxScore = score
                minMaxMove = move

    return (minMaxMove, minMaxScore)

def algorithm(state, turn, depth, height, width, match):
    global x
    global y
    global length
    x = height
    y = width
    length = match
    print('### Game move ###')
    print(state)
    data = parallelA(state, turn, depth)
    score = data[1]
    return score