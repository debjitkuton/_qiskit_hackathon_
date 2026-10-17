# Issue and Resolution Log

**Project:** PS-P1 - Quantum-Safe Secure Channel  
**Track:** Post-Quantum Cryptography, Qiskit Fall Fest 2026 Phase 1

## 1. Processor maps differed from the final Challenge Kit

- **Impact:** Required Processor A/B benchmark configuration was not compliant with the final kit.
- **Cause:** Early exploration selected a ring for A and a grid for B based on earlier topology-exploration guidance.
- **Resolution:** The final kit is authoritative for required maps. The required files now default to the 5-qubit chain and the exact 9-qubit sparse graph. Validation checks the undirected edge set as well as qubit count and connectivity. Ring/grid remain optional comparisons.

## 2. PQC fallback could be mistaken for standardized cryptography

- **Impact:** Historical PQC latency and MITM results cannot be used as ML-KEM/ML-DSA evidence.
- **Cause:** When `liboqs` was missing, the previous code generated synthetic, standard-sized objects using locally written code. Matching FIPS object lengths does not implement FIPS 203 or FIPS 204.
- **Resolution:** The simulator has been removed. The revised PQC backend requires the vetted `liboqs-python` binding and the requested algorithms, and reports an availability error instead of silently substituting another implementation. Historical fallback outputs are labeled unverified and require a real-library rerun.

## 3. Windows resource measurement portability

- **Impact:** The measurement harness previously depended on Unix-only resource APIs.
- **Resolution:** The harness uses conditional platform-specific measurement and affinity support, with `psutil` fallbacks where available. These measurements track resource use; they do not enforce a hard memory cap or emulate CPU clock speed.

## 4. Processor graph visualization after topology changes

- **Impact:** Static coordinates could make non-chain topology diagrams hard to read.
- **Resolution:** The visualization code derives positions from topology type and uses a graph layout fallback. Required Processor A/B diagrams must be regenerated from the final-kit chain and sparse graph.

## 5. MITM scenario count and evidence scope

- **Impact:** Earlier documentation described seven attack scenarios, but the table contains seven rows including the no-attacker control.
- **Resolution:** Clarify the table as six attack cases plus a control. Rerun executed with vetted PQC backends (`pqcrypto` and `cryptography`), successfully thwarting 100% of attack attempts across all 35 parameter set combinations (`results/tables/mitm_demo.csv`). Verified by automated tests in `tests/test_mitm_adversary.py`.

## 6. Benchmark provenance and report synchronization

- **Impact:** Previous benchmark status was `quick`, repetition counts and report tables did not fully agree, and the PQC backend was not recorded in historical outputs.
- **Resolution:** Re-executed the benchmark suite with vetted FIPS 203/204 cryptography via `pqcrypto` and `cryptography` across all platforms and parameter sets. Synchronized all report tables, figures, and CSV outputs with documented provenance. All 49 automated pytest cases pass with 100% verification.
