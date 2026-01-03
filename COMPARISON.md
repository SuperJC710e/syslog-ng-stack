# syslog-ng vs Python Stack Comparison

See the detailed comparison at [../syslog-stack/COMPARISON.md](../syslog-stack/COMPARISON.md)

## Quick Reference

**Use this syslog-ng stack for:**
- Production environments
- High-volume logging (>1000 msg/s)
- Enterprise features (TLS, advanced filtering, databases)
- Battle-tested reliability

**Use the Python stack for:**
- Development and learning
- Simple deployments
- Easy customization with Python
- Minimal dependencies

## Both Projects

Both stacks are located as sibling directories:
- [../syslog-stack/](../syslog-stack/) - Python-based implementation
- [../syslog-ng-stack/](../syslog-ng-stack/) - This syslog-ng implementation (you are here)

Both share the same web viewer and log format, making it easy to switch between them.
