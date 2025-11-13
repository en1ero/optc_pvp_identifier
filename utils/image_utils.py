import cv2
import numpy as np
from skimage.feature import match_template
from alive_progress import alive_bar
from imagehash import phash
from PIL import Image, ImageOps, ImageFont, ImageDraw
import os
import platform
import datetime
import json

from utils.stats_utils import make_counter
from utils.constants import IPHONE_11_PRO, IMAGE_SETTINGS, OVERLAY_COLORS, UNIT_ID_MAPPINGS
from utils.validation import (
    validate_screenshot_file, validate_screenshot_dimensions, 
    validate_anchor_detection, ValidationError
)

overlay_images = {
        "red": os.path.join('images', 'overlays', 'str.png'),
        "green": os.path.join('images', 'overlays', 'dex.png'),
        "blue": os.path.join('images', 'overlays', 'qck.png'),
        "yellow": os.path.join('images', 'overlays', 'psy.png'),
        "purple": os.path.join('images', 'overlays', 'int.png'),
        "black": os.path.join('images', 'overlays', 'dual.png'),
        "empty": os.path.join('images', 'overlays', 'empty.png')
    }

# Use device-specific coordinates
xy = IPHONE_11_PRO['anchor_coords']

if platform.system() == "Windows":
    FONT = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 50)
    FONT_RANK = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 75)
    FONT_SUBSCRIPT = ImageFont.truetype("C:/Windows/Fonts/ariali.ttf", 16)
    FONT_SUBTITLE = ImageFont.truetype("C:/Windows/Fonts/ariali.ttf", 30)
else:
    FONT = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 50)
    FONT_RANK = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 75)
    FONT_SUBSCRIPT = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Italic.ttf", 16)
    FONT_SUBTITLE = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Italic.ttf", 30)


def make_anchor_from_image(file_path):
    """Create anchor template from reference image with error handling"""
    try:
        ref = cv2.imread(file_path, 0)
        if ref is None:
            raise ValidationError(f"Could not load anchor image: {file_path}")
        
        anchor_img = ref[xy[0]:xy[1], xy[2]:xy[3]]
        if anchor_img.size == 0:
            raise ValidationError(f"Invalid anchor coordinates for image: {file_path}")
        
        return anchor_img
    except Exception as e:
        raise ValidationError(f"Error creating anchor from {file_path}: {str(e)}")


def find_anchor_position(img, anchor_img):
    """Find anchor position in screenshot with validation"""
    search_area = IPHONE_11_PRO['search_area']
    search_region = img[:search_area['height'], :search_area['width']]
    
    resulting_image = match_template(search_region, anchor_img)
    validate_anchor_detection(resulting_image)
    
    x, y = np.unravel_index(np.argmax(resulting_image), resulting_image.shape)
    return x, y

def extract_unit_coordinates(anchor_x, anchor_y):
    """Calculate unit extraction coordinates based on anchor position"""
    config = IPHONE_11_PRO['team_extraction']
    
    # Extract constants for readability
    captain_offset = config['captain_offset']
    crew_offset = config['crew_offset'] 
    row_gap = config['row_gap']
    unit_gap = config['unit_gap']
    small_gap = config['small_gap']
    
    units_coords = []
    
    # Extract coordinates for 3 teams (24 units total)
    for team in range(3):
        team_base_x = anchor_x + captain_offset + team * row_gap
        team_base_y = anchor_y
        
        # Captain (1 unit)
        units_coords.append((
            team_base_x, team_base_x + 196,  # x1, x2 (253-57=196)
            team_base_y - 383, xy[3] - 257   # y1, y2
        ))
        
        # Crew members (7 units)
        crew_base_x = anchor_x + crew_offset + team * row_gap
        crew_base_y = team_base_y - 178
        
        for unit_idx in range(7):
            if unit_idx < 4:
                y_offset = unit_idx * unit_gap
            else:
                y_offset = unit_idx * unit_gap + small_gap
                
            units_coords.append((
                crew_base_x, crew_base_x + 103,  # x1, x2 (245-142=103)
                crew_base_y + y_offset, xy[3] - 145 + y_offset  # y1, y2
            ))
    
    return units_coords

def extract_units_from_coordinates(img, units_coords):
    """Extract unit images from calculated coordinates"""
    units = []
    unit_size = IMAGE_SETTINGS['unit_size']
    
    for x1, x2, y1, y2 in units_coords:
        # Validate coordinates are within image bounds
        if x1 < 0 or x2 >= img.shape[0] or y1 < 0 or y2 >= img.shape[1]:
            print(f"Warning: Unit coordinates out of bounds: ({x1},{x2},{y1},{y2})")
            # Create empty unit as fallback
            unit = np.zeros((unit_size, unit_size), dtype=np.uint8)
        else:
            unit = img[x1:x2, y1:y2]
            if unit.size == 0:
                print(f"Warning: Empty unit extracted at ({x1},{x2},{y1},{y2})")
                unit = np.zeros((unit_size, unit_size), dtype=np.uint8)
            else:
                unit = cv2.resize(unit, dsize=(unit_size, unit_size), interpolation=cv2.INTER_CUBIC)
        
        units.append(unit)
    
    return units

