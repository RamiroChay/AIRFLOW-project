FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir streamlit pymongo pandas

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
