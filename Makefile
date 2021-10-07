DB_NAME = csv_db
TABLES_DICT = /tmp/tables.pickle

build:
	docker build -t pg .

run:
	docker run --rm --name pg -e POSTGRES_PASSWORD=123 -v $(csv_dir):/csv_dir -d pg && \
	docker exec pg python load.py --csv-dir=/csv_dir --db-name=$(DB_NAME) --tables-dict=$(TABLES_DICT) && \
	docker exec -it pg psql -U postgres $(DB_NAME); \
	docker stop pg

run_dev:
	docker run --rm --name pg -e POSTGRES_PASSWORD=123 -v $(shell /bin/pwd)/src:/src -v $(csv_dir):/csv_dir -d pg && \
	docker exec pg python load.py --csv-dir=/csv_dir --db-name=$(DB_NAME) --tables-dict=$(TABLES_DICT) && \
	docker exec -it pg bash; \
	docker stop pg
