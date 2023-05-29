import psycopg2

# На случай очистки базы
def delete_tables(cur):
    try:
        cur.execute("""
            drop table clients_list cascade;
            drop table phones_list cascade;
            """)
        print('База данных очищена.')
    except:
        cur.rollback()
        print('Что-то пошло не так.')
# Создание таблиц
def create_db(cur):
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
        cur.rollback()
        print('Структура базы данных не изменилась.')
# Добавление клиента
def add_client(cur, first_name, last_name, email, phones=None):
    try:
        cur.execute("""
        INSERT INTO clients_list(firstname, lastname, email) VALUES(%s, %s, %s);
        """, (first_name, last_name, email))
        print('Клиент успешно добавлен.')
    except:
        print('Данного клиента добавить не получилось.')
# Добавление телефона
def add_phone(cur, client_id, phone):
    try:
        cur.execute("""
        INSERT INTO phones_list(phone, client_id) VALUES(%s, %s);
        """, (phone, client_id))
        print('Телефон успешно добавлен.')
    except:
        print('Данный телефон уже есть либо клиент не найден.')
# Изменение данных
def change_client(cur, client_id, first_name=None, last_name=None, email=None, phones=None):
    if client_id > 0 and first_name is not None:
        cur.execute("""
        UPDATE clients_list SET firstname=%s WHERE client_id=%s;
        """, (first_name, client_id,))
        print('Имя успешно изменено.')
    else:
        print('Имя не изменено.')        
    
    if client_id > 0 and last_name is not None:
        cur.execute("""
        UPDATE clients_list SET lastname=%s WHERE client_id=%s;
        """, (last_name, client_id,))
        print('Фамилия успешна изменена.')
    else:
        print('Фамилия не изменена.')
    
    if client_id > 0 and email is not None:
        cur.execute("""
        UPDATE clients_list SET email=%s WHERE client_id=%s;
        """, (email, client_id,))
        print('Email успешно изменен.')
    else:
        print('Имя не изменено.')
    
    if client_id > 0 and phones is not None:
        old_phone = get_phone_client(cur, phones)
        if old_phone == phones:
            print('Такой номер телефона уже есть.')         
        else: 
            phone_id = get_id_phone_client(cur, client_id)
            if phone_id == '0':
                print('У клиента еще нет телефонов.')
                add_phone(cur, client_id, phones)
            else:
                cur.execute("""
                UPDATE phones_list SET phone=%s WHERE phone_id=%s;
                """, (phones, phone_id,))
                print('Телефон успешно изменен.') 
    else:
        print('Телефон не изменен.') 
# Поиск телефона
def find_phone(cur, phone):
    cur.execute("""
    select phone from phones_list where phone = %s;
    """, (phone,))
    res = cur.fetchone()
    if res is None:
        return '0'
    else:
        return res[0]
# Удаление телефона 
def delete_phone(cur, client_id, phone):
    q_phone = find_phone(cur, phone)
    if q_phone == '0':
        print('Такого номера телефона нет.')
    else:
        cur.execute("""
        DELETE FROM phones_list WHERE phone = %s and client_id = %s;
        """, (phone, client_id,))
        print('Номер телефона удален.')
# Удаление клиента        
def delete_client(cur, client_id):
    cur.execute("""
    select client_id from clients_list where client_id = %s;
    """, (client_id,))
    res = cur.fetchone()
    if res[0] > 0:
        cur.execute("""
        DELETE FROM phones_list WHERE client_id = %s;
        """, (client_id,))
        cur.execute("""
        DELETE FROM clients_list WHERE client_id = %s;
        """, (client_id,))
        print('Клиент удален.')
    else:
        print('Такого клиента нет.')
