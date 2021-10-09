build:
	docker build -t pg .

run:
	touch $(csv_dir)/psql_history.sql && \
	docker run --rm --name pg -v $(csv_dir):/csv -v $(csv_dir)/psql_history.sql:/var/lib/postgresql/.psql_history -d pg && \
	docker exec pg python load.py && \
	docker exec -it pg psql -U postgres && \
	docker exec -it pg python dump.py; \
	docker stop pg

run_dev:
	docker run --rm --name pg -v $(shell /bin/pwd)/src:/src -v $(csv_dir):/csv -d pg && \
	docker exec pg python load.py && \
	docker exec -it pg bash && \
	docker exec -it pg python dump.py; \
	docker stop pg
