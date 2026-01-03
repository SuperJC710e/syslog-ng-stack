FROM balabit/syslog-ng:4.5.0

# Install logrotate for log rotation
USER root
RUN apk add --no-cache logrotate

# Copy configuration files
COPY syslog-ng.conf /etc/syslog-ng/syslog-ng.conf
COPY logrotate.conf /etc/logrotate.conf
COPY rotate-logs.sh /usr/local/bin/rotate-logs.sh

# Make rotation script executable
RUN chmod +x /usr/local/bin/rotate-logs.sh

# Create logs directory
RUN mkdir -p /app/logs

# Create syslog user/group if not exists
RUN addgroup -g 1000 -S syslog 2>/dev/null || true
RUN adduser -u 1000 -S syslog -G syslog 2>/dev/null || true

# Set permissions
RUN chown -R syslog:syslog /app/logs /etc/syslog-ng

# Create supervisor config to run both syslog-ng and logrotate
RUN apk add --no-cache supervisor

COPY supervisord.conf /etc/supervisord.conf

# Expose syslog ports
EXPOSE 514/udp 514/tcp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD pgrep -x syslog-ng || exit 1

# Use supervisord to manage both processes
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
