# -*- coding: utf-8 -*-
"""生成 PWA 图标（192/512，青绿底白字"英二"）"""
from PIL import Image, ImageDraw, ImageFont

for size in (192, 512):
    img = Image.new('RGB', (size, size), '#0d9488')
    d = ImageDraw.Draw(img)
    # 圆角背景层次感：中心浅一点的圆
    d.ellipse([size*0.08]*2 + [size*0.92]*2, fill='#14b8a6')
    try:
        font = ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc', int(size*0.32))
    except OSError:
        font = ImageFont.load_default()
    d.text((size/2, size*0.42), '英二', font=font, fill='white', anchor='mm')
    try:
        f2 = ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc', int(size*0.14))
    except OSError:
        f2 = ImageFont.load_default()
    d.text((size/2, size*0.70), '精翻', font=f2, fill='#ccfbf1', anchor='mm')
    img.save(rf'D:\ai code\english-reading\pwa\icons\icon-{size}.png')
print('icons ok')
