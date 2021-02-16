import sys, time, logging, subprocess, shlex, os
from .verb import access as _access
from . import log as loggie
from collections import namedtuple
from multiprocessing import Process, Queue
import matplotlib.pyplot as plt
import seaborn as sb
import numpy as np

def callAccess(q, turnOnTime, null):
    os.dup2(null, sys.stdout.fileno())
    os.dup2(null, sys.stderr.fileno())

    Args = namedtuple('Args', ['host', 'port', 'time', 'every_n',
                            'tx_power', 'tari', 'session',
                            'population', 'read_words', 'write_words',
                            'count', 'mb', 'word_ptr', 'access_password','tag_filter_mask'])
    args = Args(host=['192.168.0.2'], port=5084, time=turnOnTime, every_n=10,
            tx_power=0, tari=0,
            session=2, population=3,
            read_words=56, write_words=None, count=0,
            mb=3, word_ptr=48,
            access_password=0, tag_filter_mask=None)
    logger.debug('access args: %s', args)
    _access.main(args, q)


def realtimeDrawing(q):
    count = 0

    def normalization(strList):
        strList = [int(i,16) for i in strList]
        return strList

    def update(frame):
        pass
    
    while(True):
        if not q.empty():
            dataFromReader = q.get()
            if dataFromReader =="END":
                print(f'# of count: {count}')
                exit()
            print(dataFromReader)
            count+=1





if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    loggie.init_logging()
    null = os.open(os.devnull, os.O_RDWR)
    turnOnTime = 2

    q = Queue()

    th1 = Process(target=callAccess, args=(q, turnOnTime, null))
    th1.start()
    th2 = Process(target=realtimeDrawing, args=(q,))
    th2.start()
    th1.join(turnOnTime)
    th1.kill()
    q.put("END")
    os.close(null)
    th2.join()
    q.close()
    q.join_thread()
    cmd = 'sllurp reset 192.168.0.2'
    subprocess.call(shlex.split(cmd))