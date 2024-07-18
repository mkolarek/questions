import argparse
import json

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=str, help="Input XML file path.")
parser.add_argument("--input_schema", type=str, help="Input schema file path.")
parser.add_argument("--output_sample", type=str, help="Output sample directory path.")

args = parser.parse_args()

spark = SparkSession.builder.appName("Sample data").getOrCreate()

with open(args.input_schema) as f:
    schema_json = json.load(f)

schema = StructType.fromJson(schema_json)

df = (
    spark.read.format("xml")
    .options(rowTag="page")
    .schema(schema)
    .options(samplingRatio=0.0001)
    .load(args.input)
)

sample = df.sample(0.0001)

(
    sample.write.format("xml")
    .options(rowTag="page")
    .options(rootTag="pages")
    .options(compression="bzip2")
    .save(args.output_sample)
)
