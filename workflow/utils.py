import os
from os import path
from typing import List

def make_dir(dir:str):
    """A helper-function to create a directroy, if it does not exist.

    Args:
        dir (str): Path to the directroy.
    """
    if not os.path.exists(dir):
        os.makedirs(dir)


def find_file(directory: str, search_file :str) -> List[str]:
    """Finds file in given directory and its subdirectories.

    Args:
        directory (str): Directory to search in.
        search_file (str): File to search in directory.

    Returns:
        List[str]: 
    """
   
    paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            if search_file.lower() in file.lower():
                paths.append(os.path.join(root, file))

    return paths
