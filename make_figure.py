from PIL import Image, ImageDraw, ImageFont

W, H = 2400, 1400
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)

blocks = [
    "Источник сообщения", "Сообщение", "Модель измерения",
    "Количественная оценка информации", "Интерпретация результата"
]
xs = [80, 520, 940, 1360, 1880]
for i, (x, t) in enumerate(zip(xs, blocks)):
    d.rounded_rectangle((x, 560, x+420, 840), radius=20, outline="black", width=4)
    d.text((x+30, 670), t, fill="black")
    if i < len(xs)-1:
        d.line((x+420,700,xs[i+1],700), fill="black", width=4)
        d.polygon([(xs[i+1]-20,690),(xs[i+1],700),(xs[i+1]-20,710)], fill='black')

img.save('information_measure_scheme.png', dpi=(300,300))
print('Saved information_measure_scheme.png')
