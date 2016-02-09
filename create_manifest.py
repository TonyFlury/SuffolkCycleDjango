#!/usr/bin/env python
"""
# SuffolkCycleDjango : Implementation of create_manifest.py

Summary : 
    <summary of module/class being implemented>
Use Case : 
    As a <actor> I want <outcome> So that <justification>

Testable Statements :
    Can I <Boolean statement>
    ....
"""
import sys
import os
import hashlib

__version__ = "0.1"
__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '09 Feb 2016'

def get_sha224(file_path):
    m = hashlib.sha224()
    try:
        with open(file_path, 'rb') as f:
            m.update(f.read())
    except BaseException as e:
        sys.stderr.write("Error creating signature for '{}': {}".format(file_path, e))
        return None

    return m.hexdigest()

def walk_files():
    for root, dirs, files in os.walk(os.getcwd()):
        for f in files:
            name, ext = os.path.splitext(f)
            if ext not in ['.py', '.html', '.gif', '.png', '.css']:
                continue
            yield os.path.join(root, f)

        if 'env' in dirs:
            dirs.remove('env')

        if 'media' in dirs:
            dirs.remove('media')

if __name__ == '__main__':
    total = 0
    try:
        with open('manifest.txt', 'w') as manifest:
            for path in walk_files():
                signature = get_sha224(path)
                if signature:
                    manifest.write('{}\t{}\n'.format(os.path.relpath(path), signature))
                    sys.stdout.write('{}\n'.format(os.path.relpath(path)))
                    total += 1
    except BaseException as e:
        sys.stderr.write("Error generating manifest file : {}".format(e))
        sys.exit(1)

    print "{} files processed".format(total)