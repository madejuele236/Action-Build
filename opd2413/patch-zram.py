"""Add optional codecs without changing defaults or module-loader policy."""
import re
import subprocess
import sys
from pathlib import Path

patch_dir = Path(sys.argv[1])
kconfig = Path('drivers/block/zram/Kconfig')
original = kconfig.read_text()
choice = re.search(r'(choice\n.*?\nendchoice)', original, re.S).group(1)
default = re.search(r'^\s*default (ZRAM_DEF_COMP_\w+)$', choice, re.M).group(1)
module_loader = Path('kernel/module/main.c').read_bytes()
for name in ('lz4kd.patch', 'lz4k_oplus.patch'):
    sections = re.split(r'(?=^diff )', (patch_dir / name).read_text(), flags=re.M)
    # The upstream codec patch also modifies blacklist handling. Omit that hunk.
    patch = ''.join(s for s in sections if not (
        s.startswith('diff ') and 'kernel/module/main.c' in s.splitlines()[0]))
    subprocess.run(['patch', '--batch', '-p1', '-F', '3'], input=patch,
                   text=True, check=True)
updated = kconfig.read_text()
updated, count = re.subn(r'(?m)^(\s*default )ZRAM_DEF_COMP_\w+(\s*)$',
                         lambda m: m[1] + default + m[2], updated, count=1)
if count != 1:
    raise SystemExit('Could not restore the stock ZRAM default')
kconfig.write_text(updated)
if Path('kernel/module/main.c').read_bytes() != module_loader:
    raise SystemExit('ZRAM patch unexpectedly modified the module loader')
# The delta encoder calls internal helpers in the base encoder. Keep both in
# one module so those helpers need not become globally exported kernel APIs.
codec_makefile = Path('lib/lz4kd/Makefile')
codec_make = codec_makefile.read_text()
old = 'obj-$(CONFIG_LZ4KD_COMPRESS) += lz4kd_encode.o lz4kd_encode_delta.o'
new = ('obj-$(CONFIG_LZ4KD_COMPRESS) += lz4kd_compress.o\n'
       'lz4kd_compress-y := lz4kd_encode.o lz4kd_encode_delta.o')
if codec_make.count(old) != 1:
    raise SystemExit('Unexpected LZ4KD Makefile; review the module linkage')
codec_makefile.write_text(codec_make.replace(old, new))
print('Preserved ZRAM default:', default)
