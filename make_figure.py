import struct
import zlib

OUT = 'information_measure_scheme.png'


def png_chunk(tag, data):
    return struct.pack('!I', len(data)) + tag + data + struct.pack('!I', zlib.crc32(tag + data) & 0xffffffff)


def make_png(path):
    w, h = 1600, 500
    img = bytearray([255, 255, 255] * w * h)

    def set_px(x, y, r=0, g=0, b=0):
        if 0 <= x < w and 0 <= y < h:
            i = (y * w + x) * 3
            img[i:i+3] = bytes((r, g, b))

    def rect(x0, y0, x1, y1):
        for x in range(x0, x1 + 1):
            set_px(x, y0); set_px(x, y1)
        for y in range(y0, y1 + 1):
            set_px(x0, y); set_px(x1, y)

    def line(x0, y0, x1, y1):
        dx = abs(x1 - x0); sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0); sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            set_px(x0, y0)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy; x0 += sx
            if e2 <= dx:
                err += dx; y0 += sy

    blocks = [(30, 170, 290, 330), (340, 170, 600, 330), (650, 170, 910, 330), (960, 170, 1220, 330), (1270, 170, 1530, 330)]
    for b in blocks:
        rect(*b)
    for i in range(4):
        x0 = blocks[i][2]
        x1 = blocks[i+1][0]
        y = 250
        line(x0, y, x1, y)
        line(x1-12, y-8, x1, y)
        line(x1-12, y+8, x1, y)

    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw.extend(img[y*stride:(y+1)*stride])

    png = b'\x89PNG\r\n\x1a\n'
    png += png_chunk(b'IHDR', struct.pack('!IIBBBBB', w, h, 8, 2, 0, 0, 0))
    png += png_chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += png_chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)


if __name__ == '__main__':
    make_png(OUT)
    print('Created', OUT)
