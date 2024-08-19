import argparse
import json

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, ArrayType

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=str, help="Input XML file path.")
parser.add_argument("--input_schema", type=str, help="Input schema file path.")

args = parser.parse_args()

spark = SparkSession.builder.appName("Load to Postgres").getOrCreate()


def flatten(schema, prefix=None):
    fields = []
    for field in schema.fields:
        name = (
            prefix + "." + "`" + field.name + "`" if prefix else "`" + field.name + "`"
        )
        dtype = field.dataType
        if isinstance(dtype, ArrayType):
            dtype = dtype.elementType
        if isinstance(dtype, StructType):
            fields += flatten(dtype, prefix=name)
        else:
            fields.append(
                name
                + " AS "
                + name.replace("`", "").replace(".", "_").replace(":", "_")
            )
    return fields


with open(args.input_schema) as f:
    schema_json = json.load(f)

schema = StructType.fromJson(schema_json)

df = spark.read.format("xml").options(rowTag="page").schema(schema).load(args.input)

(
    df.filter(df.redirect._title.isNull())
    .filter(~df.title.contains("Wikipedia:"))
    .filter(~df.title.contains("Template:"))
    .filter(~df.title.contains("Draft:"))
    .filter(~df.title.contains("Category:"))
    .filter(~df.title.contains("Portal:"))
    .filter(~df.title.contains("File:"))
    .createOrReplaceTempView("wiki")
)

flattened = spark.sql("SELECT {} FROM wiki".format(", ".join(flatten(schema))))

(
    flattened.write.format("jdbc")
    .option("url", "jdbc:postgresql://localhost/wiki")
    .option("dbtable", "wiki.wiki")
    .option("user", "wiki")
    .option("password", "wiki")
    .option("driver", "org.postgresql.Driver")
    .save()
)
