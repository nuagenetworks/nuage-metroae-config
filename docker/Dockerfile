FROM centos:7
COPY requirements.txt /root
RUN yum install -y python3-pip
RUN rm -f /usr/bin/python && ln -s /usr/bin/python3 /usr/bin/python
RUN pip3 install -r /root/requirements.txt
ENV LC_ALL=en_US.utf8
WORKDIR /metroaeconfig

