#!/usr/bin/python3

import cmd, sys, getpass, datetime, os

def printarray(arr):
    for i, a in enumerate(arr):
        print(f'{i+1}) {a}')

class EDiagShell(cmd.Cmd):
    doc_header = 'Доступные команды, чтобы посмотреть описание команды используйте help <команда>'
    prompt = 'ediag> '
    project = ''
    username = getpass.getuser()
    listp = []
    intro = f'Добро пожаловать в equipmentdiagnostics {username}!'
    #def do_echo(self, arg):
        #'аргументы выведет воот'
        #print(arg)

    def do_quit(self, arg):
        'завершить equipmentdiagnostics'
        ans = input("Вы действительно хотите покинуть equipmentdiagnostics? y/n: ")
        if ans == 'y':
            print(f'Досвидания {self.username}')
            return True

    def do_createp(self, arg):
        'Создать проект \nПример: ediag> createp <имя проекта>'
        if arg:
            self.listp.append(arg)
            print(f'Создан проект {arg}!')
        else:
            print('Укажите имя!')

    def do_listp(self, arg):
        'Показать существующие проекты'
        if self.project == '':
            if len(self.listp) > 0:
                printarray(self.listp)
            else:
                print('Проектов нет!')
        else:
            print('Использлвать вне проекта')

    def do_usep(self, arg):
        'Загрузить проект'
        if arg:
            if arg in self.listp:
                self.prompt = f'{arg}@ediag> '
                self.project = arg
                #print('Загружен файл 1024/1024')
            else:
                print(f'Проект {arg} не существует!')
        else:
            print('Укажите имя!')

    def do_quitp(self, arg):
        'Выйти из проекта'
        if self.project == '':
            print('Вы не в проекте')
        else:
            self.prompt = 'ediag> '
            print(f'Выход из проекта {self.project}')
            self.project = ''

    def do_load(self, arg):
        "Загрузить датасет"
        if arg:
            if self.project == '':
                print('Вы не в проекте')
            else:
                print(f'Загружен {arg}')
                print('Загружен файл 1024/1024')
                print('Остаточный ресурс: 56%')
                print('Подшипник изнашивается')
        else:
            print('Укажите путь!')

    def do_trend(self, arg):
        'Постоение графика тренда'
        if arg:
            print(f'График стренда построен! {os.getcwd()}/{arg}')
        else:
            print(f'График стренда построен! {os.getcwd()}/{datetime.date.today()}.png')

    def do_removep(self, arg):
        'Удалить проект'
        if self.project == '':
            if arg and arg in self.listp:
                a = input(f'Вы действительно хотите удалить {arg}? y/n ')
                if a == 'y':
                    self.listp.remove(arg)
                    print(f'Удален проект {arg}')
            else:
                if arg:
                    print(f'Проекта не {arg} существует!')
                else:
                    print('Укажите имя проекта!')

    def do_reference(self, arg):
        "Сменить модель"
        if arg:
            if self.project == '':
                print('Вы не в проекте')
            else:
                print(f'Загружен {arg}')
                print(f'Создана новая модель!')
        else:
            print('Укажите путь!')


if __name__ == '__main__':
    EDiagShell().cmdloop()
