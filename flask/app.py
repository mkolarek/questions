from flask import Flask, render_template, request, redirect, url_for
import psycopg
import requests

import json
import random
import time

app = Flask(__name__)
app.config["SECRET_KEY"] = "your secret key"

DB_CONN_STRING = "host=localhost dbname=wiki user=wiki password=wiki"
OLLAMA_HOST = "http://localhost:11434"

EXAMPLE_QUESTION = {
    "question_text": "Question text?",
    "answers": [
        {"selection": "a", "answer_text": "First answer"},
        {"selection": "b", "answer_text": "Second answer"},
        {"selection": "c", "answer_text": "Third answer"},
        {"selection": "d", "answer_text": "Fourth answer"},
    ],
    "correct_answer": "a",
}

app.logger.info("Getting number of articles...")

tic = time.perf_counter()
with psycopg.connect("host=127.0.0.1 dbname=wiki user=wiki password=wiki") as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(title) FROM wiki.wiki;")
        for record in cur:
            app.logger.info("Number of articles: %s", record[0])
            NUMBER_OF_ROWS = record[0]
toc = time.perf_counter()
app.logger.info("Number of articles fetched in %0.4f seconds.", toc - tic)


def get_random_article():
    row_id = random.randrange(NUMBER_OF_ROWS)

    with psycopg.connect(DB_CONN_STRING) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT title, \"revision_text__VALUE\"
                FROM wiki.wiki 
                WHERE row_id = {};""".format(row_id)
            )
            for record in cur:
                app.logger.info("Article title and row_id: %s, %s", record[0], row_id)
                return record


def generate_question(article_content):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "model": "llama3",
        "prompt": "Please generate a multiple-choice question with four possible answers, based on the following article: {}. Base your question only on the provided article content. Only respond with a JSON response. Base your JSON response on the following example {}".format(
            article_content, EXAMPLE_QUESTION
        ),
        "stream": False,
    }

    response = requests.post(
        OLLAMA_HOST + "/api/generate", headers=headers, data=json.dumps(data)
    )

    app.logger.info("Response: %s", response.json())

    question = (
        "{" + response.json()["response"].split("{", 1)[1].rsplit("}", 1)[0] + "}"
    )

    app.logger.info("Question: %s", question)

    return question


@app.route("/question", methods=["GET", "POST"])
def question():
    if request.method == "POST":
        if request.form["answer"] == request.form["correct_answer"]:
            app.logger.info("Correct answer!")
        else:
            app.logger.info("Wrong answer.")
        return redirect(
            url_for(
                "result",
                answer=request.form["answer"],
                correct_answer=request.form["correct_answer"],
            )
        )

    app.logger.info("Getting random article...")

    tic = time.perf_counter()
    random_article = get_random_article()
    toc = time.perf_counter()
    app.logger.info("Article fetched in %0.4f seconds.", toc - tic)

    app.logger.info("Generating question...")
    tic = time.perf_counter()
    question_string = generate_question(article_content=random_article)
    toc = time.perf_counter()
    app.logger.info("Question generated in %0.4f seconds.", toc - tic)

    question_json = json.loads(question_string)
    question_json["article_title"] = random_article[0]
    question_json["article_link"] = "https://en.wikipedia.org/wiki/{}".format(
        random_article[0].replace(" ", "_")
    )
    random.shuffle(question_json["answers"])

    return render_template("question.html", question=question_json)


@app.route("/question/result", methods=["GET"])
def result():
    app.logger.info(
        "Request content on result page: %s, %s",
        request.args["answer"],
        request.args["correct_answer"],
    )
    return render_template(
        "result.html",
        answer=request.args["answer"],
        correct_answer=request.args["correct_answer"],
    )
