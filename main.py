import os

from pyspark.sql import functions as F
from pyspark.sql import types as T
# from pyspark.sql import SparkSession

import mlflow

from pip._internal.operations import freeze


def main():
    for dep in freeze.freeze():
        print(f"DEPENDENCY {dep}")


    from dbruntime.spark_connection import (
        initialize_spark_connection,
        is_pinn_mode_enabled,
    )

    spark_handles, _ = initialize_spark_connection(is_pinn_mode_enabled())
    sc = spark_handles["sc"]
    spark = spark_handles["spark"]

    try:
        sc.addPyFile(os.path.abspath("databricks_repo_sync.zip"))
    except Exception:
        # If the file was already added, continue
        pass

    from databricks_repo_sync_test import plus_one

    # spark = SparkSession.builder.getOrCreate()
    df = spark.createDataFrame([(0,),(1,)], ("i",))
    plus_one_udf = F.udf(plus_one, T.IntegerType())
    df = df.withColumn("j", plus_one_udf("i"))
    df.show()
    result = df.select(
        F.avg("j").alias("avg"),
        F.max("j").alias("max"),
        F.min("j").alias("min"),
    ).collect()[0]
    mlflow.log_metric("j_avg", result.avg)
    mlflow.log_metric("j_min", result.min)
    mlflow.log_metric("j_max", result.max)


if __name__ == "__main__":
    main()
