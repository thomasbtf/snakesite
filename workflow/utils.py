import os


def make_dir(dir:str):
    """A helper-function to create a directroy, if it does not exist.

    Args:
        dir (str): Path to the directroy.
    """
    if not os.path.exists(dir):
        os.makedirs(dir)


def find_file(directory: str, search_file :str) -> str:
    """Finds relative path of file in given directory and its subdirectories.

    Args:
        directory (str): Directory to search in.
        search_file (str): File to search in directory.

    Returns:
        str:  Path to file.
    """
   
    paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if  file.lower().endswith(search_file.lower()):
                paths.append(os.path.join(root, file))

    if not paths:
        return ""

    paths = [ele for ele in paths if ".test" not in ele]
    shortest_path = min(paths, key=len)
    relative_path = shortest_path.replace(directory, "").strip("/")
    
    return relative_path
