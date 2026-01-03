# Syslog-ng Stack

Enterprise-grade syslog server using **syslog-ng** with a modern web interface for viewing and analyzing syslog messages.

## Why syslog-ng?

This project uses [syslog-ng](https://www.syslog-ng.com/) instead of the Python implementation:

- **Production-Ready**: Battle-tested in enterprise environments
- **High Performance**: Written in C, handles thousands of messages/second
- **Feature-Rich**:
  - Advanced filtering and routing
  - Built-in TLS/SSL support
  - Multiple output formats (JSON, CSV, etc.)
  - Correlation and pattern matching
  - Message parsing and rewriting
- **Native Log Rotation**: Integrated with logrotate
- **Reliability**: Disk-based message buffering
- **Scalability**: Multi-threaded architecture

## Architecture

This project consists of two services:

- **syslog-ng-server**: Production-grade syslog receiver with logrotate
- **syslog-viewer**: Web-based viewer (same as Python stack)

### Platform Support

- **syslog-ng-server**: `linux/amd64`, `linux/arm64`
- **syslog-viewer**: `linux/amd64`, `linux/arm64`

## Features

### Syslog-ng Server
- RFC 3164/5424 compliant
- UDP and TCP syslog reception on port 514
- Automatic log rotation via logrotate (100MB per file, keep 10 files)
- Compressed rotated logs (.gz)
- JSON Lines output format
- Console output for debugging
- High-performance multi-threaded processing
- Supervisor-managed processes (syslog-ng + logrotate)

### Syslog Viewer
- Modern, dark-themed web interface
- Real-time log updates
- Advanced filtering (severity, source, text search)
- Color-coded severity levels
- Statistics dashboard
- Auto-scroll toggle

## Quick Start

### Using Docker Compose (Recommended)

1. Navigate to the project directory:
   ```bash
   cd syslog-ng-stack
   ```

2. Start the stack:
   ```bash
   docker-compose up -d
   ```

3. Access the web interface:
   ```
   http://localhost:8080
   ```

4. Send test syslog messages:
   ```bash
   # Using logger (Linux/Mac)
   logger -n localhost -P 514 "Test message from syslog-ng"

   # Using PowerShell (Windows)
   $udpClient = New-Object System.Net.Sockets.UdpClient
   $msg = [System.Text.Encoding]::ASCII.GetBytes("<134>Test from PowerShell to syslog-ng")
   $udpClient.Send($msg, $msg.Length, "localhost", 514)
   $udpClient.Close()
   ```

### View Logs

```bash
# View all logs
docker-compose logs

# Follow syslog-ng-server logs
docker-compose logs -f syslog-ng-server

# Follow viewer logs
docker-compose logs -f syslog-ng-viewer
```

### Stop the Stack

```bash
docker-compose down
```

To also remove the log volume:
```bash
docker-compose down -v
```

## Configuration

### syslog-ng Configuration

Edit [syslog-ng-server/syslog-ng.conf](syslog-ng-server/syslog-ng.conf) to customize:

- Sources (UDP/TCP ports, TLS)
- Filters (by severity, facility, content)
- Destinations (files, databases, remote servers)
- Message parsing and rewriting
- Performance tuning

Example: Add TLS support:
```
source s_tls {
    network(
        transport("tls")
        port(6514)
        tls(
            key-file("/path/to/key.pem")
            cert-file("/path/to/cert.pem")
            ca-dir("/path/to/ca.d")
        )
    );
};
```

### Log Rotation Configuration

Edit [syslog-ng-server/logrotate.conf](syslog-ng-server/logrotate.conf) to customize:

```conf
/app/logs/syslog.jsonl {
    size 100M          # Rotate when file reaches 100MB
    rotate 10          # Keep 10 rotated files
    daily              # Also rotate daily
    compress           # Compress old files
    delaycompress      # Don't compress immediately
}
```

### Environment Variables

Available in `docker-compose.yml`:
- `TZ`: Timezone (default: UTC)

### Custom Ports

Edit the `docker-compose.yml` file:

```yaml
services:
  syslog-ng-server:
    ports:
      - "5140:514/udp"
      - "5140:514/tcp"
  syslog-ng-viewer:
    ports:
      - "8888:8080"
```

## Log Storage

Logs are stored in JSON Lines format at `/app/logs/syslog.jsonl`:

```json
{
  "timestamp": "2026-01-02T12:34:56.789+00:00",
  "source": "192.168.1.100",
  "protocol": "UDP",
  "facility": "local0",
  "severity": "info",
  "priority": "134",
  "message": "Application started",
  "raw": "<134>Application started"
}
```

### Rotated Logs

Rotated logs are compressed and numbered:
- `syslog.jsonl` - Current log file
- `syslog.jsonl.1.gz` - Most recent rotated file
- `syslog.jsonl.2.gz` - Second most recent
- ...
- `syslog.jsonl.10.gz` - Oldest kept file

### Accessing Logs

```bash
# View current log file
docker exec syslog-ng-server cat /app/logs/syslog.jsonl

# View rotated logs
docker exec syslog-ng-server zcat /app/logs/syslog.jsonl.1.gz

# List all log files
docker exec syslog-ng-server ls -lh /app/logs/
```

### Backup Logs

```bash
# Backup entire log directory
docker run --rm -v syslog-ng-stack_syslog-data:/data -v $(pwd):/backup alpine tar czf /backup/syslog-backup.tar.gz -C /data .
```

## Advanced syslog-ng Features

### Filtering by Severity

Add to `syslog-ng.conf`:
```
filter f_error {
    level(err..emerg);
};

destination d_errors {
    file("/app/logs/errors.jsonl" template(t_json));
};

log {
    source(s_udp);
    source(s_tcp);
    filter(f_error);
    destination(d_errors);
};
```

### Filtering by Facility

```
filter f_mail {
    facility(mail);
};

destination d_mail {
    file("/app/logs/mail.jsonl" template(t_json));
};
```

### Message Parsing

```
parser p_apache {
    csv-parser(
        columns("timestamp", "host", "method", "url", "status")
        delimiters(" ")
    );
};
```

### Sending to Remote Syslog

```
destination d_remote {
    network(
        "remote-syslog-server.example.com"
        port(514)
        transport("tcp")
    );
};
```

## Performance Tuning

Edit `syslog-ng.conf` options:

```
options {
    # Increase buffer size for high-volume environments
    log_fifo_size(10000);

    # Adjust threading
    threaded(yes);

    # Flush messages to disk every N messages
    flush_lines(100);

    # Memory buffer size
    log_msg_size(65536);
};
```

## Comparison: syslog-ng vs Python Server

| Feature | Python Server | syslog-ng |
|---------|--------------|-----------|
| Performance | Good (~1000 msg/s) | Excellent (>10000 msg/s) |
| Memory Usage | Low | Very Low |
| Log Rotation | Custom Python code | Native logrotate |
| Filtering | Basic | Advanced (regex, complex rules) |
| Output Formats | JSON only | JSON, CSV, databases, etc. |
| TLS Support | Manual implementation | Built-in |
| Reliability | Good | Excellent (disk buffering) |
| Configuration | Python code | Config file |
| Setup Complexity | Simple | Moderate |
| Use Case | Small deployments | Enterprise production |

## Troubleshooting

### Check syslog-ng status

```bash
docker exec syslog-ng-server supervisorctl status
```

### Check syslog-ng configuration

```bash
docker exec syslog-ng-server syslog-ng -s
```

### View syslog-ng logs

```bash
docker-compose logs syslog-ng-server
```

### Force log rotation

```bash
docker exec syslog-ng-server logrotate -f /etc/logrotate.conf
```

### No logs appearing

1. Check if syslog-ng is running:
   ```bash
   docker exec syslog-ng-server pgrep syslog-ng
   ```

2. Check configuration syntax:
   ```bash
   docker exec syslog-ng-server syslog-ng -s
   ```

3. Watch logs in real-time:
   ```bash
   docker-compose logs -f syslog-ng-server
   ```

## Security Considerations

- Container runs syslog-ng as non-root where possible
- Viewer has read-only access to log volume
- TLS support available for encrypted transmission
- Log files stored with restrictive permissions (0644)

## Documentation

- [syslog-ng Documentation](https://www.syslog-ng.com/technical-documents/doc/syslog-ng-open-source-edition/)
- [syslog-ng GitHub](https://github.com/syslog-ng/syslog-ng)
- [Logrotate Manual](https://linux.die.net/man/8/logrotate)

## License

This project is provided as-is for educational and production use.
