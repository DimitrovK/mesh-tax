# Rerun, 2026-10-06

A reader pointed out that the load generator in the original run sat inside the mesh, so a
"one hop" request crossed two proxies and all 32 connections shared one outbound proxy.
This rerun separates that from a per-request cost. Same cluster shape and Linkerd release
as the original (DOKS 1.36.3, 3 x s-4vcpu-8gb, fra1, edge-26.9.3).

`bench.py <label> <repeats>` runs seven configurations; `extra.yaml` adds a load generator
in an unmeshed namespace and a four-replica one inside the mesh.

Median requests per second at 32 connections, one hop (range in brackets):

- unmeshed, 8 runs across two passes: 30,278 (25,050 to 52,720)
- meshed, load generator inside the mesh, 5 runs: 6,009 (5,560 to 6,667)
- meshed, load generator outside the mesh, 5 runs: 13,000 (12,558 to 14,288)
- meshed, 4 load generators x 8 connections, 5 runs: 10,927 (9,445 to 11,296)

The proxy runs one worker thread by default (`LINKERD2_PROXY_CORES=1`, `tokio_rt_workers 1`).
`out/meshed_maxcores4` is the same sweep with `config.linkerd.io/proxy-cpu-limit: "4"`
(`tokio_rt_workers 4`).

The original README's statement that the proxy had no core restriction was wrong.
