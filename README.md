# Technical-Case
Repository for Data &amp; Analytics Case Study

## Tools/Softwares Used
* **PostgreSQL** as main database
* **Airflow** for data ingestion and orchestration
* **dbt** for data transformation

## Local Setup
Install airflow and dbt-core
```
pip install airflow dbt-core dbt-postgres
```

## Cloud Setup
Create an airflow and dbt instance in our prefered cloud providor

## Data Ingestion
In your airflow instance, set up the `postgres_default` connection to point to your PostgreSQL database.

Add the `comics_ingestion.py` file to the dags folder of your airflow instance.

The code is configured to start the ingestion from the first comic. If you want to start at a later comic number, change the `default_var` parameter to the value you want in the code segment below:

```python
comic_number = int(Variable.get("comic_number", default_var=0)) + 1
```

## Data transformation
Set up your `profiles.yml` to connect to your PostgreSQL dadatabase.

Then run:
```
dbt run
```