FROM apache/airflow:2.10.5

USER airflow

# Use constraints file to ensure compatibility
RUN pip install --no-cache-dir \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-3.8.txt" \
    pyspark \
    elasticsearch \
    apache-airflow-providers-apache-spark \
    "apache-airflow-providers-openlineage>=1.8.0"