FROM apache/airflow:2.8.1

RUN pip install --no-cache --upgrade pip
RUN pip install --no-cache --upgrade setuptools
RUN pip install --no-cache --upgrade wheel
RUN pip install --no-cache --upgrade psycopg2-binary
RUN pip install --no-cache --upgrade apache-airflow-providers-postgres
RUN pip install --no-cache --upgrade apache-airflow-providers-sftp
RUN pip install --no-cache --upgrade apache-airflow-providers-ssh
RUN pip install --no-cache pymongo


USER airflow