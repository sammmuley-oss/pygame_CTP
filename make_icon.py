from PIL import Image
import struct, zlib, io, os

img = Image.open('assets/logo.png').convert('RGBA')

# Save each size as separate PNG bytes in memory, then build proper ICO
sizes = [256, 128, 64, 48, 32, 16]
png_datas = []
for s in sizes:
    resized = img.resize((s, s), Image.LANCZOS)
    buf = io.BytesIO()
    resized.save(buf, format='PNG')
    png_datas.append(buf.getvalue())

# Build ICO header
num = len(sizes)
header = struct.pack('<HHH', 0, 1, num)  # reserved, type=1 (ICO), count
offset = 6 + num * 16  # header + directory entries

entries = b''
image_data = b''
for i, (s, data) in enumerate(zip(sizes, png_datas)):
    sz = s if s < 256 else 0  # 256 is stored as 0 in ICO format
    entries += struct.pack('<BBBBHHII', sz, sz, 0, 0, 1, 32, len(data), offset)
    offset += len(data)
    image_data += data

with open('icon.ico', 'wb') as f:
    f.write(header + entries + image_data)

size = os.path.getsize('icon.ico')
print(f'icon.ico created: {size} bytes ({size//1024} KB)')
