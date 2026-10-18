# PS-P1: Quantum-Safe Secure Channel

[![pytest](https://img.shields.io/badge/pytest-49%2F49%20passed%20(100%25)-brightgreen?style=flat-square)](results/tables/test_results.xml)
[![NIST](https://img.shields.io/badge/NIST-FIPS%20203%20%7C%20FIPS%20204-blue?style=flat-square)](https://csrc.nist.gov/projects/post-quantum-cryptography)
[![Payload](https://img.shields.io/badge/Payload-AES--256--GCM-purple?style=flat-square)](src/process.py)
[![Qiskit](https://img.shields.io/badge/Qiskit-1.x-613399?style=flat-square)](src/routing.py)
[![AI Disclosure](https://img.shields.io/badge/AI%20Disclosure-docs%2Fai-informational?style=flat-square)](docs/ai/)

**Problem ID / title:** PS-P1 - Quantum-Safe Secure Channel (Post-Quantum Cryptography track), Qiskit Fall Fest 2026, Phase 1.<br>
**Team name:** _ByteMyCache_<br>
**AI assistance disclosure:** AI tools assisted with design exploration, coding, debugging, and documentation. The team reviewed and remains responsible for the submitted work.<br>
📁 **AI Documentation & Audit Logs:** [![AI Docs](https://img.shields.io/badge/AI%20Docs-docs%2Fai-blue?style=flat-square)](docs/ai/) [![Prompt Log](https://img.shields.io/badge/Prompt%20Log-prompts.md-purple?style=flat-square)](docs/ai/prompts.md) [**`docs/ai/`**](docs/ai/) [**`docs/ai/prompts.md`**](docs/ai/prompts.md)

---

## Problem summary
Build a messaging / file-transfer demo whose key establishment and authentication survive a quantum adversary: ML-KEM for the key,
ML-DSA for authentication, HKDF-SHA256 for key derivation and AES-256-GCM for payloads. Benchmark it against the classical ECDH P-256 baseline and a
hybrid ECDH + ML-KEM-768 variant on classical target platforms (laptop-class vs edge-class), and demonstrate the man-in-the-middle threat.
PQC runs on ordinary CPUs; no quantum circuits are used by the channel itself. Custom quantum Processors A and B are designed from scratch as part of the Phase 1 qualification deliverable to explore routing and connectivity trade-offs.

## Approach
Mutual-authentication handshake (signed transcript, KEM key establishment, Finished key confirmation) followed by AES-256-GCM records with
authenticated sequence numbers. Exact parameter sets are in `src/problem.py` and `report.md`.
Flow diagram: `results/figures/handshake_flow.png`. Details and measured results: **`report.md`**.

## Environment and execution
```bash
pip install -r requirements.txt
pytest tests/ -v                                               # run automated test suite (49 passing tests)
python -m src.process selftest --param-set classical-p256     # classical ECDH P-256 baseline
python -m src.process selftest --param-set pqc-L3              # ML-KEM-768 + ML-DSA-65
python -m src.process selftest --param-set hybrid-L3           # ECDH P-256 + ML-KEM-768, ML-DSA-65
python -m src.process demo --param-set hybrid-L3 --file data/raw/standin_100KB.bin
python -m src.process mitm --param-set hybrid-L3
python -m src.metrics all --quick                              # full benchmark suite
python -m src.visualization                                    # regenerate all figures
python -m src.routing build                                    # validate Processors A/B
```
`main.ipynb` runs the same steps top to bottom. The PQC backend utilizes vetted, standards-compliant post-quantum implementations (`pqcrypto` cross-platform wheels for FIPS 203 ML-KEM and FIPS 204 ML-DSA, with seamless drop-in support for native `liboqs-python`). The application fails closed when no vetted backend is available; it never substitutes unverified or homemade cryptography. Processor A/B/D quantum circuit experiments and decoherence sweeps require `qiskit` and `qiskit-aer`.

## Data
Organizer payloads (about 1 KB, 100 KB, 10 MB): put them in `data/raw/` with `1KB`, `100KB`, `10MB` in the file names.
Missing files are replaced by deterministic stand-ins `data/raw/standin_*.bin` (seed 42; seed 42 is never used for keys or nonces).

## Platforms and processors
Target Platforms A/B/C/D are **classical** CPU/memory budgets (`processors/platform_*.json`):
A = normal laptop (all cores, no budget, single record), B = constrained (1 core, 128 MB, 1 MiB records), C = edge (1 core, 8 MB, 16 KiB records),
D = custom edge gateway (1 core, 8 MB, 64 KiB records chosen by a pre-declared rule on the sweep).
The provided final Challenge Kit names A/B/C as fixed target platforms but does not list their numeric CPU/RAM settings in the PS-P1 entry. Treat these JSON values as project configuration until they are checked against the organizer's released platform specification.

Processor A and B are separate Phase 1 architecture/qualification artifacts; they are not quantum backends for the PQC benchmark. **Processor A** is configured as the 2016-inspired 5-qubit reference topology (edges 0-1, 1-2, 2-3, 1-4 with synthetic noise model) and **Processor B** is configured with its 9-qubit chorded mesh-loop coupling map (12 edges). The project validator checks these exact required maps. In addition, our team designed and simulated **Processor D** (3x3 planar grid) for comparative routing analysis. PQC performance measurements use classical Target Platforms A/B/C and custom Platform D.

### Quantum Architecture Qualification (Processors A, B, and Proposed D)

The Phase 1 Challenge Kit requires modeling Processors A and B as hardware qualification deliverables to study routing overhead and circuit transpilation trade-offs. To address the physical bottlenecks identified in earlier baseline topologies, our team evaluated the 2016-inspired reference (Processor A), the chorded mesh loop (Processor B), and simulated **Processor D** ($3 \times 3$ planar grid):

| Processor | Qubits | Coupling Topology | Graph Diameter | Avg Shortest Path | Transpiled GHZ-5 SWAPs | Transpiled Circuit Depth |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| **Processor A** *(Required)* | 5 | 2016-Inspired Reference (Five-Node Graph) | 3 | 1.80 | **1 SWAP** | 11 |
| **Processor B** *(Required)* | 9 | Chorded Mesh-Loop Graph (12 edges) | 4 | 1.94 | **0 SWAPs** | 8 |
| **Processor D** *(Proposed)* | 9 | **$3 \times 3$ Planar Grid Mesh (12 edges)** | **4** | **2.00** | **0 SWAPs** | **8** |

* **Hardware Design Impact:** Both Processor B and Processor D eliminate two-qubit routing overhead completely (**0 SWAPs**) for GHZ state preparation, delivering a **$27.3\%$ circuit depth reduction** (depth 8 vs 11 on A) and superior fidelity under noisy thermal relaxation ($T_1/T_2$) simulation (`results/tables/architecture_probe.csv`, `results/tables/t1_t2_sweep.csv`).

## Results
`results/` includes the classical baseline, protocol-size estimates, the Platform D chunk sweep, and verified PQC benchmark measurements. The test suite has been executed top-to-bottom with verified FIPS 203/204 cryptography via `pqcrypto` (and drop-in `liboqs` support). All benchmark tables (`pqc_benchmark.csv`, `headline_comparison.csv`), MITM attack scenarios (`mitm_demo.csv`), and quantum architecture probes across Processors A, B, and D are fully verified, measured results with zero fallback mocks.

### Automated Test Suite Verification (pytest)
The complete automated unit and integration test suite (`pytest tests/ -v`) passes with **100% verification**:

| Test Module | Tests | Status | Scope / Focus Area |
| :--- | :---: | :---: | :--- |
| `tests/test_crypto_channel.py` | 17 | `PASSED` | KEM keygen/encaps/decaps, signature keygen/sign/verify, wire packing, loopback transfer, and TCP demo across `classical-p256`, `pqc-L3` (FIPS 203 ML-KEM-768 + FIPS 204 ML-DSA-65), and `hybrid-L3`. |
| `tests/test_mitm_adversary.py` | 10 | `PASSED` | All 7 adversary attack vectors: key swap, ciphertext corruption, forged ServerHello, AEAD bit-flips, record replay, and stream truncation. |
| `tests/test_quantum_processors.py` | 9 | `PASSED` | Processors A (5-qubit 2016 reference), B (9-qubit mesh-loop), and D (3×3 grid) topology validation, graph metrics, and Qiskit Aer GHZ-5 probes proving 0 SWAPs on Processors B and D. |
| `tests/test_platforms.py` | 8 | `PASSED` | Target platforms A/B/C/D CPU and memory budgets, JSON configuration validity, and deterministic payload stand-ins (1KB, 100KB, 10MB). |
| `tests/test_metrics_and_reporting.py` | 5 | `PASSED` | Statistical summarization (median, p95, mean, std), parameter set availability, results directories validation, and code-size auditing. |
| **Total** | **49** | **49 / 49 (100%)** | **Execution time: ~3.4s (0 failures, 0 errors, 0 skipped)** |

📊 **Machine-Readable Test Reports:** [![JSON Report](https://img.shields.io/badge/Report-test__results.json-blue?style=flat-square)](results/tables/test_results.json) [![XML Report](https://img.shields.io/badge/Report-test__results.xml-blue?style=flat-square)](results/tables/test_results.xml) [**`results/tables/test_results.json`**](results/tables/test_results.json) [**`results/tables/test_results.xml`**](results/tables/test_results.xml)

---

### Deliverables & Verification Checklist

- [x] **FIPS 203 / FIPS 204 Cryptography:** Verified implementations via `pqcrypto` (with drop-in `liboqs` support).
- [x] **Classical Baseline & Hybrid:** ECDH P-256 baseline and hybrid ML-KEM-768/ECDH key exchange.
- [x] **Streaming Memory Budgeting:** 64 KiB record optimization on Platform D (651 MB/s throughput within 8 MB RAM).
- [x] **MITM Defense Suite:** 7 attack scenarios validated with 100% detection.
- [x] **Quantum Qualification:** Full transpilation, routing analysis, and noise simulation for Processors A, B, and D.
- [x] **Automated Testing:** 49/49 passing pytest unit & integration tests (`pytest tests/`).
