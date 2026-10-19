"""Validate portable schemas, compatibility parity and public artifact hygiene."""
import json
import pathlib
import re
from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parents[1]
FILES = ['plugin.json', 'mcp.json', '.mcp.json', '.claude-plugin/plugin.json',
         '.claude-plugin/marketplace.json', '.codex-plugin/plugin.json',
         '.cursor-plugin/plugin.json', 'config/cursor.mcp.json',
         'skills/billr/SKILL.md', 'skills/billr/references/tools.md',
         'skills/billr/references/workflows.md', 'assets/icon.png',
         'assets/logo.png', 'LICENSE', 'NOTICE', 'README.md']
ENDPOINT = 'https://mcp.billr.cc'

def check(condition, message):
    if not condition:
        raise ValueError(message)

def safe_path(root, name):
    p = root / name
    check(not p.is_symlink(), 'Symlinks are not distributed')
    check(p.resolve().is_relative_to(root.resolve()), 'Path escapes package')
    check(p.exists(), f'Missing path: {name}')
    return p

def validate(root=ROOT):
    def read(name):
        return json.loads(safe_path(root, name).read_text())
    for name in FILES:
        p = safe_path(root, name)
        check(p.is_file(), f'Not a file: {name}')
        if p.suffix != '.png':
            t = p.read_text()
            check(not re.search(r'(?:sk_live_|rk_live_|billr_sk_|ghp_)[A-Za-z0-9]{16,}|-----BEGIN .*PRIVATE KEY-----', t), f'Possible secret: {name}')
            check(not re.search(r'/Users/|/private/tmp/|billr-hosted|\.agents/sessions', t), f'Private content: {name}')
    for name in ('plugin', 'mcp'):
        schema = json.loads((ROOT / 'schemas' / f'{name}.schema.json').read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(read(f'{name}.json'))
    core = read('plugin.json')
    check(core['repository'] == 'https://github.com/ethanplusai/billr-plugins', 'Wrong distribution repository')
    for name, transport in [('mcp.json', 'streamable-http'), ('.mcp.json', 'http'), ('config/cursor.mcp.json', None)]:
        servers = read(name)['mcpServers']
        expected = {'url': ENDPOINT}
        if transport:
            expected['type'] = transport
        check(servers == {'billr': expected}, f'Unexpected server/auth settings: {name}')
    for name in ('.claude-plugin/plugin.json', '.cursor-plugin/plugin.json', '.codex-plugin/plugin.json'):
        vendor = read(name)
        for key in ('name', 'version', 'description', 'repository', 'license'):
            check(vendor[key] == core[key], f'Metadata drift: {name}/{key}')
        for key in ('skills', 'mcpServers', 'logo'):
            if key in vendor:
                safe_path(root, vendor[key])
    interface = core['extensions']['com.openai']['interface']
    for key in ('composerIcon', 'logo'):
        safe_path(root, interface[key])
    check(read('.codex-plugin/plugin.json')['interface'] == interface, 'OpenAI interface drift')
    market = read('.claude-plugin/marketplace.json')
    check(len(market['plugins']) == 1 and market['plugins'][0]['source'] == './', 'Invalid marketplace source')
    skill = (root / 'skills/billr/SKILL.md').read_text()
    check(skill.startswith('---\nname: billr\n'), 'Invalid skill frontmatter')
    check(f'version: {core["version"]}' in skill, 'Skill version drift')
    return len(FILES)

if __name__ == '__main__':
    print(f'Validated schemas, metadata, endpoints, paths and hygiene for {validate()} package files')
