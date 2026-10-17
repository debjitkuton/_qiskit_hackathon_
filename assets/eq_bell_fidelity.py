"""Bell state fidelity.

Run from anywhere:  python eq_bell_fidelity.py
Writes eq_bell_fidelity.png next to this script. Needs only matplotlib.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"mathtext.fontset": "cm", "font.family": "serif"})

OUT = Path(__file__).resolve().parent / "eq_bell_fidelity.png"
EQUATION = r"""$F = \langle \Phi^{+} | \rho | \Phi^{+} \rangle$"""

fig = plt.figure(figsize=(0.1, 0.1))
fig.patch.set_facecolor("white")
fig.text(0, 0, EQUATION, fontsize=26, color="black")
fig.savefig(OUT, dpi=300, bbox_inches="tight", pad_inches=0.12, facecolor="white")
plt.close(fig)
print("wrote", OUT)
