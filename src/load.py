import argparse
import os
import pandas as pd
import pickle
import psycopg2
import re
import sys

from time import time, sleep
from pandas.core.series import Series
from pathlib import Path
from psycopg2 import OperationalError
from psycopg2.extensions import connection

DATA_TYPES = {
    'int64': 'int8',
    'float64': 'float8',
    'bool': 'bool',
    'object': 'text',
}

CSV_DIR = os.getenv('CSV_DIR')
TABLES_META = os.getenv('TABLES_META')


def simplify_name(fname: str) -> str:
    fname = re.sub('\.csv$', '', fname)
    fname = re.sub('[^a-zA-Z0-9]', '_', fname)
    return fname.lower()


def copy_expression(tname: str, fields: Series) -> str:
    tfields = list()
    for field, ftype in fields.items():
        tfield = simplify_name(field)
        if ftype == 'bool':
            tfields.append(
                f'case when "{tfield}" = true then \'TRUE\''
                f' else \'FALSE\' end as "{tfield}"'
            )
        elif ftype == 'float64':
            tfields.append(
                f'case when "{tfield}"::text not like \'%.%\''
                f' then "{tfield}"::text||\'.0\''
                f' else "{tfield}"::text end as "{tfield}"'
            )
        else:
            tfields.append(f'"{tfield}"')

    tfields = ','.join(tfields)
    return f"(select {tfields} from {tname} order by id)"


def create_table(conn: connection, fname: str, fields: Series) -> dict:
    tname = simplify_name(fname)
    meta = {
        'copy_expr': copy_expression(tname, fields),
        'tablename': tname,
        'filename': fname,
        'fields': [],
        'tablefields': [],
        'remove_newline': True,
    }

    tfields = list()
    for field, ftype in fields.items():
        tfield = simplify_name(field)
        meta['fields'].append(field)
        meta['tablefields'].append(tfield)

        if ftype.name not in DATA_TYPES:
            raise ValueError(f"{ftype.name} is not supported")

        tfields.append(f'"{tfield}" {DATA_TYPES[ftype.name]}')

    conn.cursor().execute(
        f"create table {tname}"
        f" (id serial, {','.join(tfields)})"
    )
    return meta


def load(conn: connection, csv_file: Path) -> dict:
    df = pd.read_csv(csv_file, iterator=True, chunksize=10000)

    dtypes = None
    for chunk in df:
        if dtypes is None or (chunk.dtypes > dtypes).any():
            dtypes = chunk.dtypes

    meta = create_table(conn, csv_file.name, dtypes)

    fields = ','.join([f'"{f}"' for f in meta['tablefields']])
    with csv_file.open('r') as f:
        conn.cursor().copy_expert(
            f"copy {meta['tablename']}({fields})"
            f" from stdin with header csv", f
        )
    with csv_file.open('rb') as f:
        f.seek(-1, os.SEEK_END)
        if f.read(1) == b'\n':
            meta['remove_newline'] = False

    return meta


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load CSV files into DB")
    parser.add_argument(
        "--just-compile",
        action="store_true",
        help="Don't do actual load but just compile"
             " the script to speedup the first load",
    )
    args = parser.parse_args()
    if args.just_compile:
        sys.exit(0)

    # FIXME perhaps there's a better way to get notified when DB is up
    retries = 10
    for retry in range(1, retries+1):
        if retry == retries:
            # let it die
            conn = psycopg2.connect(host='localhost', user='postgres')
        else:
            try:
                conn = psycopg2.connect(host='localhost', user='postgres')
            except OperationalError:
                sleep(0.2)

    meta = list()
    total_t = time()
    for f in Path(CSV_DIR).iterdir():
        if not f.name.endswith('.csv'):
            continue

        print(f"Loading [{f.name}] ... ", flush=True, end='')
        t = time()
        meta.append(load(conn, f))
        print('{:.3f} s'.format(time() - t))

    print('Done in {:.3f} s'.format(time() - total_t))

    conn.commit()
    conn.cursor().close()
    conn.close()

    with open(TABLES_META, 'wb') as fp:
        pickle.dump(meta, fp)
