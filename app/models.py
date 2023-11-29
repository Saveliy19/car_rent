'''
В этом файле описано подключение к бд, а также вся работа с данными из таблиц.
'''

from werkzeug.security import generate_password_hash, check_password_hash

from app.routes import session

import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import app
from app import login

from flask_login import UserMixin

class Database(object):



    @classmethod
    def _connect_to_db(cls) -> psycopg2:
        try:
            # Подключение к существующей базе данных
            cls._connection = psycopg2.connect(user='nikita',
                                        password="nikita",
                                        host='localhost',
                                        database='zdrive')

        #обработка ошибок при подключении
        except psycopg2.OperationalError as ex:
            print(f'the operational error:\n{ex}')
        except BaseException as ex:
            print(f'other error:\n{ex}')
        else:
            print("Успешное подключение к БД\n")
        return cls._connection
    
    # метод для обработки запросов на добавление-обновление-удаление данных
    @classmethod
    def execute_query(cls, query) -> bool:
        cls._connect_to_db()
        cls._connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = cls._connection.cursor()
        try:
            cursor.execute(query)
        except psycopg2.OperationalError as ex:
            print(f'the operational error:\n{ex}')
        except BaseException as ex:
            print(f'the error:\n{ex}')
        else:
            print('Запрос выполнен успешно!\n')
            return True
        finally:
            if cls._connection:
                cursor.close()
                cls._connection.close()
                print("Соединение с PostgreSQL закрыто\n")
        return False

    # метод обработки селект-запросов
    @classmethod
    def select_query(cls, query) -> list:
        cls._connect_to_db()
        cls._connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = cls._connection.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchall()
        except psycopg2.OperationalError as ex:
            print(f'the operational error:\n{ex}')
        except BaseException as ex:
            print(f'the error:\n{ex}')
        else:
            print('Вот результат селекта:\n')
            print(result)
            return result
        finally:
            if cls._connection:
                cursor.close()
                cls._connection.close()
                print("Соединение с PostgreSQL закрыто\n")
        return None

    @classmethod
    def insert_returning(cls, query: str) -> object:
        cls._connect_to_db()
        cls._connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = cls._connection.cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchone()
        except psycopg2.OperationalError as ex:
            print(f'the operational error:\n{ex}')
        except BaseException as ex:
            print(f'the error:\n{ex}')
        else:
            print('the insert returning query is successfully')
            return result
        return None


class Client(UserMixin):


    def __init__(self,
                id: int = 0,
                username: str = "",
                passport: str = "",
                name: str = "",
                password_hash: str = "",
                balance: int = 0,
                city_id: int = 0,
                age : int = 0):

                self.id : int = id
                self.username: str = username
                self.passport: str = passport
                self.name : str = name
                self.password_hash: str = password_hash
                self.balance: int = balance
                self.city_id: int = city_id
                self.age : int = age
                self.role = "client"

    def __repr__(self):
        return f'<User {self.username}>'

    def __str__(self):
        string = f'{self.name}:' + '\r\n' + f'{self.username}'
        return string

    #список всех юзеров
    def get_list():
        query = f'''SELECT ID, NAME FROM CLIENT;'''
        result = Database.select_query(query)
        return result

    # генерация хэш-пароля
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)
        print("Пароль для пользователя успешно сгенерирован")
        print(self.password_hash)


    #смена пароля
    def update_password(self):
        query = f'''UPDATE CLIENT
                    SET PASSWORD_HASH = '{self.password_hash}'
                    WHERE USERNAME = '{self.username}';'''
        return Database.execute_query(query)

    # проверка хэша
    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)

    #смена айди города пользователя
    def change_city_id(self, id):
        query = f'''UPDATE CLIENT
                    SET CITY_ID = '{id}'
                    WHERE USERNAME = '{self.username}';'''
        return Database.execute_query(query)

    #добавляем пользователя
    def adduser(self):
        query = f'''INSERT INTO CLIENT (USERNAME, PASSPORT, NAME, PASSWORD_HASH, CITY_ID, AGE) 
                    VALUES ('{self.username}', '{self.passport}', '{self.name}', '{self.password_hash}', '{self.city_id}', '{self.age}');'''
        return Database.execute_query(query)

    #пополнение
    def add_balance(self, rubles):
        query = f'''UPDATE CLIENT
                    SET BALANCE = BALANCE + {int(rubles)}
                    WHERE USERNAME = '{self.username}';'''
        return Database.execute_query(query)

    def add_balance_by_username(username, rubles):
        query = f'''UPDATE CLIENT
                    SET BALANCE = BALANCE + {int(rubles)}
                    WHERE USERNAME = '{username}';'''
        return Database.execute_query(query)

    #списание со счета
    def write_off_balance(self, rubles):
        query = f'''UPDATE CLIENT
                    SET BALANCE = BALANCE - {int(rubles)}
                    WHERE USERNAME = '{self.username}';'''
        return Database.execute_query(query)

     #получаем пользователя по id
    def get_by_id(id: int):
        print(f"вот такой id передается для поиска {id}")
        query = f'''SELECT * FROM CLIENT WHERE ID = '{id}';'''
        result = Database.select_query(query)
        print(f"Пользователь с таким id {result}")
        if result is None or len(result)==0:
            return None
        else:
            params = result[0]
            return Client(* params)
    

    #получаем пользователя по логину
    def get_by_username(username: str):
        query = f'''SELECT * FROM CLIENT WHERE USERNAME = '{username}';'''
        result = Database.select_query(query)
        if result is None or len(result)==0:
            return None
        else:
            print(result)
            params = result[0]
            return Client(* params)

    def get_city_by_username(username):
        query = f'''SELECT CITY_ID FROM CLIENT
                    WHERE USERNAME = '{username}';'''
        result = Database.select_query(query)
        print('Айди города:\n')
        print(f'{result}\n')
        result = result[0]
        result = result[0]
        return result


