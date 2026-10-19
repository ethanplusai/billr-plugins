"""Generate compatibility declarations from the canonical portable manifest."""
import json
from validate import ROOT

def generated():
    core=json.loads((ROOT/'plugin.json').read_text())
    base={k:v for k,v in core.items() if k not in ('$schema','extensions')}
    server=json.loads((ROOT/'mcp.json').read_text())['mcpServers']['billr']
    url=server['url']
    return {
        '.claude-plugin/plugin.json': base,
        '.claude-plugin/marketplace.json': {
            'name':'billr','owner':{'name':'Billr','email':'help@billr.cc'},
            'metadata':{'description':'Official hosted Billr integration packages.'},
            'plugins':[{'name':'billr','source':'./','description':core['description']}]},
        '.codex-plugin/plugin.json': {**base,'interface':core['extensions']['com.openai']['interface'],'mcpServers':'./.mcp.json','skills':'./skills/'},
        '.cursor-plugin/plugin.json': {**base,'logo':'assets/logo.png','skills':'./skills/','mcpServers':'./config/cursor.mcp.json'},
        '.mcp.json': {'mcpServers':{'billr':{'type':'http','url':url}}},
        'config/cursor.mcp.json': {'mcpServers':{'billr':{'url':url}}},
    }

if __name__=='__main__':
    for name,value in generated().items():
        (ROOT/name).write_text(json.dumps(value,indent=2)+'\n')
    print('Synchronized compatibility manifests')
