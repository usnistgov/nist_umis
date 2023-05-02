FROM python:3.10
ENV PYTHONUNBUFFERED 1
WORKDIR /app
RUN apt-get update && apt-get install -y vim python curl bash libmariadb-dev-compat libmariadb-dev default-mysql-client

COPY . /app
RUN pip install -r requirements.txt
#COPY ./app/entrypoint.sh /app/entrypoint.sh
# - TODO - Default values for image, add secret mgmt with docker-compose in production
#EXPOSE 8000
ENTRYPOINT /app/entrypoint.sh