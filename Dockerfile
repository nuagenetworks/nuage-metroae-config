FROM centos
FROM python:2.7.10
MAINTAINER Eswar Chennareddygari (eswar.chennareddygari@nokia.com)
COPY ./ /source
WORKDIR /source
VOLUME /data
RUN pip install -r requirements.txt