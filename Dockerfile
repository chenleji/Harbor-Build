FROM python

MAINTAINER chenleji@wise2c.com

COPY ./prepare.py /root/prepare.py
COPY ./templates /root/templates

WORKDIR /root

