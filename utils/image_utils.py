import cv2
import numpy as np
from skimage.feature import match_template
from alive_progress import alive_bar
from imagehash import phash
from PIL import Image, ImageOps, ImageFont, ImageDraw
import os
import platform
import datetime

from utils.stats_utils import make_counter

overlay_images = {
        "red": os.path.join('images', 'overlays', 'str.png'),
        "green": os.path.join('images', 'overlays', 'dex.png'),
        "blue": os.path.join('images', 'overlays', 'qck.png'),
        "yellow": os.path.join('images', 'overlays', 'psy.png'),
        "purple": os.path.join('images', 'overlays', 'int.png'),
        "black": os.path.join('images', 'overlays', 'dual.png')
    }

xy = [910, 950, 460, 530]

def make_template_from_image(file_path):
    ref = cv2.imread(file_path, 0)
    template = ref[xy[0]:xy[1], xy[2]:xy[3]]
    return template


def get3Teams(img, template, target_hashes, index):
    resulting_image = match_template(img[:1000, :600], template)
    x, y = np.unravel_index(np.argmax(resulting_image), resulting_image.shape)

    # Define the 8 seperate unit areas
    off = 107
    off_s = 26
    x1 = 57
    gap = 310
    x2 = 142

    units = []
    for i in range(3):
        units.append(img[x+x1+i*gap : x+253+i*gap, y-383 : xy[3]-257])
        units.append(img[x+x2+i*gap : x+245+i*gap, y-178 : xy[3]-145])
        units.append(img[x+x2+i*gap : x+245+i*gap, y-178+off : xy[3]-145+off])
        units.append(img[x+x2+i*gap : x+245+i*gap, y-178+off*2 : xy[3]-145+off*2])
        units.append(img[x+x2+i*gap : x+245+i*gap, y-178+off*3 : xy[3]-145+off*3])
        units.append(img[x+x2+i*gap : x+245+i*gap, y-178+off*4+off_s : xy[3]-145+off*4+off_s])
        units.append(img[x+x2+i*gap : x+245+i*gap, y-178+off*5+off_s : xy[3]-145+off*5+off_s])
        units.append(img[x+x2+i*gap : x+245+i*gap, y-178+off*6+off_s : xy[3]-145+off*6+off_s])

    resized_units = [cv2.resize(unit, dsize=(112, 112), interpolation=cv2.INTER_CUBIC) for unit in units]
    matches = []
    with alive_bar(len(units), title=f'Finding matches for 3 Teams from image {index+1}/33') as bar:
        for img in resized_units:
            current_hash = phash(Image.fromarray(img, 'L'), hash_size=16)

            best_match = None
            best_difference = 256
            for file_path, target_hash in target_hashes.items():
                difference = current_hash - target_hash
                if difference < best_difference:
                    best_match = file_path
                    best_difference = difference
            matches.append(best_match)
            bar()

    return matches


def getMatchesFromScreenshots(screenshot_list, template, hashes):
    matches = []
    for index, path in enumerate(screenshot_list):
        img = cv2.imread(path, 0)
        matches.extend(get3Teams(img, template, hashes, index))

        # Handle Anni Shanks Visual Evolution
        for i, match in enumerate(matches):
            if os.path.basename(match) == "4153.png":
                matches[i] = os.path.join(os.path.dirname(match), "4152.png")

    return matches


def create_perceptual_hashes(image_file_list):
    hashes = {}
    with alive_bar(len(image_file_list), title=f'Making Perceptual Hashes for {len(image_file_list)} images') as bar:
        for image_file in image_file_list:
            image_hash =  phash(Image.open(image_file).convert('L'), hash_size=16)
            hashes[image_file] = image_hash
            bar()
    return hashes


def buildCollage(matches):
    s = 112
    col = 8
    crop = 14
    w = 92
    row = len(matches) // col
    new = Image.new("RGBA", (s*col, s*row))
    for i in range(col * row):
        img = Image.open(matches[i]).convert("RGBA")
        r, g, b, _ = img.getpixel((32, 19))
        closest_color = get_closest_color(r, g, b)
        overlay = Image.open(overlay_images[closest_color])
        img = img.crop((crop, crop, img.width - crop, img.height - crop))
        padding = (overlay.width - img.width) // 2
        img = ImageOps.expand(img, border=padding, fill=(0, 0, 0, 0))
        img = overlay_image(img, overlay)
        new.paste(img, (w * (i % col), s * (i // col)))
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


def build_ranked_collage(teams, path_dict, rows, n_team_comps):
    images = []
    final_width = 0
    spacing_hor = 92
    rows_collage = rows

    for col in range(1,n_team_comps+1):
        mc = make_counter(teams, col).most_common(rows)
        s = 112
        crop = 14
        w = 92
        new = Image.new("RGBA", (w*col, s*rows - 20))
        num = Image.new("RGBA", (w, s*rows - 20))
        draw = ImageDraw.Draw(num)
        if platform.system() == "Windows":
            font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 50)
        else:
            font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 50)

        if len(mc) < rows:
            rows = len(mc)
            print(f"Only {rows} teams available in col {col}.")

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
                new.paste(img, (w * i, s * j))
                draw.text((w//2, w//2 + s*j), str(mc[j][1]), fill="white", font=font, anchor="mm", align="right")

        # concat new and num horizontally with spacing_hor
        new_num = Image.new("RGBA", (w*col + w, s*rows - 20))
        new_num.paste(new, (w, 0))
        new_num.paste(num, (0, 0))
        images.append(new_num)
        final_width += new_num.width + spacing_hor

    final = Image.new("RGBA", (final_width, s*rows_collage - 20))
    pos_hor = 0
    for i in range(n_team_comps):
        final.paste(images[i], (pos_hor, 0))
        pos_hor += images[i].width + spacing_hor

    now = datetime.datetime.now()
    file_name = f'{now.strftime("%Y_%m_%d")}.png'
    result_dir = os.path.join('results', 'ranked_combinations')
    final.save(os.path.join(result_dir, file_name))