class Administrator(UserMixin):


    def __init__(self,
                id: int = 0,
                username: str = "",
                password_hash: str = "",
                name: str = ""):

                self.id : int = id
                self.username: str = username
                self.password_hash: str = password_hash
                self.name : str = name
                self.role = "admin"

    def __repr__(self):
        return f'<User {self.username}>'

    def __str__(self):
        string = f'{self.name}:' + '\r\n' + f'{self.username}'
        return string

     # проверка пароля
    def check_password(self, password: str):
        if self.password_hash == password:
            return True
        return False

    # генерация хэш-пароля
    def set_password(self, password: str):
        self.password_hash = password
        print("Пароль для пользователя успешно сгенерирован")
        print(self.password_hash)

    #смена пароля
    def update_password(self):
        query = f'''UPDATE ADMINISTRATOR
                    SET PASSWORD_HASH = '{self.password_hash}'
                    WHERE USERNAME = '{self.username}';'''
        return Database.execute_query(query)

     #получаем админа по id
    def get_by_id(id: int):
        print(f"вот такой id передается для поиска {id}")
        query = f'''SELECT * FROM ADMINISTRATOR WHERE ID = '{id}';'''
        result = Database.select_query(query)
        print(f"Пользователь с таким id {result}")
        if result is None or len(result)==0:
            return None
        else:
            params = result[0]
            return Administrator(* params)

    def get_city_by_id(admin_id):
        query = f'''SELECT DISTINCT(CITY.ID)
                    FROM CITY JOIN DEALER_CENTRE
                    ON DEALER_CENTRE.CITY_ID = CITY.ID
                    JOIN CENTRE_ADMINISTRATOR
                    ON CENTRE_ADMINISTRATOR.DEALER_ID=DEALER_CENTRE.ID
                    WHERE CENTRE_ADMINISTRATOR.ADMINISTRATOR_ID='{admin_id}';'''
        result = Database.select_query(query)
        print('Айди города:\n')
        print(f'{result}\n')
        result = result[0]
        result = result[0]
        return result

    #получаем админа по логину
    def get_by_username(username: str):
        query = f'''SELECT * FROM ADMINISTRATOR WHERE USERNAME = '{username}';'''
        result = Database.select_query(query)
        if result is None or len(result)==0:
            return None
        else:
            print(result)
            params = result[0]
            return Administrator(* params)

