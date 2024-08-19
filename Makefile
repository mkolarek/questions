SPARK-XML := com.databricks:spark-xml_2.12:0.18.0
POSTGRESQL := org.postgresql:postgresql:42.7.3

all: install schema.json sample load add_row_id download_model web

install:
	poetry install

build:
	docker build -t postgres:local postgres/

run: build
	docker run -d \
		--name wiki-postgres \
		-p 5432:5432 \
		-v /custom/mount:/var/lib/postgresql/data \
		-e POSTGRES_PASSWORD=postgres \
		-e PGDATA=/var/lib/postgresql/data/pgdata \
		postgres:local
	
	docker run -d \
		--name ollama \
		-p 11434:11434 \
		-v ollama:/root/.ollama \
		--gpus=all \
		ollama/ollama

start:
	docker start wiki-postgres
	docker start ollama

stop:
	docker stop wiki-postgres
	docker stop ollama

rm: stop
	docker rm wiki-postgres
	docker rm ollama

schema.json:
	poetry run \
	    spark-submit \
		--packages ${SPARK-XML} \
		--driver-memory 7g \
		pyspark/infer_schema.py \
		--input ${WIKIDATA_DUMP} \
		--output_schema schema.json

sample: schema.json
	poetry run \
		spark-submit \
		--packages ${SPARK-XML} \
		--driver-memory 7g \
		pyspark/sample.py \
		--input ${WIKIDATA_DUMP} \
		--input_schema schema.json \
		--output_sample sample

load: run schema.json
	poetry run \
		spark-submit \
		--packages ${POSTGRESQL},${SPARK-XML} \
		--driver-memory 7g \
		pyspark/load_to_postgres.py \
		--input ${WIKIDATA_DUMP} \
		--input_schema schema.json

add_row_id:
	docker exec \
		-e PGPASSWORD=wiki \
		wiki-postgres \
		psql \
		-U wiki \
		-h 127.0.0.1 \
		-d wiki \
		-c 'ALTER TABLE wiki.wiki ADD row_id SERIAL;'

download_model: run
	docker exec -it ollama ollama pull llama3

web: start
	poetry run \
		flask \
		--app=flask/app.py \
		run

clean: rm
	docker image rm postgres:local
	rm -rf sample/
	rm -f schema.json
	rm -rf .venv/
