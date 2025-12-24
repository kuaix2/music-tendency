# Base image Airflow
FROM apache/airflow:2.9.2

USER root

# Installer Spark, pyspark, Elasticsearch client et provider Airflow pour Spark
RUN pip install --no-cache-dir \
    pyspark \
    elasticsearch \
    apache-airflow-providers-apache-spark

USER airflow
