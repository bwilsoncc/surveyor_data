import os

DEFAULT_IMAGETYPES = [
    'tif', 'tiff',
    'jpg',
    'pdf',
]

def get_files(source, imagetypes=DEFAULT_IMAGETYPES):
    """
    Walk the tree rooted at 'source' and look for files with extensions listed in 'imagetypes' list.
    Returns a list of matching files,
    a dictionary of matching files indexed by extension,
    and a count of how many we ignored.
    """
    d = dict()
    l = list()
    ignored = list()
    for root,dirs,files in os.walk(source):
        print(root)
        for file in files:
            f,e = os.path.splitext(file)
            e = e[1:].lower()
            if e in imagetypes:
                if e not in d: d[e] = list()
                pathname = os.path.join(root,file)
                d[e].append(pathname)
                l.append(pathname)
            else:
                ignored.append(file)
    return l, d, ignored

if __name__ == "__main__":
    from config import Config
    lst,dct,ignored = get_files(Config.SOURCE)
    print(lst)
    print(dct)
    print(ignored)
