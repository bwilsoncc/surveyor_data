import os

DEFAULT_IMAGETYPES = [
    'tif', 'tiff',
    'jpg',
    'pdf',
]

def get_files(source, imagetypes=DEFAULT_IMAGETYPES):
    """
    Walk the tree rooted at 'source' and look for files with extensions listed in 'imagetypes' list.
    Returns a list of matching files and a list of ignored files.
    """
    matching = list()
    ignored = list()
    for root,dirs,files in os.walk(source):
        #print(root)
        for file in files:
            f,e = os.path.splitext(file)
            e = e[1:].lower()
            if e in imagetypes:
                pathname = os.path.join(root,file)
                matching.append(pathname)
            else:
                ignored.append(file)
    return matching, ignored

def get_ext_dict(files):
    """
    Build a dictionary and count how many of each extension occurs in a file list.
    """
    d = dict()
    for path in files:
        f,e = os.path.splitext(path.lower())
        if e in d:
            d[e] += 1
        else:
            d[e] = 1
    return d

if __name__ == "__main__":
    from config import Config
    matching,ignored = get_files(Config.SOURCE)
    print(matching)
    print(ignored)

    d = get_ext_dict(matching)
    print('matching:', d)

    d = get_ext_dict(ignored)
    print('ignored:', d)


