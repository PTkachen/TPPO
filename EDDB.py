import mysql.connector

def db_config(): #Создание конфиг файла
    cfg = {}
    host = cfg['Host'] = input('host: ')
    cfg['DBName'] = input('Имя базы данных: ')
    name = cfg['UserName'] = input('Имя пользователя: ')
    cfg['Password'] = getpass.getpass(f'Пароль для {name}@{host}: ')
    with open('db_config.json', 'w') as f:
        json.dump(cfg, f)

class edDB:
    def connectToDB(self, host, user, password, db):
    	self.connection = mysql.connector.connect(
        host=host,
        user=user,
        passwd=password,
        database=db,
        auth_plugin='mysql_native_password'
    	)

    	self.cursor = self.connection.cursor()


    def checkTableExists(self, tablename='Trend'):
        self.cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = '{0}'
            """.format(tablename.replace('\'', '\'\'')))

        if self.cursor.fetchone()[0] == 1:
    	   	self.cursor.close()
    	   	return True

        return False

    def insert_dots(self, dots):
        query = "INSERT INTO Trend(PROJNAME,DOT) VALUES(%s,%s)"

        self.cursor.executemany(query, dots)

        self.connection.commit()
        
    def get_dots(self, projname):
        query = "SELECT DOT FROM Trend WHERE PROJNAME = %s"

        self.cursor.execute(query, (projname,))

        dots = self.cursor.fetchall()

        self.connection.commit()

        return dots
    def delete_book(self, book_id):
        #db_config = read_db_config()

        query = "DELETE FROM Trend WHERE PROJNAME = %s"

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


    def SelectTable(self):
    	self.cursor.execute("SELECT * FROM Trend")
		myresult = self.cursor.fetchall()
