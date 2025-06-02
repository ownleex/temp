#!/bin/sh

echo "" >> /usr/local/coreruleset/crs-setup.conf
echo "SecAction \"id:900000, phase:1, pass, t:none, nolog, tag:'OWASP_CRS', ver:'OWASP_CRS/4.15.0-dev', setvar:tx.blocking_paranoia_level=3\"" >> /usr/local/coreruleset/crs-setup.conf

sed -i "s/\${DOMAIN_NAME}/$DOMAIN_NAME/g" /etc/nginx/conf.d/transcendence_fr.conf
sed -i "s/\${PORT_NUM}/$PORT_NUM/g" /etc/nginx/conf.d/transcendence_fr.conf

nginx -g 'daemon off;'
