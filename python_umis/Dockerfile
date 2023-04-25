##########################################################
# Dockerfile to run a Django-based web application
# Based on a Python image
############################################################
# Set the base image to use to python:2.7 and specify maintainer
FROM python:3.10
ENV PYTHONUNBUFFERED 1
WORKDIR /app
RUN apt-get update && apt-get install -y vim python curl bash libmariadb-dev-compat libmariadb-dev default-mysql-client
# Setup pip

#RUN curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py" \
#    && python get-pip.py

COPY ./nist_umis-main /app
COPY ./app/requirements.txt /app
RUN pip install -r requirements.txt
#COPY ./app/entrypoint.sh /app/entrypoint.sh
# - TODO - Default values for image, add secret mgmt with docker-compose in production
#EXPOSE 8000
ENTRYPOINT /app/entrypoint.sh
#CMD python manage.py runserver 8000