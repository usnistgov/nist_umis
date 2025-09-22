FROM python:3.13
ENV PYTHONUNBUFFERED 1
WORKDIR /app
RUN apt-get update && apt-get install -y vim python curl bash libmariadb-dev-compat libmariadb-dev default-mysql-client

COPY . /app
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pip -r requirements.txt

ARG USERNAME=cuser
ARG USER_UID=3815
ARG USER_GID=3815

RUN groupadd --gid $USER_GID $USERNAME && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

RUN chown -R cuser:cuser /app && chmod -R o-rwx /app

USER cuser

ENTRYPOINT /app/entrypoint.sh
