from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import io
from PIL import Image
import time
from math import isnan

def uint(x):
    return (np.array(x)*255).astype('uint8')


def Im2Bytes(Im):
    img_byte_arr = io.BytesIO()
    Im.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr

def axisoff():
    plt.tick_params(axis='both', which='both', top=False,
                    bottom=False, left=False, right=False,
                    labelbottom=False, labelleft=False)
def nonzero(im):
    r = np.ravel(im)
    return r[r>0]

def Im2Bytes(Im):
    img_byte_arr = io.BytesIO()
    Im.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


def cmpixel(im, cmap, cmin = 0, cmax = None):
    cm = plt.get_cmap(cmap)
    if cmax == None or cmax > np.max(im):
        cmax = np.max(im)
    im = im.copy()
    im[im < cmin] = 0
    im[im > cmax] = cmax
    im_n = im/max(np.max(im), 0.00001)
    im_new = np.zeros((im.shape[0], im.shape[1], 3))
    
    c_df = pd.DataFrame(im_n)
    c_df = c_df.stack().reset_index()
    c_vec = cm(c_df.iloc[:,2])
    for j in [0,1,2]:
            im_new[c_df.iloc[:,0], c_df.iloc[:,1], j] = c_vec[:,j]
            im_new[im==0,j] = 0
    return Image.fromarray(uint(im_new))


def cmhist(im, cmap , cmin = 0, cmax = None, bins=128):
    cm = plt.get_cmap(cmap)
    if cmax == None or cmax > np.max(im):
        cmax = np.max(im)
    im = im.copy()
    fig = plt.figure(facecolor=(1,1,1), figsize=(1.5,6))
    if len(nonzero(im))<5:
        n, bins, patches = plt.hist(nonzero(im), bins, orientation="horizontal")
    else:
        n, bins = np.histogram(nonzero(im), bins)
        bin_centers = 0.5 * (bins[:-1] + bins[1:])
        col = bin_centers - min(bin_centers)
        col /= cmax
        col[col>1] = 1.0

    
        plt.barh(bins[:-1], n, height=bins[2]-bins[1], left=-n/2, color=cm(col))

        if cmin:
            plt.axhline(cmin, color = 'blue',linestyle='--')
        if cmax:
            plt.axhline(cmax, color = 'red', linestyle='--')

        plt.ylim(bottom=0, top = np.max(im))
        xlim = np.max(n[np.where(bins>cmin)[0]-1])/2*1.1
        plt.xlim(-xlim, xlim)
    plt.tick_params(axis='both', which='both', top=False,
                        bottom=False, left=False, right=True,
                        labelbottom=False, labelleft=False, labelright=True)
    fig.tight_layout(pad=0.1)
    plt.gca().set_facecolor((0,0,0))

    fig.canvas.draw()
    image_from_plot = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    image_from_plot = image_from_plot.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    Im_hist = Image.fromarray(image_from_plot)
    plt.close()
    return Im_hist

def dualthresh(im, cmin, cmax):
    if cmax == None or isnan(cmax):
        cmax = np.max(im)
    if cmin == None or isnan(cmin):
        cmin = 0
    im = im.copy()
    im[im < cmin] = 0
    im[im > cmax] = cmax
    im = im/max(cmax, 0.00001)
    return im

def overlay(data, fn, m1, rcf, cmin1, cmax1, m2=None, cmin2=None, cmax2=None):
    im1 = rcf(fn = fn, m = m1, data = data)
    im1 = dualthresh(im1, cmin1, cmax1)
    if m2:
        im2 = rcf(fn = fn, m = m2, data = data)
        im2 = dualthresh(im2, cmin2, cmax2)
        im_new = np.dstack((im1, im2, np.zeros_like(im1)))
    else:
        im_new = np.dstack((im1, np.zeros_like(im1), np.zeros_like(im1)))
    im_new = uint(im_new)
    return Image.fromarray(im_new)

def findnotna(df):
    return np.ravel(df.values[np.logical_not(df.isna())])



    

