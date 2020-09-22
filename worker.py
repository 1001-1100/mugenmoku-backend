import time
import zmq
import random
import numpy as np
from minimax import algorithm 

def worker():
    print('Starting worker...')
    ip = '112.211.34.213'
    recv_port = '5557'
    send_port = '5558'
    context = zmq.Context()
    # recieve work
    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.connect('tcp://'+ip+':'+recv_port)
    # send work
    consumer_sender = context.socket(zmq.PUSH)
    consumer_sender.connect('tcp://'+ip+':'+send_port)

    print('Worker started!')
    
    while True:
        work = consumer_receiver.recv_json()
        state = np.array(work['state'])
        turn = work['turn']
        depth = work['depth']
        move = work['move']
        height = work['height']
        width = work['width']
        length = work['length']
        if(turn):
            state[move[0]][move[1]] = 1 
        else:
            state[move[0]][move[1]] = -1 
        score = algorithm(state,not turn,depth,height,width,length)
        result = {'state':state.tolist(), 'turn':turn, 'depth':depth, 'move':move, 'score':score}
        consumer_sender.send_json(result)

worker()
