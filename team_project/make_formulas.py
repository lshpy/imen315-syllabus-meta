"""LaTeX 수식 → PNG 이미지 생성 (matplotlib mathtext)"""
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path(__file__).parent / "formulas"
OUT.mkdir(exist_ok=True)


def render(latex, filename, fontsize=36):
    fig = plt.figure(figsize=(8, 1.2))
    fig.patch.set_alpha(0)
    ax = fig.add_subplot(111)
    ax.axis("off")
    ax.text(0.5, 0.5, f"${latex}$", ha="center", va="center",
            fontsize=fontsize, color="#0F141F")
    plt.savefig(OUT / filename, transparent=True, bbox_inches="tight",
                pad_inches=0.1, dpi=200)
    plt.close()
    print(f"  ✅ {filename}")


# 1. Utility Learning
render(r"U(n) = U(n{-}1) + \alpha \cdot \left[R(n) - U(n{-}1)\right]",
       "f_utility.png")

# 2. Memory Activation
render(r"B = \ln\!\left(\sum_{j=1}^{n} t_j^{-d}\right), \quad T_{retrieval} = e^{-B}",
       "f_memory.png")

# 3. Working Memory
render(r"\text{Capacity} \approx 7 \pm 2 \text{ chunks}", "f_wm.png", fontsize=32)

# 4. Framing
render(r"\text{Loss aversion} \approx 2 \times \text{Gain seeking}",
       "f_framing.png", fontsize=32)

print(f"\n저장 위치: {OUT}")
