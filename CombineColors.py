from PIL import Image, ImageFont, ImageDraw
import matplotlib.pyplot as plt
import numpy as np
import sys
import copy

colors_default = {
    'cyan': (0, 237, 255), 
    'magenta': (255, 0, 171), 
    'yellow': (255, 237, 0), 
    'red': (255, 0, 0),
    'blue': (0, 71, 171), 
    'green': (0, 181, 0),
    'perano':(167,184,248), # blue with slight purple
    'onahau':(204,238,255), # pale cyan
    'seagull':(136,204,238), # gray cyan
    'deco':(204,221,170), # gray yellow green
    'primerose':(238,238,187), # gray yellow
    'pink':(255,190,204), # pink
    'silver':(190,190,190), # light gray
    'apricot':(238,136,102), # orange
    'teal':(0, 153,136), # dirty cyan
    'cerise':(238,61,119), # violet red
    'purple':(170, 68,153), # Mulberry
    'olive':(170,170,0), # dirty yellow
    'wine':(136,34,85), # dirty pink
    'sundance':(201,181,81), # dirty pear
    'white':(255,255,255),
    'black':(0,0,0),
    'grey':(79,79,79)
}

abbr_dict = {
    'c':'cyan',
    'm':'magenta',
    'y': 'yellow', 
    'r':'red',
    'b':'blue',
    'g':'green',
    'w':'white',
    'd':'black'
}

for a in abbr_dict.keys():
    colors_default[a] = colors_default[abbr_dict[a]]


def CombineColor(pages, pagecolors = {}, bg = 'black', mode = 'layer', palette = {}, addlegend = True, normalize = True, colors_default = colors_default):
    '''
    Combine grayscale channels into one multicolor visualization.
    Returns a PIL image, which can be converted to np array by np.array(image).
    Use colorbar() to see all the colors.
    
    Inputs:
        pages: either a dict {pagename : pagedata}, or a 3d np array stacked along the 3rd axis.
        pagecolors: either a dict {pagename : colorname}, or a list/array of colornames. Channels not assigned colors will be colored automatically.
        bg: background color. Shown when all channels are 0. 
        mode: can be "layer", "blend" or "add".
            layer: overlapped areas shown as the latest channel.
            blend: overlapped areas shown as intermediate colors, as the colors are mixed. 
            add: overlapped areas shown as the added colors, as the colored beams add up as white light.
        palette: a dict {colorname : (r, g, b)}. rgb values are (0, 255). 
        addlegend: bool. whether adding legend at the bottom of the image. default = True.
        normalize: bool. If true, each channel will be independently max-normalized to (0,1) first. default = True.
        colors_default: Default palette. Set it to {} if only using custome colors.
    '''
    pages = copy.deepcopy(pages)
    pagecolors = copy.deepcopy(pagecolors)
    palette = copy.deepcopy(palette)
    colors_default = copy.deepcopy(colors_default)
    # pages_dict {pagename : pagedata}
    if hasattr(pages, 'keys'):
        pages_dict = pages
    elif hasattr(pages, 'shape'):
        pages_dict = {f'{i}': pages[:,:,i] for i in range(pages.shape[2])}
    else:
        raise TypeError("pages must be a dict or a 3D NP array.")
    pagenames = list(pages_dict.keys())
    
    
    # pagecolors {pagename : colorname}
    if not hasattr(pagecolors, 'keys'):
        pagecolors = { pagenames[i]:pagecolors[i] for i in range(len(pagecolors))}
    

    # if pagecolors is given in rgb instead of color names
    for k in pagecolors.keys():
        if not type(pagecolors[k]) == str:
            palette[f'{k}_color_'] = copy.deepcopy(pagecolors[k])
            pagecolors[k] = f'{k}_color_'

    # color_dict {colorname : rgb}
    color_dict = palette
    for c in colors_default.keys():
        if c not in color_dict.keys():
            color_dict[c] =  colors_default[c]
    
    colors = [c for c in list(color_dict.keys()) if c not in list(pagecolors.values()) + ['white','black','w','d']]

    # assign colors to undeclared pages.
    for pagename in pagenames:
        if pagename not in pagecolors.keys():
            pagecolors[pagename] = colors[0]
            colors = colors[1:]

    # pcolor_dict { pagename : rgb }
    for p in pagenames:
        if pagecolors[p] not in color_dict.keys():
            raise KeyError(f'{pagecolors[p]} RGB value not defined.')

    pcolor_dict = { p : color_dict[pagecolors[p]] for p in pagenames}

    # initialize
    im = np.zeros([pages_dict[pagename].shape[0], pages_dict[pagename].shape[1], 3])
    # layover
    
    if mode == 'blend':
        # devided by number of mixed colors at each pixel
        nn = np.dstack(list(pages_dict.values()))
        nn = np.sum(nn>0, axis=2)
        nn = np.where(nn == 0, 1, nn)

    for p in pagenames: # pagename
        D = pages_dict[p] # data
        D = D/max(1, np.max(D)) if normalize else D
        c = pcolor_dict[p] # rgb
        
        if mode =='layer':
            for j in [0,1,2]:
                im[:,:,j] = np.where(D>0, D*c[j], im[:,:,j])
        elif mode == 'blend':
            for j in [0,1,2]:
                im[:,:,j] = im[:,:,j] + D*c[j]/nn
        elif mode == 'add':
            for j in [0,1,2]:
                im[:,:,j] = im[:,:,j] + D*c[j]
        else:
            raise ValueError('mode has to be one of layer, blend or add.')


    if mode == 'add':
        im = np.where(im > 255, 255, im)
    

    bg_mask = np.logical_not(np.any(np.stack([v for v in pages_dict.values()], axis=0), axis=0))
    for j in [0,1,2]:
        im[:,:,j] = np.where(bg_mask, color_dict[bg][j], im[:,:,j])

    
    # im = (im/np.max(im)*255).astype('uint8')
    im = im.astype('uint8')

    Im = Image.fromarray(im)
    if addlegend:
        Im = add_legend(Im, pcolor_dict)
    return Im

