from math import isnan
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import pickle
import ipywidgets as widgets
from IPython.display import display
from datetime import datetime
from helper_functions import *

class ThresholdGUI:
    def __init__(self, data, fn_ls, markers, func_dict, outdir, cmins_table=None, cmaxs_table=None):
        self.data = data
        self.fn_ls = fn_ls
        self.markers = markers
        self.outdir = outdir
        self.rcf = func_dict['readchannel']
        self.stf = func_dict['savetiff']
        self.cmins = cmins_table if not type(cmaxs_table) == type(None) else pd.DataFrame(index=fn_ls, columns=markers)
        self.cmaxs = cmaxs_table if not type(cmaxs_table)  == type(None) else pd.DataFrame(index=fn_ls, columns=markers)
        self.cur_im = {}
        self.cur_hist = {}
        self.cur_raw = {}
        self.cur_overlay = {}
        self.flag_update = True
        # for fn in fn_ls:
        #     for m in markers:
        #         if isnan(self.cmaxs.loc[fn,m]):
        #             self.cmaxs.loc[fn,m] = np.max(self.rcf(data=self.data, fn=fn, m=m))
        
        
        # Selectbox

        self.drop_fn = widgets.Dropdown(
            description='Spot',
            options = fn_ls,
            value = fn_ls[0],
            style={'description_width': 'initial'},
            layout={'width': 'initial'}
        )
        self.drop_filter = widgets.Dropdown(
            description = 'Filter',
            options = ["All", "unprocessed" ,"processed"],
            value = "All",
            style={'description_width': 'initial'},
            layout={'width': 'initial'}
        )
        self.drop_m = widgets.Dropdown(
            description='Marker',
            options = markers,
            value = markers[0],
            style={'description_width': 'initial'},
            layout={'width': 'initial'}
        )
        self.drop_overlay = widgets.Dropdown(
            description='overlay',
            options = [None] + markers,
            value = None,
            style={'description_width': 'initial'},
            layout={'width': 'initial'}
        )
        self.drop_cmap = widgets.Dropdown(
            description='cmap',
            options = ['hot','afmhot','gist_heat','viridis','plasma','inferno'],
            value = 'hot',
            style={'description_width': 'initial'},
            layout={'width': 'initial'}
        )
        box_select = widgets.VBox((self.drop_fn, self.drop_m, self.drop_overlay, self.drop_cmap),
            layout = widgets.Layout(display='flex',
                        flex_flow='column',
                        align_items='initial',
                        width='100%')
        )


        # tab_im

        self.w_im = widgets.Image()

        self.w_raw = widgets.Image()

        self.w_overlay = widgets.Image()

        tab_im = widgets.Tab()
        tab_im.children = [self.w_raw, self.w_im, self.w_overlay]
        for i,v in enumerate( ['Raw','Thresholded', 'Overlay']):
            tab_im.set_title(i, v)
        tab_im.selected_index = 1


        # range box

        self.w_hist = widgets.Image()
        self.slide_range = widgets.FloatRangeSlider(
            label='t',
            value=(0,4), 
            min=0, 
            max=4, 
            step=0.01, 
            continuous_update=True, 
            readout=False,
            orientation = 'vertical',
            layout=widgets.Layout(height='600px', width='auto')
        )
        
        self.text_cmin = widgets.FloatText(
            value=0,
            step = 0.2,
            description='Min:',
            style={'description_width': 'initial'},
            layout=widgets.Layout( width='auto')
        )
        self.text_cmax = widgets.FloatText(
            value=0,
            step = 0.2,
            description='Max:',
            style={'description_width': 'initial'},
            layout=widgets.Layout( width='auto')
        )

    


        # range history

        self.select_cmin = widgets.Select(
            options=[0],
            description='Min list:',
            disabled=False,
            style={'description_width': 'initial'},
            layout=widgets.Layout( width='auto')
        )

        self.select_cmax = widgets.Select(
            options=["Max"],
            description='Max lst:',
            disabled=False,
            style={'description_width': 'initial'},
            layout=widgets.Layout( width='auto')
        )


        # control panel
        self.button_nextslide = widgets.Button(
            description='Next spot',
            disabled=False,
            button_style='', 
            tooltip='Go to current marker in next spot.',
            icon='angle_down' ,
            style={'description_width': 'initial'},
            layout={'width': 'initial'}
        )

        self.button_nextmarker = widgets.Button(
            description='Next marker',
            disabled=False,
            button_style='', 
            tooltip='Go to next marker in current spot.',
            icon='angle_right',
            style={'description_width': 'initial'},
            layout={'width': 'initial'}
        )

        self.button_exportimage = widgets.Button(
            description='Output Image',
            disabled=False,
            button_style='success',
            tooltip='Save thresholds and output current channel.',
            icon='image',
            style={'description_width': 'initial'},
            layout={'width': 'initial'}
        )

        self.button_exporttable = widgets.Button(
            description='Output csv',
            disabled=False,
            button_style='success', 
            tooltip='Export thresholds in csv.',
            icon='table' ,
            style={'description_width': 'initial'},
            layout={'width': 'initial'}
        )

        self.label_report = widgets.Label()

        box_buttons = widgets.VBox((self.button_nextslide, self.button_nextmarker, self.button_exportimage, self.button_exporttable))
        App = widgets.GridspecLayout(10, 15, height='auto',align_items='center')
        App[:,:9] = tab_im
        App[1:9,9:11] = self.w_hist
        App[1:9,11] = self.slide_range
        App[0,9:12] = self.text_cmax
        App[9,9:12] = self.text_cmin

        App[3:7, 13:15] = widgets.VBox((self.select_cmin, self.select_cmax))
        App[0:3,13:15] = box_select
        App[7:10,13:15] = box_buttons

        
        self.App = widgets.VBox((App, self.label_report))
        display(self.App)


        
        def cbk_drop_fn(change):
            if change['type'] == 'change' and change['name'] == 'value':
            
                fn = self.drop_fn.value
                m = self.drop_m.value
                im  = self.rcf(data=self.data, fn=fn, m=m)
                self.slide_range.max = np.max(im)
                cmin = self.cmins.loc[fn, m] if not isnan(self.cmins.loc[fn, m]) else 0
                cmax = self.cmaxs.loc[fn, m] if not isnan(self.cmaxs.loc[fn, m]) else self.slide_range.max
                self.slide_range.value = (cmin, cmax)

                # update_im()
                self.update_raw()
                # update_overlay()
                # update_hist()
                self.report('ROI changed. Ready.')
        
        def cbk_drop_filter( *args):  
            fn = self.drop_fn.value
            if self.drop_filter.value == 'All':
                self.drop_m.options = self.markers
            else:
                if len(self.drop_m.options) > 1:
                    idx = np.where(self.cmins.loc[fn,:].isna())
                    if len(idx) > 1:
                        self.drop_m.options = self.markers[idx]
                        self.drop_m.value = self.drop_m.options[0]
            self.report('Filter changed. Ready.')

        def cbk_drop_m(change):
                if change['type'] == 'change' and change['name'] == 'value':
                    fn = self.drop_fn.value
                    m = self.drop_m.value
                    im  = self.rcf(data=self.data, fn=fn, m=m)
                    self.update_histories()
                    self.slide_range.max = np.max(im)
                    cmin = self.cmins.loc[fn, m] if not isnan(self.cmins.loc[fn, m]) else 0
                    cmax = self.cmaxs.loc[fn, m] if not isnan(self.cmaxs.loc[fn, m]) else self.slide_range.max
                    self.slide_range.value = (cmin, cmax)
                    self.text_cmin.value = cmin
                    self.text_cmax.value = cmax
                    self.update_raw()
                    self.report('Marker changed. Ready.')

        def cbk_drop_overlay(change):
            if change['type'] == 'change' and change['name'] == 'value':
                self.update_overlay()
                self.report('Overlay updated. Ready.')

        def cbk_drop_cmap(change):
            if change['type'] == 'change' and change['name'] == 'value':
                
                self.update_im()
                self.update_raw()
                self.update_hist()
                self.report('Colormap changed. Ready.')

        def cbk_slide_range(change):
            if change['type'] == 'change' and change['name'] == 'value':
                self.text_cmin.value = self.slide_range.value[0]
                self.text_cmax.value = self.slide_range.value[1]
                self.slide2histories()
                self.update_im()
                self.update_overlay()
                self.update_hist()
                self.report('Thresholds changed. Ready.')

        def cbk_text_cmin(*args):
            self.slide_range.value = (self.text_cmin.value, self.text_cmax.value)

        def cbk_text_cmax(*args):
            self.slide_range.value = (self.text_cmin.value, self.text_cmax.value)
        

        def cbk_select_cmin(change):
            if change['type'] == 'change' and change['name'] == 'value':
                if not self.select_cmin.value == None:
                    self.slide_range.value = (self.select_cmin.value, self.text_cmax.value) 

        def cbk_select_cmax(change):
            if change['type'] == 'change' and change['name'] == 'value':
                if not self.select_cmax.value == None:
                    if self.select_cmax.value == "Max":
                        self.slide_range.value = (self.text_cmin.value, self.slide_range.max)
                    else:
                        self.slide_range.value = (self.text_cmin.value, float(self.select_cmax.value))

        def cbk_button_nextslide( *args):
            if self.drop_fn.index < len(self.drop_fn.options)-1:
                self.drop_fn.index += 1
            else:
                self.drop_fn.index = 0
                self.report('Jumped back to first spot. Ready.')

        def cbk_button_nextmarker( *args):
            if self.drop_m.index < len(self.drop_m.options)-1:
                self.drop_m.index += 1
            else:
                self.drop_m.index = 0
                self.report('Jumped back to first marker. Ready.')

        def cbk_button_exportimage( *args):
            try:
                self.report('Recording thresholds and outputing tiff file ...')
                fn = self.drop_fn.value
                m = self.drop_m.value
                im  = self.rcf(data=self.data, fn=fn, m=m)
                (cmin, cmax) = self.slide_range.value
                self.cmins.loc[fn,m] = cmin
                if cmax < np.max(im):
                    self.cmaxs.loc[fn,m] = cmax
                self.stf(fn, m, im, cmin, cmax, self.outdir)
                self.report(f'Outputed at {os.path.join(outdir,fn,f"{m}.tiff")}. Ready.')
                self.update_histories()
            except Exception as e:
                self.report(e)


        def cbk_button_exporttable( *args):
            self.cmins.to_csv(os.path.join(outdir,'cmins.csv'))
            self.cmaxs.to_csv(os.path.join(outdir,'cmaxs.csv'))
            self.report(f'cmins and cmaxs exported as csv at {outdir}.')


        
        # initialization
        fn = self.drop_fn.value
        m = self.drop_m.value
        im  = self.rcf(data=self.data, fn=fn, m=m)
        self.slide_range.max = np.max(im)
        cmin = self.cmins.loc[fn, m] if not isnan(self.cmins.loc[fn, m]) else 0
        cmax = self.cmaxs.loc[fn, m] if not isnan(self.cmaxs.loc[fn, m]) else self.slide_range.max
        self.slide_range.value = (cmin, cmax)

        self.text_cmin.value = self.slide_range.value[0]
        self.text_cmax.value = self.slide_range.value[1]

        self.update_im()
        self.update_raw()
        self.update_overlay()
        self.update_hist()
        self.update_histories()

        
        self.slide_range.observe(cbk_slide_range,names='value')
        self.text_cmax.observe(cbk_text_cmax)
        self.text_cmin.observe(cbk_text_cmin)
        self.drop_fn.observe(cbk_drop_fn)
