# AI Assistance and Prompt Summary

**Project:** PS-P1 — Quantum-Safe Secure Channel  
**Track:** Post-Quantum Cryptography, Qiskit Fall Fest 2026 Phase 1  
**Team:** ByteMyCache  

## Disclosure and review process

AI tools were used as development assistants for requirement interpretation, design exploration, code drafting, debugging, benchmark analysis, and documentation. The team reviewed all outputs, verified implementation behavior, and confirmed that all claims match reproducible evidence.

This log summarizes the main assistance sessions and technical decisions chronologically to date.

---

## Session 1 — Separate PQC benchmark from processor qualification

**Prompt summary:** Interpret the guidance for PS-P1 and distinguish the classical computing platforms from the Processor A/B qualification models.

**AI contribution:** Organized the work into two distinct parts: (1) the secure-channel implementation and its benchmarks run as classical software on host CPUs; (2) Processors A and B are architecture artifacts for broader qualification requirements.

**Decision:** Keep the cryptographic benchmark on classical computing platforms (A–D). Do not describe ML-KEM or ML-DSA operations as quantum-circuit executions.

---

## Session 2 — Adopt required Processor A/B maps from final Challenge Kit

**Prompt summary:** Align the processor models with the final Challenge Kit definitions and evaluate connectivity and routing costs.

**AI contribution:** Identified that the final Challenge Kit mandates the 5-qubit nearest-neighbor chain for Processor A and a 9-qubit sparse tree for Processor B. Helped calculate graph metrics and baseline routing estimates.

**Decision:** Update `processor_A.json` and `processor_B.json` to the exact required maps. Retain previously explored ring and grid topologies strictly as optional comparisons.

---

## Session 3 — Design secure channel handshake and MITM threat model

**Prompt summary:** Structure a post-quantum handshake using the specified primitives and define on-path attacker scenarios.

**AI contribution:** Assisted with protocol flow documentation, signed transcripts, hybrid key derivation (`hybrid-L3`), AES-256-GCM streaming records, and a 7-case MITM evaluation matrix.

**Decision:** Use standard FIPS primitives with authenticated streaming records and sequence numbers to prevent packet replay, reordering, and truncation.

---

## Session 4 — Enforce vetted FIPS 203/204 cryptography & fail-closed backend

**Prompt summary:** Diagnose dependency behavior and ensure only real, standardized PQC implementations are used.

**AI contribution:** Identified that an earlier prototype used synthetic buffers when `liboqs` was missing. Integrated cross-platform `pqcrypto` wheels for FIPS 203 ML-KEM-768 and FIPS 204 ML-DSA-65 with drop-in `liboqs` support.

**Decision:** Eliminate all synthetic fallbacks. Enforce a strict fail-closed policy (`BackendUnavailable`) so the channel never substitutes unverified cryptography.

---

## Session 5 — Design proposed Processor D (3×3 grid) for zero-SWAP routing

**Prompt summary:** Analyze physical routing bottlenecks on Processors A and B, and design an improved architecture candidate to address them.

**AI contribution:** Simulated Qiskit circuit transpilation (SABRE routing) and identified that Processors A and B require 4 and 3 SWAPs for 5-qubit GHZ state preparation. Modeled a 9-qubit planar mesh (Processor D) and ran $T_1/T_2$ decoherence sweeps in Qiskit Aer.

**Decision:** Propose Processor D ($3\times3$ grid) in `processors/processor_D.json`. Document its zero-SWAP routing, 42.8% circuit depth reduction, and +5.38% fidelity advantage under noisy simulation.

---

## Session 6 — Platform D 64 KiB record optimization & edge streaming

**Prompt summary:** Characterize the resource/performance trade-off for custom Platform D within an 8 MB memory budget.

**AI contribution:** Scripted an automated chunk sweep from 1 KiB to single-record sizes, recording throughput, heap peaks via `tracemalloc`, and wire overhead.

**Decision:** Select 64 KiB records for Platform D, achieving 651.1 MB/s throughput within 401 KB peak heap (a 272× memory reduction compared to unchunked transfers).

---

## Session 7 — Automated test suite (49 pytest cases) & CI/CD workflow

**Prompt summary:** Build an automated unit and integration test suite and configure continuous integration for cross-platform verification.

**AI contribution:** Structured 49 test cases across 5 test modules (`tests/`) covering cryptographic primitives, MITM attacks, quantum processors, and platforms. Configured `.github/workflows/ci.yml` running across Ubuntu and Windows on Python 3.10 and 3.11.

**Decision:** Integrate the test suite into the repo and establish automated GitHub Actions CI to generate live test reports and badges.

---

## Session 8 — Documentation alignment & benchmark data synchronization

**Prompt summary:** Audit the report, README, and tables to remove stale disclaimers and ensure 100% data consistency.

**AI contribution:** Identified unsynchronized table entries in `report.md` from older test runs. Replaced them with exact values from `pqc_benchmark.csv` and `chunk_sweep.csv`. Cleaned up checklist formatting and verified links.

**Decision:** Ensure all numbers across the report, README, and CSV artifacts match live run outputs with complete provenance.

---

## Human review responsibility

All AI-assisted suggestions, scripts, and documentation were reviewed, tested, and validated by the team. All benchmark tables, quantum circuit simulations, and cryptographic test results reflect reproducible executions.
