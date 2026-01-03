# Syslog-ng Server

Enterprise-grade syslog receiver using syslog-ng with integrated log rotation.

## Features

- **High Performance**: C-based syslog-ng handles 10,000+ messages/second
- **Dual Protocol**: UDP and TCP on port 514
- **Log Rotation**: Integrated logrotate (100MB per file, keep 10)
- **Compression**: Automatic gzip compression of rotated logs
- **JSON Output**: Compatible with syslog-viewer
- **Multi-threaded**: Efficient message processing
- **Supervisor**: Manages both syslog-ng and logrotate processes

## Configuration Files

- **syslog-ng.conf**: Main syslog-ng configuration
- **logrotate.conf**: Log rotation settings
- **supervisord.conf**: Process management
- **rotate-logs.sh**: Logrotate automation script

## Usage

### Docker (Recommended)

```bash
docker build -t syslog-ng-server .
docker run -d -p 514:514/udp -p 514:514/tcp -v syslog-data:/app/logs syslog-ng-server
```

### Check Configuration

```bash
syslog-ng -s
```

### Manual Log Rotation

```bash
logrotate -f /etc/logrotate.conf
```

## Output Format

Logs are written to `/app/logs/syslog.jsonl`:

```json
{
  "timestamp": "2026-01-02T12:34:56+00:00",
  "source": "192.168.1.100",
  "protocol": "UDP",
  "facility": "local0",
  "severity": "info",
  "priority": "134",
  "message": "Application started",
  "raw": "<134>Application started"
}
```

## Advanced Configuration

### Add TLS Support

Edit `syslog-ng.conf`:
```
source s_tls {
    network(
        transport("tls")
        port(6514)
        tls(
            key-file("/path/to/key.pem")
            cert-file("/path/to/cert.pem")
        )
    );
};
```

### Filter by Severity

```
filter f_critical {
    level(crit..emerg);
};
```

### Multiple Outputs

```
destination d_mysql {
    sql(
        type(mysql)
        host("mysql-server")
        username("syslog")
        password("password")
        database("logs")
    );
};
```

## Performance Tuning

Adjust in `syslog-ng.conf`:
```
options {
    log_fifo_size(10000);
    flush_lines(100);
    threaded(yes);
};
```

## Requirements

- Docker or syslog-ng 4.5+
- logrotate
- supervisor (for multi-process management)
