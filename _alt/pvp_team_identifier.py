from skimage.feature import match_template
from matplotlib import pyplot as plt
from alive_progress import alive_bar
from collections import Counter
from sewar.full_ref import mse
from PIL import Image
import pandas as pd
import numpy as np
import itertools
import os
import cv2
import shutil
import math


def fileList(source, file_type):
    matches = []
    for root, dirnames, filenames in os.walk(source):
        for filename in filenames:
            if filename.endswith(file_type):
                matches.append(os.path.join(root, filename))
    return matches


ref = cv2.imread("/Users/marc/Desktop/OPTC/anchor.jpeg", 0)

def get3Teams(img, num):
    # Define anchorn from screenshot
    xy = [910, 950, 460, 530]
    ref = cv2.imread("/Users/marc/Desktop/OPTC/anchor.jpeg", 0)
    anchor = ref[xy[0]:xy[1], xy[2]:xy[3]]

    # Find anchor
    resulting_image = match_template(img[:1000, :600], anchor)
    x, y = np.unravel_index(np.argmax(resulting_image), resulting_image.shape)

    # Define the 8 seperate unit areas
    off = 107
    off_s = 26
    x1 = 57
    row_gap = 310
    x2 = 142

    units = []

    for i in range(3):
        units.append(img[x+x1+i*row_gap: x+253+i*row_gap, y-383: xy[3]-257])
        units.append(img[x+x2+i*row_gap: x+245+i*row_gap, y-178: xy[3]-145])
        units.append(img[x+x2+i*row_gap: x+245+i *
                     row_gap, y-178+off: xy[3]-145+off])
        units.append(img[x+x2+i*row_gap: x+245+i*row_gap,
                     y-178+off*2:           xy[3]-145+off*2])
        units.append(img[x+x2+i*row_gap: x+245+i*row_gap,
                     y-178+off*3:           xy[3]-145+off*3])
        units.append(img[x+x2+i*row_gap: x+245+i*row_gap, y -
                     178+off*4+off_s: xy[3]-145+off*4+off_s])
        units.append(img[x+x2+i*row_gap: x+245+i*row_gap, y -
                     178+off*5+off_s: xy[3]-145+off*5+off_s])
        units.append(img[x+x2+i*row_gap: x+245+i*row_gap, y -
                     178+off*6+off_s: xy[3]-145+off*6+off_s])

    # Show Units
    fig = plt.figure(figsize=(8, 8))
    columns = 8
    rows = 3
    units_resize = units
    for i in range(0, columns * rows):
        units_resize[i] = cv2.resize(units[i], dsize=(
            112, 112), interpolation=cv2.INTER_CUBIC)
        fig.add_subplot(rows, columns, i+1)
        plt.imshow(units_resize[i])
    plt.show()

    data_dir = fileList("/Users/marc/Desktop/OPTC/optc_thumbs", '.png')
    matches = []

    with alive_bar(len(units), title=f'Finding matches for 3 Teams from image {num}/33') as bar:
        for test_img in units:
            mse_vals = []
            mse_names = []

            for path in data_dir:
                data_img = cv2.imread(path, 0)
                mse_vals.append(mse(data_img, test_img))
                mse_names.append(path)

            max_item = min(mse_vals)
            max_file = mse_names[mse_vals.index(max_item)]
            matches.append(max_file)
            bar()

    return matches

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Crush PNG files => fix ICC profiles


def crushPNGs(file_dir):
    with alive_bar(len(data_dir), title='Crushing PNGs') as bar:
        for path in file_dir:
            os.system(
                f'/usr/local/bin/pngcrush -ow -rem allb -reduce {path} > /dev/null 2>&1')
            bar()


data_dir = fileList("/Users/marc/Desktop/OPTC/optc_thumbs/jap", '.png')
# crushPNGs(data_dir)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

base_dir = fileList("/Users/marc/Desktop/OPTC/optc_thumbs/", '.png')


def moveDupes(file_dir):
    for path in file_dir:
        # copy only files
        if any(x[41:] == path[41:] and x != path for x in file_dir):
            shutil.move(
                f'/Users/marc/Desktop/OPTC/optc_thumbs/jap/{path[41:]}', "/Users/marc/Desktop/OPTC/dupes")
#moveDupes(base_dir)


def copyUniq(file_dir):
    for path in file_dir:
        shutil.copy(path, '/Users/marc/Desktop/OPTC/unique')
# copyUniq(base_dir)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Begin matching process


def getMatchesFromScreenshots(screenshot_dir):
    matches = []
    for x, path in enumerate(screenshot_dir):
        img = cv2.imread(path, 0)
        matches.extend(get3Teams(img, x))
    return matches