class City():
    def get_list():
        query = f'''SELECT * FROM CITY;'''
        result = Database.select_query(query)
        print('Список городов:\n')
        print(f'{result}\n')
        return result

    def get_by_username(username):
        query = f'''SELECT CITY_NAME FROM CITY JOIN CLIENT 
                    ON CLIENT.CITY_ID = CITY.ID
                    WHERE USERNAME = '{username}';'''
        result = Database.select_query(query)
        print('Город:\n')
        print(f'{result}\n')
        return result

    def get_list_by_admin_username(username):
        query = f'''select distinct (CITY_ID), CITY_NAME FROM CENTRE_ADMINISTRATOR JOIN DEALER_CENTRE ON CENTRE_ADMINISTRATOR.DEALER_ID = DEALER_CENTRE.ID
        JOIN CITY ON DEALER_CENTRE.CITY_ID = CITY.ID
        WHERE ADMINISTRATOR_USERNAME = '{username}';'''
        result = Database.select_query(query)
        print('Список городов:\n')
        print(f'{result}\n')
        return result

class Car():
    #добавляем новый автомобиль в автосалон
    def add(dealer_id, brand, model, year, types, costday, costhour, deposit, transmission, engine, seats, force, oil, drive, info, link):
        query = f'''INSERT INTO CAR (DEALER_ID, BRAND, MODEL, YEAR, TYPE, COSTDAY, COSTHOUR, DEPOSIT, TRANSMISSION, ENGINE, SEATS, FORCE, OIL, DRIVE, INFORMATION, LINK, IS_FREE)
        VALUES('{dealer_id}', '{brand}', '{model}', '{year}', '{types}', '{costday}', '{costhour}', '{deposit}', '{transmission}', '{engine}', '{seats}', '{force}', '{oil}', '{drive}', '{info}', '{link}', '1');'''
        print('Добавлен новый автомобиль')
        return Database.execute_query(query)

    #получаем ссылку на фото
    def get_link_by_id(id):
        query = f'''SELECT LINK FROM CAR
        WHERE ID='{id}';'''
        result = Database.select_query(query)
        print('Вот отзывы об автомобиле:\n')
        print(f'{result}\n')
        return result

    #получаем отзывы об авто по айди
    def get_feedback_by_id(id):
        query = f'''SELECT CLIENT.NAME, STARS, FEEDBACK.INFORMATION
        FROM FEEDBACK JOIN OFFER ON FEEDBACK.OFFER_ID=OFFER.ID
        JOIN CAR ON OFFER.CAR_ID=CAR.ID
        JOIN CLIENT ON OFFER.CLIENT_ID=CLIENT.ID
        WHERE CAR.ID='{id}';'''
        result = Database.select_query(query)
        print('Вот отзывы об автомобиле:\n')
        print(f'{result}\n')
        return result

    #получаем среднюю оценку автомобиля
    def get_stars_by_id(id):
        query = f'''SELECT AVG(STARS)
        FROM FEEDBACK JOIN OFFER ON FEEDBACK.OFFER_ID=OFFER.ID
        JOIN CAR ON OFFER.CAR_ID=CAR.ID
        WHERE CAR.ID='{id}';'''
        result = Database.select_query(query)
        print('Средняя оценка автомобиля:\n')
        print(f'{result}\n')
        result = result[0][0]
        return result

    #стоимость депозита
    def get_deposit_by_id(id):
        query = f'''SELECT DEPOSIT FROM CAR WHERE ID = '{id}';'''
        result = Database.select_query(query)
        print('Стоимость депозита:\n')
        print(f'{result}\n')
        result = result[0][0]
        return result

    #стоимость депозита
    def get_deposit_by_offer_id(offer_id):
        query = f'''SELECT DEPOSIT FROM CAR JOIN OFFER
                    ON OFFER.CAR_ID=CAR.ID
                    WHERE OFFER.ID='{offer_id}';'''
        result = Database.select_query(query)
        print('Стоимость депозита:\n')
        print(f'{result}\n')
        result = result[0][0]
        return result

    #модель тачки по названию
    def get_name_by_id(id):
        query = f'''SELECT BRAND, MODEL, YEAR FROM CAR WHERE ID = '{id}';'''
        result = Database.select_query(query)
        print('Название авто с таким айди:\n')
        print(f'{result}\n')
        result = f'{result[0][0]} {result[0][1]}({result[0][2]})'
        return result

    #получаем стоимость автомобиля за сутки
    def get_day_cost_by_id(id):
        query = f'''SELECT COSTDAY FROM CAR WHERE ID = '{id}';'''
        result = Database.select_query(query)
        print('Стоимость за сутки:\n')
        print(f'{result}\n')
        result = result[0][0]
        return result

    #получаем стоимость автомобиля за час
    def get_hour_cost_by_id(id):
        query = f'''SELECT COSTHOUR FROM CAR WHERE ID = '{id}';'''
        result = Database.select_query(query)
        print('Стоимость за день:\n')
        print(f'{result}\n')
        result = result[0][0]
        return result


    #получаем список всех имеющихся типов автомобилей
    def get_all_types(id):
        query = f'''SELECT DISTINCT(TYPE) 
                    FROM CAR JOIN DEALER_CENTRE
                    ON CAR.DEALER_ID=DEALER_CENTRE.ID
                    JOIN CITY ON DEALER_CENTRE.CITY_ID=CITY.ID
                    JOIN CLIENT ON CLIENT.CITY_ID=CITY.ID
                    WHERE CLIENT.ID='{id}';'''
        result = Database.select_query(query)
        print('Типы автомобилей по запросу:\n')
        print(f'{result}\n')
        result = map(lambda x: x[0] , result)
        return result

    #список всех типов автомобилей в тех автосалонах, где админ работает
    def get_all_types_by_admin_id(admin_id):
        query = f'''SELECT DISTINCT(TYPE)
                    FROM CAR JOIN DEALER_CENTRE
                    ON CAR.DEALER_ID=DEALER_CENTRE.ID
                    JOIN CITY ON DEALER_CENTRE.CITY_ID=CITY.ID
                    JOIN CENTRE_ADMINISTRATOR ON CENTRE_ADMINISTRATOR.DEALER_ID = DEALER_CENTRE.ID
                    WHERE ADMINISTRATOR_ID = '{admin_id}';'''
        result = Database.select_query(query)
        print('Типы автомобилей по запросу:\n')
        print(f'{result}\n')
        result = map(lambda x: x[0] , result)
        return result

    #получаем информацию по автомобилЯм в городе клиента
    def get_list(id):
        query = f'''SELECT CAR.ID, BRAND, MODEL, YEAR
                    FROM CAR JOIN DEALER_CENTRE
                    ON CAR.DEALER_ID = DEALER_CENTRE.ID
                    WHERE DEALER_CENTRE.CITY_ID = '{id}' AND IS_FREE=1;'''
        result = Database.select_query(query)
        print('Список автомобилей по запросу:\n')
        print(f'{result}\n')
        result = map(lambda x: (str(x[0]), str(x[1]), str(x[2]), str(x[3])) , result)

        return result
    #получаем информацию по автомобилЯм с таким названием в городе клиента
    def get_list_by_name(id, name, lower_bound, upper_bound):
        if name == 'nothing':
            query = f'''SELECT CAR.ID, BRAND, MODEL, YEAR
                    FROM CAR JOIN DEALER_CENTRE
                    ON CAR.DEALER_ID = DEALER_CENTRE.ID
                    WHERE DEALER_CENTRE.CITY_ID = '{id}' 
                    AND IS_FREE=1 
                    AND COSTDAY BETWEEN {lower_bound} AND {upper_bound};'''
        else:
            query = f'''SELECT CAR.ID, BRAND, MODEL, YEAR
                    FROM CAR JOIN DEALER_CENTRE
                    ON CAR.DEALER_ID = DEALER_CENTRE.ID
                    WHERE DEALER_CENTRE.CITY_ID = '{id}' 
                    AND IS_FREE=1 
                    AND lower(CAR.BRAND||' '||CAR.MODEL) LIKE '%{name}%'
                    AND COSTDAY BETWEEN {lower_bound} AND {upper_bound};'''
        result = Database.select_query(query)
        print('Список автомобилей по запросу:\n')
        print(f'{result}\n')
        result = map(lambda x: (str(x[0]), str(x[1]), str(x[2]), str(x[3])) , result)
        return result

    #получаем информацию по автомобилям конкретного типа в городе клиента
    def get_list_by_type(type, id):
        query = f'''SELECT CAR.ID, BRAND, MODEL, YEAR 
                    FROM CAR JOIN DEALER_CENTRE
                    ON CAR.DEALER_ID = DEALER_CENTRE.ID
                    WHERE TYPE = '{type}' AND DEALER_CENTRE.CITY_ID = '{id}' AND IS_FREE=1;'''
        result = Database.select_query(query)
        print('Список автомобилей по запросу:\n')
        print(f'{result}\n')
        result = map(lambda x: (str(x[0]), str(x[1]), str(x[2]), str(x[3])) , result)
        return result

    def get_list_by_type_name(type, id, name, lower_bound, upper_bound):
        if name == 'nothing':
            query = f'''SELECT CAR.ID, BRAND, MODEL, YEAR 
                    FROM CAR JOIN DEALER_CENTRE
                    ON CAR.DEALER_ID = DEALER_CENTRE.ID
                    WHERE TYPE = '{type}' 
                    AND DEALER_CENTRE.CITY_ID = '{id}' 
                    AND IS_FREE=1 
                    AND COSTDAY BETWEEN {lower_bound} AND {upper_bound};'''
        else:
            query = f'''SELECT CAR.ID, BRAND, MODEL, YEAR 
                    FROM CAR JOIN DEALER_CENTRE
                    ON CAR.DEALER_ID = DEALER_CENTRE.ID
                    WHERE TYPE = '{type}' 
                    AND DEALER_CENTRE.CITY_ID = '{id}' 
                    AND IS_FREE=1 
                    AND lower(CAR.BRAND||' '||CAR.MODEL) LIKE '%{name}%'
                    AND COSTDAY BETWEEN {lower_bound} AND {upper_bound};'''
        result = Database.select_query(query)
        print('Список автомобилей по запросу:\n')
        print(f'{result}\n')
        result = map(lambda x: (str(x[0]), str(x[1]), str(x[2]), str(x[3])) , result)
        return result


    def get_info_by_id(id):
        query = f'''SELECT TYPE, BRAND, MODEL, COSTDAY, COSTHOUR, TRANSMISSION, ENGINE, SEATS, FORCE, OIL, DRIVE, DEPOSIT, YEAR,
                ADRES, CITY_NAME, PHONE_NUMBER, INFORMATION
                FROM CAR JOIN DEALER_CENTRE ON CAR.DEALER_ID = DEALER_CENTRE.ID
                JOIN CITY ON DEALER_CENTRE.CITY_ID = CITY.ID
                WHERE CAR.ID = '{id}';'''
        result = Database.select_query(query)
        print('Информация об этом автомобиле:\n')
        print(f'{result}\n')
        return result

    def get_name_by_id(id):
        query = f'''SELECT BRAND, MODEL, YEAR
                FROM CAR
                WHERE CAR.ID = '{id}';'''
        result = Database.select_query(query)
        print('Название автомобиля:\n')
        print(f'{result}\n')
        return result

    # список авто с которыми может работать этот админ
    def get_car_by_admin_username(username):
        query = f'''SELECT CAR.ID, CAR.BRAND, CAR.MODEL, CAR.YEAR FROM DEALER_CENTRE
                    JOIN CENTRE_ADMINISTRATOR
                    ON CENTRE_ADMINISTRATOR.DEALER_ID=DEALER_CENTRE.ID
                    JOIN CAR
                    ON DEALER_CENTRE.ID=CAR.DEALER_ID
                    WHERE CENTRE_ADMINISTRATOR.ADMINISTRATOR_USERNAME='{username}';'''
        result = Database.select_query(query)
        print('автомобили:\n')
        print(f'{result}\n')
        return result

