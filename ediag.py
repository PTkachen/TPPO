import os, math
import numpy as np
from nn import NN

class EDiag:
    name = ''
    files = []
    path = ''
    Vector = []
    def __init__(self, p):
        self.name = p
        #load db data
        #load Vector from DB

    def loaddata(self, p):
        self.path = p
        if os.path.isdir(p):
            self.files = os.listdir(p)
        elif os.path.isfile(p):
            self.files = [p]
        else:
            print("It is a special file (socket, FIFO, device file)" )

    def preparation(self):
        NTRUE = 0
        N = len(self.files)
        flag = False
        tdata = []
        tout = []
        for i, file in enumerate(self.files):
            FILE = np.genfromtxt(f'{self.path}/{file}', delimiter = '\t')
            vect_pr = self.markup(FILE)
            nu = np.average(FILE[:, 0])
            x = np.var(FILE[:, 0])
            print(f'loaded file {i+1}/{N}', end = '\r')
                   #KURT
            if abs(vect_pr[0] - nu) > 2 * x and not flag:
                flag = True
            if flag:
                tdata.append(vect_pr / np.linalg.norm(vect_pr))
                tout.append(1 - (i - NTRUE) / N)
            else:
                NTRUE += 1
                tdata.append(vect_pr / np.linalg.norm(vect_pr))
                tout.append(1)
        print(f'Loaded all {N} files, NTRUE = {NTRUE}')
        #тут я тип обучаю
        n = NN()
        #print(np.array(tout))
        #print(np.array(tdata))
        print('fitting model...')
        n.learn(np.array(tdata), np.array(tout))
        n.save('model')
        #return (np.array(tdata), np.array(tout))

    def markup(self, FILE):
        #FILE = np.genfromtxt(f'{self.path}/{file}', delimiter = '\t')
        n = len(FILE[:, 0])
        x = np.var(FILE[:, 0])
        VARIANCE = 1 / n * sum((FILE[:, 0] - x) ** 2)
        RMS = math.sqrt(sum(FILE[:, 0] ** 2) / n)
        KURT = sum((FILE[:, 0] - x) ** 4 ) / (n * VARIANCE ** 2) - 3
        SF = RMS / ((sum(np.absolute(FILE[:, 0]))) / n)
        PvT = max(np.absolute(FILE[:, 0]))
        CF = PvT / RMS
        v = np.array([KURT, VARIANCE, RMS, SF, PvT, CF])
        #return v / np.linalg.norm(v)
        return v

    def markupfrompathnorm(self, file):
        FILE = np.genfromtxt(f'{self.path}/{file}', delimiter = '\t')
        n = len(FILE[:, 0])
        x = np.var(FILE[:, 0])
        VARIANCE = 1 / n * sum((FILE[:, 0] - x) ** 2)
        RMS = math.sqrt(sum(FILE[:, 0] ** 2) / n)
        KURT = sum((FILE[:, 0] - x) ** 4 ) / (n * VARIANCE ** 2) - 3
        SF = RMS / ((sum(np.absolute(FILE[:, 0]))) / n)
        PvT = max(np.absolute(FILE[:, 0]))
        CF = PvT / RMS
        v = np.array([KURT, VARIANCE, RMS, SF, PvT, CF])
        return v / np.linalg.norm(v)
        #return v

    def remainingresource(self, p):
        n = NN('model')
        logs = []
        if os.path.isdir(p):
            logs = os.listdir(p)
            for i in range(len(logs)):
                logs[i] = f'{p}/{logs[i]}'
        elif os.path.isfile(p):
            logs = [p]
        else:
            print("It is a special file (socket, FIFO, device file)" )
            return False

        rur = []
        for i, log in enumerate(logs):
            print(f'Loaded file {i+1}/{len(logs)}', end = '\r')
            rur.append(n.predict([list(self.markupfrompathnorm(log))]))
        print(f'Loaded all {len(logs)} files!')
        return rur

        #return n.predict([list(vect)])
