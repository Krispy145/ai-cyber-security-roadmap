
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
import json, textwrap

def load_font(size):
    for path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()

def draw_bg(w, h):
    base = Image.new("RGBA", (w, h), (14, 18, 28))
    grad = Image.new("RGBA", (1, h))
    for y in range(h):
        r = 14
        g = int(22 + 36 * (y / h))
        b = int(38 + 72 * (y / h))
        grad.putpixel((0, y), (r, g, b))
    grad = grad.resize((w, h))
    img = Image.blend(base, grad, 0.92)

    vignette = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(vignette)
    d.ellipse([-int(0.2*w), -int(0.25*h), int(0.9*w), int(1.15*h)], fill=180)
    vignette = vignette.filter(ImageFilter.GaussianBlur(int(min(w,h)*0.2)))
    overlay = Image.new("RGBA", (w, h), (20, 32, 56))
    img = Image.composite(overlay, img, vignette)
    return img

def measure(draw, text, font):
    left, top, right, bottom = draw.textbbox((0,0), text, font=font)
    return right-left, bottom-top

def smart_title(name: str) -> str:
    tokens = name.replace("_","-").split("-")
    keep_upper = {"ai","ml","api","ui","ux","cv","rag","jwt","oidc","db"}
    out = []
    for t in tokens:
        if t.lower() in keep_upper or len(t)<=3:
            out.append(t.upper())
        else:
            out.append(t.capitalize())
    return " ".join(out)


def render_repo_cover(repo, out_dir, owner=""):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    sizes = [("cover", 1200, 630), ("thumb", 800, 420)]
    for tag, W, H in sizes:
        img = draw_bg(W, H)
        draw = ImageDraw.Draw(img)

        padding = int(W * 0.06)
        x = padding
        y = padding

        title_font = load_font(72 if W >= 1100 else 56)
        sub_font   = load_font(34 if W >= 1100 else 28)
        meta_font  = load_font(22 if W >= 1100 else 18)

        title = smart_title(repo.get("name",""))
        max_title_width = W - 2*padding
        while measure(draw, title, title_font)[0] > max_title_width and title_font.size > 28:
            title_font = load_font(title_font.size - 2)
        draw.text((x, y), title, font=title_font, fill=(220, 230, 255))
        y += title_font.size + 16

        subtitle = repo.get("short_description") or repo.get("description") or ""
        max_sub_width = W - 2*padding
        wrap_chars = max(20, int(max_sub_width / (sub_font.size * 0.58)))
        for line in textwrap.wrap(subtitle, width=wrap_chars)[:3]:
            draw.text((x, y), line, font=sub_font, fill=(175, 195, 225))
            y += sub_font.size + 4

        y += 18
        topics = (repo.get("topics") or [])[:8]
        
        # Draw topic pills instead of icons
        pill_height = 32 if W >= 1100 else 28
        pill_padding = 12 if W >= 1100 else 10
        pill_font = load_font(16 if W >= 1100 else 14)
        
        cursor_x = x
        cursor_y = y
        max_width = W - 2*padding
        
        for topic in topics:
            # Clean up topic name for display
            display_topic = topic.replace("-", " ").replace("_", " ").title()
            
            # Measure text to get pill width
            text_width, text_height = measure(draw, display_topic, pill_font)
            pill_width = text_width + (pill_padding * 2)
            
            # Check if we need to wrap to next line
            if cursor_x + pill_width > x + max_width:
                cursor_x = x
                cursor_y += pill_height + 8
            
            # Draw pill background
            pill_rect = [cursor_x, cursor_y, cursor_x + pill_width, cursor_y + pill_height]
            draw.rounded_rectangle(pill_rect, radius=pill_height//2, fill=(40, 60, 100, 180))
            
            # Draw pill border
            draw.rounded_rectangle(pill_rect, radius=pill_height//2, outline=(80, 120, 180, 255), width=1)
            
            # Draw text
            text_x = cursor_x + pill_padding
            text_y = cursor_y + (pill_height - text_height) // 2
            draw.text((text_x, text_y), display_topic, font=pill_font, fill=(200, 220, 255))
            
            # Move cursor
            cursor_x += pill_width + 8
        
        y = cursor_y + pill_height + 20

        footer = f"github.com/{owner}/{repo.get('name','')}".strip("/")
        fw, fh = measure(draw, footer, meta_font)
        draw.text((W - padding - fw, H - padding - fh), footer, font=meta_font, fill=(150, 170, 200))

        out_path = out_dir / f"{repo.get('name','repo')}-{tag}.webp"
        img.save(out_path, "WEBP", quality=95, method=6)

def generate_all_from_manifest(manifest_path, output_dir):
    data = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    owner = ""
    repos = data.get("repositories", [])
    if repos and isinstance(repos[0].get("url"), str):
        parts = repos[0]["url"].rstrip("/").split("/")
        if len(parts) >= 2:
            owner = parts[-2]
    for repo in repos:
        out_dir = Path(output_dir) / repo.get("name","repo")
        render_repo_cover(repo, out_dir, owner=owner)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="manifest.json")
    ap.add_argument("--out", default="images")
    args = ap.parse_args()
    generate_all_from_manifest(args.manifest, args.out)
