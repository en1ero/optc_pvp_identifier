#!/usr/bin/env python3
"""
Create a single page layout with all teams arranged in 25 rows and 4 columns.
"""

import os
from PIL import Image, ImageDraw, ImageFont
import datetime

def create_teams_grid():
    """Create a grid layout of all team images"""
    
    # Configuration
    rows = 25
    cols = 4
    teams_per_page = rows * cols  # 100 teams
    
    # Load a sample team image to get dimensions
    sample_team = Image.open('results/teams/1.png')
    team_width, team_height = sample_team.size
    
    print(f"Team image size: {team_width}x{team_height}")
    
    # Calculate grid dimensions
    grid_width = team_width * cols
    grid_height = team_height * rows
    
    # Add space for header and margins
    header_height = 100
    margin = 20
    
    # Create the main canvas
    canvas_width = grid_width + (margin * 2)
    canvas_height = grid_height + header_height + (margin * 2)
    
    canvas = Image.new('RGBA', (canvas_width, canvas_height), color=(30, 30, 30, 255))
    
    print(f"Canvas size: {canvas_width}x{canvas_height}")
    
    # Add header
    draw = ImageDraw.Draw(canvas)
    
    # Try to load a font, fall back to default if not available
    try:
        if os.path.exists("/System/Library/Fonts/Supplemental/Arial Bold.ttf"):
            title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 36)
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 24)
        else:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Draw header text
    title = "OPTC Rumble Teams - All Defensive Teams"
    now = datetime.datetime.now()
    subtitle = f"Generated on {now.strftime('%B %d, %Y')} - Top 100 Teams"
    
    # Center the text
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (canvas_width - title_width) // 2
    
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (canvas_width - subtitle_width) // 2
    
    draw.text((title_x, margin), title, fill="white", font=title_font)
    draw.text((subtitle_x, margin + 45), subtitle, fill="lightgray", font=subtitle_font)
    
    # Load and place team images
    teams_placed = 0
    missing_teams = []
    
    for row in range(rows):
        for col in range(cols):
            team_number = row * cols + col + 1
            
            if team_number > 99:  # We only have 99 teams
                break
                
            team_file = f'results/teams/{team_number}.png'
            
            if os.path.exists(team_file):
                try:
                    team_img = Image.open(team_file)
                    
                    # Calculate position
                    x = margin + (col * team_width)
                    y = margin + header_height + (row * team_height)
                    
                    # Paste the team image
                    canvas.paste(team_img, (x, y), team_img if team_img.mode == 'RGBA' else None)
                    teams_placed += 1
                    
                except Exception as e:
                    print(f"Error loading team {team_number}: {e}")
                    missing_teams.append(team_number)
            else:
                missing_teams.append(team_number)
    
    print(f"Placed {teams_placed} teams")
    if missing_teams:
        print(f"Missing teams: {missing_teams}")
    
    # Add team numbers as overlays
    for row in range(rows):
        for col in range(cols):
            team_number = row * cols + col + 1
            
            if team_number > 99:
                break
                
            # Calculate position for number overlay
            x = margin + (col * team_width) + 10
            y = margin + header_height + (row * team_height) + 10
            
            # Draw team number with background
            number_text = str(team_number)
            try:
                number_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 20)
            except:
                number_font = ImageFont.load_default()
            
            # Draw background rectangle for number
            number_bbox = draw.textbbox((0, 0), number_text, font=number_font)
            number_width = number_bbox[2] - number_bbox[0]
            number_height = number_bbox[3] - number_bbox[1]
            
            # Background rectangle
            rect_padding = 4
            draw.rectangle([
                x - rect_padding, 
                y - rect_padding, 
                x + number_width + rect_padding, 
                y + number_height + rect_padding
            ], fill=(0, 0, 0, 180))
            
            # Draw number
            draw.text((x, y), number_text, fill="white", font=number_font)
    
    # Save the result
    output_dir = 'results/teams_grid'
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f'all_teams_grid_{now.strftime("%Y_%m_%d")}.png')
    canvas.save(output_file)
    
    print(f"Teams grid saved to: {output_file}")
    print(f"Final image size: {canvas.size}")
    
    return output_file

def main():
    print("Creating teams grid layout...")
    output_file = create_teams_grid()
    print("Done!")

if __name__ == '__main__':
    main()