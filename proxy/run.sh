#!/bin/sh

# Exit the script as soon as any command fails
set -e

# 1. Replace the environment variables in the Nginx configuration file
envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf

# 2. Start the Nginx server in the foreground
nginx -g 'daemon off;'