def get_team_images(img, anchor_img):
    """Extract team unit images from screenshot with improved error handling"""
    try:
        # Validate screenshot dimensions
        validate_screenshot_dimensions(img)
        
        # Find anchor position
        anchor_x, anchor_y = find_anchor_position(img, anchor_img)
        
        # Calculate unit coordinates
        units_coords = extract_unit_coordinates(anchor_x, anchor_y)
        
        # Extract units
        units = extract_units_from_coordinates(img, units_coords)
        
        if len(units) != 24:  # 3 teams * 8 units each
            print(f"Warning: Expected 24 units, got {len(units)}")
        
        return units
        
    except ValidationError as e:
        print(f"Error extracting teams: {e}")
        raise
    except Exception as e:
        raise ValidationError(f"Unexpected error in team extraction: {str(e)}")


def get_matches(unit_images, target_hashes, index):
    matches = []
    with alive_bar(len(unit_images), title=f'Finding matches for 3 Teams from image {index+1}/33') as bar:
        for unit_img in unit_images:
            current_hash = phash(Image.fromarray(unit_img, 'L'), hash_size=16)

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


def getMatchesFromScreenshots(screenshot_list, target_hashes):
    """Process all screenshots and return unit matches with error handling"""
    try:
        anchor_image = make_anchor_from_image('images/anchor.jpeg')
        matches = []
        failed_screenshots = []
        
        for index, path in enumerate(screenshot_list):
            try:
                screen_shot = validate_screenshot_file(path)
                unit_images = get_team_images(screen_shot, anchor_image)
                screenshot_matches = get_matches(unit_images, target_hashes, index)
                matches.extend(screenshot_matches)
                
            except ValidationError as e:
                print(f"Skipping {path}: {e}")
                failed_screenshots.append(path)
                continue
            except Exception as e:
                print(f"Unexpected error processing {path}: {e}")
                failed_screenshots.append(path)
                continue
        
        if failed_screenshots:
            print(f"\nFailed to process {len(failed_screenshots)} screenshots:")
            for failed in failed_screenshots:
                print(f"  - {failed}")
        
        if not matches:
            raise ValidationError("No valid matches found in any screenshots")
        
        # Apply unit ID mappings for alternating evolutions
        matches = apply_unit_mappings(matches)
        
        print(f"Successfully processed {len(screenshot_list) - len(failed_screenshots)} screenshots")
        return matches
        
    except Exception as e:
        raise ValidationError(f"Error processing screenshots: {str(e)}")

def apply_unit_mappings(matches):
    """Apply special unit ID mappings for alternating evolutions"""
    for i, match in enumerate(matches):
        filename = os.path.basename(match)
        if filename in UNIT_ID_MAPPINGS:
            new_filename = UNIT_ID_MAPPINGS[filename]
            matches[i] = os.path.join(os.path.dirname(match), new_filename)
    return matches


def create_perceptual_hashes(image_file_list):
    hashes = {}
    with alive_bar(len(image_file_list), title=f'Making Perceptual Hashes for {len(image_file_list)} images') as bar:
        for image_file in image_file_list:
            image_hash =  phash(Image.open(image_file).convert('L'), hash_size=16)
            hashes[image_file] = image_hash
            bar()
    return hashes


def make_overlayed_img(match):
    crop = 14
    img = Image.open(match).convert("RGBA")
    r, g, b, _ = img.getpixel((32, 19))
    closest_color = get_closest_color(r, g, b)
    overlay = Image.open(overlay_images[closest_color])
    img = img.crop((crop, crop, img.width - crop, img.height - crop))
    padding = (overlay.width - img.width) // 2
    img = ImageOps.expand(img, border=padding, fill=(0, 0, 0, 0))
    img = Image.alpha_composite(img, overlay)
    return img


