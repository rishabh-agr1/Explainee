# file_handler.py
import tempfile
import os
import atexit

_temp_files = []

def write_temp_file(content):
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w+', encoding='utf-8', suffix='.txt')
    temp_file.write(content)
    temp_file.flush()
    _temp_files.append(temp_file.name)
    return temp_file.name

def read_temp_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def delete_temp_file(path):
    try:
        os.remove(path)
    except Exception:
        pass

def cleanup_all_temp_files():
    for file in _temp_files:
        try:
            os.remove(file)
        except Exception:
            pass

# Automatically clean up all temp files at exit
atexit.register(cleanup_all_temp_files)
