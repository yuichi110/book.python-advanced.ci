import psycopg2


class Repository:
    def __init__(self, host, database, user, password):
        self._connection = psycopg2.connect(
            host=host, dbname=database, user=user, password=password
        )

    def insert_item(self, item_name):
        cur = self._connection.cursor()
        query = "INSERT INTO public.item (name) VALUES (%s);"
        cur.execute(query, (item_name,))
        self._connection.commit()
        cur.close()

    def get_items(self):
        cur = self._connection.cursor()
        cur.execute("SELECT * FROM public.item;")
        result = cur.fetchall()
        cur.close()
        return result
