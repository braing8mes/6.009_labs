#!/usr/bin/env python3

from hashlib import new
import math
from operator import invert

from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, x, y): # fixed indexing issue

    return image['pixels'][y*image['width']+x]


def set_pixel(image, x, y, c): # fixed indexing issue

    image['pixels'][y*image['width']+x] = c


def apply_per_pixel(image, func):
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [0]*len(image['pixels']),
    }

    for y in range(image['height']): # swapped iterating variables bc they were wrong
        for x in range(image['width']):
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, x, y, newcolor) # fixed coordinate swap
            
    return result


def inverted(image):
    return apply_per_pixel(image, lambda c: 255-c) # 256 -> 255


# HELPER FUNCTIONS
def get_pixel_better(image, x, y, boundary):
    if 0 <= x < image['width'] and 0<= y < image['height']:
        return image['pixels'][y*image['width']+x]
    elif boundary == 'zero':
        return 0
    elif boundary == 'extend':
        x_val = min(max(x, 0), image['width']-1) # returns the pixel in the image closest to the outside pixel
        y_val = min(max(y, 0), image['height']-1)
        return get_pixel(image, x_val, y_val)
    elif boundary == 'wrap':
        #x_val = min(max(x, 0), image['width']-1) # returns the pixel in the image closest to the outside pixel
        #y_val = min(max(y, 0), image['height']-1)
        return get_pixel(image, x%image['width'], y%image['height']) # mod function returns wrapped pixel
    else:
        return None
