import os, math
import numpy as np
from equipmentdiagnostics.nn.nn import NN
from scipy.stats import norm, kurtosis
import matplotlib.pyplot as plt
from detect_delimiter import detect

def criticalresource(rur):
    for i in range(round(len(rur) * 0.05)):
        if rur[len(rur) - 1 - i] < 0.1:
            return True
    return False

def bulildTrend(rur):
    h = (rur[-1] - rur[round(len(rur) * 0.95)]) / round(len(rur) * 0.05)
    trend = [rur[-1]]
    count = 0
    if h == 0:
        print('аа че делать')

    if h < 0:
        while trend[-1] > 0.0:
            trend.append(trend[-1] + h)
            count+=1

    if h > 0:
        while trend[-1] < 1.0:
            trend.append(trend[-1] + h)
            count+=1

    return trend, count, h

def getdelimiter(file):
    f = open(file)
    line = f.readline()
    f.close()
    delimiter = detect(line)
    return delimiter


class EDiag:
    name = ''
    files = []
    path = ''
    Vector = []
    bearings = 0
    sensors = 0
    def __init__(self, p, b, s):
        self.name = p
        self.bearings = b
        self.sensors = s
        #load db data
        #load Vector from DB
    #Метод загрузки данных. На вход принимает self - ссылку на самого себя, р - путь до файла
    def loaddata(self, p):
        self.path = p
        if os.path.isdir(p):
            self.files = [f'{p}/{x}' for x in  os.listdir(p)]
            self.files.sort()
        elif os.path.isfile(p):
            self.files = [p]
        else:
            print("Специальный файл, либо не существует" )
            return False

        return True

    def checkdata(self):
        if len(self.files) == 0:
            print('Нечего проверять')
            return False

        if self.sensors * self.bearings == 1:
            return True
        file = self.files[0]
        f = open(file)
        line = f.readline()
        f.close()
        delimiter = detect(line)
        if not delimiter:
            return False
        #print(file)
        #line = np.genfromtxt(file, delimiter = '\t')[0]

        if len(line.split(delimiter)) < int(self.bearings * self.sensors):
            return False
        else:
            return True

    #Метод подготовки данных для обчуния нейронной сети. В качестве параметров: self - путь для файлов с показаниями
    def preparation(self):
        data = []
        num = input('По номеру какого подшипника/сенсора строить?\n: ')
        try:
            num = int(num)-1
        except ValueError:
            print('Введено не число')
            return
        if num < 0:
            print('Введено не положительное число!')
            return

        for i, file in enumerate(self.files):
            delim = getdelimiter(file)
            if delim:
                FILE = np.genfromtxt(file, delimiter = delim)
                d = self.markup(FILE, num)
                if len(d) == 0:
                    print('Проверьте данные!')
                    return
                data.append(d)
                print(f'Загружен файл {i+1}/{len(self.files)}', end = '\r')
        print(f'Загржуно {len(self.files)} файлов!           ')

        plt.plot(data)
        plt.legend(['KURT', 'VARIANCE', 'RMS', 'SF', 'PvT', 'CF'])
        plt.savefig('reference.png', dpi = 300)
        print(f'График построен!\nfile://{os.path.abspath("reference.png")}')
        data = np.array([v / np.linalg.norm(v) for v in data])
        g1 = input('Хорошо до: ')
        s1 = input('Начало: ')
        try:
            g1 = int(g1)
            s1 = int(s1)
        except ValueError:
            print('Введены не числа!')
            return

        if g1 >= s1:
            print('Хорошо должно быть до начала!') ## TODO: исправить
            return
        if g1 < 0 or s1 < 0:
            print('Введены отрицательные числа!')
            return

        try:
            well = [data[int((int(s1) - int(g1)) / 2)], data[int((int(s1) - int(g1)) / 2)], data[int(g1)]]
        except IndexError:
            print('Попытка указать на несуществующие файлы')
            return

        tdata = np.concatenate((well, data[int(s1):]))
        tout = np.concatenate((np.full(3, 1.0), np.linspace(1, 0, len(tdata) - 3)))
        print('Обучение...')
        print(f'Кол-во точек для обучения: {len(tdata)}')
        n = NN()
        n.learn(tdata, tout)
        n.save(f'{os.path.expanduser("~")}/.edconf/model')



    #Метод вычисления признаков для нейронной сети. В качестве параметров: FILE - файл с текущими показаниями, self - ссылка на самого себя. Возвращает вектор признаков.
    def markup(self, FILE, b):
        #FILE = np.genfromtxt(f'{self.path}/{file}', delimiter = '\t')
        if b > FILE.shape[1]:
            print('Попытка указать на несуществующий поток')
            return []
        n = len(FILE[:, b])
        x = np.mean(FILE[:, b])
        VARIANCE = np.var(FILE[:,b])
        RMS = np.sqrt(np.mean(np.square(FILE[:,b])))
        KURT = kurtosis(FILE[:,b])
        SF = RMS / ((sum(np.absolute(FILE[:, b]))) / n)
        PvT = max(np.absolute(FILE[:, b]))
        CF = PvT / RMS
        vect = np.array([KURT, VARIANCE, RMS, SF, PvT, CF])
        return vect

    def markupfrompathnorm(self, file, b):
        deli = getdelimiter(file)
        if self.sensors * self.bearings == 1:
            deli = ' '
        if deli:
            if self.sensors * self.bearings > 1:
                FILE = np.genfromtxt(file, delimiter = deli)
                vect = self.markup(FILE, b)
                return vect / np.linalg.norm(vect)
            else:
                FILE = np.array([[m] for m in np.genfromtxt(file, delimiter = deli)])
                vect = self.markup(FILE, b)
                return vect / np.linalg.norm(vect)
        else:
            print('No delimiter!')
            return None
        #return n.predict([list(vect)])
    #Метод определения остаточного ресурса. На вход получает self - ссылку на самого себя, vect - вектор признаков. Возвращает численное значение остаточного ресурса
    def remainingresource(self, num = 0):

        if not os.path.exists(f'{os.path.expanduser("~")}/.edconf/model'):
            print('Отсутсвует модель!\nИспользуйте help reference')
            return []

        n = NN(f'{os.path.expanduser("~")}/.edconf/model')

        if not self.checkdata():
            return []

        pdata = []
        for i, file in enumerate(self.files):
            d = self.markupfrompathnorm(file, num)
            if len(d) == 0:
                print('Проверьте данные!')
                return None
            pdata.append(d)
            print(f'Загружен файл {i+1}/{len(self.files)}', end = '\r')
        print(f'Загружено {len(self.files)} файлов!            ')
        return n.predict(np.array(pdata))
