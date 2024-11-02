FROM python:3.11

WORKDIR /app

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


COPY ./tasks_module ./tasks_module

CMD ["uvicorn", "tasks_module.main:app", "--host", "0.0.0.0", "--port", "8000"]