def buildCollage(matches, s=112, cols=8):
    unique_matches = list(set(matches))
    os.makedirs(os.path.join('results', 'teams'), exist_ok=True)
    os.makedirs(os.path.join('results', 'teams', 'single'), exist_ok=True)
    for i, match in enumerate(unique_matches):
        img = Image.new("RGBA", (s,s))
        img = make_overlayed_img(match)
        img.save(os.path.join('results', 'teams', 'single', f'{i}.png'))
    rows = len(unique_matches) // cols
    all_teams = Image.new("RGBA", (s*cols, s*rows))
    new_team = Image.new("RGBA", (s*cols, s))
    for i, match in enumerate(matches):
        img = make_overlayed_img(match)
        all_teams.paste(img, (img.width * (i % cols), s * (i // cols)))
        new_team.paste(img, (img.width * (i % cols), 0))
        if i % cols == cols-1:
            new_team.save(os.path.join('results', 'teams', f'{(i + 1) // cols}.png'))
    all_teams.save(os.path.join('results', 'teams', 'all.png'))
    

def get_closest_color(r, g, b):
    """Find closest overlay color using Manhattan distance"""
    closest_color = min(
        OVERLAY_COLORS, 
        key=lambda color: abs(OVERLAY_COLORS[color][0]-r) + abs(OVERLAY_COLORS[color][1]-g) + abs(OVERLAY_COLORS[color][2]-b)
    )
    return closest_color


def write_counts_per_id_to_json(id_path_dict, counted_raw, month=6, year=2024):
    counts = {id_key: {'count': 0, 'rank': None} for id_key in id_path_dict.keys()}

    i = 0
    for id_val, count in counted_raw:
        counts[id_val[0]]['count'] = count
        counts[id_val[0]]['rank'] = i+1
        i += 1

    directory = 'data'
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory,'counts_per_id_{}_{}.json'.format(month, year))
    with open(file_path, 'w') as fp:
        json.dump(counts, fp, indent=4)


def make_power_ranking(counted_range, current_total, month=None, year=None):
    file_path_current = os.path.join('data', 'counts_per_id_{}_{}.json'.format(month, year))
    
    # Handle previous month file (might be from previous year)
    prev_month = month - 1
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year = year - 1
    
    file_path_previous = os.path.join('data', 'counts_per_id_{}_{}.json'.format(prev_month, prev_year))
    
    with open(file_path_current, 'r') as fp:
        current = json.load(fp)
    
    # Try to load previous month data, if it doesn't exist, return None to skip power rankings
    try:
        with open(file_path_previous, 'r') as fp:
            previous = json.load(fp)
    except FileNotFoundError:
        print(f"No previous month data found ({file_path_previous}). Skipping power ranking features.")
        return None

    count_and_rank_gains = []
    for id_val, _ in counted_range:
        if id_val[0] not in previous: 
            count_gain = None
            rank_gain = None
        elif previous[id_val[0]]['count'] == 0:
            count_gain = current[id_val[0]]['count']
            rank_gain = current_total - current[id_val[0]]['rank']
        else:
            count_gain = current[id_val[0]]['count'] - previous[id_val[0]]['count']
            rank_gain =  previous[id_val[0]]['rank'] - current[id_val[0]]['rank']

        count_and_rank_gains.append((id_val[0], count_gain, rank_gain))
    return count_and_rank_gains

def write_power_ranking_to_collage(count_and_rank_gains, canvas, i, s, w):
    light_red = (255, 144, 128, 200)
    light_green = (144, 255, 144, 200)
    if count_and_rank_gains[i][2] != None:
        if count_and_rank_gains[i][2] > 0:
            canvas.text((s//2*3, s*i + s-16), '+'+str(count_and_rank_gains[i][2]), fill=light_green, font=FONT_SUBSCRIPT, anchor="mm", align="center")
        elif count_and_rank_gains[i][2] < 0:
            canvas.text((s//2*3, s*i + s-16), str(count_and_rank_gains[i][2]), fill=light_red, font=FONT_SUBSCRIPT, anchor="mm", align="center")
        else:
            pass
        if count_and_rank_gains[i][1] > 0:
            canvas.text((s*2 + w//2, s*i + s-16), '+'+str(count_and_rank_gains[i][1]), fill=light_green, font=FONT_SUBSCRIPT, anchor="mm", align="center")
        elif count_and_rank_gains[i][1] < 0:
            canvas.text((s*2 + w//2, s*i + s-16), str(count_and_rank_gains[i][1]), fill=light_red, font=FONT_SUBSCRIPT, anchor="mm", align="center")
        else:
            pass
    return canvas


def add_power_ranking_icons(count_and_rank_gains, canvas, s, w):
    same = os.path.join('images', 'power_ranking','same.png')
    up = os.path.join('images', 'power_ranking','up.png')
    down = os.path.join('images', 'power_ranking','down.png')
    new = os.path.join('images', 'power_ranking','new.png')

    for i in range(len(count_and_rank_gains)):
        if count_and_rank_gains[i][2] == None:
            img = Image.open(new)
        elif count_and_rank_gains[i][2] == 0:
            img = Image.open(same)
        elif count_and_rank_gains[i][2] > 0:
            img = Image.open(up)
        elif count_and_rank_gains[i][2] < 0:
            img = Image.open(down)
        canvas.paste(img, (s, s*i), img)
    return canvas

def build_ranked_collage(teams, path_dict, rows=20, n_max_units=5, s=112, spacing_hor=92, month='Month', year='Year'):
    images = []
    final_width = -spacing_hor
    rows_collage = rows
    w = 92
    pad = s - w
    
    for col in range(1, n_max_units+1):
        counted = make_counter(teams, col)
        if col == 1:
            counted_raw = counted.most_common(len(counted))
            write_counts_per_id_to_json(path_dict, counted_raw, month=month, year=year)
            counted_range = counted.most_common(rows)
            count_and_rank_gains = make_power_ranking(counted_range, len(counted_raw), month=month, year=year)

        counted_range = counted.most_common(rows)

        new = Image.new("RGBA", (w*col, s*rows - 20))
        num = Image.new("RGBA", (w, s*rows - 20))
        draw = ImageDraw.Draw(num)

        if len(counted_range) < rows:
            rows = len(counted_range)
            print(f"Only {rows} teams available in col {col}.")

        for i in range(col):
            for j in range(rows):
                img = make_overlayed_img(path_dict[counted_range[j][0][i]])
                new.paste(img, (w * i, s * j))
                draw.text((img.width//2, img.width//2 + s*j), str(counted_range[j][1]), fill="white", font=FONT, anchor="mm", align="right")

        # concat new and num horizontally with spacing_hor
        new_num = Image.new("RGBA", (img.width*col + img.width, s*rows - 20))
        new_num.paste(new, (img.width, 0))
        new_num.paste(num, (0, 0))
        images.append(new_num)
        final_width += new_num.width + spacing_hor

    # Put all teams into a collage
    teams_collage = Image.new("RGBA", (final_width, s*rows_collage - 20))   
    pos_hor = 0
    for i in range(n_max_units):
        teams_collage.paste(images[i], (pos_hor, 0))
        pos_hor += images[i].width + spacing_hor

    # paste alternating dark/light bars onto background and write descending ranks
    bg = Image.new("RGBA", (teams_collage.width + s*2, teams_collage.height + pad))
    for i in range(rows_collage):
        dark = 15
        light = 35
        color = (light, light, light, 255) if i % 2 == 0 else (dark, dark, dark, 255)
        bg.paste(Image.new("RGBA", (final_width + s*2, s), color=color), (0, s*i))
        ranks = ImageDraw.Draw(bg)
        ranks.text((s//2, s*i + s//2), str(i + 1), fill="gray", font=FONT_RANK, anchor="mm", align="center")
        if count_and_rank_gains is not None:
            ranks = write_power_ranking_to_collage(count_and_rank_gains, ranks, i, s, w)

    # paste teams_collage onto bg
    bg_with_teams = ImageOps.expand(teams_collage, border=(s*2, pad//2, 0, pad//2), fill=(0, 0, 0, 0))
    bg_with_teams = Image.alpha_composite(bg, bg_with_teams)

    # paste power ranking icons onto bg_with_teams (only if previous data exists)
    if count_and_rank_gains is not None:
        collage = add_power_ranking_icons(count_and_rank_gains, bg_with_teams, s, w)
    else:
        collage = bg_with_teams

    # Make header
    header = Image.new("RGBA", (collage.width, 256), color=(dark, dark, dark, 255))
    draw = ImageDraw.Draw(header)
    title = 'Most Common Units in Pirate Rumble Top 100'
    month_abbr = ['Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'June', 'July', 'Aug.', 'Sept.', 'Oct.', 'Nov.', 'Dec.']
    month_num = int(month)
    subtitle = f'Championship ({month_abbr[month_num-1]} {year}) - Defensive Teams'
    draw.text((collage.width//2, 64), title, fill="white", font=FONT, anchor="mm", align="center")
    draw.text((collage.width//2, 112), subtitle, fill="white", font=FONT_SUBTITLE, anchor="mm", align="center")

    # draw column titles
    draw.text((s, header.height-48), "RANK", fill="white", font=FONT, anchor="mm", align="center")
    col_titles = ['SOLO', 'DUO', 'TRIO', 'QUARTET', 'QUINTET', 'SEXTET', 'SEPTET', 'OCTET']
    pos_hor = 0
    for i in range(n_max_units):
        draw.text((pos_hor + s*2 + images[i].width//2 + w//2, header.height-48), col_titles[i], fill="white", font=FONT, anchor="mm", align="center")
        pos_hor += images[i].width + spacing_hor

    # paste header onto final
    final = Image.new("RGBA", (collage.width, collage.height + header.height))
    final.paste(header, (0, 0))
    final.paste(collage, (0, header.height))

    # save image
    now = datetime.datetime.now()
    file_name = f'{now.strftime("%Y_%m_%d")}.png'
    result_dir = os.path.join('results', 'ranked_combinations')
    final.save(os.path.join(result_dir, file_name))
    print(f'Collage saved to: {os.path.join(result_dir, file_name)}')