class Offer():
    #получаем офферы, с которыми может работать этот админ
    def get_by_admin_username(admin_username):
        query = f'''SELECT OFFER.ID, CAR.BRAND, CAR.MODEL, CAR.YEAR, CLIENT.NAME
                    FROM OFFER JOIN CLIENT ON OFFER.CLIENT_ID = CLIENT.ID
                    JOIN CAR ON OFFER.CAR_ID = CAR.ID
                    JOIN DEALER_CENTRE ON OFFER.DEALER_ID = DEALER_CENTRE.ID
                    JOIN CENTRE_ADMINISTRATOR ON CENTRE_ADMINISTRATOR.DEALER_ID = DEALER_CENTRE.ID
                    WHERE CENTRE_ADMINISTRATOR.ADMINISTRATOR_USERNAME = '{admin_username}'
                    AND IS_COMPLITED=0;'''
        result = Database.select_query(query)
        print('Администратор работает с этими заказами:\n')
        print(f'{result}\n')
        return result

    #меняем статус заказа на выполнен
    def set_is_complited(offer_id):
        query = f'''UPDATE OFFER
                    SET IS_COMPLITED = 1
                    WHERE ID='{offer_id}';'''
        return Database.execute_query(query)

    #добавляем отзыв на заказ
    def add_feedback_by_id(offer_id, stars, information, dealer_stars, dealer_information):
        query = f'''INSERT INTO FEEDBACK (OFFER_ID, STARS, INFORMATION, DELAER_STARS, DEALER_INFORMATION)
                VALUES ('{offer_id}', '{stars}', '{information}', '{dealer_stars}', '{dealer_information}');'''
        return Database.execute_query(query)

    # меняем отметку о комментарии
    def change_feedback_status(offer_id):
        query = f'''UPDATE OFFER
                    SET HAVE_FEEDBACK = 1 WHERE ID='{offer_id}';'''
        return Database.execute_query(query)

    #добавление нового оффера
    def add(client_id, username, passport, dealer_id, car_id, hours, cost, date, time):
        query = f'''INSERT INTO OFFER (CLIENT_ID, CLIENT_USERNAME, CLIENT_PASSPORT, DEALER_ID, CAR_ID, HOURS_NUMBER, COST, IS_COMPLITED, HAVE_FEEDBACK, "DATE", "TIME")
        VALUES ('{client_id}', '{username}', '{passport}', '{dealer_id}', '{car_id}', '{hours}', '{cost}', '0', '0', '{date}', '{time}');'''
        return Database.execute_query(query)

    #незавершенные офферы по айди оффера
    def get_unfinished_list_by_id(offer_id):
        query = f'''SELECT CAR.BRAND, CAR.MODEL, CAR.YEAR, HOURS_NUMBER, to_char("DATE", 'dd-mm-YYYY'), "TIME", CLIENT.NAME, CLIENT.USERNAME
                    FROM CAR JOIN OFFER ON OFFER.CAR_ID=CAR.ID JOIN DEALER_CENTRE ON DEALER_CENTRE.ID = OFFER.DEALER_ID
                    JOIN CLIENT ON CLIENT.ID=OFFER.CLIENT_ID
                    WHERE OFFER.ID = '{offer_id}' AND IS_COMPLITED=0;'''
        result = Database.select_query(query)
        #result = list(map(lambda x: (str(x[0]), str(x[1]), str(x[2]), str(x[3]), str(x[4]), str(x[5]), str(x[6]), str(x[7])) , result))
        return result

    #незаверщенная аренда по логину пользователя
    def get_unfinished_list_by_username(username):
        query = f'''SELECT CAR.BRAND, CAR.MODEL, CAR.YEAR, HOURS_NUMBER, OFFER.COST, to_char("DATE", 'dd-mm-YYYY'), "TIME", DEALER_CENTRE.ADRES, CAR.ID, CAR.TYPE, OFFER.ID
                    FROM CAR JOIN OFFER ON OFFER.CAR_ID=CAR.ID JOIN DEALER_CENTRE ON DEALER_CENTRE.ID = OFFER.DEALER_ID
                    WHERE OFFER.CLIENT_USERNAME = '{username}' AND IS_COMPLITED=0;'''
        result = Database.select_query(query)
        #result = list(map(lambda x: (str(x[0]), str(x[1]), str(x[2]), str(x[3]), str(x[4]), str(x[5]), str(x[6]), str(x[7])) , result))
        return result

    #заверщенная аренда по логину пользователя С ОТЗЫВОМ
    def get_finished_list_by_username_with_feedback(username):
        query = f'''SELECT CAR.BRAND, CAR.MODEL, CAR.YEAR, HOURS_NUMBER, OFFER.COST, to_char("DATE", 'dd-mm-YYYY'), "TIME", DEALER_CENTRE.ADRES, CAR.ID, CAR.TYPE
                    FROM CAR JOIN OFFER ON OFFER.CAR_ID=CAR.ID JOIN DEALER_CENTRE ON DEALER_CENTRE.ID = OFFER.DEALER_ID
                    WHERE OFFER.CLIENT_USERNAME = '{username}' AND IS_COMPLITED=1 AND HAVE_FEEDBACK=1;'''
        result = Database.select_query(query)
        #result = map(lambda x: (str(x[0]), str(x[1]), str(x[2]), str(x[3]), str(x[4]), str(x[5]), str(x[6]), str(x[7])) , result)
        return result

    #заверщенная аренда по логину пользователя БЕЗ ОТЗЫВА
    def get_finished_list_by_username_without_feedback(username):
        query = f'''SELECT CAR.BRAND, CAR.MODEL, CAR.YEAR, HOURS_NUMBER, OFFER.COST, to_char("DATE", 'dd-mm-YYYY'), "TIME", DEALER_CENTRE.ADRES, OFFER.ID, CAR.ID, CAR.TYPE
                    FROM CAR JOIN OFFER ON OFFER.CAR_ID=CAR.ID JOIN DEALER_CENTRE ON DEALER_CENTRE.ID = OFFER.DEALER_ID
                    WHERE OFFER.CLIENT_USERNAME = '{username}' AND IS_COMPLITED=1 AND HAVE_FEEDBACK=0;'''
        result = Database.select_query(query)
        #result = map(lambda x: (str(x[0]), str(x[1]), str(x[2]), str(x[3]), str(x[4]), str(x[5]), str(x[6]), str(x[7])) , result)
        return result


