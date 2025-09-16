#!/bin/sh

# Replace PORT placeholder in nginx config
envsubst '${PORT}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

# Start nginx
nginx -g "daemon off;"