# Поиск клиента
def find_client(cur, first_name=None, last_name=None, email=None, phone=None):
    if first_name is not None:
        cur.execute("""
        select clients_list.client_id, clients_list.firstname, clients_list.lastname, clients_list.email, phones_list.phone 
        from clients_list
        join phones_list on phones_list.client_id  = clients_list.client_id 
        where firstname = %s;
        """, (first_name,))
        res = cur.fetchall()
        if res is None:
            print('Клиента с таким именем нет.')
        else:
            for i in res:
                cl_id, f_name, l_name, c_email, c_phone = i
                print(f'ID клиента: {cl_id}, Имя: {f_name}, Фамилия: {l_name}, Эл. почта: {c_email}, Телефон: {c_phone}')
    
    elif last_name is not None:
        cur.execute("""
        select clients_list.client_id, clients_list.firstname, clients_list.lastname, clients_list.email, phones_list.phone 
        from clients_list
        join phones_list on phones_list.client_id  = clients_list.client_id 
        where lastname = %s;
        """, (last_name,))
        res = cur.fetchall()
        if res is None:
            print('Клиента с таким именем нет.')
        else:
            for i in res:
                cl_id, f_name, l_name, c_email, c_phone = i
                print(f'ID клиента: {cl_id}, Имя: {f_name}, Фамилия: {l_name}, Эл. почта: {c_email}, Телефон: {c_phone}')

    elif email is not None:
        cur.execute("""
        select clients_list.client_id, clients_list.firstname, clients_list.lastname, clients_list.email, phones_list.phone 
        from clients_list
        join phones_list on phones_list.client_id  = clients_list.client_id 
        where email = %s;
        """, (email,))
        res = cur.fetchall()
        if res is None:
            print('Клиента с таким именем нет.')
        else:
            for i in res:
                cl_id, f_name, l_name, c_email, c_phone = i
                print(f'ID клиента: {cl_id}, Имя: {f_name}, Фамилия: {l_name}, Эл. почта: {c_email}, Телефон: {c_phone}')
    
    elif phone is not None:
        cur.execute("""
        select clients_list.client_id, clients_list.firstname, clients_list.lastname, clients_list.email, phones_list.phone 
        from clients_list
        join phones_list on phones_list.client_id  = clients_list.client_id 
        where phone = %s;
        """, (phone,))
        res = cur.fetchall()
        if res is None:
            print('Клиента с таким именем нет.')
        else:
            for i in res:
                cl_id, f_name, l_name, c_email, c_phone = i
                print(f'ID клиента: {cl_id}, Имя: {f_name}, Фамилия: {l_name}, Эл. почта: {c_email}, Телефон: {c_phone}')
    
    else:
        print('Что-то пошло не так')
        pass
# Поиск ID клиента (вспомогательная функция)
def get_id_client(cur, client_id):
    cur.execute("""
    select client_id,  firstname, lastname, email from clients_list cl where client_id = %s;
    """, (client_id,))
    res = cur.fetchone()
    return res[0]
# Поиск телефона клиента (вспомогательная функция)
def get_phone_client(cur, phone):
    cur.execute("""
    select phone from phones_list where phone = %s;
    """, (phone,))
    res = cur.fetchone()
    if res is None:
        return '0'
    else:
        return res[0]
# Поиск ID телефона клиента (вспомогательная функция)
def get_id_phone_client(cur, client_id):
    cur.execute("""
    select phone_id from phones_list where client_id = '1';
    """, (client_id,))
    res = cur.fetchone()
    if res is None:
        return '0'
    else:
        return res[0]
    

if __name__ == '__main__':
    # Переменные для тестирования
    client_id = '2'
    first_name = 'John'
    last_name = 'Kmith'
    email ='Tast@mail.ru'
    phone = '79781111144'
    new_first_name = 'Anno'
    new_last_name = 'Fathon'
    new_email = 'kast@mail.ru'
    new_phone = '79782222288'

    with psycopg2.connect(database='dataclients', user='postgres', password='7753191qq') as conn:
        with conn.cursor() as cur:
            
            # delete_tables(cur) 
            # create_db(cur)
            # add_client(cur, first_name, last_name, email)
            # add_phone(cur, get_id_client(cur, client_id), phone)
            # change_client(cur, get_id_client(cur, client_id), first_name=None, last_name=new_last_name, email=new_email, phones=None)
            # delete_phone(cur, client_id, phone)
            # delete_client(cur, client_id)
            find_client(cur, first_name=first_name, last_name=None, email=None, phone=None)
    conn.close()