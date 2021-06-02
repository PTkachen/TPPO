#!/usr/bin/python3

import cmd, sys, getpass, datetime, os, json#, dbClass

if not os.path.dirname(os.path.split(sys.path[0])[0]) in sys.path:
	sys.path.append(os.path.split(sys.path[0])[0])

print('Загрузка TensorFlow...')
from equipmentdiagnostics.ediag.ediag import *
import matplotlib.pyplot as plt
from equipmentdiagnostics.EDDB.EDDB import *
from scipy.signal import savgol_filter

def main():
    class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKCYAN = '\033[96m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

    colors = [bcolors.HEADER,
              bcolors.OKGREEN,
              bcolors.OKCYAN,
              bcolors.WARNING,
              bcolors.OKBLUE]
    art = r'''                   _                            _
                  (_)                          | |
   ___  __ _ _   _ _ _ __  _ __ ___   ___ _ __ | |_
  / _ \/ _` | | | | | '_ \| '_ ` _ \ / _ \ '_ \| __|
 |  __/ (_| | |_| | | |_) | | | | | |  __/ | | | |_
  \___|\__, |\__,_|_| .__/|_| |_| |_|\___|_| |_|\__|
     | (_)| |       | |              | | (_)
   __| |_ |_| _  __ |_| __   ___  ___| |_ _  ___ ___
  / _` | |/ _` |/ _` | '_ \ / _ \/ __| __| |/ __/ __|
 | (_| | | (_| | (_| | | | | (_) \__ \ |_| | (__\__ \
  \__,_|_|\__,_|\__, |_| |_|\___/|___/\__|_|\___|___/
                 __/ |
                |___/                                '''

    home = os.path.expanduser('~')
    if not os.path.exists(f'{home}/.edconf'):
    	print(f'Создание {home}/.edconf')
    	os.mkdir(f'{home}/.edconf')

    db = loadconfig()

    print('Подключение к базе данных')
    database = edDB(db['Host'], db['UserName'], db['Password'], db['DBName'])


    if not database.checkTableExists('Trend'):
        print(f'Таблица {db["DBName"]}.Trend не существует!\nСоздание...')
        database.CreateTrendTable()

    if not database.checkTableExists('Projects'):
        print(f'Таблица {db["DBName"]}.Projects не существует!\nСоздание...')
        database.CreateProjectsTable()

    def printarray(arr):
        for i, a in enumerate(arr):
            print(f'{i+1}) {a}')

    import random
    ###############################################################################################################
    class EDiagShell(cmd.Cmd):
        doc_header = 'Доступные команды, чтобы посмотреть описание команды используйте help <команда>'
        prompt = 'ediag> '
        project = None
        username = getpass.getuser()
        listp = database.SelectProjectsTable()
        intro = colors[random.randint(0, random.randint(0, len(colors) - 1))] + art + bcolors.ENDC + f'\nДобро пожаловать в equipmentdiagnostics {username}!'

        def do_quit(self, arg):
            'завершить equipmentdiagnostics'
            ans = input("Вы действительно хотите покинуть equipmentdiagnostics? y/n: ")
            if ans == 'y':
                print(f'Досвидания {self.username}')
                database.CloseConnecton()
                return True

        def do_createp(self, arg):
            'Создать проект \nПример: createp <имя проекта>'
            if arg:
                if arg in self.listp:
                    print(f'{arg} уже существует!')
                else:
                    b = input('Кол-во подшипников: ')
                    s = input('Кол-во сенсоров на один подшипник: ')
                    try:
                        bearings = int(b)
                        sensors = int(s)
                    except ValueError:
                        print("Введены не числа!")
                        return
                    #self.listp.append(arg)
                    database.insert_project_stats(arg, bearings, sensors, '1.0', '0.0')
                    self.listp = database.SelectProjectsTable()
                    print(f'Создан проект {arg}!')
            else:
                print('Укажите имя!')

        def do_listp(self, arg):
            'Показать существующие проекты'
            if self.project == None:
                if len(self.listp) > 0:
                    printarray(self.listp)
                    #printarray(database.get_projects())
                else:
                    print('Проектов нет!')
            else:
                print('Использлвать вне проекта')

        def do_usep(self, arg):
            'Загрузить проект\nПример: usep <имя проекта>'
            if arg:
                if arg in self.listp:
                    b, s = database.get_Project_stats(arg)
                    self.prompt = f'{arg}@ediag> '
                    self.project = EDiag(arg, b, s)
                    print(f'Подшипников: {b}\nСенсоров: {s}')
                    if database.dataexists(arg):
                        print(f'Остаточный ресурс: {round(database.get_lastrur(arg) * 100, 1)}%')
                        print(f'Trend: {database.get_lasttrend(arg)}')
                        if criticalresource(database.get_dots(arg)):
                            print(f'{bcolors.WARNING}!ВНИМАНИЕ! НИЗКИЙ ОСТАТОЧНЫЙ РЕСУРС !ВНИМАНИЕ!{bcolors.ENDC}')
                    else:
                        print(f'В проекте {arg} нет данных!')
                else:
                    print(f'Проект {arg} не существует!')
            else:
                print('Укажите имя!')

        def do_quitp(self, arg):
            'Выйти из проекта'
            if self.project == None:
                print('Вы не в проекте')
            else:
                self.prompt = 'ediag> '
                print(f'Выход из проекта {self.project.name}')
                self.project = None

        def do_load(self, arg):
            "Загрузить датасет\nПример: load /путь/до/данных/"
            if arg or self.project:
                if self.project == None:
                    print('Вы не в проекте')
                else:
                    args = arg.split(' ')
                    if self.project.loaddata(args[-1]):
                        if not self.project.checkdata():
                            print('Данные не соответствуют')
                        else:
                            if self.project.bearings * self.project.sensors > 1:
                                num = input(f'По номеру какого канала строить 1:{self.project.bearings * self.project.sensors}?: ')
                                try:
                                    num = int(num)-1
                                except ValueError:
                                    print('Введено не число')
                                    return
                                if num < 0 or num > self.project.bearings * self.project.sensors -1:
                                    print('Попытка указать на несуществующий поток')
                                    return
                            else:
                                num = 0
                            rur = self.project.remainingresource(int(num))
                            if len(rur) > 0:
                                if rur[-1][0] <= rur[0][0]:
                                    print('Подшипник изнашивается')
                                else:
                                    print('Подшипник обкатывается')
                                flag = criticalresource(rur)
                                if len(rur) >= 101:
                                    rur2 = savgol_filter(rur[:,0], 101, 3)
                                else:
                                    rur2 = rur[:,0]
                                #print(f'hello{avg}')
                                print(f'Остаточный ресурс {round(rur2[-1] * 100, 1)}%')
                                if flag:
                                    print(f'{bcolors.WARNING}!ВНИМАНИЕ! НИЗКИЙ ОСТАТОЧНЫЙ РЕСУРС !ВНИМАНИЕ!{bcolors.ENDC}')

                                self.lastmes = len(rur)
                                if database.dataexists(self.project.name):
                                    print('Удаление старых данных!')
                                    database.clean(self.project.name)
                                print(f'Запись в базу данных {database.dbname}!')
                                database.insert_dots([(self.project.name, str(r[0])) for r in rur])
                                database.update_project(self.project.name, rur2[-1])
                                #print(f'{bcolors.WARNING}!ВНИМАНИЕ! РЕЗКОЕ ИЗМЕНЕНИЕ ТРЕНДА !ВНИМАНИЕ!{bcolors.ENDC}')
                                #print([r[0][0] for r in rur])
            else:
                print('Укажите путь!')

        def do_trend(self, arg):
            'Постоение графика тренда\nПример: trend <название картинки>\nЕсли не указать название то сохранится в формате <дата>.png'
            lastmes = 0
            if self.project == None:
                print('Вы не в проекте')
            else:
                mes = np.array(database.get_dots(self.project.name))
                lastmes = len(mes)
                if len(mes) <= 0:
                    print('Нет данных для построения')
                else:
                    print('Построение графика...')
                    plt.clf()
                    if len(mes) >= 101:
                        plt.plot(mes, '.')
                        smooth = savgol_filter(mes, 101, 3)
                        t, c, h = bulildTrend(smooth)
                        print(f'Trend:{h}')
                        database.update_projectTrend(self.project.name, h)
                        if c > 0 and h < 0:
                            print(f'Отсалось {c} чтений')
							
                        plt.plot(np.concatenate((smooth, t)))
                        plt.legend(['Остатончный ресурс', 'График'])
                    else:
                        plt.plot(mes, '-')
                        plt.legend(['Остаточный ресурс'])
                        print('Недостаточно точек!!')

                    if lastmes > 0:
                        plt.axvline(x=(lastmes), color='r')

                    if arg:
                        img = f'{os.getcwd()}/{arg}.png'
                        plt.savefig(img, dpi = 300)
                        print(f'График тренда построен!\nfile://{img}')
                    else:
                        img = f'{os.getcwd()}/{datetime.date.today()}.png'
                        plt.savefig(img, dpi = 300)
                        print(f'График тренда построен!\nfile://{img}')

        def do_removep(self, arg):
            'Удалить проект\nПример: removep <имя проекта>'
            if self.project == None:
                if arg and arg in self.listp:
                    a = input(f'Вы действительно хотите удалить {arg}? y/n ')
                    if a == 'y':
                        #self.listp.remove(arg)
                        database.delete_book(arg);
                        self.listp = database.SelectProjectsTable()
                        print(f'Удален проект {arg}')
                else:
                    if arg:
                        print(f'Проекта не {arg} существует!')
                    else:
                        print('Укажите имя проекта!')

        def do_reference(self, arg):
            '''Обучить новую модель по датасету
ВНИМАНИЕ! для обучения нобходима возможность посмотреть график !ВНИМАНИЕ!
Необходимо будет указать номер файла до которого все было хорошо,
номер файла с которого началась поломка
Пример: reference /путь/до/данных'''
            if arg:
                if self.project == None:
                    print('Вы не в проекте')
                else:
                    if arg == '-r' or arg == '--restore':
                        if os.path.exists('model_bc'):
                            x = input('Точно? y/n ')
                            if x == 'y':
                                print('Восстановление')
                                if os.path.exists('model'):
                                    os.rmdir('model')
                                os.rename('model_bc', 'model')
                        else:
                            print('Нет')

                    else:
                        print(f'{bcolors.WARNING}!ВНИМАНИЕ! для обучения нобходима возможность посмотреть график !ВНИМАНИЕ!{bcolors.ENDC}')
                        x = input('Продолжить? y/n ')
                        if x == 'y':
                            if self.project.loaddata(arg):
                                self.project.preparation()
            else:
                print('Укажите путь!')

        def do_configdb(self, arg):
            'Сменить данные для подключения к базе данных'
            db_config()
            database.CloseConnecton()
            print('Reconnecting...')
            database.edDB(db['Host'], db['UserName'], db['Password'], db['DBName'])


    EDiagShell().cmdloop()

if __name__ == '__main__':
    main()
