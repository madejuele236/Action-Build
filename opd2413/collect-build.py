"""Keep the files needed to inspect the build and later enable ZRAM."""
import json
import shutil
import subprocess
from pathlib import Path

common = Path('kernel_workspace/kernel_platform/common')
out = common / 'out'
evidence = Path('opd2413-output/evidence')
optional = Path('opd2413-output/optional-zram')
evidence.mkdir(parents=True, exist_ok=True)
optional.mkdir(parents=True, exist_ok=True)
subprocess.run(['python3', 'opd2413/check-config.py', str(out / '.config')], check=True)
for name in ('.config', 'Module.symvers', 'System.map', 'include/config/kernel.release'):
    shutil.copy2(out / name, evidence / Path(name).name)
for name in ('source-lock.json', 'source-transports.json', 'components.json', 'inputs.json', 'README.md'):
    shutil.copy2(Path('opd2413') / name, evidence / name)
with (evidence / 'source-changes.patch').open('w') as dest:
    subprocess.run(['git', '-C', str(common), 'diff'], stdout=dest, check=True)
modules = []
for pattern in ('drivers/block/zram/*.ko', 'crypto/lz4*.ko', 'crypto/842.ko',
                'lib/lz4*/*.ko', 'lib/842/*.ko'):
    for path in out.glob(pattern):
        relative = path.relative_to(out)
        target = optional / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        info = subprocess.run(['modinfo', str(path)], capture_output=True,
                              text=True, check=True).stdout
        modules.append({'path': str(relative), 'modinfo': info})
if not (optional / 'drivers/block/zram/zram.ko').is_file():
    raise SystemExit('Optional zram.ko was not produced')
(optional / 'modules.json').write_text(json.dumps(modules, indent=2) + '\n')
(optional / 'README.txt').write_text(
    'Optional build-matched modules. This is NOT an installable root module.\n'
    'No service script, sysctl, ZRAM size or algorithm is changed by this archive.\n'
    'Keep stock system_dlkm/vendor_dlkm for the first boot.\n'
    'Later deployment needs dependency/signature/ABI checks and a reboot;\n'
    'do not unload an active swap device. Verify against the kernel from this run.\n')
(evidence / 'validation-status.txt').write_text(
    'Resolved configuration and optional module production checked.\n'
    'Vendor-module ABI/KMI compatibility: pending comparison with target firmware.\n'
    'Boot, root, KPM, suspend/resume, pen and DroidSpaces runtime: pending.\n')
print(f'Collected build evidence and {len(modules)} optional modules')
