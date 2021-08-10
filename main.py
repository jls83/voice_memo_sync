import datetime
import os
import shutil
import sqlite3
import time

DATABASE_FILE_PATH = '/Users/jls83/Library/Application Support/com.apple.voicememos/Recordings/CloudRecordings.db'
QUERY_STRING = 'SELECT ZCUSTOMLABEL, ZPATH, ZDATE FROM ZCLOUDRECORDING'

DESTINATION_PATH_TEMPLATE = '/Users/jls83/Documents/not_recordings/{}.m4a'


def get_rows_from_db():
    rows = []
    try:
        conn = sqlite3.connect(DATABASE_FILE_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        rows = [dict(row) for row in cur.execute(QUERY_STRING).fetchall()]
    except sqlite3.Error as e:
        print('SQLite failed to read from table', e)
    finally:
        if conn:
            conn.close()

    return rows


def generate_os_last_edited_date(time_float):
    time_diff = datetime.timedelta(seconds=time_float)
    dt_obj = datetime.datetime(2001, 1, 1) + time_diff
    return time.mktime(dt_obj.timetuple())


def copy_files(rows):
    for row in rows:
        src = row['ZPATH']
        row_label = row['ZCUSTOMLABEL'].replace('/', '-')
        dst = DESTINATION_PATH_TEMPLATE.format(row_label)
        create_time = generate_os_last_edited_date(row['ZDATE'])

        try:
            shutil.copy2(src, dst)
            os.utime(dst, (time.time(), create_time))
        except OSError:
            print('\tThere was an error copying {}'.format(src))
            continue
        except shutil.SameFileError:
            print('\tThere was an error copying {} to {}'.format(src, dst))
            dst = DESTINATION_PATH_TEMPLATE.format(row_label + '_1')
            shutil.copy2(src, dst)


if __name__ == '__main__':
    rows = get_rows_from_db()
    copy_files(rows)
