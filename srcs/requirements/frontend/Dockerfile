# syntax=docker/dockerfile:1
# escape=\

FROM node:23.9.0-alpine3.20a@sha256:d328a006af9cd556fec56d3fb325ce8fdee988b511dfdfe90d3182bed900aecd

RUN apk update \
	&& apk upgrade \
	&& apk add vim curl

ARG VITE_DOMAIN_NAME
ARG VITE_PORT_NUM

WORKDIR /home/frontend

COPY --chown=root:root ./conf/index.html index.html
COPY --chown=root:root ./conf/package-lock.json package-lock.json
COPY --chown=root:root ./conf/package.json package.json
COPY --chown=root:root ./conf/public public
COPY --chown=root:root ./conf/src src

RUN npm install \
	&& npm install serve@14.2.4 \
	&& npm run build

CMD ["sh", "-c", "npx serve -s /home/frontend/dist -p 3000"]