def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings 'zero', 'extend', or 'wrap',
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of 'zero', 'extend', or 'wrap', return
    None.

    Otherwise, the output of this function should have the same form as a 6.009
    image (a dictionary with 'height', 'width', and 'pixels' keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE

    Kernel will be an array of arrays so it's 2-D structural integrity can be maintained.
    """
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [0]*len(image['pixels']),
    }
    kernel_height = len(kernel)
    kernel_width = len(kernel[0])
    for y in range(image['height']): 
        for x in range(image['width']):
            total = 0 #sum the inner product
            for x_kernel in range(kernel_width):
                for y_kernel in range(kernel_height):
                    x_p = x - kernel_width//2 + x_kernel #index of pixel to be multiplied in the image
                    y_p = y - kernel_height//2 + y_kernel #index of pixel to be multiplied in the image
                    total += get_pixel_better(image, x_p, y_p, boundary_behavior) * kernel[y_kernel][x_kernel]
            set_pixel(result, x, y, total)
    return result
def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    new_pixels = []
    for i in image['pixels']:
        i = round(min(255, max(0, i))) # set pixel within bounds and then round if it is not an integer
        new_pixels.append(i)
    image['pixels'] = new_pixels
    return image


# FILTERS
def blur_box_maker(n): # helper function to make blur box
    seed = 1/n**2
    return [[seed]*n]*n

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    blur_kernel = blur_box_maker(n)
    
    # then compute the correlation of the input image with that kernel using
    # the 'extend' behavior for out-of-bounds pixels
    result = correlate(image, blur_kernel, 'extend')

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    return round_and_clip_image(result)

def sharpened(image, n):
    """
    Return a new image representing the result of applying a sharpener (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    seed = -1/n**2
    blur_kernel = [[seed]*n for _ in range(n)] #?????????? 
    
    blur_kernel[n//2][n//2] += 2 
    return round_and_clip_image(correlate(image, blur_kernel, 'extend')) # make sure image is valid

def edges(image):
    '''Implement a really neat filter called a Sobel operator, which is useful for detecting edges in images.
    Takes an image as input and returns a new image resulting from the above operations (where the edges should be emphasized)'''
    k_x = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    k_y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
    o_x = correlate(image, k_x, 'extend')
    o_y = correlate(image, k_y, 'extend')
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': [0]*len(image['pixels']),
    }
    for y in range(image['height']): 
        for x in range(image['width']):
            o_xy = math.sqrt(get_pixel_better(o_x, x, y, 'extend')**2 + get_pixel_better(o_y, x, y, 'extend')**2) # add the pixel values together and square root
            set_pixel(result, x, y, o_xy)
    return round_and_clip_image(result) 
# COLOR FILTERS

def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def f(color_image):

        red = {'width': color_image['width'],
        'height': color_image['height'],
        'pixels': [i[0] for i in color_image['pixels']]
        }
        green = {'width': color_image['width'],
        'height': color_image['height'],
        'pixels': [i[1] for i in color_image['pixels']]
        }
        blue = {'width': color_image['width'],
        'height': color_image['height'],
        'pixels': [i[2] for i in color_image['pixels']]
        }
        filt_red = filt(red)
        filt_green = filt(green)
        filt_blue = filt(blue)
        my_list = []
        for i in range(len(color_image['pixels'])):
            my_list.append((filt_red['pixels'][i], filt_green['pixels'][i], filt_blue['pixels'][i])) # recombine tuple
        return {'width': color_image['width'],
        'height': color_image['height'],
        'pixels': my_list}
    return f

def color_swap(image): # my creative project
    '''swaps RGB colors of the photo'''
    init_color = image['pixels']
    new_color = []
    for each in (init_color):
        new_color.append((each[1], each[2], each[0]))
    return {'width': image['width'],
    'height': image['height'],
    'pixels': new_color}

def make_blur_filter(n): # returns function that executes blurred
    def blur(image):
        blur_kernel = blur_box_maker(n)
        result = correlate(image, blur_kernel, 'extend')
        return round_and_clip_image(result)
    return blur

def make_sharpen_filter(n): # returns function that executes sharpened
    def sharpen(image):
        seed = -1/n**2
        blur_kernel = [[seed]*n for _ in range(n)] #??????????
    
        blur_kernel[n//2][n//2] += 2
        return round_and_clip_image(correlate(image, blur_kernel, 'extend'))
    return sharpen

def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def f(image):
        for i in range(len(filters)): # iterate through the filters
            image = filters[i](image)
        return image
    return f


# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_greyscale_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    my_kernel = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    #bluegill_inv = inverted(load_greyscale_image('test_images/bluegill.png'))
    #pigbird_kernel = correlate(load_greyscale_image('test_images/pigbird.png'), my_kernel, 'zero')
    #save_greyscale_image(bluegill_inv, 'bluegill_inv.png')
    #save_greyscale_image(pigbird_kernel, 'pigbird_filtered.png')
    #pigbird_extend = correlate(load_greyscale_image('test_images/pigbird.png'), my_kernel, 'extend')
    #save_greyscale_image(pigbird_extend, 'pigbird_extended.png')
    #pigbird_wrap = correlate(load_greyscale_image('test_images/pigbird.png'), my_kernel, 'wrap')
    #save_greyscale_image(pigbird_wrap, 'pigbird_wrapped.png')
    #blurred_cat = blurred(load_greyscale_image('test_images/cat.png'), 13)
    #save_greyscale_image(blurred_cat, 'blurred_cat.png')
    #blurred_cat_zero = blurred(load_greyscale_image('test_images/cat.png'), 13)
    #save_greyscale_image(blurred_cat_zero, 'blurred_cat_zero.png')
    #blurred_cat_wrap = blurred(load_greyscale_image('test_images/cat.png'), 13)
    #save_greyscale_image(blurred_cat_wrap, 'blurred_cat_wrap.png')
    # python = sharpened(load_greyscale_image('test_images/python.png'),11)
    # save_greyscale_image(python, 'python_sharpened.png')
    # construct = edges(load_greyscale_image('test_images/construct.png'))
    # save_greyscale_image(construct, 'construct_edges.png')

    # color_invert = color_filter_from_greyscale_filter(inverted)
    # invert_cat = color_invert(load_color_image('test_images/cat.png'))
    # save_color_image(invert_cat, 'invert_cat.png')
    # color_blur = color_filter_from_greyscale_filter(make_blur_filter(9))
    # color_sharpen = color_filter_from_greyscale_filter(make_sharpen_filter(7))

    # python = color_blur(load_color_image('test_images/python.png'))
    # sparrow = color_sharpen(load_color_image('test_images/sparrowchick.png'))
    # save_color_image(python, 'python.png')
    # save_color_image(sparrow, 'sparrow.png')
    # filter1 = color_filter_from_greyscale_filter(edges)
    # filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    # filt = filter_cascade([filter1, filter1, filter2, filter1])
    # frog = load_color_image('test_images/frog.png')
    # save_color_image(filt(frog), 'frog.png')
    shroom = load_color_image('test_images/mushroom.png')
    save_color_image(color_swap(shroom), 'shroom_on_shroom.png')