DB_NAME = csv_db
TABLES_META = /tmp/tables_meta.pickle

build:
	docker build -t pg .

run:
	docker run --rm --name pg -e POSTGRES_PASSWORD=123 -v $(csv_dir):/csv_dir -d pg && \
	docker exec pg python load.py --csv-dir=/csv_dir --db-name=$(DB_NAME) --tables-meta=$(TABLES_META) && \
	docker exec -it pg psql -U postgres $(DB_NAME) && \
	docker exec -it pg python dump.py --csv-dir=/csv_dir --db-name=$(DB_NAME) --tables-meta=$(TABLES_META); \
	docker stop pg

run_dev:
	docker run --rm --name pg -e POSTGRES_PASSWORD=123 -v $(shell /bin/pwd)/src:/src -v $(csv_dir):/csv_dir -d pg && \
	docker exec pg python load.py --csv-dir=/csv_dir --db-name=$(DB_NAME) --tables-meta=$(TABLES_META) && \
	docker exec -it pg bash && \
	docker exec -it pg python dump.py --csv-dir=/csv_dir --db-name=$(DB_NAME) --tables-meta=$(TABLES_META); \
	docker stop pg
