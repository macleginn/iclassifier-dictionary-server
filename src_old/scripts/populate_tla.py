import sqlite3
import json
from pprint import pprint

import LibDictionary as ld


def process_record(record_dict):
    entry = record_dict['name']
    if 'en' in record_dict['translations']:
        short_meaning = record_dict['translations']['en']
    else:
        short_meaning = f"de: {record_dict['translations']['de']}"
    string_id = f'{entry} {short_meaning}'
    meaning = f"en: {record_dict['translations'].get('en', '')}; de: {record_dict['translations'].get('de', '')}"
    return ld.DictionaryEntry(
        string_id = string_id,
        entry = entry,
        short_meaning = short_meaning,
        meaning = meaning,
        examples = '',
        comments = '')


conn = sqlite3.connect('../../data/dictionary.sqlite')
cursor = conn.cursor()
cursor.execute("""
DROP TABLE IF EXISTS tla;
""")
cursor.execute("""
create table tla (
       id integer primary key not null,
       `string_id` text not null,
       entry text not null,
       `short_meaning` text,
       meaning text,
       examples text,
       comments text
);""")

with open('../../dictionaties_raw/aaew_wlist_small.json', 
          'r',
          encoding='utf-8') as inp:
    aaew_dict = json.load(inp)
    for key, value in aaew_dict.items():
        entry_id = int(key)
        entry = process_record(value)
        cursor.execute(
            """
            INSERT INTO tla 
            (
                id,
                `string_id`,
                entry,
                `short_meaning`,
                meaning,
                examples,
                comments
            )
            VALUES (?,?,?,?,?,?,?)""",
            (entry_id,
             entry.string_id,
             entry.entry,
             entry.short_meaning,
             entry.meaning,
             entry.examples,
             entry.comments))

conn.commit()
