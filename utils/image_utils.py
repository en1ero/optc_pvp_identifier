import cv2
import numpy as np
from skimage.feature import match_template
from matplotlib import pyplot as plt
from alive_progress import alive_bar
from imagehash import phash
from PIL import Image, ImageOps, ImageFont, ImageDraw
import os

from utils.stats_utils import make_counter

XY = [910, 950, 460, 530]

def make_template_from_image(file_path):
    ref = cv2.imread(file_path, 0)
    template = ref[XY[0]:XY[1], XY[2]:XY[3]]

    return template

def get3Teams(img, template, hashes, index):
    resulting_image = match_template(img[:1000, :600], template)
    x, y = np.unravel_index(np.argmax(resulting_image), resulting_image.shape)

    # Define the 8 seperate unit areas
    off = 107
    off_s = 26
    x1 = 57
    row_gap = 310
    x2 = 142

    units = []

    for i in range(3):
        units.append(img[x+x1+i*row_gap: x+253+i*row_gap, y-383: XY[3]-257])
        units.append(img[x+x2+i*row_gap: x+245+i*row_gap, y-178: XY[3]-145])
        units.append(img[x+x2+i*row_gap: x+245+i *
                     row_gap, y-178+off: XY[3]-145+off])
        units.append(img[x+x2+i*row_gap: x+245+i*row_gap,
                     y-178+off*2:           XY[3]-145+off*2])
        units.append(img[x+x2+i*row_gap: x+245+i*row_gap,
                     y-178+off*3:           XY[3]-145+off*3])
        units.append(img[x+x2+i*row_gap: x+245+i*row_gap, y -
                     178+off*4+off_s: XY[3]-145+off*4+off_s])
        units.append(img[x+x2+i*row_gap: x+245+i*row_gap, y -
                     178+off*5+off_s: XY[3]-145+off*5+off_s])
        units.append(img[x+x2+i*row_gap: x+245+i*row_gap, y -
                     178+off*6+off_s: XY[3]-145+off*6+off_s])

    # Show Units
    rows = 3
    cols = 8
    resized_units = [cv2.resize(unit, dsize=(112, 112), interpolation=cv2.INTER_CUBIC) for unit in units]
    # fig, ax = plt.subplots(rows, cols, figsize=(8, 8))
    # for i in range(cols * rows):
    #     ax[i // cols, i % cols].imshow(resized_units[i])
    # plt.show()

    matches = []

    with alive_bar(len(units), title=f'Finding matches for 3 Teams from image {index+1}/33') as bar:
        for img in resized_units:
            target_hash = phash(Image.fromarray(img, 'L'))

            best_match = None
            best_difference = 50
            for file, hash in hashes.items():
                difference = target_hash - hash
                if difference < best_difference:
                    best_match = file
                    best_difference = difference
            matches.append(best_match)
            bar()

    return matches

def getMatchesFromScreenshots(screenshot_dir, template, hashes):
    matches = []
    for index, path in enumerate(screenshot_dir):
        img = cv2.imread(path, 0)
        matches.extend(get3Teams( img, template, hashes, index))
    return matches

def create_perceptual_hashes(directory):
    hashes = {}
    for file in directory:
        hash =  phash(Image.open(file).convert('L'))
        hashes[file] = hash
    return hashes

def buildCollage(matches):
    s = 112
    col = 8
    row = len(matches) // col
    new = Image.new("RGBA", (s*col, s*row))
    for i in range(col * row):
        img = Image.open(matches[i])
        new.paste(img, (s * (i % col), s * (i // col)))
    new.show()
    
def get_closest_color(r,g,b):
    colors = {
        "red": (248,49,68),
        "green": (70,164,39),
        "blue": (3,98,231),
        "yellow": (255,214,5),
        "purple": (143,17,210),
        "black": (81,52,51)
    }
    closest_color = min(colors, key=lambda color: abs(colors[color][0]-r) + abs(colors[color][1]-g) + abs(colors[color][2]-b))
    return closest_color

def overlay_image(img, overlay):
    return Image.alpha_composite(img, overlay)

def build_ranked_collage(teams, path_dict, col, rows):
    mc = make_counter(teams, col).most_common(rows)
    s = 112
    crop = 14
    h = 92
    new = Image.new("RGBA", (h*col, s*rows - 20))
    num = Image.new("RGBA", (h, s*rows - 20))
    draw = ImageDraw.Draw(num)
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 50)

    overlay_images = {
        "red": os.path.join('images', 'overlays', 'str.png'),
        "green": os.path.join('images', 'overlays', 'dex.png'),
        "blue": os.path.join('images', 'overlays', 'qck.png'),
        "yellow": os.path.join('images', 'overlays', 'psy.png'),
        "purple": os.path.join('images', 'overlays', 'int.png'),
        "black": os.path.join('images', 'overlays', 'dual.png')
    }

    if len(mc) < rows:
        rows = len(mc)
        print(f"Only {rows} teams available in col {col}.")

    if col > 1:
        for i in range(col):
            for j in range(rows):
                img = Image.open(path_dict[mc[j][0][i]]).convert("RGBA")
                r, g, b, _ = img.getpixel((32, 19))
                closest_color = get_closest_color(r, g, b)
                overlay = Image.open(overlay_images[closest_color])
                img = img.crop((crop, crop, img.width - crop, img.height - crop))
                padding = (overlay.width - img.width) // 2
                img = ImageOps.expand(img, border=padding, fill=(0, 0, 0, 0))
                img = overlay_image(img, overlay)
                new.paste(img, (h * i, s * j))
                draw.text((s//2, s * j + s//2), str(mc[j][1]), fill="white", font=font, anchor="mm", align="right")
    else:
        for j in range(rows):
            img = Image.open(path_dict[mc[j][0][0]]).convert("RGBA")
            r, g, b, _ = img.getpixel((32, 19))
            closest_color = get_closest_color(r, g, b)
            overlay = Image.open(overlay_images[closest_color])
            img = img.crop((crop, crop, img.width - crop, img.height - crop))
            padding = (overlay.width - img.width) // 2
            img = ImageOps.expand(img, border=padding, fill=(0, 0, 0, 0))
            img = overlay_image(img, overlay)
            new.paste(img, (0, s * j))
            draw.text((s//2, s * j + s//2), str(mc[j][1]), fill="white", font=font, anchor="mm", align="right")

    new.save(f'results/ranked_combinations/{col}.png')
    num.save(f'results/ranked_combinations/{col}_num.png')