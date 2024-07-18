# questions

A collection of `pyspark` scripts exploring Wikipedia data dumps and how they can be used to generate questions.

## Description

More information about this project can be found in its' accompanying dev journal here [Asking questions](https://mkolarek.github.io).

## Getting started

This project uses [poetry](https://python-poetry.org/) for Python dependency management and running the scripts, [Docker](https://www.docker.com/) for containerization, and [GNU Make](https://www.gnu.org/software/make/) as a build tool. With these three tools installed, you can run

`make WIKIDATA_DUMP=<path_to_xml.bz2_file`

and all the necessary steps should be done out of the box.

### Install

The Python dependencies of the project are listed in the `pyproject.toml` and can be installed by running

`make install`

or 

`poetry install`

### Preparing the environment

For loading the data into PostgreSQL, we need to build our own extended `postgres` Docker image that prepares the `wiki` database. To do this, we run:

`make build`

After a successful build, we can run the container with

`make run`

and stop it with 

`make stop`.

## Running the ETL jobs

There are three separate ETL jobs that we can run:

### Schema discovery

`make schema.json`

infers the schema of our dataset and stores it in `schema.json`

### Sample generation

`make sample`

uses the inferred `schema.json` and creates a sample of our data in the `sample/` directory, in order to make further data exploration easier and quicker.

### Cleaning up and loading the data

`make load`

uses the inferred `schema.json` and flattens our dataset, filtering out redirect articles and storing the data into the `wiki` database in our `wiki-postgres` container.

## Cleaning up

We can clean up our environment by running

`make clean`

| WARNING: This removes all of our generated data artifacts, as well as our extended `postgres` Docker image.
