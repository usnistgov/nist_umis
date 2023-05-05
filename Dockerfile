FROM python:3.10
ENV PYTHONUNBUFFERED 1
WORKDIR /app
RUN apt-get update && apt-get install -y vim python curl bash libmariadb-dev-compat libmariadb-dev default-mysql-client

COPY . /app
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pip -r requirements.txt
ENTRYPOINT /app/entrypoint.sh