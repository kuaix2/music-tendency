from pyspark.sql import SparkSession
import os
import glob

DATA_DIR = "/opt/airflow/data"
OUTPUT_DIR = os.path.join(DATA_DIR, "parquet")
os.makedirs(OUTPUT_DIR, exist_ok=True)

spark = SparkSession.builder.appName("csv_to_parquet").getOrCreate()

# Find all CSV files in data folder
csv_files = glob.glob(os.path.join(DATA_DIR, "*.csv"))

for csv_file in csv_files:
    df = spark.read.option("header", True).option("inferSchema", True).csv(csv_file)
    
    base_name = os.path.basename(csv_file).replace(".csv", ".parquet")
    output_path = os.path.join(OUTPUT_DIR, base_name)
    
    df.write.mode("overwrite").parquet(output_path)
    print(f"Converted {csv_file} -> {output_path}")

spark.stop()
