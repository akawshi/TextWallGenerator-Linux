from PIL import Image, ImageDraw, ImageFont
import numpy as np
import unicodedata
from pathlib import Path

fontsize = 256  # フォントサイズ


# =========================
# fonts ディレクトリから ttf を1つ取得
# =========================
def get_font_path():
    base_dir = Path(__file__).resolve().parent
    fonts_dir = base_dir / "fonts"

    if not fonts_dir.exists():
        raise FileNotFoundError("fonts directory not found")

    fonts = sorted(fonts_dir.glob("*.ttf"))
    if not fonts:
        raise FileNotFoundError("no .ttf font found in fonts directory")

    return fonts[0]


# =========================
# 文字を画像に変換
# =========================
def char2image(char, ttfontname=None):
    # 全角 / 半角判定
    fullwide = unicodedata.east_asian_width(char) in "FWA"
    canvasSize = (fontsize, fontsize) if fullwide else (int(fontsize / 2), fontsize)

    img = Image.new("RGB", canvasSize, (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # フォント取得（ttfontname は無視して fonts/ から選ぶ）
    font_path = get_font_path()
    font = ImageFont.truetype(str(font_path), fontsize)

    draw.text((0, 0), char, fill=(0, 0, 0), font=font)

    return img, fullwide


# =========================
# 画像 → マトリクス
# =========================
def image2matrix(img, fullwide, n_dot):
    dotsize = fontsize / n_dot
    _n_dot = n_dot if fullwide else int(n_dot / 2)

    matrix = []
    img_array = np.array(img)

    for iy in range(n_dot):
        row = []
        for ix in range(_n_dot):
            c_x = int(ix * dotsize + (dotsize / 2))
            c_y = int(iy * dotsize + (dotsize / 2))
            value = img_array[c_y][c_x][0]
            row.append(1 if value < 120 else 0)
        matrix.append(row)

    return matrix


# =========================
# マトリクス → 矩形
# =========================
def div2rectangle(matrix, fullwide, n_dot):
    _n_dot = n_dot if fullwide else int(n_dot / 2)
    matrix = np.array(matrix, dtype=bool)

    arrangement = []

    while True:
        h_lines = []
        v_lines = []

        # Horizontal
        for i in range(n_dot):
            start_j = None
            for j in range(_n_dot):
                if matrix[i, j] and start_j is None:
                    start_j = j
                if not matrix[i, j] and start_j is not None:
                    h_lines.append((j - start_j, i, start_j))
                    start_j = None
            if start_j is not None:
                h_lines.append((_n_dot - start_j, i, start_j))

        # Vertical
        for j in range(_n_dot):
            start_i = None
            for i in range(n_dot):
                if matrix[i, j] and start_i is None:
                    start_i = i
                if not matrix[i, j] and start_i is not None:
                    v_lines.append((i - start_i, start_i, j))
                    start_i = None
            if start_i is not None:
                v_lines.append((n_dot - start_i, start_i, j))

        if not h_lines and not v_lines:
            break

        h_lines.sort(key=lambda x: x[0], reverse=True)
        v_lines.sort(key=lambda x: x[0], reverse=True)

        if not h_lines or (v_lines and v_lines[0][0] >= h_lines[0][0]):
            h, i, j = v_lines[0]
            arrangement.append((j, n_dot - i - h, 1, h))
            for r in range(i, i + h):
                matrix[r, j] = False
        else:
            w, i, j = h_lines[0]
            arrangement.append((j, n_dot - i - 1, w, 1))
            for c in range(j, j + w):
                matrix[i, c] = False

    return arrangement
