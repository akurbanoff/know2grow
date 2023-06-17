FROM python:3.11.0rc1

RUN mkdir /know2grow

WORKDIR /know2grow

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD gunicorn src.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000