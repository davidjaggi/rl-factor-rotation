import os


def load_package_path():
    """
    Loads the root path of the project.
    """
    # return the path of the project
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_root_path():
    """
    Loads the root path of the project.
    """
    # return the path of rl factor rotation
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_data_path():
    """
    Loads the data path of the project.
    """
    # return the path of the data
    return os.path.join(load_root_path(), 'data')

if __name__ == "__main__":
    print(f"Package path: {load_package_path()}")
    print(f"Root path: {load_root_path()}")
    print(f"Data path: {load_data_path()}")
