import os, math
import numpy as np
from nn import NN
from scipy.stats import norm, kurtosis
import matplotlib.pyplot as plt

def criticalresource(rur):
    for i in range(round(len(rur) * 0.05)):
        if rur[len(rur) - 1 - i] < 0.1:
            return True
    return False

class EDiag:
    name = ''
    files = []
    path = ''
    Vector = []
    def __init__(self, p):
        self.name = p
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
            print("Специальный файл (socket, FIFO, device file)" )
            return False

        return True

    #Метод подготовки данных для обчуния нейронной сети. В качестве параметров: self - путь для файлов с показаниями
    def oldpreparation(self):
        NTRUE = 0 # Номер последнего файла до точки невозврата
        N = len(self.files)
        flag = 0 # Флаг для определения этапа обучения нейронной сети
        tdata = [] # Массив вопросов для обучения нейронной сети
        tout = [] # Массив ответов для нейронной сети
        startPoint = [] # Массив для значений до точки невозврата
        #x2 = []
        #nur = []
        for i, file in enumerate(self.files):
            FILE = np.genfromtxt(file, delimiter = '\t')
            vect_pr = self.markup(FILE)
            nu = np.average(FILE[:, 0])
            x = np.mean(FILE[:, 0])
            print(f'Загружен файл {i+1}/{N}', end = '\r')
                   #KURT
            # Определяем точку невозврата. Если точка найдена flag = 1
            # Пока точка не найдена, записываем во вспомогательный массив все значения
            if abs(vect_pr[0] - nu) > abs(x * 600) and flag == 0:
                flag = 1
                #print(i+1)
            #x2.append(abs(x * 500))

            #nur.append(abs(vect_pr[0] - nu))
            if flag == 0:
                startPoint.append(vect_pr / np.linalg.norm(vect_pr))


            #if abs(vect_pr[0] - nu) > 2 * x and flag == 0:
            #    flag = 1

            #print(f'{i+1}|{abs(vect_pr[2] - nu)}|{2 * x}')
            # Если точка невозврата найдена, записываем в основной массив только три значения - вопроса, для которых ответ будет 1 - эквивален 100% остаточного ресурса.
            # Изменяем значение flag = 2, последующие значения будем сразу записывать в основной массив вопросов
            if flag == 1:
                NTRUE = len(startPoint) - 1
                tdata.append(startPoint[0])
                tdata.append(startPoint[-1])
                tdata.append(startPoint[round(NTRUE / 2)])
                flag = 2
                for i in range(3):
                    tout.append(1)

            # Записываем вопросы и ответы после точки невозвратаfor i, file im
            if flag == 2:
                tdata.append(vect_pr / np.linalg.norm(vect_pr))
                tout.append(tout[-1] - (1 / (N - NTRUE - 1)))

        print(f'Загружено {N} фалов , NTRUE = {NTRUE}')
        # Обучение
        n = NN()
        #print(np.array(tout))
        #print(np.array(tdata))
        print('Обучение...')
        print(f'Кол-во точек для обучения: {len(tdata)}')
        n.learn(np.array(tdata), np.array(tout))
        n.save('model')
        #print(startPoint)
        #return (np.array(tdata), np.array(tout), x2, nur)

    def preparation(self):
        data = []
        num = int(input('По номеру какого подшипника/сенсора строить?\n: '))
        for i, file in enumerate(self.files):
            FILE = np.genfromtxt(file, delimiter = '\t')
            data.append(self.markup(FILE, num))
            print(f'Загружен файл {i+1}/{len(self.files)}', end = '\r')
        print(f'Загржуно {len(self.files)} файлов!           ')

        plt.plot(data)
        plt.legend(['KURT', 'VARIANCE', 'RMS', 'SF', 'PvT', 'CF'])
        plt.savefig('reference.png', dpi = 300)
        print(f'График построен!\nfile://{os.path.abspath("reference.png")}')
        data = np.array([v / np.linalg.norm(v) for v in data])
        g1 = input('Хорошо до: ')
        s1 = input('Начало: ')
        #s2 = input(' Конец: ')
        #s3 = input('Начало: ')
        #s4 = input(' Конец: ')
        well = [data[int((int(s1) - int(g1)) / 2)], data[int((int(s1) - int(g1)) / 2)], data[int(g1)]]
        #tdata =  np.concatenate((well, data[int(s1):int(s2)], data[int(s3):int(s4)], [data[-1]]))
        tdata = np.concatenate((well, data[int(s1):]))
        tout = np.concatenate((np.full(3, 1.0), np.linspace(1, 0, len(tdata) - 3)))
        #print(tdata)
        #print(tout)
        print('Обучение...')
        print(f'Кол-во точек для обучения: {len(tdata)}')
        n = NN()
        n.learn(tdata, tout)
        x = input('Сохранить старую модель? y/n ')
        if x == 'y':
            os.rename('model', 'model_bc')
            print('backup')
        n.save('model')



    #Метод вычисления признаков для нейронной сети. В качестве параметров: FILE - файл с текущими показаниями, self - ссылка на самого себя. Возвращает вектор признаков.
    def markup(self, FILE, b):
        #FILE = np.genfromtxt(f'{self.path}/{file}', delimiter = '\t')
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
        FILE = np.genfromtxt(file, delimiter = '\t')
        vect = self.markup(FILE, b)
        return vect / np.linalg.norm(vect)

        #return n.predict([list(vect)])
    #Метод определения остаточного ресурса. На вход получает self - ссылку на самого себя, vect - вектор признаков. Возвращает численное значение остаточного ресурса
    def remainingresource(self):
        n = NN('model')
        pdata = []
        for i, file in enumerate(self.files):
            pdata.append(self.markupfrompathnorm(file, 0))
            print(f'Загружен файл {i+1}/{len(self.files)}', end = '\r')
        print(f'Загружено {len(self.files)} файлов!            ')
        return n.predict(np.array(pdata))
