# syntax=docker/dockerfile:1
# escape=\

FROM nginx@sha256:0c57fe90551cfd8b7d4d05763c5018607b296cb01f7e0ff44b7d047353ed8cc0

RUN apk update \
	&& apk upgrade \
	&& apk add vim openssl g++ autoconf automake build-base git curl-dev geoip \
	lmdb pcre2-dev libtool libxml2-dev yajl pkgconf zlib-dev linux-headers

RUN mkdir -p /etc/nginx/ssl /static/api /static/chat
RUN openssl req -x509 -nodes \
	-out /etc/nginx/ssl/transcendence.pem \
	-keyout /etc/nginx/ssl/transcendence.key \
	-subj "/C=FR/ST=Alpes-Maritimes/L=Nice/O=Ecole\ 42/OU=Ecole/CN=localhost/emailAddress=mcordes@student.42nice.fr"

WORKDIR /home
RUN git clone https://github.com/owasp-modsecurity/ModSecurity.git \
	&& cd /home/ModSecurity \
	&& git submodule init \
	&& git submodule update \
	&& ./build.sh \
	&& ./configure --with-pcre2 \
	&& make \
	&& make install \
	&& cd /home \
	&& git clone https://github.com/owasp-modsecurity/ModSecurity-nginx.git \
	&& wget http://nginx.org/download/nginx-1.27.1.tar.gz \
	&& tar zxvf nginx-1.27.1.tar.gz \
	&& cd /home/nginx-1.27.1 \
	&& ./configure --with-compat --add-dynamic-module=/home/ModSecurity-nginx \
	&& make modules \
	&& cp objs/ngx_http_modsecurity_module.so /etc/nginx/modules/ \
	&& mkdir /etc/nginx/modsec \
	&& cd /etc/nginx/modsec \
	&& cp /home/ModSecurity/modsecurity.conf-recommended /etc/nginx/modsec/modsecurity.conf \
	&& cp /home/ModSecurity/unicode.mapping /etc/nginx/modsec/ \
	&& sed -i "s/SecRuleEngine\ DetectionOnly/SecRuleEngine\ On/" modsecurity.conf \
	&& cd /home \
	&& git clone https://github.com/coreruleset/coreruleset.git \
	&& mv coreruleset/ /usr/local/ \
	&& cd /usr/local/coreruleset \
	&& cp crs-setup.conf.example crs-setup.conf \
	&& cd /etc/nginx/modsec \
	&& sed -i "s/SecAuditEngine RelevantOnly/SecAuditEngine on/" modsecurity.conf

WORKDIR /etc/nginx/modsec
COPY --chown=root:root ./conf/main.conf ./main.conf

WORKDIR /etc/nginx
COPY --chown=root:root ./conf/nginx.conf ./nginx.conf

WORKDIR /etc/nginx/conf.d
RUN rm default.conf
COPY --chown=root:root ./conf/transcendence_fr.conf ./transcendence_fr.conf

COPY --chown=root:root ./tools/init_nginx.sh /tmp/init_nginx.sh
RUN chmod +x /tmp/init_nginx.sh

COPY ./conf/static_error.html /usr/share/nginx/html/static_error.html

EXPOSE 443

CMD ["/tmp/init_nginx.sh"]
