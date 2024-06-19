import os
from alive_progress import alive_bar

def make_file_list(source, file_type):
    excluded_substrings = ["-STR", "-QCK", "-DEX", "-PSY", "-INT", "-skull", "ship_"]
    matches = []
    for root, _, filenames in os.walk(source):
        for filename in filenames:
            if filename.endswith(file_type) and all(substr not in filename for substr in excluded_substrings):
                matches.append(os.path.join(root, filename))
    return matches


def crush_png_files(file_dir):
    '''
    Crush PNG files => fix ICC profiles
    '''
    with alive_bar(len(file_dir), title='Crushing PNGs') as bar:
        for path in file_dir:
            os.system(
                f'/usr/local/bin/pngcrush -ow -rem allb -reduce {path} > /dev/null 2>&1')
            bar()

def select_unique_files(file_dir):
    unique_names = set()
    unique_paths = []

    for file_path in file_dir:
        if os.path.basename(file_path) not in unique_names:
            unique_names.add(os.path.basename(file_path))
            unique_paths.append(file_path)
        
    return unique_paths

def make_id_path_dictionary(file_paths):
    dict = {}
    for path in file_paths:
        if os.path.basename(path)[:-4] != 'null':
            dict[os.path.basename(path)[:-4]] = path
    
    return dict


