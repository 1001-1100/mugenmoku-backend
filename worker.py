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
    recv_addr = 'tcp://'+ip+':'+recv_port
    send_addr = 'tcp://'+ip+':'+send_port
    workerID = int(time.time() % 100_000)
    # receive work
    consumer_receiver = context.socket(zmq.REQ)
    consumer_receiver.connect(recv_addr)
    # send work
    consumer_sender = context.socket(zmq.PUSH)
    consumer_sender.connect(send_addr)
    print('Worker',workerID,'started!')
    
    while True:
        print("Sending request...")
        consumer_receiver.send_string(str(workerID))
        work = consumer_receiver.recv_json()
        print("Received work!")
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
        result = {'workerid':workerID,'state':state.tolist(), 'turn':turn, 'depth':depth, 'move':move, 'score':score}
        print("Finished work!")
        print("Attempting to send...")
        consumer_sender.send_json(result)
        print("Work sent!")

worker()
