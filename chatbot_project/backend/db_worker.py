"""
    Database Workers for connecting to different DBMS.
    Has a worker for a test SQLite database.
"""

import sqlite3
import traceback
from typing import List
from abc import ABC, abstractmethod
from contextlib import contextmanager

from models import FrameElemType, FrameElem, Frame, InitContact, ContactWithChat


class DbWorker(ABC):
    @abstractmethod
    def init_db(self):
        pass

    @abstractmethod
    def get_elem_types(self):
        pass

    @abstractmethod
    def get_dialog_frames(self):
        pass

    @abstractmethod
    def get_frame_elems(self, id_frame):
        pass

    @abstractmethod
    def get_next_frame(self, id_frame):
        pass

    @abstractmethod
    def insert_user(self, id_frame, cursor):
        pass

    @abstractmethod
    def get_no_telegram_chats(self):
        pass

    @abstractmethod
    def set_has_telegram(self, id_chat):
        pass

    @abstractmethod
    def close(self):
        pass


class SqliteDbWorker(DbWorker):
    def __init__(self):
        self.conn = sqlite3.connect('/test_db/test.db')

    @contextmanager
    def get_cursor(self, commit: bool = False) -> sqlite3.Cursor:
        cursor = self.conn.cursor()
        try:
            yield cursor
        except:
            traceback.print_exc()
        else:
            if commit:
                self.conn.commit()
        finally:
            cursor.close()

    def init_db(self) -> None:
        with self.get_cursor() as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS contact
                                          (id_contact INTEGER PRIMARY KEY AUTOINCREMENT, 
                                          first_name varchar(255), 
                                          last_name varchar(255), 
                                          email varchar(255), 
                                          phone varchar(15))
                        ''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS dialog
                                          (id_dialog INTEGER PRIMARY KEY AUTOINCREMENT, 
                                          ref_id_contact INTEGER, 
                                          create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                          has_telegram INTEGER NOT NULL CHECK (has_telegram IN (0,1)) DEFAULT 0,
                                          FOREIGN KEY(ref_id_contact) REFERENCES contact(id_contact))
                        ''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS dialog_frame_elem_type
                              (id_dialog_frame_elem_type INTEGER PRIMARY KEY AUTOINCREMENT, title varchar(255));
            ''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS dialog_frame
                              (id_dialog_frame INTEGER PRIMARY KEY AUTOINCREMENT, frame_num int, frame_message_text text);
            ''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS dialog_frame_elem
                              (id_dialog_frame_elem INTEGER PRIMARY KEY AUTOINCREMENT, 
                              ref_id_dialog_frame INTEGER,
                              ref_id_dialog_frame_elem_type INTEGER,
                              frame_elem_text varchar(255),
                              FOREIGN KEY(ref_id_dialog_frame) REFERENCES dialog_frame(id_dialog_frame),
                              FOREIGN KEY(ref_id_dialog_frame_elem_type) REFERENCES dialog_frame_elem_type (id_dialog_frame_elem_type));
            ''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS frame_transition
                              (ref_id_dialog_frame INTEGER,
                              ref_id_dialog_frame_elem INTEGER,
                              ref_id_dialog_frame_next INTEGER,
                              FOREIGN KEY(ref_id_dialog_frame) REFERENCES dialog_frame (id_dialog_frame),
                              FOREIGN KEY(ref_id_dialog_frame_elem) REFERENCES dialog_frame_elem (id_dialog_frame_elem));
            ''')

            cursor.execute('''INSERT OR REPLACE INTO dialog_frame_elem_type VALUES (1, 'button')''')
            cursor.execute('''INSERT OR REPLACE INTO dialog_frame 
                              VALUES 
                              (1, 1, 'Привіт, я EPAM бот. Ти реєструвався на наш івент "JavaScript як спосіб вирватися із сірих буднів".\nПишу дізнатися, що про нього думаєш. Але перед цим, обери, якою мовою буде зручніше спілкуватися'), 
                              (2, 2, 'Супер, погнали?'), 
                              (3, 3, 'Что тебе понравилось больше всего?'), 
                              (4, 3, 'Жаль. Может, взглянешь тогда на наши открытые позиции по JavaScript?'), 
                              (5, 4, 'Отлично, рад, что тебе зашло. Возможно, хочешь поделиться мыслями по улучшению, посоветовать спикера. А может ты хочешь сам стать спикером?'), 
                              (6, 4, 'Я понял. Спасибо за ответ. У меня в запасе есть и другая информация про EPAM'), 
                              (7, 5, 'Спасибо за твой фидбек.\nУ нас, кстати, есть открытые позиции по JavaScript сейчас, интересно обсудить?'),  
                              (8, 6, '/add_hr');
            ''')
            cursor.execute('''INSERT OR REPLACE INTO dialog_frame_elem (id_dialog_frame_elem, ref_id_dialog_frame, 
                                                                        ref_id_dialog_frame_elem_type, frame_elem_text)
                              VALUES 
                              (1, 1, 1, 'Русский'),

                              (2, 2, 1, 'Ок'),
                              (3, 2, 1, 'Давай нет'),

                              (4, 4, 1, 'Ок'),
                              (5, 4, 1, 'Сейчас не актуально'),

                              (6, 5, 1, 'Твои рекомендации'),
                              (7, 5, 1, 'Посоветовать спикера'),
                              (8, 5, 1, 'Стать спикером'),

                              (9, 7, 1, 'Да'),
                              (10, 7, 1, 'Нет');
            ''')

            cursor.execute('''DELETE FROM frame_transition''')
            cursor.execute('''INSERT OR REPLACE INTO frame_transition (ref_id_dialog_frame, ref_id_dialog_frame_elem, 
                                                                       ref_id_dialog_frame_next)
                              VALUES 
                              (1, 1, 2),
                              (2, 2, 3),
                              (2, 3, 4),
                              (3, NULL, 5),
                              (5, NULL, 7),
                              (5, 6, 7),
                              (5, 7, 8),
                              (5, 8, 8),
                              (7, 9, 8),
                              (7, 10, 8);
            ''')

            self.conn.commit()

    def get_elem_types(self) -> List[FrameElemType]:
        with self.get_cursor() as cursor:
            cursor.execute("""SELECT id_dialog_frame_elem_type,
                                    title
                             FROM   dialog_frame_elem_type
                             """)
            return [FrameElemType(id_type=i[0], title=i[1]) for i in cursor.fetchall()]

    def get_dialog_frames(self) -> List[Frame]:
        with self.get_cursor() as cursor:
            cursor.execute("""SELECT dialog_frame.id_dialog_frame,
                                     dialog_frame.frame_message_text,
                                     dialog_frame.frame_num
                         FROM   dialog_frame
                         """)
            return [Frame(id_frame=i[0], frame_message=i[1], frame_num=i[2]) for i in cursor.fetchall()]

    def get_frame_elems(self, id_frame: int) -> List[FrameElem]:
        with self.get_cursor() as cursor:
            cursor.execute("""SELECT dialog_frame_elem.id_dialog_frame_elem,
                                        dialog_frame_elem.ref_id_dialog_frame_elem_type,
                                        dialog_frame_elem.frame_elem_text,
                                        frame_transition.ref_id_dialog_frame_next
                                 FROM   dialog_frame_elem
                                 JOIN   frame_transition 
                                    ON (dialog_frame_elem.id_dialog_frame_elem = frame_transition.ref_id_dialog_frame_elem)
                                 WHERE  dialog_frame_elem.ref_id_dialog_frame = %d
                                 """ % id_frame)
            return [FrameElem(id_dialog_frame_elem=j[0],
                              type=j[1],
                              text=j[2],
                              next_frame=j[3]) for j in cursor.fetchall()]

    def get_next_frame(self, id_frame: int) -> int:
        with self.get_cursor() as cursor:
            cursor.execute("""SELECT ref_id_dialog_frame_next
                                     FROM   frame_transition
                                     WHERE  ref_id_dialog_frame = %d
                        """ % id_frame)
            res = cursor.fetchone()
            return res[0] if res else None

    @contextmanager
    def transaction(self) -> sqlite3.Cursor:
        cursor = self.conn.cursor()
        cursor.execute("begin")
        try:
            yield cursor
        except:
            traceback.print_exc()
            print("failed!")
            cursor.execute("rollback")
            raise
        else:
            cursor.execute("commit")
        finally:
            cursor.close()

    def insert_user(self, contact: InitContact, cursor: sqlite3.Cursor) -> int:
        cursor.execute("""INSERT INTO contact (first_name, last_name, phone, email)
                          VALUES ('{firstName}', '{lastName}', '{phone}', '{email}')
                          -- RETURNING id_contact
                       """.format(firstName=contact.first_name, lastName=contact.last_name,
                                  phone=contact.phone, email=contact.email))

        contact_ = cursor.lastrowid
        cursor.execute("""INSERT INTO dialog (ref_id_contact)
                                 VALUES ({idContact})
                            -- RETURNING id_dialog
                        """.format(idContact=contact_))
        dialog = cursor.lastrowid
        return dialog

    def get_no_telegram_chats(self) -> List[InitContact]:
        with self.get_cursor() as cursor:
            cursor.execute("""SELECT contact.first_name, 
                                     contact.last_name,
                                     contact.phone, 
                                     contact.email,
                                     dialog.id_dialog
                              FROM   contact
                              JOIN   dialog ON (dialog.ref_id_contact = contact.id_contact)
                              WHERE  dialog.has_telegram = 0
                           """)
            res = [ContactWithChat(first_name=i[0], last_name=i[1], phone=i[2], email=i[3], id_chat=i[4]) for i in
                   cursor.fetchall()]
            return res

    def set_has_telegram(self, id_chat) -> bool:
        res = False
        with self.get_cursor(commit=True) as cursor:
            cursor.execute("""UPDATE dialog
                              SET  has_telegram = 1
                              WHERE id_dialog = {idDialog}
                           """.format(idDialog=id_chat))
            res = cursor.lastrowid
        return bool(res)

    def close(self) -> None:
        self.conn.close()
