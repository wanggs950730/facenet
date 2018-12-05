
import pymysql
from PIL import Image
from PIL import ImageTk



class Sql:
    def __init__(self, cursor, db):
        self.cursor = cursor
        self.db = db

    # def get_cursor_and_db(self, cursor, db):
    #     self.cursor = cursor
    #     self.db = db

    # execute sql operation
    def db_operation(self, sql):
        try:
            # 执行sql语句
            self.cursor.execute(sql)
            # 提交到数据库执行
            self.db.commit()
            print("commit success!")
        except:
            # 如果发生错误则回滚
            self.db.rollback()
            print("commit failed!")

    def get_photo(self,name):
        sql = "select photo_path from Employee where name = '%s'" %name
        result = []
        try:
            # 执行sql语句
            self.cursor.execute(sql)
            # 提交到数据库执行
            result = self.cursor.fetchall()
        except:
            # 如果发生错误则回滚
            self.db.rollback()
            print("commit failed!")
        load = []
        for path in result:
            path = 'photo/' + path[0]            
            img = Image.open(path)
            render = ImageTk.PhotoImage(img)
            load.append(render)
        
        return load[0]


        