from PIL import Image

src = Image.open("logo-dooku.png").convert("RGBA")

# Trim white padding & convert white to transparent + tint to cream
pixels = src.load()
w, h = src.size
for y in range(h):
    for x in range(w):
        r, g, b, a = pixels[x, y]
        if r > 240 and g > 240 and b > 240:
            pixels[x, y] = (0, 0, 0, 0)
        else:
            pixels[x, y] = (241, 234, 230, a)

bbox = src.getbbox()
logo = src.crop(bbox)
lw, lh = logo.size

# Find letter columns by scanning vertical pixel density
density = []
for x in range(lw):
    count = 0
    for y in range(lh):
        if logo.getpixel((x, y))[3] > 0:
            count += 1
    density.append(count)

# Identify gaps (columns with very low density) to detect letter boundaries
threshold = 2
gaps = []
in_gap = False
gap_start = 0
for x, d in enumerate(density):
    if d < threshold:
        if not in_gap:
            in_gap = True
            gap_start = x
    else:
        if in_gap:
            in_gap = False
            gaps.append((gap_start, x - 1))

# Letter segments = regions between gaps
letters = []
prev_end = 0
for g_start, g_end in gaps:
    if g_start > prev_end:
        letters.append((prev_end, g_start - 1))
    prev_end = g_end + 1
if prev_end < lw:
    letters.append((prev_end, lw - 1))

print(f"detected {len(letters)} letter segments:", letters)

# In "DOOKU", the OO infinity is the middle joined glyph
# It should be the 2nd segment (index 1) if D-OO-K-U or DOOKU split
# Take all segments except first (D) and last two (K, U)
if len(letters) >= 4:
    oo_start = letters[1][0]
    oo_end = letters[-3][1]
else:
    # fallback: crop center 30%
    oo_start = int(lw * 0.30)
    oo_end = int(lw * 0.62)

oo = logo.crop((oo_start, 0, oo_end + 1, lh))
oo_bbox = oo.getbbox()
oo = oo.crop(oo_bbox)
ow, oh = oo.size

# Square canvas
pad = int(max(ow, oh) * 0.22)
side = max(ow, oh) + pad * 2
canvas = Image.new("RGBA", (side, side), (30, 29, 27, 255))
ox = (side - ow) // 2
oy = (side - oh) // 2
canvas.paste(oo, (ox, oy), oo)

canvas.resize((180, 180), Image.LANCZOS).save("apple-touch-icon.png")
canvas.resize((192, 192), Image.LANCZOS).save("favicon-192.png")
canvas.resize((512, 512), Image.LANCZOS).save("favicon-512.png")
canvas.resize((32, 32), Image.LANCZOS).save("favicon-32.png")
canvas.resize((16, 16), Image.LANCZOS).save("favicon-16.png")

ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
canvas.save("favicon.ico", sizes=ico_sizes)

print("done")
