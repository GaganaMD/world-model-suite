"""Compressed phase graph for the audited G6 failure case, rendered from the
preserved artifacts:

Left  : reference G6 silent-auction ground-truth graph (5 states / 4 edges),
        loaded from run_1/05_evaluation/.../ground_truth_graph.pth.
Right : the Claude Opus 5 run-1 candidate (claude_opus_5_G6_s01_r0,
        matched F1 0.0383, 101 states / 81 transitions), compressed by
        aggregating every state under its verified phase prefix
        (s0 type draw | bid_* 4 type-conditioned bid states | tie_* 16
        tie states | end_* 80 terminals). Edge counts and bid vocabulary are
        aggregated from the preserved world_model.json, not drawn by hand.
"""
import json
import os
from collections import Counter, defaultdict

import graphviz
from PIL import Image as PILImage, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
OUT_DIR = os.path.join(ROOT, "report", "game_case_figures")
os.makedirs(OUT_DIR, exist_ok=True)

RUN1 = os.path.join(ROOT, "experiments", "openrouter_game_study", "run_1")
GT_PTH = os.path.join(RUN1, "05_evaluation", "claude_opus_5_G6_s01_r0", "ground_truth_graph.pth")
WM_JSON = os.path.join(RUN1, "04_world_models", "claude_opus_5_G6_s01_r0", "world_model.json")

FONTS = ("C:/Windows/Fonts/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/arialbd.ttf")


def get_font(size=22):
    for p in FONTS:
        try:
            return ImageFont.truetype(p, size)
        except IOError:
            continue
    return ImageFont.load_default()


def render(dot, name):
    path = os.path.join(OUT_DIR, name)
    dot.render(path, cleanup=True)
    return path + ".png"