def color2rgb(pagecolors = {}, palette = {}, colors_default = colors_default):
    color_d = copy.deepcopy(colors_default)

    for k in palette.keys():
        color_d[k] = palette[k]
    
    # pagecolors {pagename : colorname}
    if not hasattr(pagecolors, 'keys'):
        colors = [color_d[pagecolors[i]] for i in len(pagecolors)]
    else:
        colors = {k:color_d[pagecolors[k]] for k in pagecolors.keys()}

    return colors

    
def add_legend(im, pcolor_dict, bg=(0,0,0)):
    pagenames = list(pcolor_dict.keys())
    width, height = im.size
    '''
    Add colored legend of element names below an image.
    '''
    # select font
    if 'darwin' in sys.platform:
        Fontttf = "Lao Sangam MN.ttf"
    else:
        Fontttf = "arial.ttf"
    
    padding = int(height*0.05)
    fontheight = int(padding*0.7)
    font = ImageFont.truetype(Fontttf, fontheight)

    fulltext = "    ".join(pagenames)
    textwidth = font.getsize(fulltext)[0]
    if textwidth > width:
        padding = int(np.floor(width/textwidth*padding))
        fontheight = int(padding*0.7)
        font = ImageFont.truetype(Fontttf, fontheight)

    new_height = height + padding
    Im_new = Image.new(im.mode, (width, new_height), bg)
    Im_new.paste(im, (0,0))
    draw = ImageDraw.Draw(Im_new)
        
    for i, p in enumerate(pagenames):
        c = pcolor_dict[p]
        x = int(width/len(pagenames)*i + width/len(pagenames)/2 - font.getsize(p)[0]/2)
        draw.text((x, height), p,font=font, fill=c)

    return Im_new

def legendbar(c_dict = colors_default, width = 1):
    n = len(c_dict)
    ims = {}
    for i,k in enumerate(c_dict):
        im = np.zeros((n*width, width))
        im[i*width:(i+1)*width, :] = 1
        ims[k] = im
    im = CombineColor(ims, c_dict, bg = 'w', addlegend=False)
    plt.imshow(im)
    
    plt.tick_params(axis='both', which='both', top=False,
                    bottom=False, left=False, right=False,
                    labelbottom=False, labelleft=False, labelright=True)

    plt.yticks(ticks = width*np.arange(n) + np.floor(0.35*width), labels=list(c_dict.keys()))


def getcolornames( includeAbbr = True):
    if includeAbbr:
        return [c for c in colors_default.keys()]
    else:
        return [c for c in colors_default.keys() if len(c)>1]


def axisoff():
    plt.tick_params(axis='both', which='both', top=False,
                    bottom=False, left=False, right=False,
                    labelbottom=False, labelleft=False)



def whiteframe(COLOR = 'white'):
    for spine in plt.gca().spines.values():
        spine.set_edgecolor(COLOR)