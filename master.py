import time
import zmq
import multiprocessing
import numpy as np

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

class producer(multiprocessing.Process):
    def __init__(self, state, turn, depth, moves, height, width, length, q):
        multiprocessing.Process.__init__(self)
        self.state = state
        self.turn = turn
        self.depth = depth
        self.moves = moves
        self.height = height 
        self.width = width
        self.length = length
        self.q = q

    def run(self):
        context = zmq.Context()
        zmq_socket = context.socket(zmq.PUSH)
        zmq_socket.bind("tcp://*:5557")
        # Start your result manager and workers before you start your producers
        for move in self.moves:
            work_message = {
                'state':self.state.tolist(),
                'turn':self.turn,
                'depth':self.depth,
                'move':move.tolist(),
                'height':self.height,
                'width':self.width,
                'length':self.length,
            }
            zmq_socket.send_json(work_message)

class collector(multiprocessing.Process):
    def __init__(self, q):
        multiprocessing.Process.__init__(self)
        self.q = q

    def run(self):
        context = zmq.Context()
        results_receiver = context.socket(zmq.PULL)
        results_receiver.bind("tcp://*:5558")
        # collecter_data = {}
        while(not self.q.full()):
            result = results_receiver.recv_json()
            self.q.put(result)

        maxResult = q.get() 
        while(not q.empty()):
            result = q.get()
            if(maxResult['score'] <= result['score']):
                maxResult = result
        print(maxResult)

height = 3
width = 3
length = 3
state = np.zeros((height,width))
board = Board(state, height, width, length)
moves = board.get_possibilities()
turn = True
depth = float('inf')
q = multiprocessing.Queue(len(moves))

print("Starting collector...")
collector(q).start()

print("Starting producer...")
producer(state,turn,depth,moves,height,width,length,q).start()

