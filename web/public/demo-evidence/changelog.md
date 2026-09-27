# Acme SDK 2.4.0 changelog

- Preserves `Client.send(request)` and `Client.status()` public call signatures.
- Adds optional `timeout_ms` configuration with a backward-compatible default.
- Removes no documented response fields.
- Internal retry implementation changed without changing public return types.
