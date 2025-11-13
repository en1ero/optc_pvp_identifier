# Device and image processing constants

# iPhone 11 Pro specific coordinates
IPHONE_11_PRO = {
    'name': 'iPhone 11 Pro',
    'anchor_coords': [910, 950, 460, 530],  # [y1, y2, x1, x2] for anchor detection
    'team_extraction': {
        'captain_offset': 57,
        'crew_offset': 142,
        'row_gap': 310,
        'unit_gap': 107,
        'small_gap': 26,
        'captain_coords': (-383, 530-257),  # relative to anchor (x_offset, x_end)
        'crew_coords': (-178, 530-145),     # relative to anchor (x_offset, x_end)
    },
    'search_area': {
        'height': 1000,
        'width': 600,
    }
}

# Image processing settings
IMAGE_SETTINGS = {
    'unit_size': 112,
    'crop_border': 14,
    'hash_size': 16,
    'perceptual_hash_threshold': 256,
}

# File filtering
EXCLUDED_SUBSTRINGS = ["-STR", "-QCK", "-DEX", "-PSY", "-INT", "-skull", "ship_"]

# Color mappings for overlays
OVERLAY_COLORS = {
    "red": (248, 49, 68),
    "green": (70, 164, 39),
    "blue": (3, 98, 231),
    "yellow": (255, 214, 5),
    "purple": (143, 17, 210),
    "black": (81, 52, 51),
    "empty": (31, 22, 12)
}

# Special unit ID mappings (for alternating evolutions)
UNIT_ID_MAPPINGS = {
    # Shanks units with identical stats
    "4153.png": "4152.png",  # Shanks - Reigning Over the New Era / Shaking the Great Era of Piracy
    
    # Luffy/Yamato units with identical stats  
    "3878.png": "3877.png",  # Luffy & Yamato - Prepared for the Final Showdown / Declaring War on the Demon
    
    # Straw Hat Pirates - Merveille's Adventurer vs Dream Chaser versions
    "1114.png": "0519.png",  # Monkey D. Luffy - Merveille's Adventurer / Dream Chaser
    "1115.png": "0520.png",  # Monkey D. Luffy - Straw Hat Pirates' Attack / A Pirate Who Lives By His Code
    "1116.png": "0521.png",  # Sanji - Merveille's Adventurer / Dream Chaser
    "1117.png": "0522.png",  # Sanji - Straw Hat Pirates' Attack / A Pirate Who Lives By His Code
    "1118.png": "0523.png",  # Nami - Merveille's Adventurer / Dream Chaser
    "1119.png": "0524.png",  # Nami and Billy the Thunder Bird / A Pirate Who Lives By Her Code
    "1172.png": "0525.png",  # Brook - Merveille's Adventurer / Dream Chaser
    "1173.png": "0526.png",  # Brook - Straw Hat Pirates' Attack / A Pirate Who Lives By His Code
    "1174.png": "0553.png",  # Roronoa Zoro - Merveille's Adventurer / Dream Chaser
    "1175.png": "0554.png",  # Roronoa Zoro - Straw Hat Pirates' Attack / A Pirate Who Lives By His Code
}