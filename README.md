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
Create an airflow and dbt instances in our prefered cloud providor

## Data Ingestion
In your airflow instance, set up the `postgres_default` connection to point to your PostgreSQL database.

Add the `comics_ingestion.py` file to the dags folder of your airflow instance.

The code is configured to start the ingestion from the first comic. If you want to start at a later comic number, change the `default_var` parameter to the value you want in the code segment below:

```python
comic_number = int(Variable.get("comic_number", default_var=0)) + 1
```

The DAG is configured to run every monday, wednesday and friday at 6 am. If you want to trigger the automation at another time, change the `start_date` parameter in the `default_args` dict.

## Data transformation
Set up your `profiles.yml` to connect to your PostgreSQL dadatabase.

The airflow implementation is configured to trigger also the dbt transformations.

If you are using a local setup and want to keep this automation, set up a `dbt_project_path` variable in your airflow instance, pointing to the dbt project folder.

If you are using a cloud setup or don't want to trigger the automation on airflow, remove the `run_dbt` and `test_dbt` tasks from the DAG and setup your own automation.