# src/path.py

import os

def get_relative_path(relative_path):
    """
    相対パスを絶対パスに変換する
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, relative_path)