screenshot_dir = fileList("/Users/marc/Desktop/OPTC/screenshots", '.PNG')
matches = getMatchesFromScreenshots(screenshot_dir)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Arrange Images to 8 by X collage


def buildCollage(matches):
    s = 112
    col = 8
    row = len(matches) // col
    new = Image.new("RGBA", (s*col, s*row))
    for i in range(col):
        for j in range(row):
            img = Image.open(matches[j * col + i])
            new.paste(img, (s * i, s * j))
    new.show()


buildCollage(matches)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Start statistics section

team_id = []
id = 1
for i in range(len(matches)):
    team_id.append(id)
    if i != 0 and (i+1) % 8 == 0:
        id = id + 1

df = pd.DataFrame()
unit_id_raw = [s[47:-4] for s in matches]
unit_id = [s[47:-4] for s in matches if s !=
           '/Users/marc/Desktop/OPTC/optc_thumbs/null.png']
counted = Counter(unit_id_raw)
df['Unit'] = unit_id_raw
df['Team No'] = team_id

counted = Counter(matches)


def possibleCominations(total, sample):
    return math.factorial(total) / (math.factorial(sample) * math.factorial(total - sample))


total_pos = possibleCominations(len(counted), 5)

teams = []
for i in range(int(len(matches)/8)):
    teams.append(sorted(unit_id_raw[i*8:i*8+8]))
    teams[i] = [s for s in teams[i] if s != ""]

counted_c_1 = Counter(unit_id)

c_2 = []
for i in range(len(teams)):
    duos_iter = list(itertools.combinations(teams[i], 2))
    c_2.extend(duos_iter)
counted_c_2 = Counter(c_2)

c_3 = []
for i in range(len(teams)):
    trios_iter = list(itertools.combinations(teams[i], 3))
    c_3.extend(trios_iter)
counted_c_3 = Counter(c_3)

c_4 = []
for i in range(len(teams)):
    quads_iter = list(itertools.combinations(teams[i], 4))
    c_4.extend(quads_iter)
counted_c_4 = Counter(c_4)

c_5 = []
for i in range(len(teams)):
    fives_iter = list(itertools.combinations(teams[i], 5))
    c_5.extend(fives_iter)
counted_c_5 = Counter(c_5)

c_6 = []
for i in range(len(teams)):
    sixes_iter = list(itertools.combinations(teams[i], 6))
    c_6.extend(sixes_iter)
counted_c_6 = Counter(c_6)

c_7 = []
for i in range(len(teams)):
    sevens_iter = list(itertools.combinations(teams[i], 7))
    c_7.extend(sevens_iter)
counted_c_7 = Counter(c_7)

teams_full = [e for e in teams if len(e) == 8]
c_8 = []
for i in range(len(teams_full)):
    c_8.append(tuple(teams_full[i]))
counted_c_8 = Counter(c_8)


# Collage Time !!
def buildCollage1(counter_obj):
    mc = counter_obj.most_common()
    s = 112
    col = 1
    row = 10
    new = Image.new("RGBA", (s*col, s*row))
    num = Image.new("RGBA", (s, s*row))
    for i in range(col):
        for j in range(row):
            img = Image.open(f'/Users/marc/Desktop/OPTC/unique/{mc[j][0]}.png')
            new.paste(img, (s * i, s * j))
            img = Image.open(
                f'/Users/marc/Desktop/OPTC/numbers/{mc[j][1]}.png')
            num.paste(img, (0, s * j))
    new.save(f'/Users/marc/Desktop/OPTC/ranked_combinations/{col}.png')
    num.save(f'/Users/marc/Desktop/OPTC/ranked_combinations/{col}_num.png')    


buildCollage1(counted_c_1)


def buildCollage2(counter_obj):
    mc = counter_obj.most_common()
    s = 112
    col = 2
    row = 10
    new = Image.new("RGBA", (s*col, s*row))
    num = Image.new("RGBA", (s, s*row))
    for i in range(col):
        for j in range(row):
            img = Image.open(
                f'/Users/marc/Desktop/OPTC/unique/{mc[j][0][i]}.png')
            new.paste(img, (s * i, s * j))
            img = Image.open(
                f'/Users/marc/Desktop/OPTC/numbers/{mc[j][1]}.png')
            num.paste(img, (0, s * j))
    new.save(f'/Users/marc/Desktop/OPTC/ranked_combinations/{col}.png')
    num.save(f'/Users/marc/Desktop/OPTC/ranked_combinations/{col}_num.png')


buildCollage2(counted_c_2)


