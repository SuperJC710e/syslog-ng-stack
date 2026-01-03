FROM balabit/syslog-ng:4.10.2

# Install logrotate for log rotation
USER root
RUN apt-get update && apt-get install -y logrotate && rm -rf /var/lib/apt/lists/*

# Copy configuration files
COPY syslog-ng.conf /etc/syslog-ng/syslog-ng.conf
COPY logrotate.conf /etc/logrotate.conf
COPY rotate-logs.sh /usr/local/bin/rotate-logs.sh

# Make rotation script executable
RUN chmod +x /usr/local/bin/rotate-logs.sh

# Create logs directory
RUN mkdir -p /app/logs

# Create syslog user/group if not exists
RUN groupadd -g 1000 syslog 2>/dev/null || true
RUN useradd -u 1000 -g syslog -M syslog 2>/dev/null || true

# Set permissions
RUN chown -R syslog:syslog /app/logs /etc/syslog-ng

# Create supervisor config to run both syslog-ng and logrotate
RUN apt-get update && apt-get install -y supervisor && rm -rf /var/lib/apt/lists/*

COPY supervisord.conf /etc/supervisord.conf

# Expose syslog ports
EXPOSE 514/udp 514/tcp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD syslog-ng-ctl healthcheck --timeout 5

# Override the base image's entrypoint and use supervisord to manage both processes
ENTRYPOINT []
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