#         self.drop_filter.observe(cbk_drop_filter)
        self.drop_m.observe(cbk_drop_m)
        self.drop_overlay.observe(cbk_drop_overlay)
        self.drop_cmap.observe(cbk_drop_cmap)
        self.select_cmin.observe(cbk_select_cmin)
        self.select_cmax.observe(cbk_select_cmax)
        self.button_exportimage.on_click(cbk_button_exportimage)
        self.button_exporttable.on_click(cbk_button_exporttable)
        self.button_nextmarker.on_click(cbk_button_nextmarker)
        self.button_nextslide.on_click(cbk_button_nextslide)

        self.slide2histories()

    def update_im(self, *args):
        self.report('Updating thresholded image...')
        fn = self.drop_fn.value
        m = self.drop_m.value
        self.w_im.value = Im2Bytes(cmpixel(
            self.rcf(data=self.data, fn=fn, m=m), 
            cmap = self.drop_cmap.value, 
            cmin = self.slide_range.value[0],
            cmax = self.slide_range.value[1]))
        self.w_im.layout.width = 'auto'
        self.report('Ready.')

    def update_raw(self, *args):
        self.report('Updating raw image...')
        fn = self.drop_fn.value
        m = self.drop_m.value
        self.w_raw.value = Im2Bytes(cmpixel(
            self.rcf(data=self.data, fn=fn, m=m), 
            cmap=self.drop_cmap.value, 
            cmin = 0,
            cmax = None))
        self.w_raw.layout.width = 'auto'
        self.report('Ready.')

    def update_overlay(self, *args):
        self.report('Updating overlay image...')
        fn = self.drop_fn.value
        m = self.drop_m.value
        if self.drop_overlay.value:
            m2 = self.drop_overlay.value
            self.w_overlay.value = Im2Bytes(overlay(
                    data = self.data, fn=fn,
                    m1=m, m2=m2,
                    cmin1 = self.slide_range.value[0],
                    cmin2 =  self.cmins.loc[fn, m2],
                    cmax1 = self.slide_range.value[1],
                    cmax2 = self.cmaxs.loc[fn, m2],
                    rcf = self.rcf
                    ))
        else:
            self.w_overlay.value = Im2Bytes(overlay(
                    data = self.data, fn=fn,
                    m1=m, 
                    cmin1 = self.slide_range.value[0],
                    cmax1 = self.slide_range.value[1],
                    rcf = self.rcf
                    ))
        self.report('Ready.')

    def update_hist(self, *args):
        self.report('Updating histogram...')
        fn = self.drop_fn.value
        m = self.drop_m.value
        self.w_hist.value = Im2Bytes(cmhist(
            self.rcf(data=self.data, fn=fn, m=m), 
            cmap=self.drop_cmap.value, 
            cmin = self.slide_range.value[0],
            cmax = self.slide_range.value[1]))    
        self.w_hist.layout.width = 'auto'
        self.w_hist.layout.height = '600px'
        self.report('Ready.')

    def update_histories(self, *args):
        self.report('Updating histories...')
        m = self.drop_m.value
        self.select_cmin.options = np.concatenate([[0], np.sort(findnotna(self.cmins[m]))])        
        if self.slide_range.value[0] in self.select_cmin.options:
            self.select_cmin.value = self.slide_range.value[0]
        else:            
            self.select_cmin.value = None

        self.select_cmax.options = np.concatenate([["Max"], np.sort(findnotna(self.cmaxs[m]))[::-1]])
        if self.slide_range.value[1] == self.slide_range.max:
            self.select_cmax.value = "Max"
        elif str(self.slide_range.value[1]) in self.select_cmax.options:
            self.select_cmax.value = str(self.slide_range.value[1])
        else:            
            self.select_cmax.value = None
        self.report('Ready.')

    def report(self, msg):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.label_report.value = f'{current_time}     {msg}'

    def getcur(self):
        return {'fn': self.drop_fn.value, 'm': self.drop_m.value, 'cmap':self.drop_cmap.value, 'overlay':self.drop_overlay.value, 'cmin':self.slide_range.value[0], 'cmax':self.slide_range.value[1]}

    def slide2histories(self):
        if self.slide_range.value[0] in self.select_cmin.options:
            self.select_cmin.value = self.slide_range.value[0]
        else:            
            self.select_cmin.value = None

        if self.slide_range.value[1] == self.slide_range.max:
            self.select_cmax.value = "Max"
        elif str(self.slide_range.value[1]) in self.select_cmax.options:
            self.select_cmax.value = str(self.slide_range.value[1])
        else:            
            self.select_cmax.value = None
