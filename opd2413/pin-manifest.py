"""Pin the three device source projects to the published .400 release."""
import json
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

path = Path(sys.argv[1])
lock = json.loads(Path(__file__).with_name('source-lock.json').read_text())
tree = ET.parse(path)
found = set()
for project in tree.getroot().findall('project'):
    name = project.get('name')
    if name in lock:
        project.set('upstream', 'refs/heads/' + lock[name]['ref'])
        project.set('revision', lock[name]['sha'])
        found.add(name)
expected = set(lock) - {'kernel_manifest'}
if found != expected:
    raise SystemExit(f'Device manifest mismatch: {found} != {expected}')
tree.write(path, encoding='UTF-8', xml_declaration=True)
print('Pinned device projects:', ', '.join(sorted(found)))
