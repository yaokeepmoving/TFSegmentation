import numpy as np
import h5py
import argparse
import os
from scipy import misc
import matplotlib.pyplot as plt
from tqdm import tqdm

import pdb


def readCityScapes(hf, path_images, path_labels, args, split='train'):
    names = []
    for root, dirs, files in os.walk(path_images):
        for f in sorted(files):
            if f.split('.')[-1].lower() == 'png':
                names.append(f)
                temp = root
            else:
                continue
    print("number of found images in \n %s \n is %s" % (path_images, len(names)))

    hf.create_dataset('names_' + split, data=names)
    img = misc.imread(temp + '/' + names[-1])
    h, w, c = img.shape
    if args.rescale is not None:
        h = int(h * args.rescale)
        w = int(w * args.rescale)
    shape = (len(names), c, h, w)

    pdb.set_trace()
    image_dset = hf.create_dataset('images_' + split, shape, dtype=np.uint8)
    i = 0
    for root, dirs, files in os.walk(path_images):
        for f in sorted(files):
            if f.split('.')[-1].lower() == 'png':
                img = misc.imread(root + '/' + f)
                if args.rescale is not None:
                    img = misc.imresize(img, (h, w))
                    plt.imshow(img)
                    plt.show()
                    img = img.transpose(2, 0, 1)
                if img.shape != (c, h, w):
                    print("an image is skipped due to inconsistet shape with %s" % str(img.shape))
                    continue
                image_dset[i, :c, :h, :w] = img
                i = i + 1
                if i % 100 == 1:
                    print("%sth image has processed" % (str(i)))

    print("%s images have processes in total" % str(i))

    shape = (len(names), h, w)
    image_dset = hf.create_dataset('labels_' + split, shape, dtype=np.uint8)
    i = 0
    for root, dirs, files in os.walk(path_labels):
        for f in sorted(files):
            if f.split('.')[-1].lower() == 'png' and 'labelIds' in f:
                img = misc.imread(root + '/' + f)
                if args.rescale is not None:
                    img = misc.imresize(img, (h, w))
                if img.shape != (h, w):
                    print("an image is skipped due to inconsistet shape with %s" % str(img.shape))
                    continue
                image_dset[i, :h, :w] = img
                if i % 100 == 1:
                    print("%sth label has processed" % (str(i)))
                i = i + 1
    print("%s labels was processesed in total" % str(i))


def main(args):
    hf = h5py.File(args.output_file, 'w')
    train_images_path = args.root + 'leftImg8bit/train/darmstadt'
    train_labels_path = args.root + 'gtCoarse/train/darmstadt'
    valid_images_path = args.root + 'leftImg8bit/val/lindau'
    valid_labels_path = args.root + 'gtCoarse/val/lindau'
    readCityScapes(hf, train_images_path, train_labels_path, args, split='train')
    readCityScapes(hf, valid_images_path, valid_labels_path, args, split='valid')
    hf.close()


def custom_read_cityscape(hf, path_images, path_labels, args_, split='train'):
    names = []
    root = path_images

    # Read all image files in the path_images directory
    for root, dirs, files in os.walk(path_images):
        for f in sorted(files):
            if f.split('.')[-1].lower() == 'png':
                names.append(f)
            else:
                continue

    # Print statistics
    print("number of found images in \n %s is %s img" % (path_images, len(names)))
    print(root)

    # read an image to get the shape
    img = misc.imread(root + '/' + names[-1])
    h, w, c = img.shape

    # rescale the shape
    if args_.rescale is not None:
        h = int(h * args_.rescale)
        w = int(w * args_.rescale)
    shape = (len(names), h, w, c)
    print("Shape of images is %s" % (str(shape)))

    # Create a dataset for images
    image_dataset = hf.create_dataset('images_' + split, shape, dtype=np.uint8)

    # loop on images and scale and save
    i = 0
    for f in tqdm(names):
        img = misc.imread(root + '/' + f)
        if args_.rescale is not None:
            img = misc.imresize(img, (h, w))
        if img.shape != (h, w, c):
            print("an image is skipped due to inconsistet shape with %s" % str(img.shape))
            continue
        image_dataset[i, :h, :w, :c] = img
        i = i + 1

    print("%s images have processes in total" % str(i))

    shape = (len(names), h, w)
    print("Shape of labels is %s" % (str(shape)))

    # Read all image files in the path_images directory
    names = []
    for root, dirs, files in os.walk(path_labels):
        for f in sorted(files):
            if f.split('.')[-1].lower() == 'png' and 'labelIds' in f:
                names.append(f)
            else:
                continue

    # Create a dataset for labels
    image_dataset = hf.create_dataset('labels_' + split, shape, dtype=np.uint8)
    root = path_labels
    i = 0
    for f in tqdm(names):
        img = misc.imread(root + '/' + f)
        if args_.rescale is not None:
            img = misc.imresize(img, (h, w))
        if img.shape != (h, w):
            print("an image is skipped due to inconsistent shape with %s" % str(img.shape))
            continue
        image_dataset[i, :h, :w] = img
        i = i + 1
    print("%s labels was processed in total" % str(i))


def custom_main(args_):
    hf = h5py.File(args_.output_file, 'w')
    train_images_path = args_.root + 'images/aachen'
    train_labels_path = args_.root + 'labels/aachen'
    custom_read_cityscape(hf, train_images_path, train_labels_path, args_, split='train')
    hf.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default='/data/cityscapes/',
                        help='path to the dataset root that includes leftImg8bit_trainextra leftImg8bit_valid/train and gtCoarse')
    parser.add_argument("--rescale", default=0.25, type=float,
                        help="rescale ratio. eg --rescale 0.5")
    parser.add_argument("--output_file", default='leftImg8bit_extra.h5',
                        help="output file for the h5 dataset.")
    parser.add_argument("--mode", default="normal", help="Mode of preparation")
    args = parser.parse_args()
    if args.mode == "normal":
        main(args)
    elif args.mode == "custom":
        custom_main(args)
    else:
        print("Please choose a proper mode first THANKS.")
        exit(-1)
