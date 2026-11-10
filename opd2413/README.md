# OPD2413 V2 first build

Target: ColorOS OPD2413_16.0.9.400(CN01), official Linux 6.6.118 sources.
Upstream workflow snapshot: Numbersf/Action-Build d8e1dff309f8ab35b40afbf27d5444e095be8010.
`source-lock.json` records the three OnePlus commits explicitly published for this firmware.

Features: built-in SukiSU Ultra, KPM, SUSFS, Netfilter/IPSet/IPv6 NAT,
BBRv3 and DroidSpaces support. Re:Kernel and LSM_BBG remain disabled.
HMBIRD handling follows upstream with SCHED_HMBIRD=false, including automatic
OGKI/GKI compatibility handling when needed; no additional scheduler tuning.

`ZRAM_BUILD=true` compiles extra codecs as modules and an optional zram.ko.
`ZRAM=0/lz4kd/8589934592` does not create the automatically activated root module.
The optional module archive is separate from AnyKernel3 and has no installer.
Preserve the source's default compressor and module loader. No sysctl is written,
no swap size is changed, no container or performance module is installed.
The modified networking and namespace kernel paths still require real-device
verification; compiling capabilities alone does not prove stock-equivalent behavior.

The resolved .config, Module.symvers, System.map and source diff are uploaded.
FAST_BUILD compilation is not a completed vendor ABI/KMI comparison. The target
firmware's modules and a first boot are still required to validate compatibility.
Keep the target firmware's original boot/init_boot and a working fastboot restore
path available before deployment. No flashing is performed by this workflow.

DroidSpaces: do not enable CFS_BANDWIDTH or CGROUP_PIDS on stock vendor modules.
Its documented SUSFS workaround requires disabling global mount hiding;
SUSFS configurations remain outside DroidSpaces' official support.
Runtime acceptance: boot, SukiSU authorization, KPM load/query/unload, suspend and
wake, pen input, and DroidSpaces requirements probes. These are pending.

Sources:
- https://github.com/OnePlusOSS/kernel_manifest/blob/oneplus/sm8750/oneplus_pad_2_pro_b.xml
- https://www.droidspaces.org/docs/kernel-configuration.html
- https://www.droidspaces.org/docs/installation-android.html

## Stable SUSFS integration fix

The first compile passed 28 resolved configuration checks, then failed because
SukiSU calls the SUSFS priority UID filter API but omits its Kconfig entry.
The small Kconfig patch restores the definition from the official SUSFS patch,
and the resolved-option check now includes it. Both component revisions are
pinned in `components.json` and `inputs.json`; SUSFS_DEV remains false.
Compilation caches are preserved after failures to reduce the cost of retries.
