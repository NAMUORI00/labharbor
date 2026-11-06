# LabHarbor

**A visual control room for shared GPU research servers.**

[한국어](README.ko.md) · [Architecture](docs/ARCHITECTURE.md) · [Operations](docs/OPERATIONS.md)

LabHarbor maps a GPU server into laboratories, accounts and shared storage. Open a lab to inspect its accounts, adjust supported resource limits, browse official NVIDIA image tags, create live file backups, or export a one-page environment sheet in English or Korean.

## What works in 0.5

- Isometric server/GPU/storage diagrams and drill-down settings pages.
- Five-second incremental status refresh, server-side caching, hidden-tab pause and retry backoff.
- CPU and memory limits through `docker update`, with no container replacement. Running-memory reductions are rejected.
- Existing-container registration. No research containers are created by the installer or UI.
- NVIDIA CUDA and PyTorch image catalogs, cached for 15 minutes. Presets are preferences, not an image deployment operation.
- Live lab backups of exported container filesystems plus persistent bind-mounted storage, with SHA-256 manifests.
- Conditional in-container user creation for writable containers with persistent `/home` and unrestricted SSH account configuration.
- English/Korean UI selected from browser language or a manual selector. Translation files live in `app/locales/*.json`.
- English/Korean PDF environment sheets, generated in memory. Entered passwords are neither persisted nor logged.

## Explicit boundaries

GPU assignment and base-image replacement generally require container recreation; **this release never performs them**. It does not create containers, provision disks, grant host sudo, expose a Docker socket to researchers, or restart Docker/NVIDIA services.

Read-only one-user containers cannot acquire additional accounts through this UI. The UI explains this rather than silently weakening their isolation. The root-access preset is a requested configuration only, not a live privilege change.

Live backups are **not application-consistent snapshots**. Files can change while copied. They include sensitive account/configuration data and stay root-readable on the server. Restoration is an operator-reviewed maintenance procedure, not a one-click action.

## Install

Supported runtime: Linux, systemd, Docker, NVIDIA driver + NVIDIA Container Toolkit, Python 3.10–3.12 and its venv module. Ubuntu 22.04 / x86-64 was used for live verification. Other hosts require validation before enabling mutations.

```sh
sudo python3 install.py --check
sudo python3 install.py
```

The setup prompts for the administrator, listen IP, port, backup directory and GPU indexes allowed for changes. Leave the GPU list empty for monitoring-only use. It installs two dedicated services, then you register existing environments in the browser.

Source installs resolve pinned dependencies from PyPI. The downloadable package includes Linux x86-64 / CPython 3.10 wheels for offline dependency installation. No GPU workload image is downloaded automatically.

For network access, choose the server's specific internal IP. Use HTTPS via a trusted reverse proxy or an SSH tunnel on untrusted networks. The application itself serves HTTP.

## Update

```sh
sudo python3 install.py --update
```

Only LabHarbor services are restarted. Server-specific settings under `/etc/h200-console` are preserved. The previous application is retained under `/opt/h200-console/app.backup-*`. The installer is an interactive CLI wizard; there is no unauthenticated browser setup endpoint.

## Development

```sh
python3 -m unittest discover -s tests -v
node --check app/static/console.js
```

The control broker runs as root behind an owner-restricted Unix socket. The web process runs as a dedicated non-login account. Every live mutation checks both lab and GPU allowlists. No user-provided shell command is accepted. See [security notes](SECURITY.md) before extending control actions.

## Validation scope

Validated on one live H200 host: bilingual routes, official tag retrieval, bilingual one-page PDFs, GPU-0 test-account CPU adjustments without changes to container ID/start time, and a live test-lab backup with archive and checksum validation. Production labs were read-only during validation. Fresh installation on another physical server, restoration, and account creation in a writable research container have not been live-tested.

## License

MIT. Bundled Nanum Gothic font: SIL Open Font License; see `app/fonts/OFL.txt`. Third-party Python wheels retain their upstream licenses.
