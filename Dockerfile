FROM python:3.8-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
# RUN python manage.py migrate --databases==users
COPY . .
CMD ["python", "manage.py", "migrate", "--database=users"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

