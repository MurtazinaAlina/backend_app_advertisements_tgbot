FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /code

ADD . .

RUN pip install -r requirements.txt

RUN python manage.py makemigrations
RUN python manage.py migrate

CMD python manage.py runserver 0.0.0.0:8000