def buildCollage3(counter_obj):
    mc = counter_obj.most_common()
    s = 112
    col = 3
    row = 10
    new = Image.new("RGBA", (s*col, s*row))
    num = Image.new("RGBA", (s, s*row))
    for i in range(col):
        for j in range(row):
            img = Image.open(
                f'/Users/marc/Desktop/OPTC/unique/{mc[j][0][i]}.png')
            new.paste(img, (s * i, s * j))
            img = Image.open(
                f'/Users/marc/Desktop/OPTC/numbers/{mc[j][1]}.png')
            num.paste(img, (0, s * j))
    new.save(f'/Users/marc/Desktop/OPTC/ranked_combinations/{col}.png')
    num.save(f'/Users/marc/Desktop/OPTC/ranked_combinations/{col}_num.png')


buildCollage3(counted_c_3)


def buildCollage4(counter_obj):
    mc = counter_obj.most_common()
    s = 112
    col = 4
    row = 10
    new = Image.new("RGBA", (s*col, s*row))
    num = Image.new("RGBA", (s, s*row))
    for i in range(col):
        for j in range(row):
            img = Image.open(
                f'/Users/marc/Desktop/OPTC/unique/{mc[j][0][i]}.png')
            new.paste(img, (s * i, s * j))
            img = Image.open(
                f'/Users/marc/Desktop/OPTC/numbers/{mc[j][1]}.png')
            num.paste(img, (0, s * j))
    new.save(f'/Users/marc/Desktop/OPTC/ranked_combinations/{col}.png')
    num.save(f'/Users/marc/Desktop/OPTC/ranked_combinations/{col}_num.png')


buildCollage4(counted_c_4)


def buildCollage5(counter_obj):
    mc = counter_obj.most_common()
    s = 112
    col = 5
    row = 10
    new = Image.new("RGBA", (s*col, s*row))
    num = Image.new("RGBA", (s, s*row))
    for i in range(col):
        for j in range(row):
            img = Image.open(
                f'/Users/marc/Desktop/OPTC/unique/{mc[j][0][i]}.png')
            new.paste(img, (s * i, s * j))
            img = Image.open(
                f'/Users/marc/Desktop/OPTC/numbers/{mc[j][1]}.png')
            num.paste(img, (0, s * j))
    new.save(f'/Users/marc/Desktop/OPTC/ranked_combinations/{col}.png')
    num.save(f'/Users/marc/Desktop/OPTC/ranked_combinations/{col}_num.png')


buildCollage5(counted_c_5)


def buildCollage6(counter_obj):
    mc = counter_obj.most_common()
    s = 112
    col = 6
    row = 10
    new = Image.new("RGBA", (s*col, s*row))
    num = Image.new("RGBA", (s, s*row))
    for i in range(col):
        for j in range(row):
            img = Image.open(
                f'/Users/marc/Desktop/OPTC/unique/{mc[j][0][i]}.png')
            new.paste(img, (s * i, s * j))
            img = Image.open(
                f'/Users/marc/Desktop/OPTC/numbers/{mc[j][1]}.png')
            num.paste(img, (0, s * j))
    new.save(f'/Users/marc/Desktop/OPTC/ranked_combinations/{col}.png')
    num.save(f'/Users/marc/Desktop/OPTC/ranked_combinations/{col}_num.png')


buildCollage6(counted_c_6)


def buildCollage7(counter_obj):
    mc = counter_obj.most_common()
    s = 112
    col = 7
    row = 10
    new = Image.new("RGBA", (s*col, s*row))
    num = Image.new("RGBA", (s, s*row))
    for i in range(col):
        for j in range(row):
            img = Image.open(
                f'/Users/marc/Desktop/OPTC/unique/{mc[j][0][i]}.png')
            new.paste(img, (s * i, s * j))
            img = Image.open(
                f'/Users/marc/Desktop/OPTC/numbers/{mc[j][1]}.png')
            num.paste(img, (0, s * j))
    new.save(f'/Users/marc/Desktop/OPTC/ranked_combinations/{col}.png')
    num.save(f'/Users/marc/Desktop/OPTC/ranked_combinations/{col}_num.png')


buildCollage7(counted_c_7)


def buildCollage8(counter_obj):
    mc = counter_obj.most_common()
    s = 112
    col = 8
    row = 10
    new = Image.new("RGBA", (s*col, s*row))
    num = Image.new("RGBA", (s, s*row))
    for i in range(col):
        for j in range(row):
            img = Image.open(
                f'/Users/marc/Desktop/OPTC/unique/{mc[j][0][i]}.png')
            new.paste(img, (s * i, s * j))
            img = Image.open(
                f'/Users/marc/Desktop/OPTC/numbers/{mc[j][1]}.png')
            num.paste(img, (0, s * j))
    new.save(f'/Users/marc/Desktop/OPTC/ranked_combinations/{col}.png')
    num.save(f'/Users/marc/Desktop/OPTC/ranked_combinations/{col}_num.png')


buildCollage8(counted_c_8)
