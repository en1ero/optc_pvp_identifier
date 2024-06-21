from utils.file_utils import*
from utils.image_utils import*
from utils.stats_utils import* 



def main(thumbnail_path, screenshot_path):
    file_list = make_file_list(thumbnail_path, '.png')
    unique_file_list = select_unique_files(file_list)
    id_path_dict = make_id_path_dict(file_list)

    # Make file list from screenshots directory
    screenshot_list = make_file_list(screenshot_path, '.PNG')

    target_hashes = create_perceptual_hashes(unique_file_list) 

    matches = getMatchesFromScreenshots(screenshot_list, target_hashes)

    buildCollage(matches)

    id_raw, counted = get_ids(matches)

    teams = make_teams(id_raw, matches)

    # Collage Time !!
    n_rows = 25
    team_comps = 5
    build_ranked_collage(teams, id_path_dict, n_rows, team_comps)



if __name__ == '__main__':
    
    thumbnail_path = os.path.join('optc-db.github.io', 'api', 'images', 'thumbnail')
    screenshot_path = os.path.join('images', 'screenshots')

    main(thumbnail_path, screenshot_path)