from utils.file_utils import make_file_list, select_unique_files, make_id_path_dict
from utils.image_utils import create_perceptual_hashes, getMatchesFromScreenshots, buildCollage, build_ranked_collage
from utils.stats_utils import get_ids, make_teams
from utils.validation import validate_required_files, validate_thumbnail_directory, ValidationError
from utils.create_teams_grid import create_teams_grid
from utils.create_compact_teams_grid import create_compact_teams_grid
import os



def main(thumbnail_path, screenshot_path, month=9, year=2025):
    """Main analysis function with comprehensive error handling"""
    try:
        print("Starting OPTC Rumble Analysis...")
        
        # Validate required files and directories
        print("Validating required files...")
        validate_required_files()
        validate_thumbnail_directory(thumbnail_path)
        
        # Make file list and perceptual hashes from thumbnail directory
        print("Processing thumbnail images...")
        file_list = make_file_list(thumbnail_path, '.png')
        file_list.append('images/null.png')
        
        if len(file_list) < 100:  # Sanity check
            print(f"Warning: Only found {len(file_list)} thumbnail images. Expected more.")
        
        unique_file_list = select_unique_files(file_list)
        id_path_dict = make_id_path_dict(file_list)
        target_hashes = create_perceptual_hashes(unique_file_list) 

        # Make file list from screenshots directory
        print("Processing screenshots...")
        screenshot_list = make_file_list(screenshot_path, '.PNG')
        screenshot_list = sorted(screenshot_list)
        
        if len(screenshot_list) == 0:
            raise ValidationError(f"No screenshots found in {screenshot_path}")
        
        print(f"Found {len(screenshot_list)} screenshots to process")
        
        # Get matches from screenshots and perceptual hashes
        matches = getMatchesFromScreenshots(screenshot_list, target_hashes)    

        # Strip file paths from matches to get raw IDs
        id_list, _ = get_ids(matches)
        
        # Translate IDs to Teams of 8 Units 
        teams_list = make_teams(id_list, matches)
        
        print(f"Analyzed {len(teams_list)} teams")

        # Generate output
        print("Generating collages...")
        
        # All Teams by actual In-Game Ranking
        buildCollage(matches)
        
        # Counted Units and Combinations
        build_ranked_collage(teams_list, id_path_dict, rows=25, n_max_units=5, month=month, year=year)
        
        # Generate team grid visualizations
        print("Generating team grid layouts...")
        create_teams_grid()
        create_compact_teams_grid()
        
        print("Analysis completed successfully!")
        
    except ValidationError as e:
        print(f"Validation Error: {e}")
        print("Please check your input files and try again.")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("Please check the error message and try again.")
        return False
    
    return True



if __name__ == '__main__':
    thumbnail_path = os.path.join('optc-db.github.io', 'api', 'images', 'thumbnail')
    screenshot_path = os.path.join('images', 'screenshots')

    success = main(thumbnail_path, screenshot_path, month=11, year=2025)
    if not success:
        exit(1)
    
    


