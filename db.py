
import sys
import sqlite3 as sql

def makeGraveDatabase():
    conn = sql.connect('graves.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE findAGrave
        (id INTEGER IDENTITY, INTEGER PRIMARY KEY, url TEXT,
         name TEXT, birth TEXT, birthplace TEXT, death TEXT, deathplace TEXT,
         burial TEXT, plot TEXT, more_info BOOL)''')
    conn.close()

def addRowToDatabase(grave):
    row = (grave['id'],)
    keys = ['graveid']
    for key in grave.keys():
        if key == 'id':
            continue
        row += (grave[key],)
        keys.append(key)

    col_names = '(' + ', '.join(keys) + ')'
    value_hold = '(' + '?,' * (len(keys) - 1)  + '?)'
    insert = 'INSERT INTO findAGrave ' + col_names + ' VALUES ' + value_hold

    try:
        conn = sql.connect('graves.db')
        c = conn.cursor()
        c.executemany(insert, [row])
        conn.commit()
        conn.close()
    except:
        print('Memorial #' + grave['id'] + ' is already in database.')

def extractBirth(grave, str):
    try:
        if 'Birthplace' in str:
            grave.update({'birth': str.split('\n')[0]})
            grave.update({'birthplace': str.split('\n')[1].replace('Birthplace: ', '')})
        else:
            grave.update({'birth': str})
    except:
        print('error:', sys.exc_info())

def extractDeath(grave, str):
    if 'Death place:' in str:
        grave['death'] = str.split('\n')[0]
        grave['deathplace'] = str.split('\n')[1].replace('Death place: ', '')
    else:
        grave['death'] = str
