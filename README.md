# Billr plugins

Connect your AI assistant to **hosted Billr** at https://mcp.billr.cc. Review unbilled work and unpaid invoices, log time and expenses, and draft invoices and estimates.

You need a [Billr account](https://billr.cc) and applicable [plan access](https://billr.cc/pricing). Installing a plugin does not include a subscription. This repository contains integration packages, not the Billr application or a local MCP server.

## Connect safely

Use OAuth: sign in on Billr, choose the intended business, and approve only the permissions you need. Start with read-only access. Never paste passwords or tokens into a chat. Sending, payment and deletion actions need your explicit request and the corresponding connection permission.

## Install

### Claude Code

Once this repository is published:

```sh
claude plugin marketplace add ethanplusai/billr-plugins
claude plugin install billr@billr
```

Open `/mcp` and authenticate Billr. To test a local checkout, run `claude --plugin-dir /absolute/path/to/billr-plugins`.

### Cursor

This repository includes an Agent Plugins package and a Cursor compatibility manifest. Import the local checkout using Cursor's plugin settings for testing. Marketplace installation will be available after review; there is no published marketplace listing yet.

### Codex and ChatGPT

The portable package includes the hosted MCP connection and billing skill. The release ZIP is intended for plugin import and directory review. Until publication, a direct MCP connection can be configured in a supported client's connector settings using `https://mcp.billr.cc`.

For Codex CLI's direct MCP connection (without installing the skill):

```sh
codex mcp add billr --url https://mcp.billr.cc
codex mcp login billr
```

### Claude and Grok Bot

For custom MCP connections, use `https://mcp.billr.cc` and complete Billr OAuth. A direct connection is not a marketplace plugin installation. Grok Bot uses **Connect apps** and Cursor's plugin ecosystem; separate Grok Bot acceptance testing is required. Grok Bot is distinct from Grok web/API and OpenClaw.

## Package format

`plugin.json`, `mcp.json`, and `skills/billr/` implement [Agent Plugins 1.0.0](https://agent-plugins.org/specification). Vendor compatibility manifests declare the same hosted endpoint in their supported formats. No credential is bundled. Assets and licensing are included.

## Development

Edit the root portable manifest and the single `skills/billr/` source. Run
`python3 scripts/sync_manifests.py` after changing manifest metadata or the
MCP endpoint, then run the validation below. Do not edit compatibility copies
independently.

```sh
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate.py
python3 -m unittest discover -s tests
python3 scripts/package.py
```

The ZIP includes only the runtime package, README, and license files. Tests and build scripts are not installed. Automated package checks do not establish successful authentication in every client.

[Documentation](https://billr.cc/docs/connect) · [Support](https://billr.cc/support) · [Privacy](https://billr.cc/legal/privacy) · [Terms](https://billr.cc/legal/terms)
