#Base image
FROM python:2.7.10-slim

#User Info
MAINTAINER Nuage Networks Devops (deveops@nuagenetworks.net)

#Copy source files into /source directory
COPY ./ /source
WORKDIR /source

#Define date volume for templates and user data
VOLUME /data

# install python requirements
RUN pip install -r requirements.txt
