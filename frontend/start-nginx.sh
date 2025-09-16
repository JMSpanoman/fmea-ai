#!/bin/sh

# Replace PORT and BACKEND_URL placeholders in nginx config
envsubst '${PORT},${BACKEND_URL}' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

# Start nginx
nginx -g "daemon off;"
