import os
import argparse
import numpy as np
import imghdr
import shutil
import utils as ut 
from pyvi.pyvi import ViTokenizer


def main(folder, fr=0, to=None):
    files = os.listdir(folder)
    print(len(files))
    if not to:
        to = len(files)
    rg = np.arange(fr, to)
    for x in rg:
        name = get_article_name(x)
        fd = '%s/%s' % (folder, name)
        file = '%s/%s.txt' % (folder, name)
        if os.path.isdir(fd):
            shutil.rmtree(fd)
        if os.path.isfile(file):
            os.remove(file)

# fill index article with '000000' -> '000123'
def get_article_name(index, max_length=6):
    try:
        str_index = str(index)
        end = -len(str_index)
        arr = np.zeros(max_length, dtype='int32')
        for index, i in enumerate(str_index):
            arr[index + end] = int(i)
        return ''.join([str(x) for x in arr])
    except Exception:
        print('Max length of title is %' & max_length)
        return '000000'


def remove_empty_folder(root):
    for f in os.listdir(root):
        if os.path.isdir(f) and not len(os.listdir(f)):
            os.rmdir(f)


def change_image_format(root):
    for f in os.listdir(root):
        path = '%s/%s' % (root, f)
        if os.path.isdir(path): 
            if not len(os.listdir(path)):
                os.rmdir(path)
            else:
                for img in os.listdir(path):
                    form = img.split('.')
                    img_path = '%s/%s' % (path, img)
                    real_for = imghdr.what(img_path)
                    if form[-1] is not real_for:
                        os.rename(img_path, '%s/%s.%s' % (path, form[0], real_for))


def word_segment(root):
    directory = 'seg/%s' % get_container_folder(root)
    ut.create_folder(directory)
    files = [f for f in os.listdir(root) if os.path.isfile('%s/%s' % (root, f))]
    total = len(files)
    for index, f in enumerate(files):
        path = '%s/%s' % (root, f)
        content = ut.load_file(path)
        if len(content) >= 3:
            title = content[0].replace('\n', '')
            par = content[2].replace('\n', '')
            title = ViTokenizer.tokenize(unicode(title, 'UTF-8'))
            par = ViTokenizer.tokenize(unicode(par, 'UTF-8'))
            ut.save_file_utf8('%s/%s' % (directory, f), title + '\n' + par)
        ut.update_progress((index + 1) * 1.0 / total)
            

def get_container_folder(path):
    return os.path.basename(os.path.normpath(path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-F", "--folder",
                        help="folder to perform")
    parser.add_argument("-f", "--fr", help="from index", type=int)
    parser.add_argument("-t", "--to", help="to index", type=int)
    parser.add_argument("-re", "--remove_empty", type=int)
    parser.add_argument("-cf", "--format_change", type=int)
    parser.add_argument("-s", "--word_segment", type=int)
    parser.add_argument("-a", "--all", type=int)
    

    args = parser.parse_args()
    if args.remove_empty:
        if args.all:
            for x in os.listdir('./'):
                remove_empty_folder(x)
        else:
            remove_empty_folder(args.folder)
    elif args.format_change:
        if args.all:
            for x in os.listdir('./'):
                remove_empty_folder(x)
        else:
            change_image_format(args.folder)
    elif args.word_segment:
        word_segment(args.folder)
    else: 
        main(args.folder, args.fr, args.to)

