#!/usr/bin/env python3
"""Premium 10-second vertical product spot renderer. Genuine photos only; all working assets are temporary."""
import argparse, hashlib, json, math, re, shutil, subprocess, tempfile
from pathlib import Path
from urllib.parse import urlparse
import ipaddress, socket
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

W, H, FPS = 1080, 1920, 30
MAX_BYTES = 12 * 1024 * 1024
ALLOWED = {"image/jpeg", "image/png", "image/webp"}
ACCENT = (210, 255, 74)
BG_TOP = (8, 13, 24)
BG_BOTTOM = (20, 29, 47)

def run(cmd):
    p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p.returncode:
        raise RuntimeError(p.stdout[-6000:])
    return p.stdout

def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"
    ]
    for f in candidates:
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()

def safe_text(s, limit):
    s = re.sub(r"[^A-Za-z0-9 .,&'()!?+-]", "", s).strip()
    return s[:limit]

def download(url, dest):
    u = urlparse(url)
    if u.scheme != "https" or not u.hostname or u.username or u.password:
        raise ValueError("Only public HTTPS image URLs accepted")
    for info in socket.getaddrinfo(u.hostname, None):
        if not ipaddress.ip_address(info[4][0]).is_global:
            raise ValueError("Image host resolves to non-public IP")
    with requests.get(url, stream=True, timeout=(15, 45), headers={"User-Agent": "PremiumProductRenderer/2.0"}) as r:
        r.raise_for_status()
        ctype = r.headers.get("Content-Type", "").split(";")[0].lower()
        if ctype not in ALLOWED:
            raise ValueError("Unsupported image content type: " + ctype)
        total = 0
        with open(dest, "wb") as f:
            for chunk in r.iter_content(131072):
                if not chunk:
                    continue
                total += len(chunk)
                if total > MAX_BYTES:
                    raise ValueError("Image exceeds 12 MB")
                f.write(chunk)
    with Image.open(dest) as im:
        im.verify()
    return total, ctype

def make_background():
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        t = y / (H - 1)
        c = tuple(int(BG_TOP[k] * (1-t) + BG_BOTTOM[k] * t) for k in range(3))
        for x in range(W):
            glow = max(0, 1 - math.sqrt(((x-850)/850)**2 + ((y-580)/900)**2)) * 12
            px[x, y] = tuple(min(255, int(v + glow)) for v in c)
    d = ImageDraw.Draw(im, "RGBA")
    # Fine grid and restrained orbital accents create depth without competing with the product.
    for x in range(0, W, 72):
        d.line((x, 0, x, H), fill=(255,255,255,8), width=1)
    for y in range(0, H, 72):
        d.line((0, y, W, y), fill=(255,255,255,7), width=1)
    for i in range(22):
        x = (i * 197 + 83) % W
        y = (i * 317 + 121) % H
        r = 2 + (i % 3)
        d.ellipse((x-r,y-r,x+r,y+r), fill=(210,255,74,65))
    return im

