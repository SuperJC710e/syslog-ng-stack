#!/bin/sh
# Log rotation script for syslog-ng
# Runs logrotate periodically

set -e

echo "Starting log rotation service..."

# Run logrotate every hour
while true; do
    # Run logrotate
    /usr/sbin/logrotate -v /etc/logrotate.conf

    # Sleep for 1 hour
    sleep 3600
done
