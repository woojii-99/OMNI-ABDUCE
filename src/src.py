# Title: OMNI-ABDUCE — 옴니데이터 귀추적 시각화 미니앱

from __future__ import annotations
import argparse
from dataclasses import dataclass
from typing import Dict, Tuple, List
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

def _try_set_korean_font():
    try:
        import matplotlib

        for fname in ["NanumGothic", "AppleGothic", "Malgun Gothic", "Noto Sans CJK KR"]:
            try:
                plt.rcParams["font.family"] = fname
                # 테스트 렌더링 시도
                fig = plt.figure()
                plt.text(0.5, 0.5, "한글폰트", ha="center")
                plt.close(fig)
                return
            except Exception:
                continue
        plt.rcParams["axes.unicode_minus"] = False
    except Exception:
        pass

_try_set_korean_font()

# --------- 작은 CPT/사전확률 정의 ---------
@dataclass
class CPT:
    # P(Alarm | Burglary, Earthquake, Fire)
    # P(Smoke | Fire)
    alarm_given: Dict[Tuple[int, int, int], float]
    smoke_given_fire: Dict[int, float]

# 간단 prior (활성 원인 수를 작게 두는 경향)
PRIORS = {
    "Burglary": 0.35,
    "Earthquake": 0.35,
    "Fire": 0.45,
}

CPTS = CPT(
    alarm_given={
        (0, 0, 0): 0.01,
        (1, 0, 0): 0.90,
        (0, 1, 0): 0.70,
        (0, 0, 1): 0.60,
        (1, 1, 0): 0.95,
        (1, 0, 1): 0.96,
        (0, 1, 1): 0.92,
        (1, 1, 1): 0.99,
    },
    smoke_given_fire={
        0: 0.05,
        1: 0.95,
    },
)

def likelihood(hypothesis: Dict[str, int], obs: Dict[str, bool]) -> float:
    b = hypothesis.get("Burglary", 0)
    e = hypothesis.get("Earthquake", 0)
    f = hypothesis.get("Fire", 0)
    p_alarm = CPTS.alarm_given[(b, e, f)]
    p_smoke = CPTS.smoke_given_fire[f]
    lh = 1.0
    if "Alarm" in obs:
        lh *= p_alarm if obs["Alarm"] else (1.0 - p_alarm)
    if "Smoke" in obs:
        lh *= p_smoke if obs["Smoke"] else (1.0 - p_smoke)
    return lh

def score(hypothesis: Dict[str, int], obs: Dict[str, bool]) -> float:
    # Posterior ∝ likelihood × prior(활성 원인들의 곱)
    prior = 1.0
    for k, v in hypothesis.items():
        if v == 1:
            prior *= PRIORS[k]
        else:
            # 비활성에 대한 약한 패널티(완전 무시는 아님)
            prior *= 0.75
    return likelihood(hypothesis, obs) * prior

def enumerate_hypotheses() -> List[Dict[str, int]]:
    causes = ["Burglary", "Earthquake", "Fire"]
    hyps: List[Dict[str, int]] = []
    for mask in range(1, 1 << len(causes)):  # 공집합 제외
        h = {c: 1 if (mask >> i) & 1 else 0 for i, c in enumerate(causes)}
        hyps.append(h)
    return hyps

# --------- 시각화 ---------
def visualize(top_h: Dict[str, int], top_score: float, observations: Dict[str, bool], out_path: str = "omni_abduce_demo.png"):
    fig, ax = plt.subplots(figsize=(8, 5))
    pos = {
        "Burglary": (0.1, 0.75),
        "Earthquake": (0.1, 0.25),
        "Fire": (0.1, 0.50),
        "Alarm": (0.8, 0.60),
        "Smoke": (0.8, 0.30),
    }

    # 제목 박스
    title_text = "OMNI-ABDUCE — 옴니데이터 귀추적 시각화"
    ax.add_patch(Rectangle((0.02, 0.91), 0.96, 0.07, fill=False))
    ax.text(0.5, 0.945, title_text, ha="center", va="center", fontsize=13)

    def draw_node(name: str, highlight: bool = False, observed=None):
        x, y = pos[name]
        r = 0.06 if not highlight else 0.08
        circ = Circle((x, y), r, fill=False, linewidth=3 if highlight else 1.5)
        ax.add_patch(circ)
        label = name
        if observed is True:
            label += " ✓"
        elif observed is False:
            label += " ✗"
        ax.text(x, y, label, ha="center", va="center", fontsize=11)

    def arrow(frm: str, to: str):
        x1, y1 = pos[frm]
        x2, y2 = pos[to]
        arr = FancyArrowPatch((x1 + 0.07, y1), (x2 - 0.07, y2),
                              arrowstyle='-|>', mutation_scale=15, lw=1.5)
        ax.add_patch(arr)

    # 간선
    arrow("Burglary", "Alarm")
    arrow("Earthquake", "Alarm")
    arrow("Fire", "Alarm")
    arrow("Fire", "Smoke")

    # 원인 노드(최상 가설은 두껍게)
    for cause in ["Burglary", "Earthquake", "Fire"]:
        draw_node(cause, highlight=(top_h.get(cause, 0) == 1))

    # 효과 노드(관측 마크)
    draw_node("Alarm", observed=observations.get("Alarm", None))
    draw_node("Smoke", observed=observations.get("Smoke", None))

    # 설명 텍스트
    lines = [
        "관측: " + ", ".join([f"{k}={v}" for k, v in observations.items()]),
        "최상 가설: " + (", ".join([k for k, v in top_h.items() if v == 1]) or "(없음)"),
        f"점수(unnormalized): {top_score:.4g}",
    ]
    ax.text(0.02, 0.05, "\n".join(lines), ha="left", va="bottom", fontsize=10)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.show()
    print(f"Saved figure to: {out_path}")

# --------- 메인 ---------
def str2bool(s: str) -> bool:
    return s.strip().lower() in {"1", "true", "t", "yes", "y"}

def main():
    parser = argparse.ArgumentParser(description="OMNI-ABDUCE — 옴니데이터 귀추적 시각화")
    parser.add_argument("--alarm", type=str, default="true", help="Alarm observed? (true/false)")
    parser.add_argument("--smoke", type=str, default="true", help="Smoke observed? (true/false)")
    parser.add_argument("--out", type=str, default="omni_abduce_demo.png", help="Output PNG path")
    args = parser.parse_args()

    observations = {
        "Alarm": str2bool(args.alarm),
        "Smoke": str2bool(args.smoke),
    }

    hyps = enumerate_hypotheses()
    scored = [(h, score(h, observations)) for h in hyps]
    scored.sort(key=lambda x: x[1], reverse=True)
    top_h, top_score = scored[0]

    visualize(top_h, top_score, observations, out_path=args.out)

if __name__ == "__main__":
    main()
