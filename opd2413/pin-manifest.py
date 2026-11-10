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

# CodeLinaro's Git transport can be unavailable while its commit archives work.
# All revisions below remain those in the original OnePlus manifest.
transports = json.loads(Path(__file__).with_name('source-transports.json').read_text())
by_source = {entry['source']: entry for entry in transports}
ET.SubElement(tree.getroot(), 'remote', {
    'name': 'clo-github', 'fetch': 'https://github.com/CodeLinaro-mirror'})
for project in list(tree.getroot().findall('project')):
    if project.get('remote') != 'clo-la':
        continue
    entry = by_source[project.get('name')]
    if project.get('revision') != entry['revision'] or project.get('path') != entry['path']:
        raise SystemExit('Transport mapping no longer matches the pinned manifest')
    if entry['transport'] == 'archive':
        tree.getroot().remove(project)
    else:
        project.set('remote', 'clo-github')
        project.set('name', entry['mirror'].split('/', 1)[1])
        project.attrib.pop('upstream', None)
tree.write(path, encoding='UTF-8', xml_declaration=True)
print('Pinned device projects:', ', '.join(sorted(found)))
print('CodeLinaro revisions preserved; using GitHub mirrors and commit archives')
