"""
this is the openration of the database

# author: ChuXiaokai
# date: 2016/3/25
"""
import MySQLdb

# ServerDatabase
# Database in server
class ServerDatabase(object):
    def __init__(self):
        self.connect()

        # self-checking
        # check for if webapp exists
        try:  # database webapp
            self.cursor.execute('CREATE DATABASE IF NOT EXISTS webapp')
            self.cursor.execute('USE webapp')
        except:
            pass  # db has existed

        try:  # table account
            self.cursor.execute('CREATE TABLE IF NOT EXISTS account(user varchar(40), passwd varchar(40), num_mcs int)')
        except:
            pass

        try:  # table docker
            self.cursor.execute('CREATE TABLE IF NOT EXISTS docker(mc_id varchar(40), user varchar(40), connect_info varchar(100), detail varchar(100))')
        except:
            pass

        try:  # source
            self.cursor.execute('CREATE TABLE IF NOT EXISTS source(source_name varchar(40), map varchar(40), shell_path varchar(100), detail varchar(100))')
        except:
            pass

        self.conn.commit()
        print("Success init database")


    def connect(self):
        """
        :return: connect to the mysql
        """
        try:
            self.conn = MySQLdb.connect(host='localhost', user='root', passwd='123456', port=3306)
            self.cursor = self.conn.cursor()
            print("Success connect to database")
        except:
            print("Failed to connect to database")

