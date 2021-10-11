abs_csv_dir = $(abspath $(csv_dir))

build:
	docker build -t pg .

run:
	touch $(abs_csv_dir)/.pgcli_history && \
	docker run --rm --name pg \
		-v $(abs_csv_dir):/csv \
		-v $(abs_csv_dir)/.pgcli_history:/root/.config/pgcli/history \
		-d pg && \
	docker exec pg python load.py && \
	docker exec -it pg pgcli -U postgres && \
	docker exec -it pg python dump.py; \
	docker stop pg

run_dev:
	docker run --rm --name pg \
		-v $(shell /bin/pwd)/src:/src \
		-v $(abs_csv_dir):/csv \
		-d pg && \
	docker exec -it pg bash; \
	docker stop pg
