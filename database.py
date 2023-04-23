import psycopg2
from config import user, password, db_name


with psycopg2.connect(user=user, password=password, database=db_name) as conn:
    conn.autocommit = True


def create_table_users():  # references users(id_vk)

    with conn.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS seen_person(
            id SERIAL,
            id_vk varchar(50) PRIMARY KEY,
            user_id varchar(50));
        """)


def insert_data_search(id_vk):
    with conn.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO seen_person (id_vk) 
           VALUES (%s)""",(id_vk,))

def insert_data_users(user_id):
    with conn.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO seen_person (user_id) 
           VALUES (%s)""",(user_id,))

def check():
    with conn.cursor() as cursor:
        cursor.execute(
            f"""SELECT sp.id_vk
            FROM seen_person AS sp;"""
        )
        seen_person = cursor.fetchall()
        return seen_person


def drop_users():
    with conn.cursor() as cursor:
        cursor.execute(
            """DROP TABLE  IF EXISTS seen_person CASCADE;"""
        )


def creating_database():
    drop_users()
    create_table_users()




if __name__ == '__main__':
    creating_database()



