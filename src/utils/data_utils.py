import numpy as np
from PIL import Image
import time


def render(arr):
    """
    Render an array as an image
    Args:
        arr: np array (np.uint8) representing an image
    """
    img = Image.fromarray(arr)
    img.show()


def get_max_shape(arrays):
    """
    Args:
        images: list of arrays
    """
    shapes = map(lambda x: list(x.shape), arrays)
    ndim = len(arrays[0].shape)
    max_shape = []
    for d in range(ndim):
        max_shape += [max(shapes, key=lambda x: x[d])[d]]

    return max_shape


def pad_batch_images(images):
    """
    Args:
        images: list of arrays
    """

    # 1. max shape
    max_shape = get_max_shape(images)

    # 2. apply formating
    batch_images = 255 * np.ones([len(images)] + list(max_shape))
    for idx, img in enumerate(images):
        batch_images[idx, :img.shape[0], :img.shape[1]] = img

    return batch_images.astype(np.uint8)


def pad_batch_formulas(formulas):
    """
    Args:
        formulas: (list) of list of ints
    Returns:
        array: of shape = (batch_size, max_len) of type np.int32
    """
    max_len = max(map(lambda x: len(x), formulas))
    batch_formulas = np.zeros([len(formulas), max_len], dtype=np.int32)
    for idx, formula in enumerate(formulas):
        batch_formulas[idx, :len(formula)] = np.asarray(formula, dtype=np.int32)

    return batch_formulas


def minibatches(data_generator, minibatch_size):
    """
    Args:
        data_generator: generator of (img, formulas) tuples
        minibatch_size: (int)
    Returns: 
        list of tuples
    """
    x_batch, y_batch = [], []
    for (x, y) in data_generator:
        if len(x_batch) == minibatch_size:
            yield x_batch, y_batch
            x_batch, y_batch = [], []

        x_batch += [x]
        y_batch += [y]

    if len(x_batch) != 0:
        yield x_batch, y_batch


def load_vocab(filename):
    """
    Args:
        filename: (string) path to vocab txt file one word per line
    Returns:
        dict: d[token] = id
    """
    vocab = dict()
    with open(filename) as f:
        for idx, token in enumerate(f):
            token = token.strip()
            vocab[token] = idx

    return vocab