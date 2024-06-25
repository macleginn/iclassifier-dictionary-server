import sqlite3

import LibDictionary as ld


def process_line(line):
    traditional, simplified, rest = line.split(' ', 2)
    print(f"{traditional} | {simplified} | {rest}")
    translit, meanings = rest.split('] ', 1)
    translit = translit[1:]
    meanings = meanings.strip()[1:-1]
    short_meaning, *other_meanings_arr = meanings.split('/', 1)
    if other_meanings_arr:
        other_meanings = other_meanings_arr[0]
    else:
        other_meanings = ''
    
    entry = f"{traditional} ({simplified}, [{translit}])"
    return ld.DictionaryEntry(
        string_id = traditional,
        entry = entry,
        short_meaning = short_meaning,
        meaning = other_meanings,
        examples = '',
        comments = '')

conn = sqlite3.connect('../../data/dictionary.sqlite')
cursor = conn.cursor()
cursor.execute("""
DROP TABLE IF EXISTS chinese;
""")
cursor.execute("""
create table chinese (
       id integer primary key not null,
       `string_id` text not null,
       entry text not null,
       `short_meaning` text,
       meaning text,
       examples text,
       comments text
);""")

with open('../../dictionaties_raw/cedict_1_0_ts_utf-8_mdbg.txt', 
          'r',
          encoding='utf-8') as inp:
    for l in inp:
        if l.startswith('#'):
            continue
        entry = process_line(l)
        cursor.execute(
            """
            INSERT INTO chinese 
            (
                `string_id`,
                entry,
                `short_meaning`,
                meaning,
                examples,
                comments
            )
            VALUES (?,?,?,?,?,?)""",
            (entry.string_id,
             entry.entry,
             entry.short_meaning,
             entry.meaning,
             entry.examples,
             entry.comments))

conn.commit()
