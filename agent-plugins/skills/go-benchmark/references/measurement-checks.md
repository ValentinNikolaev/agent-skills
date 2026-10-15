# Go Measurement Checks

## Benchmark validity

- Confirm the benchmark actually exercises the production operation with representative inputs. Do not move required parsing, allocation, copying, or cleanup outside timing and then claim the full operation improved.
- Separate cold start, steady state, setup, cache hits/misses, and I/O effects. Keep input mutability and precomputed state equivalent between variants.
- Inspect compiler elimination and inlining against the Go version and benchmark API. Consume results through an appropriate observable; a global sink is not a universal requirement. Record any instrumentation that changes the hot path.
- Keep correctness assertions separate from timing claims. A faster variant that skips work, changes output/error behavior, or leaks resources is not an equivalent optimization.
- `b.RunParallel` measures concurrent throughput under its configured parallelism, not automatically request latency. Record GOMAXPROCS, synchronization, contention, and workload distribution.

## Comparison validity

- Require the same hardware, toolchain, harness, fixture, build tags/flags, and meaningful runtime settings. Changing a benchmark along with implementation can invalidate the comparison even at the same revision.
- Run repeated samples and record contention or throttling. Do not benchmark variants concurrently on shared CPUs, including separate worktrees or agents.
- Use the declared decision threshold and uncertainty. Do not treat an absent significance marker as proof of equivalence; say what resolution the experiment supports.
- Distinguish ns/op, B/op, allocs/op, and custom metrics. Lower allocation count alone does not establish lower latency or retained memory.
- When comparing historical reports, identify environment/harness mismatches before calculating percentage change. Missing baseline values are unknown, not zero.

## Profiles

- Select the profile for the question: CPU for on-CPU work; allocation profiles for churn; heap retention for live memory; mutex/block profiles for contention; execution trace for scheduling and timing. Absence from a CPU profile does not rule out I/O wait.
- Keep profile overhead and sampling limits visible. A benchmark profile, a live-service profile, and a production request trace describe different workloads.
- Request only the scope and duration needed. Use existing authorized local artifacts by default; never publish profiles or enable unauthenticated network endpoints automatically.
- Identify a supported bottleneck and a falsifiable next experiment. Do not apply a generic pooling, caching, unsafe, or concurrency recipe without workload evidence and correctness constraints.

Selected measurement and profile-interpretation principles adapt [Samber's benchmark references](https://github.com/samber/cc-skills-golang/tree/8e899e20ff0cd4dc524af3993e4c62d8ee8c5717/skills/golang-benchmark/references), under the parent package's scoped MIT license. Tool/API details remain subject to the project's supported versions.
