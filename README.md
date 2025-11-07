# iptvportal-py
Modern Python SDK for IPTVPortal JSONSQL API - Full-featured client with sync/async support, query builder, resource managers, and CLI

- [IPTVPORTAL JSONSQL API DOCS](https://iptvportal.cloud/support/api/)
- [IPTVPORTAL JSONSQL API CODE EXAMPLES 1](https://ftp.iptvportal.cloud/doc/API/examples/)
- [IPTVPORTAL JSONSQL API CODE EXAMPLES 2](https://ftp.iptvportal.cloud/doc/API/ODS_API_inserter/)

## Installation Instructions

### Supported Python Versions
- Python 3.12 or newer is required.

### Quick Install (uv/uvx)
```bash
uv pip install iptvportal-py
# or system-wide:
sudo uvx pip install iptvportal-py
```

### Classic pip
```bash
pip install iptvportal-py
```

### Development Install
Clone the repo and install in editable mode (with dev tools and docs):
```bash
git clone https://github.com/pv-udpv/iptvportal-py.git
cd iptvportal-py
uv pip install -e .[dev,docs]
```

### Configuration and Environment
Copy and edit the example environment file for your setup:
```bash
cp .env.example .env
```
Customize variables for your deployment, using `IPTVPORTAL_` and nested `IPTVPORTAL_CLIENT__` as needed.  
You may place `.env` in your userspace config or system directory (see below).

#### Userspace Directories
Upon first use, the SDK will create:
- Logs: `~/.local/log/iptvportal`
- Config: `~/.config/iptvportal`
- Data: `~/.local/share/iptvportal`
- Cache: `~/.cache/iptvportal`

#### System-wide Directories
If installed globally (with `sudo uvx pip`):
- Config: `/etc/iptvportal`
- Data: `/var/lib/iptvportal`
- Logs: `/var/log/iptvportal`

### CLI Usage
After install, the command-line tool is available:
```bash
iptvportal --help
```
Example commands:
```bash
iptvportal subscriber list --limit 10
iptvportal media list --limit 5
```

### Uninstall
```bash
uv pip uninstall iptvportal-py
```

#### For more details
See the [full documentation](https://github.com/pv-udpv/iptvportal-py) and example notebooks for advanced usage and integration.
