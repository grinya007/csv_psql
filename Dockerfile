FROM postgres:14 AS base

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip postgresql-plpython3-14 less vim && \
    apt-get remove --purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && \
    rm -rf /usr/share/man /tmp/* /var/cache/apt/archives/* /var/lib/apt/lists/* /var/lib/dpkg/info/*

RUN ln -s /usr/bin/python3 /usr/bin/python


FROM base AS build

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential python3-dev postgresql-server-dev-14 && \
    apt-get remove --purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && \
    rm -rf /usr/share/man /tmp/* /var/cache/apt/archives/* /var/lib/apt/lists/* /var/lib/dpkg/info/*


RUN mkdir /pip
ENV PIP_TARGET=/pip
ENV PYTHONPATH=/pip
RUN pip install pandas psycopg2 pgcli


FROM base

ENV EDITOR=vim
ENV PAGER="less -S"
ENV PYTHONPYCACHEPREFIX=/tmp
ENV POSTGRES_HOST_AUTH_METHOD=trust
ENV TABLES_META=/tmp/tables_meta.pickle
ENV CSV_DIR=/csv
ENV PIP_TARGET=/pip
ENV PYTHONPATH=/pip
ENV PATH="$PATH:/pip/bin"

RUN mkdir /pip
RUN mkdir /csv
RUN mkdir /src
COPY src/* /src/
WORKDIR /src

COPY --from=build /pip/ /pip/

USER postgres
COPY db/init.sql /docker-entrypoint-initdb.d/
RUN docker-entrypoint.sh

USER root
RUN mkdir -p /root/.config/pgcli
COPY db/pgcli_config /root/.config/pgcli/config

RUN python load.py --just-compile
RUN python dump.py --just-compile

CMD ["postgres"]
