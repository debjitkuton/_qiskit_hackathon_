# AI-Assisted Engineering Methodology & Decision Record

**Project:** PS-P1 — Quantum-Safe Secure Channel & Hardware Qualification  
**Track:** Post-Quantum Cryptography & Quantum Systems Modeling  
**Event:** Qiskit Fall Fest 2026, Phase 1  
**Team:** ByteMyCache  

---

## 1. Governance & AI Collaboration Framework

In compliance with the Qiskit Fall Fest 2026 Academic Integrity and Generative AI Disclosure Guidelines, this document outlines the collaborative engineering methodology between the team and AI design assistants. 

AI tooling was utilized strictly as an interactive engineering accelerator for mathematical formulation, design space exploration, code refactoring, adversary modeling, and cross-platform CI orchestration. The human engineering team independently audited, reviewed, verified, and validated all cryptographic correctness, physical quantum models, and empirical benchmark evidence.

---

## 2. Chronological Engineering & Decision Milestones

### Session 1: Architectural Disentanglement (Classical PQC vs. NISQ Modeling)
* **Engineering Problem:** Initial hackathon problem specifications created potential ambiguity regarding whether post-quantum cryptography (PQC) was meant to execute on simulated quantum hardware backends.
* **Exploration & Analysis:** Analyzed NIST PQC deployment guidelines and Section 10 of the Challenge Kit. Established the fundamental distinction between:
  1. **Post-Quantum Cryptography:** Classical mathematical algorithms (lattice-based polynomial rings) engineered to execute efficiently on conventional CPUs while remaining mathematically resilient against Shor's and Grover's quantum algorithms.
  2. **Quantum Hardware Qualification:** Processor A (5-qubit chain) and Processor B (9-qubit tree) are NISQ hardware coupling models required to analyze compiler routing overhead and decoherence.
* **Engineering Decision:** Established a strict architectural separation: the secure channel and benchmark suite execute natively on classical host processors across Platforms A–D, while Processors A, B, and D are evaluated via Qiskit Aer for compiler and decoherence characterization.

---

### Session 2: Cryptographic Standards & Fail-Closed Policy Enforcement
* **Engineering Problem:** An early exploratory draft included synthetic standard-sized byte buffers as a fallback when native `liboqs` bindings were absent.
* **Exploration & Analysis:** Synthetic buffers matching FIPS object lengths do not constitute valid cryptographic implementations and cannot support security or latency claims.
* **Engineering Decision:** Completely eliminated all synthetic or mock cryptographic fallbacks. Enforced a strict **fail-closed security policy**:
  * Integrated **NIST FIPS 203 (ML-KEM-768)** and **NIST FIPS 204 (ML-DSA-65)** using vetted C reference implementation wheels via `pqcrypto`, with seamless drop-in support for native `liboqs-python`.
  * The system raises a terminal `BackendUnavailable` exception if vetted cryptography is missing, ensuring zero unverified claims.

---

### Session 3: Hybrid Key Derivation & Threat Model Design (`hybrid-L3`)
* **Engineering Problem:** Transitioning entirely to post-quantum lattice cryptography carries transitional risks if early lattice mathematics encounters unanticipated algebraic vulnerabilities. Conversely, classical cryptography remains vulnerable to **Harvest Now, Decrypt Later (HNDL)** attacks by future cryptanalytically relevant quantum computers (CRQCs).
* **Exploration & Analysis:** Evaluated hybrid key exchange standards from NIST SP 800-227 and IETF TLS 1.3 drafts.
* **Engineering Decision:** Implemented the `hybrid-L3` parameter set combining classical **ECDH P-256** and post-quantum **ML-KEM-768**:
  $$K_{\text{master}} = \text{HKDF-Extract}(\text{salt}, SS_{\text{classical}} \parallel SS_{\text{PQC}})$$
  This guarantees that communication security holds if *either* the elliptic curve discrete logarithm problem or the module learning-with-errors (M-LWE) lattice problem remains unbroken.

---

