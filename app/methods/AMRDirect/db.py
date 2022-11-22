import sqlite3

from exceptions import JSONRPCInternalError


def database_handler(sqlite_request: str) -> list[dict]:
    def dict_factory(cur, row):
        d = {}
        for idx, col in enumerate(cur.description):
            d[col[0]] = row[idx]
        return d

    try:
        sqlite_connection = sqlite3.connect('mbioviewer_amr.sqlite')
        sqlite_connection.row_factory = dict_factory
        cursor = sqlite_connection.cursor()

        cursor.execute(sqlite_request)

        database_content = cursor.fetchall()
        cursor.close()
    except sqlite3.Error as error:
        raise JSONRPCInternalError(data=str(error))
    except Exception as error:
        raise JSONRPCInternalError(data=str(error))
    finally:
        if (sqlite_connection):
            sqlite_connection.close()

    return database_content


__all__ = ['database_handler']
