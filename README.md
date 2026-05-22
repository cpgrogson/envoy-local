# envoy-local

> Helper tool to spin up local Envoy proxy configs for service mesh testing

---

## Installation

```bash
pip install envoy-local
```

Or install from source:

```bash
git clone https://github.com/yourorg/envoy-local.git && cd envoy-local && pip install -e .
```

---

## Usage

Generate and run a local Envoy proxy configuration in seconds:

```bash
# Start a basic HTTP proxy on port 10000 forwarding to a local service
envoy-local start --port 10000 --upstream localhost:8080

# Generate a config file without starting Envoy
envoy-local generate --port 10000 --upstream localhost:8080 --output envoy.yaml

# Start with a custom config template
envoy-local start --config my-template.yaml
```

Example output:

```
[envoy-local] Generated config: /tmp/envoy-local-abc123.yaml
[envoy-local] Starting Envoy on port 10000 → localhost:8080
[envoy-local] Envoy proxy running. Press Ctrl+C to stop.
```

---

## Requirements

- Python 3.8+
- [Envoy proxy](https://www.envoyproxy.io/docs/envoy/latest/start/install) installed and available on `$PATH`

---

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## License

This project is licensed under the [MIT License](LICENSE).