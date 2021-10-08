import argparse
import pandas as pd
import pickle
import psycopg2
import re
import sys

from time import time
from pandas.core.frame import DataFrame
from pandas.core.series import Series
from pathlib import Path
from psycopg2.extensions import connection, ISOLATION_LEVEL_AUTOCOMMIT

DATA_TYPES = {
    'int64': 'int8',
    'float64': 'float8',
    'bool': 'bool',
    'object': 'text',
}

def create_db(conn: connection, db_name: str) -> None:
    if not db_name.replace('_', '').isalnum():
        raise ValueError("db_name is unsafe")

    conn.cursor().execute(f"create database {db_name}")

def simplify_name(fname: str) -> str:
    fname = re.sub('\.csv$', '', fname)
    fname = re.sub('[^a-zA-Z0-9]', '_', fname)
    return fname.lower()

def copy_expression(tname: str, fields: Series) -> str:
    if 'bool' not in fields.values:
        return tname

    tfields = list()
    for field, ftype in fields.items():
        tfield = simplify_name(field)
        if ftype == 'bool':
            tfields.append(f'case when "{tfield}" = true then \'True\' else \'False\' end as "{tfield}"')
        else:
            tfields.append(f'"{tfield}"')

    return f"(select {','.join(tfields)} from {tname})"


def create_table(conn: connection, fname: str, fields: Series) -> dict:
    
    tname = simplify_name(fname)
    meta = {
        'copy_expr': copy_expression(tname, fields),
        'tablename': tname,
        'filename': fname,
        'fields': []
    }

    tfields = list()
    for field, ftype in fields.items():
        tfield = simplify_name(field)
        meta['fields'].append(field)

        if ftype.name not in DATA_TYPES:
            raise ValueError(f"{ftype.name} is not supported")

        tfields.append(f'"{tfield}" {DATA_TYPES[ftype.name]}')

    conn.cursor().execute(f"create table {tname} ({','.join(tfields)})")
    return meta

def load(conn: connection, csv_file: Path) -> dict:

    df = pd.read_csv(csv_file, iterator=True, chunksize=10000)

    dtypes = None
    for chunk in df:
        if dtypes is None or (chunk.dtypes > dtypes).any():
            dtypes = chunk.dtypes

    meta = create_table(conn, csv_file.name, dtypes)

    with csv_file.open('r') as f:
        conn.cursor().copy_expert(f"copy {meta['tablename']} from stdin with header csv", f)

    return meta


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load CSV files into DB")
    parser.add_argument(
        "--just-compile",
        action="store_true",
        help="Don't do actual load but just compile the script to speedup the first load",
    )
    parser.add_argument(
        "--csv-dir",
        type=str,
        help="CSV directory"
    )
    parser.add_argument(
        "--db-name",
        type=str,
        help="Database name"
    )
    parser.add_argument(
        "--tables-meta",
        type=str,
        help="Dictionary of table names to file names"
    )
    args = parser.parse_args()
    if args.just_compile:
        sys.exit(0)

    conn = psycopg2.connect(host='localhost', user='postgres')
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    create_db(conn, args.db_name)
    conn.cursor().close()
    conn.close()

    # FIXME do I need to create DB at all?
    conn = psycopg2.connect(database=args.db_name, host='localhost', user='postgres')
    
    meta = list()
    for f in Path(args.csv_dir).iterdir():
        if not f.name.endswith('.csv'):
            continue

        print(f"Loading [{f.name}] ... ", flush=True, end='')
        t = time()
        meta.append(load(conn, f))
        print('{:.3f} s'.format(time() - t))

    conn.commit()
    conn.cursor().close()
    conn.close()

    with open(args.tables_meta, 'wb') as fp:
        pickle.dump(meta, fp)
