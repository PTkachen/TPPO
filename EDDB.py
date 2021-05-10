import mysql.connector, json, getpass, os
import numpy as np

# создание / обновление конфиг файла
def createconfig():
    cfg = {}
    host = cfg['Host'] = input('host: ')
    cfg['DBName'] = input('Имя базы данных: ')
    name = cfg['UserName'] = input('Имя пользователя: ')
    cfg['Password'] = getpass.getpass(f'Пароль для {name}@{host}: ')
    with open('db_config.json', 'w') as f:
        json.dump(cfg, f)

        
# проверка на правильность конфига        
def configisvalid():
    if os.path.exists('db_config.json'):
        with open('db_config.json') as json_file:
            db = json.load(json_file)
        try:
            connection = mysql.connector.connect(
                host=db['Host'],
                user=db['UserName'],
                passwd=db['Password'],
                database=db['DBName'],
                auth_plugin='mysql_native_password')
            return True
        except mysql.connector.Error as err:
            print(err)
            return False
    else:
        print('Конфиг пропал!')

# загрузка конфига        
def loadconfig():
    if os.path.exists('db_config.json'):
        while not configisvalid():
            x = input('Cofig error! y/n')
            if x == 'y':
                createconfig()
            else:
                quit(1)
        with open('db_config.json') as json_file:
            db = json.load(json_file)
            return db
    else:
        a = input('No config y/n')
        createconfig()
        return loadconfig()


class edDB:
    def __init__(self, host, user, password, db):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            passwd=password,
            database=db,
            auth_plugin='mysql_native_password')
        self.dbname = db
        self.cursor = self.connection.cursor()

    def quickFix(self):
        self.cursor.execute('''DROP TABLE IF EXISTS fix;
        CREATE TABLE fix (
        id INT NOT NULL AUTO_INCREMENT,
        PRIMARY KEY (id) );
        ''')

        self.connection.commit()

    def SelectTable(self):
        self.cursor.execute("SELECT * FROM Trend")
        myresult = self.cursor.fetchall()

    def checkTableExists(self, tablename='Trend'):
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = '{0}'
            """.format(tablename.replace('\'', '\'\'')))

        #self.SelectTable()

        if self.cursor.fetchone()[0] == 1:
            self.cursor.close()
            self.cursor = self.connection.cursor()
            return True

        return False

    def get_projects(self):
        self.cursor.execute('SELECT DISTINCT PROJNAME FROM Trend')

        projects = self.cursor.fetchall()

        self.connection.commit()

        return projects

    def insert_dots(self, dots):
        #print(self.connection, self.cursor)
        query = "INSERT INTO Trend(PROJNAME,DOT) VALUES(%s,%s)"

        self.cursor.executemany(query, dots)

        self.connection.commit()

    def get_dots(self, projname):
        query = "SELECT DOT FROM Trend WHERE PROJNAME = %s"

        self.cursor.execute(query, (projname,))

        dots = np.array([float(x[0]) for x in self.cursor.fetchall()])

        self.connection.commit()

        return dots

    def delete_book(self, book_id):
        #db_config = read_db_config()

        query = "DELETE FROM Trend WHERE PROJNAME = %s"

        self.cursor.execute(query, (book_id,))

        query = "DELETE FROM Projects WHERE PROJNAME = %s"

        self.cursor.execute(query, (book_id,))

        self.connection.commit()

    def CloseConnecton(self):
        self.cursor.close()
        self.connection.close()

    def CreateTrendTable(self):
        sql ='''CREATE TABLE Trend(
        ID INT NOT NULL AUTO_INCREMENT,
        PROJNAME CHAR(20),
        DOT CHAR(16),
        PRIMARY KEY (ID)
     )'''
        self.cursor.execute(sql)

    def CreateProjectsTable(self):
        sql ='''CREATE TABLE Projects(
        ID INT NOT NULL AUTO_INCREMENT,
        PROJNAME CHAR(20),
        BEARINGSCOUNT INT,
        SENSORSCOUNT INT,
        RUR char(16),
        PRIMARY KEY (ID)
        )'''
        self.cursor.execute(sql)

    def SelectProjectsTable(self):
        self.cursor.execute("SELECT PROJNAME FROM Projects")
        return [x[0] for x in self.cursor.fetchall()]

    def insert_project_stats(self, name, bear, sens, rur):
        query = "INSERT INTO Projects(PROJNAME,BEARINGSCOUNT,SENSORSCOUNT, RUR) VALUES(%s,%s,%s,%s)"

        self.cursor.execute(query, (name, bear, sens, rur))

        self.connection.commit()

    def dataexists(self, name):
        self.cursor.execute(
        "SELECT PROJNAME FROM Trend WHERE PROJNAME = %s GROUP BY PROJNAME",
        (name,))
        dump = self.cursor.fetchall()
        self.cursor.close()
        self.cursor = self.connection.cursor()
        #return False
        if len(dump) == 0:
            return False
        else:
            return True

    def update_project(self, name, rur):
        self.cursor.execute(f'UPDATE Projects SET RUR = %s WHERE PROJNAME = %s',
        (str(rur), name))
        self.connection.commit()

    def get_lastrur(self, name):
        self.cursor.execute('SELECT RUR FROM Projects WHERE PROJNAME = %s',
        (name,))
        return float(self.cursor.fetchone()[0])

    def get_Project_stats(self, projname):
        query = "SELECT BEARINGSCOUNT,SENSORSCOUNT FROM Trend WHERE PROJNAME = %s"

        self.cursor.execute(query, (projname,))

        dots = self.cursor.fetchall()

        self.connection.commit()
