from pyspark.sql import SparkSession
from elasticsearch import Elasticsearch

spark = SparkSession.builder.appName("IndexData").getOrCreate()

data = [
    ("Alice", 34, "Paris"),
    ("Bob", 45, "Lyon"),
    ("Cathy", 29, "Berlin")
]

df = spark.createDataFrame(data, ["name", "age", "city"])
records = df.toPandas().to_dict(orient="records")

es = Elasticsearch("http://elasticsearch:9200")

for r in records:
    es.index(index="people", document=r)

spark.stop()
