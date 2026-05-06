from PIL import Image
import struct, io, os

img = Image.open('assets/logo.png').convert('RGBA')

# Use standard sizes that Windows requires for exe icons
# Use BMP format inside ICO (not PNG) for maximum compatibility
sizes = [256, 128, 64, 48, 32, 16]

def make_bmp_ico_entry(image, size):
    """Create a BMP-style ICO entry (universally compatible)."""
    resized = image.resize((size, size), Image.LANCZOS)
    pixels = list(resized.getdata())
    
    width = size
    height = size
    
    # BMP info header (BITMAPINFOHEADER) - height is doubled for ICO
    bmp_header = struct.pack('<IiiHHIIiiII',
        40,           # header size
        width,        # width
        height * 2,   # height (doubled for ICO: image + mask)
        1,            # planes
        32,           # bits per pixel
        0,            # compression (none)
        0,            # image size (can be 0 for uncompressed)
        0,            # x pixels per meter
        0,            # y pixels per meter
        0,            # colors used
        0             # important colors
    )
    
    # Pixel data (bottom-up, BGRA)
    pixel_data = b''
    for row in range(height - 1, -1, -1):
        for col in range(width):
            r, g, b, a = pixels[row * width + col]
            pixel_data += struct.pack('BBBB', b, g, r, a)
    
    # AND mask (transparency mask, 1 bit per pixel, padded to 4 bytes)
    mask_data = b''
    row_bytes = (width + 31) // 32 * 4
    for row in range(height - 1, -1, -1):
        row_data = bytearray(row_bytes)
        for col in range(width):
            a = pixels[row * width + col][3]
            if a < 128:
                byte_idx = col // 8
                bit_idx = 7 - (col % 8)
                row_data[byte_idx] |= (1 << bit_idx)
        mask_data += bytes(row_data)
    
    return bmp_header + pixel_data + mask_data

# Build entries - use PNG for 256 (too large for BMP), BMP for smaller
entries_data = []
for s in sizes:
    if s >= 256:
        # Use PNG for 256x256 (standard practice)
        resized = img.resize((s, s), Image.LANCZOS)
        buf = io.BytesIO()
        resized.save(buf, format='PNG')
        entries_data.append(('png', s, buf.getvalue()))
    else:
        data = make_bmp_ico_entry(img, s)
        entries_data.append(('bmp', s, data))

# Build ICO file
num_images = len(entries_data)
header = struct.pack('<HHH', 0, 1, num_images)

dir_entries = b''
image_bytes = b''
data_offset = 6 + num_images * 16

for fmt, s, data in entries_data:
    w = 0 if s >= 256 else s
    h = 0 if s >= 256 else s
    dir_entries += struct.pack('<BBBBHHII',
        w, h, 0, 0,   # width, height, color count, reserved
        1, 32,          # planes, bits per pixel
        len(data),      # size of data
        data_offset     # offset to data
    )
    data_offset += len(data)
    image_bytes += data

with open('icon.ico', 'wb') as f:
    f.write(header + dir_entries + image_bytes)

size = os.path.getsize('icon.ico')
print(f'icon.ico created: {size} bytes ({size // 1024} KB)')
print(f'Contains {num_images} sizes: {[e[1] for e in entries_data]}')