def build_scene(source, idx, count, title, subtitle, work):
    bg = make_background().convert("RGBA")
    # Soft blurred accent glow behind the product.
    glow = Image.new("RGBA", (W,H), (0,0,0,0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((120,430,960,1280), fill=(140,190,255,35))
    glow = glow.filter(ImageFilter.GaussianBlur(100))
    bg = Image.alpha_composite(bg, glow)

    with Image.open(source) as raw:
        product = ImageOps.exif_transpose(raw).convert("RGBA")
    product.thumbnail((890, 900), Image.Resampling.LANCZOS)

    # Premium floating glass panel and soft shadow.
    panel = Image.new("RGBA", (W,H), (0,0,0,0))
    shadow = Image.new("RGBA", (W,H), (0,0,0,0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((78,440,1002,1375), radius=54, fill=(0,0,0,145))
    shadow = shadow.filter(ImageFilter.GaussianBlur(38))
    panel = Image.alpha_composite(panel, shadow)
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle((70,420,1010,1360), radius=52, fill=(255,255,255,16), outline=(255,255,255,42), width=2)
    bg = Image.alpha_composite(bg, panel)

    # Fit image inside a clean, light studio stage. Never fabricate product pixels.
    stage = Image.new("RGBA", (W,H), (0,0,0,0))
    sd = ImageDraw.Draw(stage)
    sd.rounded_rectangle((100,450,980,1330), radius=40, fill=(244,246,249,255))
    # Subtle radial stage light.
    light = Image.new("RGBA", (W,H), (0,0,0,0))
    ld = ImageDraw.Draw(light)
    ld.ellipse((190,510,890,1260), fill=(255,255,255,85))
    light = light.filter(ImageFilter.GaussianBlur(75))
    stage = Image.alpha_composite(stage, light)
    stage.alpha_composite(product, ((W-product.width)//2, 870-product.height//2))
    bg = Image.alpha_composite(bg, stage)

    draw = ImageDraw.Draw(bg)
    small = font(26, True)
    headline = font(64 if len(title) < 24 else 52, True)
    subfont = font(31)
    draw.text((84,130), "PRODUCT SPOTLIGHT", font=small, fill=ACCENT)
    draw.rounded_rectangle((84,184,250,192), radius=4, fill=ACCENT)

    if idx == 0:
        label = title
        line = "DESIGNED TO STAND OUT"
    elif idx == count - 1:
        label = "THE DETAILS"
        line = subtitle
    else:
        label = ["PRECISION IN EVERY DETAIL", "MADE FOR EVERYDAY"][((idx-1) % 2)]
        line = title

    # Centered typography, restrained hierarchy.
    box = draw.textbbox((0,0), label, font=headline)
    draw.text(((W-(box[2]-box[0]))//2, 255), label, font=headline, fill=(255,255,255))
    box2 = draw.textbbox((0,0), line, font=subfont)
    draw.text(((W-(box2[2]-box2[0]))//2, 1450), line, font=subfont, fill=(213,222,237))
    draw.rounded_rectangle((84,1550,996,1554), radius=2, fill=(255,255,255,35))
    draw.rounded_rectangle((84,1550,84+int(912*(idx+1)/count),1554), radius=2, fill=ACCENT)
    draw.text((84,1600), "DETAIL • DESIGN • EXPERIENCE", font=small, fill=(150,166,190))
    draw.text((84,1775), "A CLOSER LOOK", font=font(22,True), fill=(150,166,190))
    return bg.convert("RGB")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle", default="Premium sound. Refined design.")
    ap.add_argument("--images", required=True)
    ap.add_argument("--output", default="output/product-video.mp4")
    a = ap.parse_args()
    urls = json.loads(a.images)
    if not isinstance(urls, list) or not 2 <= len(urls) <= 5:
        raise ValueError("Provide 2–5 image URLs")
    title = safe_text(a.title, 52)
    subtitle = safe_text(a.subtitle, 80)
    if not title:
        raise ValueError("Product title is empty")
    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="premium-product-render-"))
    report, scenes = [], []
    try:
        for i, url in enumerate(urls, 1):
            src = work / f"source-{i}.img"
            size, ctype = download(url, src)
            scene = build_scene(src, i-1, len(urls), title, subtitle, work)
            still = work / f"scene-{i}.jpg"
            scene.save(still, quality=95, optimize=True)
            scenes.append(still)
            report.append(f"image_{i}: downloaded_bytes={size}; mime={ctype}; validated=true")
        # Render all scenes as a single continuous camera move with animated title reveals,
        # gentle zoom, fades and a polished 30 fps H.264 output.
        inputs = []
        filters = []
        durations = [10.0 / len(scenes)] * len(scenes)
        for i, still in enumerate(scenes):
            inputs += ["-loop", "1", "-t", f"{durations[i]:.4f}", "-i", str(still)]
            start = i * durations[i]
            end = start + durations[i]
            fadein = 0.22
            fadeout = 0.22
            filters.append(
                f"[{i}:v]scale=1188:2112,zoompan=z='min(zoom+0.00035,1.045)':d=1:s={W}x{H}:fps={FPS},"
                f"fade=t=in:st=0:d={fadein},fade=t=out:st={max(0,durations[i]-fadeout):.3f}:d={fadeout},"
                f"setsar=1,format=yuv420p[v{i}]"
            )
        concat = "".join(f"[v{i}]" for i in range(len(scenes)))
        filters.append(f"{concat}concat=n={len(scenes)}:v=1:a=0[outv]")
        graph = ";".join(filters)
        run(["ffmpeg","-y",*inputs,"-filter_complex",graph,"-map","[outv]","-t","10","-r",str(FPS),
             "-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","-movflags","+faststart",str(out)])
        probe = json.loads(run(["ffprobe","-v","error","-show_entries","format=duration,size","-show_entries","stream=codec_type,width,height,codec_name","-of","json",str(out)]))
        duration = float(probe["format"]["duration"])
        video = next(s for s in probe["streams"] if s["codec_type"] == "video")
        if abs(duration-10) > 0.2 or video.get("width") != W or video.get("height") != H:
            raise RuntimeError("MP4 verification failed")
        report += ["render_style=premium_dark_studio_motion_graphics","audio=none","mp4_verified=true",
                   f"duration_seconds={duration:.3f}",f"resolution={W}x{H}",f"fps={FPS}",
                   f"codec={video.get('codec_name')}",f"size_bytes={out.stat().st_size}",
                   f"sha256={hashlib.sha256(out.read_bytes()).hexdigest()}"]
        Path("output/build-report.txt").write_text("\n".join(report)+"\n")
        print("\n".join(report))
    finally:
        shutil.rmtree(work, ignore_errors=True)

if __name__ == "__main__":
    main()
