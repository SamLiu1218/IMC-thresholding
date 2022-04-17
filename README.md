# IMC-thresholding
A GUI for manually setting thresholds for IMC channels


## libraries
Uses ipywidgets for interactive widgets, which comes with anaconda.
No additional packages should be needed.

## example data
An example data set, including 2 rois with 5 channels (CD3  CD68  Melanoma  DNA1  CD45) each, is in eg_data.p

## Usage
There are two thresholds to be set: cmin and cmax.
  - All pixels lower tha cmin will be set to 0.
  - All pixels higher than cmax will be set to cmax.

Use main.ipynb to access the tool. Load your data and modify some custom steps with scripts, then call app.ThresholdGUI() to bring up the GUI.

Control panel is on the right. On the upper right, you can choose the spot, marker, overlaying marker, and colormap.

On the lower right, you can click to switch to next spot or next marker. 

  - "Output Image" will record current thresholds and generate a tiff image. 
  
  - "Output csv" will output thresholds as cmins.csv and cmaxs.csv. Unprocessed channels will remain blank in the table.

On the left is the visualizations.

  - "raw" shows the raw channel. It won't change by thresholds.
  - "thresholded" shows the image after low cut thresholding by cmin and capping by cmax. 
  - "overlay" always shows the current channel in red and the overlaying marker in green. Colormap doesn't apply to overlay view.

In the middle is the selecting area.

  - The histogram shows pixel intensity distributions. Bars are colored by the colormap selected. Blue dash line shows the cmin, red showing cmax.
  - The slide bar is of the same scale as the histogram.
  - Use the text input to change cmin and cmax is more precise and also faster.

The min-list and max-list widgets are just to show the values already set for the current marker across all spots. They are not interactive (yet).

## Tips
Make sure to click "Output image" to record the current thresholds. To record thresholds without generating tiffs, modify the output function.

Switch between "raw" and "thresholded" to check how many pixels are filtered out.

Colormap "hot", "gist_heat" and "afmhot" are all red-to-yellow colormaps, with different progression. 

When a channel is loaded, if the thresholds were recorded it will also load the thresholds. If not, the default thresholds will be 0 and max.
