import psycopg2

def delete_tables(cur):
    """Удаляет созданные данные при каждой итерации, для отладки"""
    cur.execute("""
    DROP TABLE IF EXISTS Client_phones""")
    cur.execute("""
    DROP TABLE  IF EXISTS Clients""")
    conn.commit()


def create_db(cur):
    """Создает таблицы БД"""
    cur.execute("""
    CREATE TABLE IF NOT EXISTS Clients(  
        client_id INTEGER PRIMARY KEY,
        last_name VARCHAR(40) ,
        first_name VARCHAR(40),
        email VARCHAR(60)
    );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS Client_phones(  
            phone_number  VARCHAR PRIMARY KEY,
            client_id INTEGER REFERENCES Clients(client_id)
        );
        """)
    # Выбран № телефона как уникальный ключ
    conn.commit()


def add_client(cur, client_id, first_name, last_name, email, *phones):
    """Добавляет все данные клиента в таблицу Clients, а телефоны, если есть в Client_phones"""
    cur.execute("""
        INSERT INTO Clients (client_id, last_name, first_name, email) VALUES(%s, %s, %s,%s)
        RETURNING email, last_name, first_name;
            """, (client_id,  last_name, first_name, email))
    print(f'Добавление клиента №{client_id} - , {cur.fetchall()}')

    if phones:    # Проверяет введены ли телефоны, если да, то записывает в Client_phones
        add_phone(cur, client_id, *phones)


def add_phone(cur, client_id, *phones):
    """Добавляет телефон и id клиента в Client_phones"""
    for phone in phones:
        cur.execute("""
            INSERT INTO Client_phones (phone_number, client_id) VALUES(%s, %s) 
            RETURNING phone_number, client_id;
            """, (phone, client_id))
        print(f'Добавление телефона клиенту № {client_id} - {cur.fetchall()}')


def change_client_data(cur, client_id, first_name=None, last_name=None, email=None,
                       new_phones=None, old_phones=None):
    """Меняет данные на введеные по id клиента. Невведенные данные остаются как прежде"""
    """Если меняеются телефоны, просит ввод старых и новых"""
    print('Действие функции обновления даннх')
    if first_name:
        cur.execute("""
                    UPDATE Clients SET first_name=%s WHERE client_id=%s;""", (first_name, client_id))
        conn.commit()
    if last_name:
        cur.execute("""
                    UPDATE Clients SET first_name=%s WHERE client_id=%s;""", (last_name, client_id))
        conn.commit()
    if email:
        cur.execute("""
                    UPDATE Clients SET first_name=%s WHERE client_id=%s;""", (email, client_id))
        conn.commit()
    cur.execute("""
                    SELECT last_name, first_name, email FROM Clients WHERE client_id=%s
                    ;
                    """, (client_id,))

    print(f'Меняет данные клиента № {client_id}, измененные данные {cur.fetchall()}')
    if old_phones:    # Если есть старые телефоны на удаление
        for old_phone in old_phones:
            print('Удаляем старые номера телефонов')
            delete_phone(cur, old_phone)

    if new_phones:    # Если есть новые для вставки
        print('Добавляем новые номера телефонов')
        add_phone(cur, client_id, *new_phones)


# def change_client_data(cur, client_id , first_name = None, last_name = None, email = None,
#                        new_phones=None, old_phones=None):
# ДАННЫЙ ВАРИАНТ ФУНКЦИИ НЕ РАБОТАЕТ КОРРЕКТНО
#     cur.execute("""
#             UPDATE Clients SET first_name=%s, last_name=%s, email=%s WHERE client_id=%s
#             RETURNING email, last_name, first_name;
#             """, (first_name, last_name, email, client_id))
#     print(f'Меняет данные клиента № {client_id}, измененные данные {cur.fetchall()}')
#     #conn.commit()
#     cur.execute("""
#                 SELECT  FROM Clients WHERE client_id=%s
#                 ;
#                 """, (client_id,))
#     print(f'Меняет данные клиента № {client_id}, измененные данные {cur.fetchall()}')
#
#     if old_phones:    # Если есть старые телефоны на замену
#         for old_phone in old_phones:
#             delete_phone(cur, old_phone)
#     if new_phones:    # Если есть новые для вставки
#         add_phone(cur, client_id, *new_phones)


def delete_phone(cur, phone_number):
    """ Удаляет номер телефона из таблицы Client_phones"""
    cur.execute("""
        DELETE FROM Client_phones WHERE phone_number=%s
        RETURNING phone_number, client_id;
        """, (phone_number,))
    print(f'Удаление телефона №{phone_number}  - {cur.fetchone()}')


def delele_client(cur, id):
    """Удаляет все данные клиента из обеих таблиц, по его id"""
    """Сначала зависимая таблица"""
    cur.execute("""
        DELETE FROM Client_phones WHERE client_id=%s 
        RETURNING client_id, phone_number;
        """, (id,))
    print(f'Удаление телефонов у удалямого клиента №{id} - {cur.fetchall()}')

    cur.execute("""
        DELETE FROM Clients WHERE client_id=%s 
        ;
        """, (id,))
    conn.commit()
    print(f'Удаление остальных данных клиента №{id}')


def find_client(cur, client_id=None,  first_name=None, last_name=None, email=None, phone_number=None):
    """Находит клиента на основании введенной информации - id, имя, фамилия, телефон"""
    if phone_number:    #Проверяем был ли введен телефон
        cur.execute("""
                SELECT last_name FROM Clients 
                JOIN Client_phones ON clients.client_id=client_phones.client_id
                WHERE client_phones.phone_number=%s
                ;
                """, (phone_number,))
        print(f'Поиск клиента по номеру телефона {phone_number} - {cur.fetchall()}')

    else:
        cur.execute("""
            SELECT last_name FROM Clients 
            WHERE client_id=%s OR first_name=%s OR last_name=%s OR email=%s
            ;
            """, (client_id,  first_name, last_name, email))
        print(f'Поиск клиента по другим параметрам  - {cur.fetchall()}')


with psycopg2.connect(database="hw_db", user="postgres", password="hw_db") as conn:
    with conn.cursor() as cur:
        delete_tables(cur)
        create_db(cur)
        add_client(cur, 1, 'Any', 'Anybody', 'any@mail.foo', '+123-123', '+375-987')  #Добавляем клиента с телефонами
        add_client(cur, 2, 'Sam', 'Sambody', 'some@mail.foo')  #Добавляем клиента без телефонов
        add_client(cur, 3, 'No', 'Nobody', 'no@mail.foo', '+000-000', '+111-111')
        add_phone(cur, 2, '+375-111')  #Добаляем телефон к отдельному клиенту
        change_client_data(cur, client_id=1, first_name='Anna', old_phones=['+123-123'],
                           new_phones=['+375-010', '+375-011'])
        delete_phone(cur, '+375-987')
        delele_client(cur, 1)
        find_client(cur, client_id=2)
        find_client(cur, phone_number='+000-000')
        find_client(cur, phone_number='+375-011')   #Возвращает пустой список, т.к. клиент удален
        find_client(cur, email='no@mail.foo')
        find_client(cur, last_name='Sambody')
        find_client(cur, first_name='No')
conn.close()