def card(title, img, card_w, card_h, font):
    card_img = PILImage.new("RGB", (card_w, card_h), color=(255, 255, 255))
    d = ImageDraw.Draw(card_img)
    d.rectangle([0, 0, card_w - 1, card_h - 1], outline="#333333", width=2)
    if isinstance(img, str):
        img = PILImage.open(img)
    bbox = d.textbbox((0, 0), title, font=font)
    d.text(((card_w - (bbox[2] - bbox[0])) // 2, 20), title, fill="black", font=font)
    card_img.paste(img, ((card_w - img.width) // 2,
                         50 + 20 + ((card_h - 50 - 40 - img.height) // 2)))
    return card_img


def combine(titles, img_paths, out_name, gap=35):
    """Side-by-side cards at each panel's natural scale (no distortion)."""
    font = get_font(22)
    imgs = [PILImage.open(p) for p in img_paths]
    pad = 20
    title_h = 60
    h = max(i.height for i in imgs) + title_h + pad * 2
    xs = []
    total_w = 0
    for img in imgs:
        xs.append(total_w)
        total_w += img.width + pad * 2 + gap
    canvas = PILImage.new("RGB", (total_w - gap, h), (255, 255, 255))
    for t, img, x in zip(titles, imgs, xs):
        card_w = img.width + pad * 2
        d = ImageDraw.Draw(canvas)
        d.rectangle([x, 0, x + card_w - 1, h - 1], outline="#333333", width=2)
        bbox = d.textbbox((0, 0), t, font=font)
        d.text((x + (card_w - (bbox[2] - bbox[0])) // 2, 20), t, fill="black", font=font)
        canvas.paste(img, (x + pad, title_h + (h - title_h - pad * 2 - img.height) // 2))
    out = os.path.join(OUT_DIR, out_name)
    canvas.save(out)
    print("wrote", out)


def base_style():
    g = graphviz.Digraph(format="png")
    g.attr(rankdir="LR", size="6,4.5", dpi="180", ranksep="2.4", nodesep="0.4", bgcolor="white")
    g.attr("node", fontname="Helvetica", shape="ellipse", style="filled",
           fillcolor="lightgray", fontcolor="black", fontsize="14")
    g.attr("edge", fontname="Helvetica", color="gray50", fontsize="11")
    return g


# --------------------------------------------------------------------------
# Left panel: reference ground truth, straight from the preserved .pth
# (top-to-bottom, one node per state)
# --------------------------------------------------------------------------
import torch

gt = torch.load(GT_PTH, weights_only=False, map_location="cpu")
ref = graphviz.Digraph(format="png")
ref.attr(rankdir="TB", dpi="120", ranksep="0.9", nodesep="0.4", bgcolor="white")
ref.attr("node", fontname="Helvetica", shape="ellipse", style="filled",
         fillcolor="lightgray", fontcolor="black", fontsize="12")
ref.attr("edge", fontname="Helvetica", color="gray50", fontsize="11")
SHORT = {
    "Both bidders submit sealed bids; equal bids are coin-flip ties.":
        "s0: bid decision\\n2 bids/player (low/high)",
    "Bidder 1 wins with the higher bid.": "s1: P1 wins (higher bid)",
    "Bidder 2 wins with the higher bid.": "s2: P2 wins (higher bid)",
    "Bidder 1 wins the tie-break.": "s4: P1 wins\\n(stochastic tie-break)",
    "Bidder 2 wins the tie-break.": "s5: P2 wins\\n(stochastic tie-break)",
}
for s in gt["model"]["states"]:
    ref.node(s["id"], SHORT.get(s.get("desc", ""), s.get("desc", "")),
             fillcolor="royalblue" if s["terminal"] else "orange",
             fontcolor="white" if s["terminal"] else "black")
for src, tgt in gt["edges"]:
    ref.edge(src, tgt)
ref_path = render(ref, "g6_claude_reference")

# --------------------------------------------------------------------------
# Right panel: ALL 101 candidate states, one node each, grouped into
# graphviz clusters by verified phase prefix (top-to-bottom)
# --------------------------------------------------------------------------
wm = json.load(open(WM_JSON, encoding="utf-8"))
reps = {s["id"]: s["representation"].strip("'") for s in wm["states"]}
terminal = {s["id"]: s["terminal"] for s in wm["states"]}


def phase(state_id: str) -> str:
    rep = reps[state_id]
    if rep == "s0":
        return "type"
    return rep.split("_")[0]  # bid_* | tie_* | end_*


CLUSTERS = {
    # key: (label, fill, nodes-per-row)  -- per-row keeps the graph tall, not wide
    "type": ("Type draw (s0) — 1 state", "orange", 4),
    "bid":  ("Bid phase: bid_* — 4 type states, invented bids {0,1,2,3}", "lightgray", 4),
    "tie":  ("Tie phase: tie_* — 16 states", "lightgray", 8),
    "end":  ("Terminals: end_* — 80 states", "royalblue", 8),
}

cand = graphviz.Digraph(format="png")
cand.attr(rankdir="TB", dpi="120", ranksep="0.8", nodesep="0.14", bgcolor="white",
          compound="true", fontname="Helvetica")
cand.attr("node", fontname="Helvetica", shape="ellipse", style="filled",
          fillcolor="lightgray", fontcolor="black", fontsize="8", width="0.55",
          height="0.35", margin="0.04", penwidth="1.1")
cand.attr("edge", fontname="Helvetica", color="gray60", fontsize="7", arrowsize="0.55",
          penwidth="1.0")

by_phase = defaultdict(list)
for s in wm["states"]:
    by_phase[phase(s["id"])].append(s["id"])


def lay_rows(sub, ids, per_row, fill, fcolor):
    """Stack `ids` into top-down rows of `per_row`. Each row is a rank=same
    subgraph; invisible chaining edges force successive rows onto deeper ranks
    so all 80 terminals are visible but wrapped, never one metre-wide line."""
    rows = [sorted(ids)[i:i + per_row] for i in range(0, len(ids), per_row)]
    for ri, row in enumerate(rows):
        with sub.subgraph(name=f"row_{ri}") as r:
            r.attr(rank="same")
            for sid in row:
                r.node(sid, reps[sid], fillcolor=fill, fontcolor=fcolor)
        if ri > 0:
            sub.edge(rows[ri - 1][-1], row[0], style="invis")


for key in ("type", "bid", "tie", "end"):
    label, fill, per_row = CLUSTERS[key]
    fcolor = "white" if key == "end" else "black"
    with cand.subgraph(name=f"cluster_{key}") as c:
        c.attr(label=label, fontsize="14", fontname="Helvetica-Bold",
               color="#335577", style="rounded,filled", fillcolor="white", margin="14")
        lay_rows(c, by_phase[key], per_row, fill, fcolor)

# draw every transition outcome; collapse parallel src->dst pairs into one
# edge labelled with the number of joint actions producing it
pair_count = Counter()
for t in wm["transitions"]:
    for o in t["outcomes"]:
        pair_count[(t["state"], o["next_state"])] += 1
for (src, dst), n in sorted(pair_count.items()):
    label = None if n == 1 else f"x{n}"
    cand.edge(src, dst, label=label)

cand_path = render(cand, "g6_claude_candidate_compressed")


combine(["Reference G6: 5 states / 4 edges (2 bids/player)",
         "Claude Opus 5 run 1: all 101 states, clustered by phase prefix "
         "(matched F1 0.0383)"],
        [ref_path, cand_path],
        "g6_claude_compressed_phase.png")