### Session 4: Edge Memory Containment & Streaming Optimization (Platform D)
* **Engineering Problem:** Microcontroller and embedded gateway platforms (Platforms C & D, 8 MB RAM budget) fail when buffering multi-megabyte payloads in a single memory block.
* **Exploration & Analysis:** Designed an independently authenticated streaming record layer utilizing AES-256-GCM with 4-byte framing, 64-bit monotonically increasing sequence numbers, and an authenticated terminal flag.
* **Engineering Decision:** Conducted a comprehensive record-size sweep from 1 KiB to single-record allocations:
  * Selected **64 KiB** as the optimal operational knee for Platform D, achieving peak streaming throughput (**651.1 MB/s**) with negligible framing overhead (**0.032%**).
  * Restricted peak heap allocation during a 10 MB payload transfer to **401 KB** on Platform D and **113 KB** on Platform C—achieving a **$272\times$ memory reduction** over unchunked transfers.

---

### Session 5: Formal Adversarial Threat Modeling & Automated Defense Validation
* **Engineering Problem:** Validating that the protocol defends against active on-path man-in-the-middle adversaries without leaking sensitive internal state or allowing silent data manipulation.
* **Exploration & Analysis:** Formulated a formal adversary matrix covering 7 distinct attack vectors:
  1. Ephemeral public key substitution
  2. In-flight KEM ciphertext tampering
  3. ServerHello impersonation with forged signatures
  4. AEAD ciphertext payload bit-flipping
  5. Monotonic sequence counter replay injection
  6. Premature stream truncation without authenticated EOF
  7. Honest control baseline
* **Engineering Decision:** Built an automated adversary evaluation suite in `src/process.py` and `tests/test_mitm_adversary.py`, verifying 100% detection and fail-closed rejection across all 35 combinations of attacks and parameter sets.

---

### Session 6: Quantum Hardware Qualification & Proposed Zero-SWAP Architecture (Processor D)
* **Engineering Problem:** Phase 1 requires analyzing hardware qualification bottlenecks for Processors A (5-qubit chain) and B (9-qubit tree). The linear chain requires substantial SWAP routing overhead for multi-qubit entanglement, causing severe decoherence in near-term NISQ devices.
* **Exploration & Analysis:** Analyzed graph diameter and average shortest path lengths. Developed a custom $3 \times 3$ Planar Grid Mesh (**Processor D**) with central hub nodes to optimize GHZ state preparation and multi-qubit entanglement.
* **Engineering Decision:** Implemented and validated Processor D in `processors/processor_D.json` and `src/routing.py`:
  * Mathematically proved **0 SWAPs** required for 5-qubit GHZ state generation via Qiskit Aer (optimization level 1, SABRE routing).
  * Reduced transpiled circuit depth from 14 down to **8** ($42.8\%$ reduction).
  * Executed comprehensive $T_1/T_2$ decoherence sweeps ($10\,\mu\text{s}$ to $200\,\mu\text{s}$), demonstrating a measured **$+5.38\%$ fidelity advantage** in NISQ regimes ($T_1 \le 30\,\mu\text{s}$).

---

### Session 7: Automated Verification Architecture & Cloud CI/CD Automation
* **Engineering Problem:** Ensuring high software engineering maturity, continuous reproducibility, and cross-platform verification across disparate operating systems.
* **Exploration & Analysis:** Standardized testing frameworks using `pytest` and configured continuous integration via GitHub Actions.
* **Engineering Decision:** 
  * Authored a 49-test test suite (`tests/`) covering cryptographic correctness, MITM defense mechanisms, quantum topologies, and platform configurations, executing in **~3.1s**.
  * Implemented `.github/workflows/ci.yml` running a multi-OS (Linux and Windows) and multi-Python (3.10 and 3.11) matrix in GitHub Actions, automatically generating JUnit XML reports and powering the verified green CI badge.

---

## 3. Human Audit & Integrity Statement

The human engineering team:
1. Conducted line-by-line verification of all cryptographic primitives, protocol state transitions, and mathematical formulas.
2. Verified all empirical benchmark figures against direct CSV runtime telemetry (`pqc_benchmark.csv`, `chunk_sweep.csv`, `architecture_probe.csv`).
3. Confirmed that no simulated or mock cryptographic fallbacks exist in the production or testing pipelines.
4. Assumes complete intellectual responsibility for all code, models, and analytical claims presented in this submission.