class Dealer():
    #получаем диллерские центры по логину админа
    def get_adres_by_admin_username(username):
        query = f'''SELECT DEALER_CENTRE.ID, ADRES FROM DEALER_CENTRE
                    JOIN CENTRE_ADMINISTRATOR
                    ON CENTRE_ADMINISTRATOR.DEALER_ID=DEALER_CENTRE.ID
                    WHERE CENTRE_ADMINISTRATOR.ADMINISTRATOR_USERNAME='{username}';'''
        result = Database.select_query(query)
        print('Адреса автосалонов:\n')
        print(f'{result}\n')
        return result

    #получаем оценку по айди
    def get_stars_by_id(dealer_id):
        query = f'''SELECT AVG(DELAER_STARS)
        FROM FEEDBACK JOIN OFFER ON FEEDBACK.OFFER_ID=OFFER.ID
        JOIN DEALER_CENTRE ON OFFER.DEALER_ID=DEALER_CENTRE.ID
        WHERE DEALER_CENTRE.ID='{dealer_id}';'''
        result = Database.select_query(query)
        print('Средняя оценка автомобиля:\n')
        print(f'{result}\n')
        result = result[0][0]
        return result

    #получаем айди диллера по айди автомобиля
    def get_id_by_car_id(car_id):
        query = f'''SELECT DEALER_ID FROM CAR WHERE ID = '{car_id}';'''
        result = Database.select_query(query)
        print('Где находится автомобиль:\n')
        print(f'{result}\n')
        result = result[0][0]
        return result

    def get_feedback_by_id(dealer_id):
        query = f'''SELECT CLIENT.NAME, DELAER_STARS, DEALER_INFORMATION
        FROM FEEDBACK JOIN OFFER ON FEEDBACK.OFFER_ID=OFFER.ID
        JOIN DEALER_CENTRE ON OFFER.DEALER_ID=DEALER_CENTRE.ID
        JOIN CLIENT ON OFFER.CLIENT_ID=CLIENT.ID
        WHERE DEALER_CENTRE.ID='{dealer_id}';'''
        result = Database.select_query(query)
        print('Вот отзывы об автосалоне:\n')
        print(f'{result}\n')
        return result



#метод загрузки клиента:
@login.user_loader
def load_user(id: str):
    if session['role'] == 'admin':
        user = Administrator.get_by_id(int(id))
    elif session['role'] == 'client':
        user = Client.get_by_id(int(id))
    print(f'user loaded, user = {user}')
    return user