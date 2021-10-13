import argparse
import os
import pickle
import psycopg2
import sys

from threading import Thread
from time import time
from pathlib import Path
from psycopg2.extensions import connection
from queue import Queue

CSV_DIR = os.getenv('CSV_DIR')
TABLES_META = os.getenv('TABLES_META')
THREADS = 2

class Dumper ():
    def __init__(self, n_threads: int, conn: dict):
        self.n_threads = n_threads
        self.conn = conn

        self.q = Queue()
        self.t = []
        for i in range(n_threads):
            self.t.append(Thread(target=self.worker))
            self.t[i].daemon = True
            self.t[i].start()


    def worker(self) -> None:
        while True:
            task = self.q.get()

            try:
                self.dump(task)
            except Exception as e:
                print(f"Failed to dump {task['tablename']}: {e}")

            self.q.task_done()

    def wait(self) -> None:
        self.q.join()

    def enque(self, task: dict) -> None:
        self.q.put(task)

    def dump(self, task: dict) -> None:
        # FIXME create a connection per thread, not per task
        conn = psycopg2.connect(**self.conn)

        with task['file'].open('w') as f:
            f.write(','.join(task['fields']) + "\n")
            conn.cursor().copy_expert(f"copy {task['copy_expr']} to stdout csv", f)
        if task['remove_newline']:
            with task['file'].open('rb+') as f:
                f.seek(-1, os.SEEK_END)
                if f.read(1) == b'\n':
                    f.seek(-1, os.SEEK_END)
                    f.truncate()

        print(f"Done dumping [{task['filename']}]")
        conn.cursor().close()
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dump DB tables to CSV files")
    parser.add_argument(
        "--just-compile",
        action="store_true",
        help="Don't do actual dump but just compile the script to speedup the first dump",
    )
    parser.add_argument(
        "--no-confirm",
        action="store_true",
        help="Skip confirmation",
    )
    parser.add_argument(
        "--table",
        type=str,
        help="Dump specific table",
    )
    args = parser.parse_args()
    if args.just_compile:
        sys.exit(0)

    if not args.no_confirm:
        confirm = input('Do you want to dump db? [y/N]: ')
        if confirm != 'y':
            sys.exit(0)

    dumper = Dumper(THREADS, dict(host='localhost', user='postgres'))

    with open(TABLES_META, 'rb') as fp:
        tables = pickle.load(fp)

    for table in tables:
        if args.table and args.table != table['tablename']:
            continue
        table['file'] = Path(CSV_DIR) / table['filename']
        dumper.enque(table)

    t = time()
    dumper.wait()
    print('Done in {:.3f} s'.format(time() - t))
