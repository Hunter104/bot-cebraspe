FROM python:latest


WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python", "main.py"]
