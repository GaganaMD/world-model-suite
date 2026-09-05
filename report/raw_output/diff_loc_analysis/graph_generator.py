import os
import json
import re
import graphviz
from PIL import Image as PILImage, ImageDraw, ImageFont
from IPython.display import display, Image

def load_and_parse_json(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read().strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'```(?:json)?\s*(\{.*\}|\[.*\])\s*```', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        start, end = text.find('{'), text.rfind('}')
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end+1])
            except json.JSONDecodeError:
                pass
    return None

def generate_gv_grid_perfect_fit(case_suffix, title_prefix, gap=35):
    models = [
        ("gpt", "GPT-4o"),
        ("llama", "Llama 3.3"),
        ("claude", "Claude"),
        ("qwen", "Qwen 3.8"),
        ("deepseek", "DeepSeek")
    ]

    temp_filenames = []

    # Step 1: Render individual Graphviz images for each model
    for model_key, model_display in models:
        filepath = f"output_{model_key}_{case_suffix}.txt"
        json_data = load_and_parse_json(filepath)

        dot = graphviz.Digraph(comment=f"{model_display} - {title_prefix}", format='png')
        dot.attr(rankdir='LR', size='5,4', dpi='180')
        dot.attr('node', fontname='Helvetica', shape='ellipse', style='filled', fontcolor='black')
        dot.attr('edge', fontname='Helvetica', color='gray50')

        if not json_data or 'states' not in json_data:
            dot.node('error', 'No Graph Data', fillcolor='lightcoral')
        else:
            initial_states = [s.get('state') for s in json_data.get('initial', [])]

            for state_obj in json_data['states']:
                src_id = str(state_obj.get('id', '')).strip()
                if not src_id:
                    continue

                if src_id in initial_states:
                    color = 'orange'
                    fcolor = 'black'
                elif state_obj.get('terminal', False):
                    color = 'royalblue'
                    fcolor = 'white'
                else:
                    color = 'lightgray'
                    fcolor = 'black'

                display_label = src_id.replace('_', '\n')
                dot.node(src_id, display_label, fillcolor=color, fontcolor=fcolor)

            for state_obj in json_data['states']:
                src_id = str(state_obj.get('id', '')).strip()
                for action in state_obj.get('actions', []):
                    for nxt in action.get('next', []):
                        tgt_id = str(nxt.get('state', '')).strip()
                        prob = nxt.get('p', 0.5)

                        try:
                            p_val = float(prob)
                        except (ValueError, TypeError):
                            p_val = 0.5

                        edge_width = str(1.0 + p_val)
                        edge_color = 'black' if p_val < 0.51 else 'gray50'

                        if src_id and tgt_id:
                            dot.edge(src_id, tgt_id, label="", penwidth=edge_width, color=edge_color)

        out_filename = f"temp_{model_key}_{case_suffix}"
        dot.render(out_filename, cleanup=True)
        temp_filenames.append((model_display, f"{out_filename}.png"))

    # Step 2: Load images and compute uniform row height so all cards wrap cleanly together
    loaded_items = []
    for model_name, img_path in temp_filenames:
        if os.path.exists(img_path):
            loaded_items.append((model_name, PILImage.open(img_path)))

    if not loaded_items:
        return

    padding = 20
    header_height = 50  # Space for title size 22

    # Calculate global maximum dimensions across all 5 models to keep cards uniform in layout
    max_graph_width = max(img.width for _, img in loaded_items)
    max_graph_height = max(img.height for _, img in loaded_items)

    card_width = max_graph_width + (padding * 2)
    card_height = max_graph_height + header_height + (padding * 2)

    total_width = (card_width * len(loaded_items)) + (gap * (len(loaded_items) - 1))
    total_canvas_height = card_height

    # Create master canvas
    grid_img = PILImage.new('RGB', (total_width, total_canvas_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(grid_img)

    # Load font size 22
    font = None
    for font_path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux/Colab
        "C:/Windows/Fonts/DejaVuSans-Bold.ttf",                  # Windows
        "C:/Windows/Fonts/arialbd.ttf",                          # Windows fallback
    ):
        try:
            font = ImageFont.truetype(font_path, 22)
            break
        except IOError:
            continue
    if font is None:
        font = ImageFont.load_default()

    current_x = 0
    for model_name, img in loaded_items:
        # Create individual card surface matching the uniform dimensions
        card_img = PILImage.new('RGB', (card_width, card_height), color=(255, 255, 255))
        card_draw = ImageDraw.Draw(card_img)

        # Draw crisp square border box around the card
        card_draw.rectangle([0, 0, card_width - 1, card_height - 1], outline="#333333", width=2)

        # Draw title (Font size 22) perfectly centered horizontally at the top
        bbox = card_draw.textbbox((0, 0), model_name, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (card_width - text_width) // 2
        card_draw.text((text_x, padding), model_name, fill="black", font=font)

        # Perfectly center the inner graph image inside its allocated space with zero unnecessary dead-space
        img_x = (card_width - img.width) // 2
        img_y = header_height + padding + ((card_height - header_height - (padding * 2) - img.height) // 2)

        card_img.paste(img, (img_x, img_y))

        # Paste card onto master canvas
        grid_img.paste(card_img, (current_x, 0))
        current_x += card_width + gap

    final_output_name = f"gv_grid_{case_suffix}.png"
    grid_img.save(final_output_name)
    print(f"Generated perfectly fitted grid: {final_output_name}")

    # Display output inside Colab
    display(Image(filename=final_output_name))

    # Clean up temporary files
    for _, path in temp_filenames:
        if os.path.exists(path):
            os.remove(path)

# Run the C9 and C13 rows: original location + 3 ablation locations + no-location.
# (C9: Saudi Arabia original + China/Russia/India + no-location;
#  C13: USA original + Crowded India / China mixed religion / USA Native American + no-location.)
all_contexts = [
    ("saudi_default", "C9: Saudi Arabia (original)"),
    ("china", "C9: China"),
    ("russia", "C9: Russia"),
    ("india", "C9: India"),
    ("noloc_c9", "C9: No Location"),
    ("usa_default", "C13: USA (original)"),
    ("crowded_india", "C13: Crowded India"),
    ("china_mixed_religion", "C13: China (Mixed Religion)"),
    ("usa_native_american", "C13: USA (Native American)"),
    ("noloc_c13", "C13: No Location"),
]

if __name__ == "__main__":
    for ctx_suffix, ctx_title in all_contexts:
        print(f"\nProcessing Row: {ctx_title}")
        generate_gv_grid_perfect_fit(ctx_suffix, ctx_title, gap=35)