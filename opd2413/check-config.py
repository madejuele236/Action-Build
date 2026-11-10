"""Check resolved build configuration, not just requested Kconfig values."""
import sys
from pathlib import Path

config = dict(line.split('=', 1) for line in Path(sys.argv[1]).read_text().splitlines()
              if line.startswith('CONFIG_') and '=' in line)
required = {
    'KSU': 'y', 'KPM': 'y', 'KSU_SUSFS': 'y', 'KSU_SUSFS_PRIORITY_UID_FILTER': 'y',
    'NETFILTER': 'y', 'IP_SET': 'y', 'IP6_NF_NAT': 'y',
    'IP6_NF_TARGET_MASQUERADE': 'y', 'TCP_CONG_BBR3': 'y',
    'SYSVIPC': 'y', 'PID_NS': 'y', 'IPC_NS': 'y', 'POSIX_MQUEUE': 'y',
    'DEVTMPFS': 'y', 'NET_NS': 'y', 'VETH': 'y', 'BRIDGE': 'y',
    'SECCOMP': 'y', 'SECCOMP_FILTER': 'y', 'MEMCG': 'y',
    'ZRAM': 'm', 'CRYPTO_LZ4K': 'm', 'CRYPTO_LZ4KD': 'm',
    'CRYPTO_LZ4K_OPLUS': 'm', 'CRYPTO_LZ4HC': 'm', 'CRYPTO_842': 'm',
    'ZRAM_DEF_COMP': '"lzo-rle"', 'DEFAULT_TCP_CONG': '"cubic"',
    'MODVERSIONS': 'y',
}
errors = [f'CONFIG_{key}: expected {value}, got {config.get("CONFIG_" + key, "n")}'
          for key, value in required.items() if config.get('CONFIG_' + key) != value]
for key in ('REKERNEL', 'BBG', 'CFS_BANDWIDTH', 'CGROUP_PIDS', 'BPF_STREAM_PARSER'):
    if config.get('CONFIG_' + key, 'n') != 'n':
        errors.append(f'CONFIG_{key} unexpectedly enabled')
if errors:
    raise SystemExit('\n'.join(errors))
print(f'OPD2413: {len(required)} resolved options verified; ABI and runtime verification still pending')
