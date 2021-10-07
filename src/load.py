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

def create_table(conn: connection, tname: str, fields: Series) -> None:
    if not tname.replace('_', '').isalnum():
        raise ValueError("table name is unsafe")
    
    tfields = list()
    for field, ftype in fields.items():
        field = simplify_name(field)
        if ftype.name not in DATA_TYPES:
            raise ValueError(f"{ftype.name} is not supported")

        tfields.append(f'"{field}" {DATA_TYPES[ftype.name]}')

    conn.cursor().execute(f"create table {tname} ({','.join(tfields)})")


def load(conn: connection, tname: str, csv_file: Path) -> None:

    df = pd.read_csv(csv_file, iterator=True, chunksize=10000)

    dtypes = None
    for chunk in df:
        if dtypes is None or (chunk.dtypes > dtypes).any():
            dtypes = chunk.dtypes

    create_table(conn, tname, dtypes)

    with csv_file.open('r') as f:
        conn.cursor().copy_expert(f"copy {tname} from stdin with header csv", f)


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
        "--tables-dict",
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
    
    tnames = dict()
    for f in Path(args.csv_dir).iterdir():
        if not f.name.endswith('.csv'):
            continue

        tname = simplify_name(f.name)
        tnames[tname] = f.name

        print(f"Loading [{f.name} => {tname}] ... ", flush=True, end='')
        t = time()
        load(conn, tname, f)
        print('{:.3f} s'.format(time() - t))

    conn.commit()
    conn.cursor().close()
    conn.close()

    # FIXME will need a way to preserve field names as well
    with open(args.tables_dict, 'wb') as fp:
        pickle.dump(tnames, fp)
