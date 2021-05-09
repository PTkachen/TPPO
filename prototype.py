#!/usr/bin/python3

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

import cmd, sys, getpass, datetime, os, json#, dbClass
print('Загрузка TensorFlow...')
from ediag import *
import matplotlib.pyplot as plt
from EDDB import *

if os.path.exists('db_config.json'):
    with open('db_config.json') as json_file:
        db = json.load(json_file)
else:
    ans = input('Нет файла db_config.json!\nСоздать y/n?')
    if ans == 'y':
        db_config()
        with open('db_config.json') as json_file:
            db = json.load(json_file)
    else:
        print('No db_config')
        quit(1)

print('Подключение к базе данных')
database = edDB()
database.connectToDB(db['Host'], db['UserName'], db['Password'], db['DBName'])
if not database.checkTableExists('Trend'):
    print(f'Таблица {db["DBName"]}.Trend не существует!\nСоздание...')
    database.CreateTrendTable()

if not database.checkTableExists('Projects'):
    print(f'Таблица {db["DBName"]}.Projects не существует!\nСоздание...')
    database.CreateProjectsTable()
#else:
    #database.quickFix()

def printarray(arr):
    for i, a in enumerate(arr):
        print(f'{i+1}) {a}')

class EDiagShell(cmd.Cmd):
    doc_header = 'Доступные команды, чтобы посмотреть описание команды используйте help <команда>'
    prompt = 'ediag> '
    project = None
    username = getpass.getuser()
    listp = database.SelectProjectsTable()
    intro = f'Добро пожаловать в equipmentdiagnostics {username}!'

    def do_quit(self, arg):
        'завершить equipmentdiagnostics'
        ans = input("Вы действительно хотите покинуть equipmentdiagnostics? y/n: ")
        if ans == 'y':
            print(f'Досвидания {self.username}')
            database.CloseConnecton()
            return True

    def do_createp(self, arg):
        'Создать проект \nПример: ediag> createp <имя проекта>'
        if arg:
            if arg in self.listp:
                print(f'{arg} уже существует!')
            else:
                #self.listp.append(arg)
                database.insert_project_stats(arg, 1, 1, '1.0')
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
        'Загрузить проект'
        if arg:
            if arg in self.listp:
                self.prompt = f'{arg}@ediag> '
                self.project = EDiag(arg)
                if database.dataexists(arg):
                    print(f'Остаточный ресурс: {round(database.get_lastrur(arg) * 100, 1)}%')
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
        "Загрузить датасет"
        if arg or self.project:
            if self.project == None:
                print('Вы не в проекте')
            else:
                args = arg.split(' ')
                if self.project.loaddata(args[-1]):
                    rur = self.project.remainingresource(os.path.abspath(arg))
                    if True:
                        print(f'Остаточный ресурс {round(rur[-1][0] * 100, 1)}%')
                        if rur[-1][0] <= rur[0][0]:
                            print('Подшипник изнашивается')
                        else:
                            print('Подшипник обкатывается')

                        print(f'Запись в базу данных {database.dbname}!')
                        database.insert_dots([(self.project.name, str(r[0])) for r in rur])
                        database.update_project(self.project.name, rur[-1][0])
                        #print(f'{bcolors.WARNING}!ВНИМАНИЕ! РЕЗКОЕ ИЗМЕНЕНИЕ ТРЕНДА !ВНИМАНИЕ!{bcolors.ENDC}')
                        #print([r[0][0] for r in rur])
        else:
            print('Укажите путь!')

    def do_trend(self, arg):
        'Постоение графика тренда'
        if self.project == None:
            print('Вы не в проекте')
        else:
            mes = np.array(database.get_dots(self.project.name))
            if len(mes) <= 0:
                print('Нет данных для построения')
            else:
                print('Построение графика...')
                plt.clf()
                plt.plot(mes)
                plt.legend(['Остатончный ресурс'])
                if arg:
                    img = f'{os.getcwd()}/{arg}.png'
                    plt.savefig(img, dpi = 300)
                    print(f'График стренда построен!\nfile://{img}')
                else:
                    img = f'{os.getcwd()}/{datetime.date.today()}.png'
                    plt.savefig(img, dpi = 300)
                    print(f'График стренда построен!\nfile://{img}')

    def do_removep(self, arg):
        'Удалить проект'
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
        "Сменить модель"
        if arg:
            if self.project == None:
                print('Вы не в проекте')
            else:
                if self.project.loaddata(arg):
                    self.project.preparation()
        else:
            print('Укажите путь!')

    def do_configdb(self, arg):
        db_config()
        #database.CloseConnecton()
        #print('Reconnecting...')
        #database = edDB()
        #database.connectToDB(db['Host'], db['UserName'], db['Password'], db['DBName'])

if __name__ == '__main__':
    EDiagShell().cmdloop()
