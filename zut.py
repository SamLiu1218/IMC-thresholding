from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def MyFun():
    print(':)')
    return '?'

def report(str):
    current_time = datetime.now().strftime("%H:%M:%S")
    print(current_time, "  ", str)

def axisoff():
    plt.tick_params(axis='both', which='both', top=False,
                    bottom=False, left=False, right=False,
                    labelbottom=False, labelleft=False)

def newfig(figsize=[12,12], facecolor=[1,1,1]):
    plt.figure(figsize=figsize, facecolor=facecolor)

def CombineColor(im_dict, bg='white', mode='layer'):
    """
    Colors: blue, cyan, green, yellow, red, grey, orange, teal, magenta, purple.
    mode: layer or mix.
    """
    print(len(im_dict))
    color_dict = {
        'blue':[167,184,248],#[187,204,238],
        # 'cyan':[204,238,255],
        'cyan':[136,204,238],
        'green':[204,221,170],
        'yellow':[238,238,187],
        'red':[255,204,204],
        'grey':[190,190,190],
        'white':[255,255,255],
        'black':[0,0,0],
        'orange':[238,136,102],
        'teal':[0, 153,136],
        'magenta':[238,51,119],
        'purple':[170, 68,153],
        'olive':[170,170,0],
        'wine':[136,34,85],
        'pear':[187,204,51]
        }
    im = None
    if mode=='layer':
        for i, c in enumerate(im_dict):
            if i == 0:
                im = np.zeros([im_dict[c].shape[0], im_dict[c].shape[1], 3])
            if c not in color_dict:
                print(f'{c} not valid color.')
                continue
            for j in [0,1,2]:
                im[:,:,j] = im_dict[c]/np.max(im_dict[c])*color_dict[c][j]
    if mode=='mix':
        nn = np.dstack(list(im_dict.values()))
        nn = np.sum(nn>0, axis=2)
        for i, c in enumerate(im_dict):
            if i == 0:
                im = np.zeros([im_dict[c].shape[0], im_dict[c].shape[1], 3])
            if c not in color_dict:
                print(f'{c} not valid color.')
                continue
            for j in [0,1,2]:
                im[:,:,j] = im[:,:,j] + im_dict[c]/np.max(im_dict[c])*color_dict[c][j]/np.where(nn==0, 1, nn)


    bg_mask = np.logical_not(np.any(np.stack([v for v in im_dict.values()], axis=0), axis=0))
    for j in [0,1,2]:
        im[:,:,j] = im[:,:,j] +  bg_mask*color_dict[bg][j]
    return im.astype('uint8'), nn
    # return 0 


def M2E(M):
    '''
    Convert an adjacency matrix to an edge list.
    '''
    df = pd.DataFrame(M)
    df = df.stack().reset_index()
    ls = df.loc[df.iloc[:,2]>0, df.columns[0:2]].values
    return ls



def maskcrop(im, mask=None, padding=None, return_range=False):
    mask = mask.copy()
    im_size = im.shape
    if type(mask)==type(None):
        mask = (im>0)
    mask = mask*1
    
    xleft = np.argwhere(np.any(mask, axis=0))[0][0]
    xright = np.argwhere(np.any(mask, axis=0))[-1][0]

    ytop = np.argwhere(np.any(mask, axis=1))[0][0]
    ybot = np.argwhere(np.any(mask, axis=1))[-1][0]

    if padding == None:
        padding = int(0.05*max(xright-xleft, ybot-ytop))
    xleft = int(max(xleft - padding, 0))
    xright = int(min(xright + padding, im_size[1]))
    ytop = int(max(ytop - padding, 0))
    ybot = int(min(ybot + padding, im_size[0]))
    if len(im.shape) == 3:
        im_new = im[ytop:ybot,xleft:xright,:]
    else:
        im_new = im[ytop:ybot,xleft:xright]
    if return_range:
        return im_new, [ytop,ybot,xleft,xright]
    else:
        return im_new

