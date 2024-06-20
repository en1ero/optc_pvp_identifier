from utils.file_utils import make_file_list, select_unique_files, make_id_path_dictionary
from utils.image_utils import getMatchesFromScreenshots, make_template_from_image, create_perceptual_hashes, build_ranked_collage, buildCollage
from utils.stats_utils import get_ids, make_teams 



if __name__ == '__main__':

    # Look for every file path that ends on '.png' in directory and just keep unique file paths
    file_list = make_file_list('optc-db.github.io/api/images/thumbnail', '.png')
    unique_file_list = select_unique_files(file_list)
    path_dict = make_id_path_dictionary(file_list)

    # Make file list from screenshots directory
    screenshot_list = make_file_list('images/screenshots', '.PNG')

    template = make_template_from_image('images/anchor.jpeg')

    hashes = create_perceptual_hashes(unique_file_list) 

    matches = getMatchesFromScreenshots(screenshot_list, template, hashes)

    # buildCollage(matches)

    id_raw, counted = get_ids(matches)

    teams = make_teams(id_raw, matches)

    # Collage Time !!
    n_rows = 100
    team_comps = 8
    build_ranked_collage(teams, path_dict, n_rows, team_comps)
