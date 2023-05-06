import psycopg2
from config import user, password, db_name


with psycopg2.connect(user=user, password=password, database=db_name) as conn:
    conn.autocommit = True

# создаем таблицу
def create_table_users():

    with conn.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS seen_person(
            id SERIAL PRIMARY KEY,
            id_found INTEGER UNIQUE,
            user_id INTEGER);
        """)

# добавляем id найденных пользователей
def insert_data_search(user_id, id_found):
    with conn.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO seen_person (user_id,id_found) 
           VALUES (%s, %s)""",(user_id, id_found,))



# запрашиваем список id найденных пользователей
def check(id_found):
    with conn.cursor() as cursor:

        cursor.execute(
            f"""SELECT id_found FROM seen_person AS sp WHERE id_found = %s;""",
                       (id_found,))
        seen_person = cursor.fetchall()
        return seen_person


# удаляем таблицу
def drop_users():
    with conn.cursor() as cursor:
        cursor.execute(
            """DROP TABLE  IF EXISTS seen_person CASCADE;"""
        )


def creating_database():
    # drop_users()
    create_table_users()




if __name__ == '__main__':
    creating_database()
