"""Two diagnostic figures for the game study, using the same Graphviz card
aesthetic as diff_loc_analysis/graph_generator.py:

1. G6 (silent auction): the mechanically-valid candidate graph from
   gpt_5_6_sol_G6_s01_r0 (run_3) -- passed Lane 1 with zero findings -- versus
   a compressed phase graph of the reference structure (Lane 2 combined score
   was only 0.2979: 7 states / 52 transition edges vs reference 5 states / 6).
"""
import json
import os

import graphviz
from PIL import Image as PILImage, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT_DIR = os.path.join(ROOT, "report", "game_case_figures")
os.makedirs(OUT_DIR, exist_ok=True)

FONTS = ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "C:/Windows/Fonts/DejaVuSans-Bold.ttf",
         "C:/Windows/Fonts/arialbd.ttf")


def get_font(size=22):
    for p in FONTS:
        try:
            return ImageFont.truetype(p, size)
        except IOError:
            continue
    return ImageFont.load_default()


def style(dot):
    dot.attr(rankdir="LR", size="6,4.5", dpi="180")
    dot.attr("node", fontname="Helvetica", shape="ellipse", style="filled",
             fillcolor="lightgray", fontcolor="black")
    dot.attr("edge", fontname="Helvetica", color="gray50", fontsize="10")


def render(dot, name):
    path = os.path.join(OUT_DIR, name)
    dot.render(path, cleanup=True)
    return path + ".png"


def card(title, img_path, card_w, card_h, font):
    card_img = PILImage.new("RGB", (card_w, card_h), color=(255, 255, 255))
    d = ImageDraw.Draw(card_img)
    d.rectangle([0, 0, card_w - 1, card_h - 1], outline="#333333", width=2)
    img = PILImage.open(img_path)
    bbox = d.textbbox((0, 0), title, font=font)
    d.text(((card_w - (bbox[2] - bbox[0])) // 2, 20), title, fill="black", font=font)
    card_img.paste(img, ((card_w - img.width) // 2,
                         50 + 20 + ((card_h - 50 - 40 - img.height) // 2)))
    return card_img


def combine(titles, img_paths, out_name, gap=35):
    font = get_font(22)
    imgs = [PILImage.open(p) for p in img_paths]
    pad = 20
    w = max(i.width for i in imgs) + pad * 2
    h = max(i.height for i in imgs) + 50 + pad * 2
    canvas = PILImage.new("RGB", (w * len(imgs) + gap * (len(imgs) - 1), h), (255, 255, 255))
    x = 0
    for t, p in zip(titles, img_paths):
        canvas.paste(card(t, p, w, h, font), (x, 0))
        x += w + gap
    out = os.path.join(OUT_DIR, out_name)
    canvas.save(out)
    print("wrote", out)

# --------------------------------------------------------------------------
# Figure 2: G1 local-Qwen sample_003 -- plausible topology, wrong semantics
# (landscape / horizontal frame: one wide edge per terminal outcome)
# --------------------------------------------------------------------------
wm = json.load(open(os.path.join(ROOT, "experiments", "qwen", "G1", "sample_003", "world_model.json"), encoding="utf-8"))

g1 = graphviz.Digraph(format="png")
g1.attr(rankdir="LR", dpi="180", ranksep="2.6", nodesep="0.35", bgcolor="white")
g1.attr("node", fontname="Helvetica", shape="ellipse", style="filled", fontsize="16")
g1.attr("edge", fontname="Helvetica", color="gray50", fontsize="11")

g1.node("state_0002", "s0\n(both choose)", fillcolor="orange")
for s in wm["states"]:
    if s["id"] == "state_0002":
        continue
    g1.node(s["id"], s["representation"].strip("'"),
            fillcolor="royalblue" if s["terminal"] else "lightgray",
            fontcolor="white" if s["terminal"] else "black")

# group all joint-action outcomes by terminal state -> 3 wide edges total
grouped = {}
for t in wm["transitions"]:
    for o in t["outcomes"]:
        grouped.setdefault(o["next_state"], []).append((t["joint_action"], o))

for tgt, items in grouped.items():
    pairs, errs = [], set()
    r1 = sorted({o["rewards"]["player_1"] for _, o in items})[0]
    r2 = sorted({o["rewards"]["player_2"] for _, o in items})[0]
    obs1 = sorted({o["observations"]["player_1"] for _, o in items})
    obs2 = sorted({o["observations"]["player_2"] for _, o in items})
    for ja, o in items:
        pairs.append(f"{ja['player_1']}/{ja['player_2']}")
        if r1 == -1.0 and r2 == -1.0:
            errs.add("ERR: both lose (r=-1,-1)")
        elif "wins" in o["observations"]["player_1"] and "wins" in o["observations"]["player_2"]:
            errs.add("ERR: both players observe 'win'")
    label = ("  |  ".join(pairs) + "\n"
             f"r=({r1:+.0f},{r2:+.0f})   obs1={'; '.join(obs1)}\n"
             f"obs2={'; '.join(obs2)}"
             + ("\n" + " / ".join(sorted(errs)) if errs else ""))
    g1.edge("state_0002", tgt, label=label)

p3_path = render(g1, "g1_qwen_sample003_annotated")

combine(["Local-Qwen G1 sample_003: plausible topology (4 states)",
         "Same graph, semantics revealed: wrong rewards / player-specific observations"],
        [os.path.join(ROOT, "experiments", "qwen", "G1", "sample_003", "graph.png"), p3_path],
        "g1_qwen_topology_vs_semantics.png")
