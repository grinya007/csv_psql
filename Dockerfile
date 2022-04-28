FROM postgres:14

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3 \
        python3-pandas \
        python3-pip \
        python3-psycopg2 \
        postgresql-plpython3-14 \
        curl \
        git \
        less \
        vim \
        vim-airline \
    && apt-get remove --purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /usr/share/man /tmp/* /var/cache/apt/archives/* /var/lib/apt/lists/* /var/lib/dpkg/info/*

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN pip install pgcli

ENV EDITOR=vim
ENV PAGER=less
ENV LESS="-SRX"
ENV PYTHONPYCACHEPREFIX=/tmp
ENV POSTGRES_HOST_AUTH_METHOD=trust
ENV TABLES_META=/tmp/tables_meta.pickle
ENV CSV_DIR=/csv

USER postgres
COPY db/init.sql /docker-entrypoint-initdb.d/
RUN docker-entrypoint.sh

USER root
ENV HOME=/root
RUN mkdir -p $HOME/.config/pgcli
COPY db/pgcli_config $HOME/.config/pgcli/config

# Vim plugins
ENV GIT_SSL_NO_VERIFY=true
RUN mkdir -p $HOME/.vim/pack/plugins/start
RUN git clone --depth=1 https://github.com/nanotech/jellybeans.vim.git $HOME/.vim/pack/plugins/start/jellybeans
RUN git clone --depth=1 https://github.com/ervandew/supertab.git $HOME/.vim/pack/plugins/start/supertab
RUN git clone --depth=1 https://github.com/preservim/nerdcommenter.git $HOME/.vim/pack/plugins/start/nerdcommenter

COPY .vimrc $HOME/

RUN mkdir /csv
RUN mkdir /src
COPY src/* /src/
WORKDIR /src

RUN python load.py --just-compile
RUN python dump.py --just-compile

CMD ["postgres"]
