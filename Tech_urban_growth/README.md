Tech and Urban Growth – ETL Data Pipeline
📌 Project Overview
Tech and Urban Growth is a complete data engineering pipeline built with Apache Airflow, MongoDB, PostgreSQL, and Streamlit. It automates the ETL (Extract, Transform, Load) process of collecting, cleaning, and storing data related to population, urbanization, and air quality from various public APIs. The final data is visualized in a dynamic dashboard for analysis and exploration.

🌐 APIs Used
OpenWeatherMap (air quality)
https://openweathermap.org/api/air-pollution

World Bank - Urban Population
https://data.worldbank.org/indicator/SP.URB.TOTL.IN.ZS

World Bank - Total Population
https://data.worldbank.org/indicator/SP.POP.TOTLa

🧠 MongoDB vs PostgreSQL
PostgreSQL is used strictly as the backend database for Apache Airflow, handling metadata, DAG runs, logs, and task states.

MongoDB is the target NoSQL database used for storing the cleaned datasets from the ETL pipeline, thanks to its flexibility with semi-structured JSON-like data.

🚀 How to Launch the Project with docker-compose
Run the following command in the root directory of the project:

docker-compose up --build
docker-compose up airflow-init
docker-compose up -d

This will start the following services:

postgres: Metadata storage for Airflow

init: Initializes the Airflow database

airflow_webserver: Airflow UI (port 8080)

airflow_scheduler: DAG scheduler

mongo: MongoDB database (port 27017)

streamlit_app: Visualization dashboard (port 8501)

Ensure that Docker is installed and running on your machine.

🔁 How to Trigger the DAG and View Logs
Visit http://localhost:8080 to open the Airflow Web UI.

Log in with:

Username: airflow

Password: airflow

Enable the DAG named TechAndUrbanGrowth.

Click the play ▶️ button to trigger a manual run.

To view logs:

Click on the DAG

Click on a task (e.g., transform_population_data)

Open the logs tab

📊 How to Open the Streamlit Dashboard
Visit http://localhost:8501 in your browser. The Streamlit app will load the latest processed data from MongoDB and display interactive charts related to:

Population trends

Urbanization rates

Air quality comparisons

🔄 How XCom Is Used
XComs (short for cross-communications) in Airflow are used to pass data between tasks during DAG execution. In this project:

Transformed datasets are pushed to XCom after cleaning.

The load_all_to_mongo task pulls from XCom to load all datasets into the appropriate MongoDB collections.

This keeps the workflow modular, separating ingestion, transformation, and loading logic.