#!/usr/bin/python3

import cmd, sys, getpass, datetime, os, json#, dbClass
print('Загрузка TensorFlow...')
from ediag import *
import matplotlib.pyplot as plt

if os.path.exists('db_config.json'):
    with open('db_config.json') as json_file:
        db = json.load(json_file)
else:
    ans = input('Нет файла db_config.json!\n Создать?')
    if ans == 'y':
        db_config()
    else:
        print('No db_config')
        quit(1)

from EDDB import *
print('Подключение к базе данных')
database = edDB()
database.connectToDB(db['Host'], db['UserName'], db['Password'], db['DBName'])
if not database.checkTableExists():
    print(f'Таблица {db["DBName"]}.Trend не существует!\nСоздание...')
    database.CreateTrendTable()
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
    listp = []
    intro = f'Добро пожаловать в equipmentdiagnostics {username}!'
    if os.path.exists('projects.json'):
        with open('projects.json') as json_file:
            listp = json.load(json_file)

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
            self.listp.append(arg)
            print(f'Создан проект {arg}!')
            with open('projects.json', 'w') as f:
                json.dump(self.listp, f)
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
                rur = self.project.remainingresource(os.path.abspath(arg))
                if rur != False:
                    print(f'Остаточный ресурс {round(rur[-1][0][0] * 100, 1)}%')
                    if rur[-1][0][0] < rur[0][0][0]:
                        print('Подшипник изнашивается')
                    else:
                        print('Подшипник обкатывается')

                    database.insert_dots([(self.project.name, str(r[0][0])) for r in rur])
                    #print([r[0][0] for r in rur])
        else:
            print('Укажите путь!')

    def do_trend(self, arg):
        'Постоение графика тренда'
        if self.project == None:
            print('Вы не в проекте')
        else:
            mes = np.array([m[0] for m in database.get_dots(self.project.name)])
            if len(mes) <= 0:
                print('Нет данных для построения')
            else:
                plt.clf()
                plt.plot(mes)
                plt.legend(['Остатончный ресурс'])
                if arg:
                    img = f'{os.getcwd()}/{arg}.png'
                    print(f'График стренда построен! file://{img}')
                    plt.savefig(img, dpi = 300)
                else:
                    img = f'{os.getcwd()}/{datetime.date.today()}.png'
                    print(f'График стренда построен! file://{img}')
                    plt.savefig(img, dpi = 300)

    def do_removep(self, arg):
        'Удалить проект'
        if self.project == None:
            if arg and arg in self.listp:
                a = input(f'Вы действительно хотите удалить {arg}? y/n ')
                if a == 'y':
                    self.listp.remove(arg)
                    with open('projects.json', 'w') as f:
                        json.dump(self.listp, f)
                    database.delete_book(arg);
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
                self.project.loaddata(arg)
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
