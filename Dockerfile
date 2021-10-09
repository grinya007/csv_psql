FROM postgres:14

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip postgresql-plpython3-14 less vim && \
    apt-get remove --purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && \
    rm -rf /usr/share/man /tmp/* /var/cache/apt/archives/* /var/lib/apt/lists/* /var/lib/dpkg/info/*

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN pip install pandas psycopg2-binary

ENV EDITOR=vim
ENV PAGER="less -S"
ENV PYTHONPYCACHEPREFIX=/tmp
ENV POSTGRES_HOST_AUTH_METHOD=trust
ENV TABLES_META=/tmp/tables_meta.pickle
ENV CSV_DIR=/csv

RUN mkdir /csv
RUN mkdir /src
COPY src/* /src/
WORKDIR /src

USER postgres
COPY db/init.sql /docker-entrypoint-initdb.d/
RUN docker-entrypoint.sh

RUN python load.py --just-compile
RUN python dump.py --just-compile

CMD ["postgres"]
