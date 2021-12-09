from PIL import Image, ImageFont, ImageDraw

def addText(filename):
    path = f"imagecache/{filename}"
    img = Image.open(path)
    W, H = img.size
    padding = 4
    draw = ImageDraw.Draw(img)
    myFont = ImageFont.truetype("fonts/Trajan Pro Bold.ttf", 20)
    draw.text((W+padding,H-20), "Hero Name", (255,255,255), font = myFont)
    img.save(f'imagecache/heronames/{filename}')

addText("abaddon_lg.png")