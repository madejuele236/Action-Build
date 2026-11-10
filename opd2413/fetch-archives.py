"""Download the original toolchain commits without CodeLinaro's Git service."""
import concurrent.futures
import json
from pathlib import Path
import subprocess
import tempfile

entries = json.loads(Path(__file__).with_name('source-transports.json').read_text())


def fetch(entry):
    destination = Path(entry['path'])
    destination.mkdir(parents=True, exist_ok=True)
    print('Downloading pinned archive:', entry['path'], entry['revision'], flush=True)
    # Keep temporary archives on the enlarged build volume, not /tmp.
    with tempfile.TemporaryDirectory(prefix='.toolchain-download-', dir='.') as tmp:
        archive = Path(tmp) / 'source.tar.gz'
        subprocess.run([
            'curl', '--fail', '--location', '--silent', '--show-error',
            '--retry', '2', '--retry-delay', '3', '--connect-timeout', '30',
            '--max-time', '900', '--output', str(archive), entry['archive_url'],
        ], check=True)
        subprocess.run([
            'tar', '-xzf', str(archive), '--strip-components=1',
            '-C', str(destination),
        ], check=True)
    print('Restored original toolchain tree:', entry['path'], flush=True)


with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    list(pool.map(fetch, [e for e in entries if e['transport'] == 'archive']))

clang = Path('kernel_platform/prebuilts/clang/host/linux-x86/clang-r510928/bin/clang')
subprocess.run([str(clang.resolve()), '--version'], check=True)
