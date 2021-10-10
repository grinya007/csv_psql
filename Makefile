build:
	docker build -t pg .

run:
	touch $(csv_dir)/.pgcli_history && \
	docker run --rm --name pg \
		-v $(csv_dir):/csv \
		-v $(csv_dir)/.pgcli_history:/var/lib/postgresql/.config/pgcli/history \
		-d pg && \
	docker exec pg python load.py && \
	docker exec -it pg pgcli && \
	docker exec -it pg python dump.py; \
	docker stop pg

run_dev:
	docker run --rm --name pg -v $(shell /bin/pwd)/src:/src -v $(csv_dir):/csv -d pg && \
	docker exec pg python load.py && \
	docker exec -it pg bash && \
	docker exec -it pg python dump.py; \
	docker stop pg
