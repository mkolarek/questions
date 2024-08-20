# questions

- A collection of `pyspark` scripts exploring Wikipedia data dumps and how they can be used to generate questions.
- A small `flask`-based web app that generates questions by using `llama3` deployed via `ollama`.

## Description

More information about this project can be found in its' accompanying dev journal here:
- [Asking questions (pt. 1)](https://mkolarek.github.io/posts/asking-questions-pt-1/)
- [Asking questions (pt. 2)](https://mkolarek.github.io/posts/asking-questions-pt-2/)

## Getting started

This project uses [poetry](https://python-poetry.org/) for Python dependency management and running the scripts, [Docker](https://www.docker.com/) for containerization, and [GNU Make](https://www.gnu.org/software/make/) as a build tool. With these three tools installed, you can run

`make WIKIDATA_DUMP=<path_to_xml.bz2_file>`

and all the necessary steps should be done out of the box.

To clean everything up, run

`make clean`
