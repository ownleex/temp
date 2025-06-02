# syntax=docker/dockerfile:1
# escape=\
FROM alpine@sha256:eddacbc7e24bf8799a4ed3cdcfa50d4b88a323695ad80f317b6629883b2c2a78

RUN apk update \
	&& apk upgrade \
	&& apk add postgresql vim curl jq

RUN mkdir /etc/postgresql/game_pong_postgres
RUN mkdir /etc/postgresql/user_handler_postgres

RUN mkdir /run/postgresql \
	&& chown postgres:postgres /run/postgresql \
	&& mkdir /var/lib/postgresql/data \
	&& chown postgres:postgres /var/lib/postgresql/data \
	&& chmod 0700 /var/lib/postgresql/data

COPY --chown=postgres:postgres ./tools/00_replicat_init.sh /var/lib/postgresql/00_replicat_init.sh
RUN chmod +x /var/lib/postgresql/00_replicat_init.sh

USER postgres

RUN initdb -D /var/lib/postgresql/data

COPY --chown=postgres:postgres ./conf/pg_hba.conf /var/lib/postgresql/data/pg_hba.conf
COPY --chown=postgres:postgres ./conf/postgresql.conf /var/lib/postgresql/data/postgresql.conf

RUN chmod 700 /var/lib/postgresql/data/pg_hba.conf /var/lib/postgresql/data/postgresql.conf

USER root

COPY --chown=postgres:postgres ./tools/init.sh /home/init/init.sh
RUN chmod +x /home/init/init.sh

COPY --chown=root:root ./tools/01_replicat_init.sh /home/init/01_replicat_init.sh
RUN chmod +x /home/init/01_replicat_init.sh

USER postgres

CMD ["/home/init/init.sh"]
