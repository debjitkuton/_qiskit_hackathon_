# Mathematical Equations & Metrics Catalog

This directory contains standalone mathematical formulations, LaTeX code, and algorithmic implementations used throughout the **Quantum-Safe Secure Channel** project (Track PS-P1).

Each equation is documented in its own markdown document, providing native GitHub math rendering in preview mode and raw LaTeX code in source mode.

---

## Catalog of Equations

| Equation | Document | LaTeX Formulation | Context / Application |
| :--- | :--- | :--- | :--- |
| **Single-Qubit State** | [`eq_qubit_state.md`](eq_qubit_state.md) | $|\psi\rangle = \alpha\|0\rangle + \beta\|1\rangle,\; \|\alpha\|^2 + \|\beta\|^2 = 1$ | Computational basis representation & state normalization |
| **Bell State $\lvert\Phi^+\rangle$** | [`eq_bell_state.md`](eq_bell_state.md) | $\|\Phi^{+}\rangle = \frac{1}{\sqrt{2}}(\|00\rangle + \|11\rangle)$ | Entanglement generation across communication channels |
| **Parity Expectation $\langle ZZ \rangle$** | [`eq_zz_expectation.md`](eq_zz_expectation.md) | $\langle ZZ \rangle = \frac{N_{00} + N_{11} - N_{01} - N_{10}}{N}$ | Channel fidelity & eavesdropping parity checks |
| **Bell State Fidelity** | [`eq_bell_fidelity.md`](eq_bell_fidelity.md) | $F = \langle \Phi^{+} \| \rho \| \Phi^{+} \rangle$ | State overlap metric under noisy channel simulation |
| **Standard Error** | [`eq_standard_error.md`](eq_standard_error.md) | $\mathrm{SE} = \frac{\sigma}{\sqrt{N}},\; \mathrm{SE}_{\langle ZZ\rangle} = \sqrt{\frac{1 - \langle ZZ \rangle^2}{N}}$ | Measurement shot-noise bounds on observables |
| **Coupling Graph Metrics** | [`eq_graph.md`](eq_graph.md) | $G=(V,E),\; \bar{d} = \frac{2}{n(n-1)}\sum_{i<j} d(i,j),\; \mathrm{diam}(G) = \max_{i,j} d(i,j)$ | Routing SWAP overhead & processor topology analysis |
