import pickle 
import os
import os.path as path
import codecs


def create_folder(name):
    if not os.path.isdir(name):
        os.mkdir(name)


def save_file(name, obj, use_pickle=True):
    with open(name, 'wb') as f:
        if use_pickle:
            pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)
        else: 
            f.write(obj)


def save_file_utf8(name, obj):
    with codecs.open(name, "w", "utf-8") as file:
        file.write(u'%s' % obj)


def load_file(pathfile, use_pickle=False):
    if path.exists(pathfile):
        if use_pickle:
            with open(pathfile, 'rb') as f:
                data = pickle.load(f)
            return data 
        else:
            with open(pathfile, 'rb') as f:
                data = f.readlines()
            return data


def load_file_utf8(pathfile):
    if path.exists(pathfile):
        with codecs.open(pathfile, "r", "utf-8") as file:
            data = file.readlines()
        return data 


def check_file(pathfile):
    return path.exists(pathfile)