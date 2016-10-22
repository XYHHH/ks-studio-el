import MySQLdb


def main():
    db = MySQLdb.connect('localhost', 'root', 'dhldhl', 'dbtest')
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO animals(name) VALUES ('panda')")
        db.commit()
    except:
        db.rollback()

    cursor.execute('SELECT * FROM animals')
    print cursor.fetchall()

    db.close()

if __name__ == '__main__':
    main()
