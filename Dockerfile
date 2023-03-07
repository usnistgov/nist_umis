# Basic nginx dockerfile starting with Ubuntu 20.04
FROM ubuntu:20.04
RUN apt -y update
RUN apt -y install nginx
RUN apt -y mysql-server
