import argparse
import json

from pyspark.sql import SparkSession

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=str, help="Input XML file path.")
parser.add_argument("--output_schema", type=str, help="Output schema file path.")

args = parser.parse_args()

spark = SparkSession.builder.appName("Infer schema").getOrCreate()

df = (
    spark.read.format("xml")
    .options(rowTag="page")
    .options(samplingRatio=0.0001)
    .load(args.input)
)

schema = df.schema.json()
schema_json = json.loads(schema)

with open(args.output_schema, "w") as fp:
    json.dump(schema_json, fp)
