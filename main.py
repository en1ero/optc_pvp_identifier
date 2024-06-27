from utils.file_utils import*
from utils.image_utils import*
from utils.stats_utils import* 



def main(thumbnail_path, screenshot_path, month=6, year=2024):
    # Make file list and perceptual hashes from thumbnail directory
    file_list = make_file_list(thumbnail_path, '.png')
    file_list.append('images/null.png')
    
    unique_file_list = select_unique_files(file_list)
    id_path_dict = make_id_path_dict(file_list)
    target_hashes = create_perceptual_hashes(unique_file_list) 

    # Make file list from screenshots directory
    screenshot_list = make_file_list(screenshot_path, '.PNG')
    screenshot_list = sorted(screenshot_list)
    
    # Get matches from screenshots and perceptual hashes
    matches = getMatchesFromScreenshots(screenshot_list, target_hashes)    

    # Strip file paths from matches to get raw IDs
    id_list, _ = get_ids(matches)
    team_ids = [id_list[i:i+8] for i in range(0, len(id_list), 8)]

    # Translate IDs to Teams of 8 Units 
    teams_list = make_teams(id_list, matches)

    # All Teams by actual In-Game Ranking
    buildCollage(matches)
    
    # Counted Units and Combinations
    build_ranked_collage(teams_list, id_path_dict, rows=100, n_max_units=8, month=month, year=year)



if __name__ == '__main__':
    
    thumbnail_path = os.path.join('optc-db.github.io', 'api', 'images', 'thumbnail')
    screenshot_path = os.path.join('images', 'screenshots')

    main(thumbnail_path, screenshot_path)
    
    


