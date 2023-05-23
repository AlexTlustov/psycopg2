import psycopg2

# На случай очистки базы
def delete_tables(conn):
    cur = conn.cursor()
    try:
        cur.execute("""
            drop table clients_list cascade;
            drop table phones_list cascade;
            drop table clients_phones cascade;
            """)
        print('База данных очищена.')
    except:
        conn.rollback()
        print('Что-то пошло не так.')

def create_db(conn):
    cur = conn.cursor()
    try:
        cur.execute("""
            create table if not exists clients_list (
            client_id SERIAL PRIMARY KEY,
            firstname VARCHAR(80) NOT NULL,
            lastname VARCHAR(80) NOT NULL,
            email VARCHAR(30) UNIQUE CHECK(email !='')
            );
            create table if not exists phones_list (
            phone_id SERIAL PRIMARY KEY,
            phone VARCHAR(30) UNIQUE CHECK(phone !=''),
            client_id INTEGER NOT NULL REFERENCES clients_list(client_id)
            );
            """) 
        print('Структура базы данных создана.')
    except:
        conn.rollback()
        print('Структура базы данных не изменилась.')

def add_client(conn, first_name, last_name, email, phones=None):
    cur = conn.cursor()
    try:
        cur.execute("""
        INSERT INTO clients_list(firstname, lastname, email) VALUES(%s, %s, %s);
        """, (first_name, last_name, email))
        print('Клиент успешно добавлен.')
    except:
        conn.rollback()
        print('Данного клиента добавить не получилось.')

def add_phone(conn, client_id, phone):
    cur = conn.cursor()
    try:
        cur.execute("""
        INSERT INTO phones_list(phone, client_id) VALUES(%s, %s);
        """, (phone, client_id))
        print('Телефон успешно добавлен.')
    except:
        conn.rollback()
        print('Данный телефон уже есть либо клиент не найден.')

def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    cur = conn.cursor()
    print('Внесите данные для изменения.')
    find_ph = find_phone(conn)
    phones = input('Телефон который хотите добавить: ')
    if find_ph != None:
        cur.execute("""
        UPDATE phones_list SET phone=%s WHERE phone=%s;
        """, (phones, find_ph,))
        print('Телефон успешно изменен.')
    else:
        add_phone(conn, client_id, phones)
        print('Такой телефон не найден, добавлен как новый.')
    first_name = input('Имя которое хотите добавить: ')
    last_name = input('Фамилия которую хотите добавить: ')
    email = input('Эл. адрес который хотите добавить: ')
    cur.execute("""
    UPDATE clients_list SET firstname = %s, lastname = %s, email = %s WHERE client_id = %s;
    """, (first_name, last_name, email, client_id))
    print('Данные успешно изменены.')

def find_phone(conn):
    cur = conn.cursor()
    phone = input('Укажите телефон который хотите изменить: ')
    cur.execute("""
    select phone, client_id from phones_list where phone = %s;
    """, (phone,))
    res = cur.fetchone()
    if res != None:
        return res[0]
    else:
        print('Такого номера телефона нет.')
        return
        
def delete_phone(conn, phone):
    cur = conn.cursor()
    cur.execute("""
    select phone_id, phone, client_id from phones_list where phone = %s;
    """, (phone,))
    res = cur.fetchone()
    if res != None:
        cur.execute("""
        DELETE FROM phones_list WHERE phone = %s;
        """, (phone,))
        print('Номер телефона удален.')
    else:
        print('Такого номера телефона нет.')
        
def delete_client(conn, client_id):
    cur = conn.cursor()
    cur.execute("""
    select client_id, firstname, lastname, email from clients_list where client_id = %s;
    """, (client_id,))
    res = cur.fetchone()
    if res != None:
        cur.execute("""
        DELETE FROM phones_list WHERE client_id = %s;
        """, (client_id,))
        cur.execute("""
        DELETE FROM clients_list WHERE client_id = %s;
        """, (client_id,))
        print('Клиент удален.')
    else:
        print('Такого клиента нет.')

def find_client(conn):
    cur = conn.cursor()
    email = input('Укажите ваш Email: ')
    cur.execute("""
    select client_id,  firstname, lastname, email from clients_list cl where email = %s;
    """, (email,))
    res = cur.fetchone()
    print(f'Найден клиент: {res[2]} {res[1]}. Электронный адрес: {res[3]}')
    return res[0]

with psycopg2.connect(database='dataclients', user='postgres', password='7753191qq') as conn:
    delete_tables(conn) 
    create_db(conn)
    add_client(conn, first_name = input('Укажите ваше имя: '), last_name = input('Укажите вашу фамилию: '), email = input('Укажите ваш Email: '))
    add_phone(conn, find_client(conn), phone = input('Укажите номер телефона для добавления: '))
    change_client(conn, find_client(conn))
    delete_phone(conn, phone = input('Укажите номер телефона который нужно удалить: '))
    delete_client(conn, client_id = input('Укажите ID клиента которого нужно удалить: '))
    find_client(conn)

conn.close()