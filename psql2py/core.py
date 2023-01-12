import psycopg2


def execute(connection: psycopg2.connection, statement: str, values: dict[str, object]) -> psycopg2.cursor:
    cursor = connection.cursor()
    cursor.execute(statement, values)
    return cursor
