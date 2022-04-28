image = csv_psql
container = csv_psql_$(shell /bin/date +%s)
abs_csv_dir = $(abspath $(csv_dir))

build:
	docker build -t $(image) .

run:
	touch $(abs_csv_dir)/.pgcli_history && \
	docker run --rm --name $(container) \
		-v $(abs_csv_dir):/csv \
		-v $(abs_csv_dir)/.pgcli_history:/root/.config/pgcli/history \
		-d $(image) && \
	docker exec $(container) python load.py && \
	docker exec -it $(container) pgcli -U postgres && \
	docker exec -it $(container) python dump.py; \
	docker stop $(container)

run_dev:
	docker run --rm --name $(container) \
		-v $(shell /bin/pwd)/src:/src \
		-v $(abs_csv_dir):/csv \
		-d $(image) && \
	docker exec -it $(container) bash; \
	docker stop $(container)
