SPARK-XML := com.databricks:spark-xml_2.12:0.18.0
POSTGRESQL := org.postgresql:postgresql:42.7.3

all: install build run schema.json sample load

install:
	poetry install

build:
	docker build -t postgres:local .
	mkdir -p data

run: build
	docker run -d \
		--name wiki-postgres \
		-e POSTGRES_PASSWORD=postgres \
		-p 5432:5432 \
		-e PGDATA=/var/lib/postgresql/data/pgdata \
		postgres:local

stop:
	docker rm $$(docker stop $$(docker ps -a -q --filter="name=wiki-postgres"))

schema.json:
	poetry run \
        spark-submit \
        --packages ${SPARK-XML} \
        --driver-memory 7g \
        infer_schema.py \
        --input ${WIKIDATA_DUMP} \
        --output_schema schema.json

sample: schema.json
	poetry run \
		spark-submit \
		--packages ${SPARK-XML} \
		--driver-memory 7g \
		sample.py \
		--input ${WIKIDATA_DUMP} \
		--input_schema schema.json \
		--output_sample sample

load: run schema.json
	poetry run \
		spark-submit \
		--packages ${POSTGRESQL},${SPARK-XML} \
		--driver-memory 7g \
		load_to_postgres.py \
		--input ${WIKIDATA_DUMP} \
		--input_schema schema.json

clean: stop
	docker image rm postgres:local
	rm -rf sample/
	rm -f schema.json
	rm -rf .venv/
