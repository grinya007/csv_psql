FROM postgres:latest

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip less vim && \
    apt-get remove --purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && \
    rm -rf /usr/share/man /tmp/* /var/cache/apt/archives/* /var/lib/apt/lists/* /var/lib/dpkg/info/*

RUN ln -s /usr/bin/python3 /usr/bin/python

USER postgres
RUN initdb

USER root

ENV PAGER="less -S"
ENV EDITOR=vim

ENV PYTHONPYCACHEPREFIX=/tmp
RUN pip install pandas psycopg2-binary

RUN mkdir /csv_dir
RUN mkdir /src
COPY src/* /src
WORKDIR /src

RUN python load.py --just-compile
RUN python dump.py --just-compile

CMD ["postgres"]
