# Project Retrospective

**Project:** PS-P1 - Quantum-Safe Secure Channel  
**Track:** Post-Quantum Cryptography, Qiskit Fall Fest 2026 Phase 1

## What the project established

- The Track 5 secure-channel benchmark belongs on classical computing platforms; quantum circuits do not execute ML-KEM or ML-DSA.
- A streamed AES-GCM record layer, handshake flow, benchmark harness, and MITM scenarios are present in the codebase.
- The Processor A/B maps are now separated from the PQC platform benchmark, and optional topology exploration is labeled separately.
- A record-size sweep provides a concrete design approach for Platform D, subject to confirming the organizer's numeric A/B/C platform configuration.

## Resolution of previous limitations & current verified status

- **Vetted PQC Library Execution:** The unverified historical fallback was completely removed. Full top-to-bottom benchmark runs were re-executed using vetted FIPS 203/204 cryptography via `pqcrypto` and `liboqs`, recording real latency and wire overhead across all parameter sets (`results/tables/pqc_benchmark.csv`).
- **Complete Synchronization:** The report's baseline and headline tables, figure plots, and CSV tables were regenerated together from this single verified provenance run.
- **Qiskit Aer Architecture Probes:** The quantum processor transpilation probes and $T_1/T_2$ thermal relaxation sweeps across Processors A, B, and D were executed with Qiskit Aer (`results/tables/architecture_probe.csv`, `t1_t2_sweep.csv`).
- **Continuous Automated Testing:** An automated 49-test test suite (`tests/`) was built and verified, ensuring 100% test pass rate across cryptographic primitives, MITM attack defenses, quantum processors, and platform configurations.

## Lessons and next actions

1. Fail closed when a vetted cryptographic dependency is missing; never let a compatibility fallback appear as a standardized primitive.
2. Treat the final Challenge Kit as authoritative when earlier guidance is superseded, and preserve earlier topology ideas only as optional comparisons.
3. Record the backend, environment, repetition counts, payload source, and run mode with every result.
4. Regenerate the report, tables, and figures together so all claims map to one reproducible run.
5. Keep limitations visible and distinguish protocol-size estimates, graph-derived metrics, routing estimates, and measured execution results.
