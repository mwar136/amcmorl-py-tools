import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.axes_grid import AxesGrid
import warnings
from scipy import stats
from matplotlib.colors import ColorConverter

import scipy.signal as signal
from scipy.stats import norm
import matplotlib.font_manager as fm

def no_clip(ax): 
     "Turn off all clipping in axes ax; call immediately before drawing" 
     ax.set_clip_on(False) 
     artists = [] 
     artists.extend(ax.collections) 
     artists.extend(ax.patches) 
     artists.extend(ax.lines) 
     artists.extend(ax.texts) 
     artists.extend(ax.artists) 
     for a in artists: 
         a.set_clip_on(False)

def fill_between(x, y1, y2=0, ax=None, **kwargs):
    """Plot filled region between `y1` and `y2`.

    This function works exactly the same as matplotlib's fill_between, except
    that it also plots a proxy artist (specifically, a rectangle of 0 size)
    so that it can be added it appears on a legend.
    """
    ax = ax if ax is not None else plt.gca()
    ax.fill_between(x, y1, y2, **kwargs)
    p = plt.Rectangle((0, 0), 0, 0, **kwargs)
    ax.add_patch(p)
    return p

def format_spines(ax, which=[], hidden_color='none',
                  position=('outward', 5)):
    '''
    Convenience function for formatting spines of a plot.

    Parameters
    ----------
    ax : matplotlib axis
    which : list of strings
      names of spines (defined by matplotlib axes object) to format
    hidden_color : string
      any matplotlib color specification
    '''
    for loc, spine in ax.spines.iteritems():
        if loc in which:
            spine.set_visible(True) # in case it was hidden previously
            spine.set_position(position)
        else:
            if hidden_color != 'none':
                spine.set_color(hidden_color)
            else:
                spine.set_visible(False)

    if 'bottom' in which:
        ax.xaxis.set_ticks_position('bottom')
    elif ('top' in which) and not ('bottom' in which):
        ax.xaxis.set_ticks_position('top')
    else:
        ax.xaxis.set_ticks_position('none')
        for label in ax.get_xticklabels():
            label.set_visible(False)

    if 'left' in which:
        ax.yaxis.set_ticks_position('left')
    elif 'right' in which:
        ax.yaxis.set_ticks_position('right')
    else:
        ax.yaxis.set_ticks_position('none')
    if ('left' in which) or ('right' in which):
        for label in ax.get_yticklabels():
            label.set_visible(True)
    else:
        for label in ax.get_yticklabels():
            label.set_visible(False)

lighten = lambda x : tuple([c + (1 - c) * 0.5 \
    for c in ColorConverter().to_rgb(x)])

darken = lambda x : tuple([c * 0.5 \
    for c in ColorConverter().to_rgb(x)])

def label_subplot_spec(subplot_spec, fig, text, x=0, **kwargs):
    x = x
    y0 = subplot_spec.get_position(fig).y0
    y1 = subplot_spec.get_position(fig).y1
    y = (y0 + y1) / 2.
    kwargs.setdefault('rotation', 90)
    fig.text(x, y, text, **kwargs)

###############################################################################
# make_xkcd, from https://gist.github.com/3874297
###############################################################################

def rand_func(data):
    """ multiply data by low-pas filtered random values 
        data - input data array
    """
    length = np.size(data)
    coeffs = norm.rvs(loc=0, scale=1e-2, size=length) # random values
    b = signal.firwin(2., min(1, 9./length))
    # use low pass filter to smooth variations
    response = signal.lfilter(b, 1, coeffs) + 1 
    return data * response

def make_xkcd(ax, x_label='', y_label=''):
    """ make an xkcd style plot
        ax - axis element
        x_label, y_label - optional text for x and y axis
    """

    # add randomness to x and y of plotted lines
    pltlist = ax.get_lines()
    for p in pltlist:
        x = p.get_xdata()
        y = p.get_ydata()
        x = rand_func(x)
        y = rand_func(y)
        p.set_xdata(x)
        p.set_ydata(y)

    ax.axison = False
    # get boundaries for x and y axis
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    xsize = xmax - xmin
    ysize = ymax - ymin
    # Increase figure size to fit new custom axes
    border = 10. # border size
    xmin  -= xsize / border
    xmax  += xsize / border
    ymin  -= ysize / border
    ymax  += ysize / border
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    
    # Poor man's x-axis
    xlen  = np.size(x)
    xaxis = np.linspace(xmin, xmax - xsize / border, xlen)
    yaxis = rand_func([ysize] * xlen) - ysize + ymin + ysize / border
    ax.plot(xaxis, yaxis, 'k', lw=2)
    ax.arrow(xaxis[-1], yaxis[-1], 1e-6, 0, fc='k', lw=2, \
        head_width=ysize / 30, head_length=xsize / border)

    # Poor man's y-axis
    xaxis = rand_func([xsize] * xlen) - xsize + xmin + xsize / border
    yaxis = np.linspace(ymin, ymax - ysize / border, xlen) 
    ax.plot(xaxis, yaxis, 'k', lw=2)
    ax.arrow(xaxis[-1], yaxis[-1], 0, 1e-6, fc='k', lw=2, \
        head_width=xsize / 40, head_length=ysize / border);
    
    # Add axis description text
    # The font is available here: http://antiyawn.com/uploads/Humor-Sans.ttf
    prop = fm.FontProperties(fname='/home/amcmorl/lib/Humor-Sans.ttf')
    a = ax.text(xmax, ymin, x_label, fontproperties=prop, size=14,\
        rotation=2, horizontalalignment='right')
    ax.text(xmin, ymax, y_label, fontproperties=prop, size=14, \
        rotation=88, verticalalignment='top');

###############################################################################
# less used stuff below this line 
###############################################################################


def plot_scatter_with_lst_sq_line(x, y, ax=None, xlabel='', ylabel='', title='', ppos=(0.5,0.5)):
    # fit a line of best fit (but use P value from non-parametric correlation measure
    rho, pcor = stats.spearmanr(x, y)
    m, c, r, plin_reg, e = stats.linregress(x, y)
    lnx = np.linspace(np.min(x), np.max(x), 100)
    lny = m * lnx + c
    
    if ax == None:
        fig = plt.figure(figsize=(10,6))
        ax = fig.add_subplot(111)
    else:
        fig = ax.figure
    ax.plot(x, y, 'ko', ms=8)
    ax.plot(lnx, lny, 'k-')
    #aspect = (np.abs(np.diff(ax.get_xlim())) / np.abs(np.diff(ax.get_ylim()))).item()
    #print np.degrees(np.arctan(m * aspect))
    ax.text(ppos[0], ppos[1],r'm=%.2f P=%.4f' % (rho, plin_reg), transform=ax.transAxes)
    format_spines(ax, which=['left', 'bottom'], position=('outward', 5))
    if len(xlabel) > 0:
        ax.set_xlabel(xlabel)
    if len(ylabel) > 0:
        ax.set_ylabel(ylabel)
    if len(title) > 0:
        ax.set_title(title)
    return ax

def plot_scatter(x, y, ax=None, xlabel='', ylabel='', title='', **kwargs):
    if ax == None:
        fig = plt.figure(figsize=(10,6))
        ax = fig.add_subplot(111)
    else:
        fig = ax.figure
        
    # set some sensible defaults
    kwargs.setdefault('ms', 8)
    
    ax.plot(x, y, 'ko', **kwargs)
    format_spines(ax, which=['left', 'bottom'], position=('outward', 5))
    if len(xlabel) > 0:
        ax.set_xlabel(xlabel)
    if len(ylabel) > 0:
        ax.set_ylabel(ylabel)
    if len(title) > 0:
        ax.set_title(title)
    return ax

#~ class Margins:
    #~ def __init__(self, left=0, bottom=0, right=0, top=0, hgap=0, vgap=0):
        #~ warnings.warn("Use matplotlib.gridspec.GridSpec instead.", DeprecationWarning)
        #~ self.left = left
        #~ self.bottom = bottom
        #~ self.right = right
        #~ self.top = top
        #~ self.hgap = hgap
        #~ self.vgap = vgap
#~ 
    #~ def __str__(self):
        #~ str = "Left: %s\n" % (self.left)
        #~ str += "Bottom: %s\n" % (self.bottom)
        #~ str += "Right: %s\n" % (self.right)
        #~ str += "Top: %s\n" % (self.top)
        #~ str += "Horizontal gap: %s\n" % (self.hgap)
        #~ str += "Vertical gap: %s" % (self.vgap)
        #~ return str 
#~ 
    #~ def get_rect(self):
        #~ return [self.left, self.bottom,
                #~ 1 - self.right - self.left, 1 - self.top - self.bottom]
#~ 
    #~ def set_from_rect(self, rect, total_width=1, total_height=1):
        #~ self.left = rect[0]
        #~ self.bottom = rect[1]
        #~ width = rect[2]
        #~ height = rect[3]
        #~ self.right = total_width - width - self.left
        #~ self.top = total_height - height - self.bottom
#~ 
#~ def make_margin_from_rect(rect, hgap=0, vgap=0,
                          #~ total_width=1, total_height=1):
    #~ warnings.warn("Use matplotlib.gridspec.GridSpec instead.", DeprecationWarning)
    #~ left = rect[0]
    #~ bottom = rect[1]
    #~ width = rect[2]
    #~ height = rect[3]
    #~ right = total_width - width - left
    #~ top = total_height - height - bottom
   #~ return Margins(left, bottom, right, top, hgap, vgap)

def make_enough_rows(total, cols):
    rows = int(total / cols)
    extra = int(total % cols)
    if extra > 0:
        rows += 1
    return rows

#~ def get_ax_rect(i_ax, ncols, nrows, margin=Margins(), direction='row'):
    #~ '''Calculate rect values for axis.
    #~ '''
    #~ i_axs = np.array(i_ax)
    #~ axs = get_ax_rect(i_axs, ncols, nrows, margin=margin, direction=direction)
    #~ return axs[0]

def get_col_row(i, ncols, nrows, direction):
    warnings.warn("Use np.unravel_index instead.", DeprecationWarning)
    if direction == 'row':
        ncol = i % ncols
        nrow = i / ncols
    if direction == 'col':
        ncol = i / nrows
        nrow = i % nrows
    return ncol, nrow

#~ def get_ax_rects(i_axs, ncols, nrows, margin=Margins(), direction='row'):
    #~ '''Calculate rect values for several axes.
    #~ '''        
    #~ i_axs = np.asarray(i_axs)
    #~ assert direction in ['row', 'col']
    #~ #print "m.left", margin.left, "m.right", margin.right
    #~ w = (1 - (margin.left + margin.right + \
                  #~ (ncols - 1) * margin.hgap)) / float(ncols)
    #~ h = (1 - (margin.bottom + margin.top + \
                  #~ (nrows - 1) * margin.vgap)) / float(nrows)
    #~ #print "W", w, "H", h, "ncols", ncols
    #~ ncol, nrow = get_col_row(i_axs, ncols, nrows, direction)
    #~ l = margin.left + ncol * (w + margin.hgap)
    #~ b = margin.bottom + (nrows - nrow - 1) * (h + margin.vgap)
    #~ ax_rects = np.vstack((l, b, np.ones_like(l) * w, np.ones_like(b) * h))
    #~ return ax_rects.T

#~ def create_plot_grid(n_axes, ncols=1, margin=Margins(), fig=None,
                     #~ direction='row', sharex='none', sharey='none',
                     #~ yspines='left', xspines='bottom'):
    #~ '''Create a grid of axes suitable for plots.
#~ 
    #~ Parameters
    #~ ----------
    #~ n_axes, ncols : int
      #~ number of axes and columns
    #~ margin : Margins instance
    #~ fig : mpl figure
      #~ figure to use; if None, creates a new figure
    #~ direction : {'row', 'col'}
      #~ numbering direction for plots
    #~ sharex : {'col', 'row', 'all', 'none'}
      #~ how, if at all, to share x axes
    #~ yspines : {'left', 'all'}
      #~ where to draw y spines, relative to grid, 'all' means on all columns
    #~ xspines : {'bottom', 'all'}
      #~ where to draw x spines, relative to grid, 'all' mean on all rows
      #~ 
    #~ Returns
    #~ -------
    #~ axes : list of mpl Axes objects
    #~ '''
    #~ warnings.warn("Use matplotlib.gridspec.GridSpec instead.", DeprecationWarning)
    #~ assert(direction in ['row', 'col'])
    #~ assert(sharex in ['col', 'row', 'all', 'none'])
    #~ assert(yspines in ['left', 'all', 'none'])
    #~ assert(xspines in ['bottom', 'all'])
    #~ 
    #~ nrows = n_axes / ncols if n_axes % ncols == 0 \
        #~ else n_axes / ncols + 1
    #~ axes = []
    #~ i_axs = np.arange(n_axes)
    #~ axrects = get_ax_rects(i_axs, ncols, nrows, margin=margin,
                           #~ direction=direction)
    #~ if fig == None:
        #~ fig = plt.figure()
    #~ col_leader = None
    #~ row_leader = None
    #~ for i, axrect in enumerate(axrects):
        #~ ncol, nrow = get_col_row(i, ncols, nrows, direction)
        #~ if sharex == 'col':
            #~ if (nrow == 0) and (ncol > 0):
                #~ # reset at the top of new columns
                #~ col_leader = None
        #~ if sharey == 'row':
            #~ if (ncol == 0) and (nrow > 0):
                #~ # reset at the beginning of new rows
                #~ row_leader = None
        #~ ax = fig.add_axes(axrect, sharex=col_leader, sharey=row_leader)
#~ 
        #~ # axis sharing
        #~ if sharex == 'col':
            #~ if nrow == 0:
                #~ col_leader = ax
        #~ elif sharex == 'all':
            #~ if (nrow == 0) and (ncol == 0):
                #~ col_leader = ax
        #~ 
        #~ if sharey == 'row':
            #~ if ncol == 0:
                #~ row_leader = ax
        #~ elif sharey == 'all':
            #~ if (ncol == 0) and (nrow == 0):
                #~ row_leader = ax
                #~ 
        #~ # spines
        #~ which = []
        #~ if yspines == 'left':
            #~ if ncol == 0:
                #~ which.append('left')
        #~ elif yspines == 'all':
            #~ which.append('left')
        #~ if xspines == 'all':
            #~ which.append('bottom')
        #~ elif xspines == 'bottom':
            #~ if nrow == (nrows - 1):
                #~ which.append('bottom')
        #~ format_spines(ax, which)
        #~ axes.append(ax)
    #~ return axes
#~ 
#~ def subplot_spec2margins(subplot_spec, fig, hgap=0., vgap=0.):
    #~ bbox = subplot_spec.get_position(fig)
    #~ left, bottom, width, height = bbox.bounds
    #~ right = 1 - left - width
    #~ top = 1 - bottom - height
    #~ #print left, bottom, right, top
    #~ return Margins(left, bottom, right, top, hgap, vgap)
#~ 
#~ dashes = [[20, 2],
          #~ [2, 2],
          #~ [20, 2, 2, 2],
          #~ [20, 2, 20, 2],
          #~ [20, 2, 2, 2, 2, 2],
          #~ [20, 2, 20, 2, 2, 2],
          #~ [8, 2, 2, 2, 2, 2],
          #~ [8, 2, 2, 2]]
#~ 
#~ colours = [[0., 0., 0.],
           #~ [0., 0., 0.],
           #~ [0.5, 0.5, 0.5],
           #~ [0.5, 0.5, 0.5]]

class LineCycler():
    def __init__(self):
        self.c = 0
        self.d = 0

    def __call__(self, what='dashes'):
        if what == 'dashes' or what == 'd':
            n_styles = len(dashes)
            style = dashes[self.d % n_styles]
            self.d += 1
        else:
            n_styles = len(colours)
            style = colours[self.c % n_styles]
            self.c += 1
        return style

class FigNumer():
    def __init__(self):
        self.next_num = 0

    def __call__(self):
        next_num = self.next_num
        self.next_num += 1
        return next_num

def plot_panels(array, fig=None, nrows=1, panel_labels=None, extra_col=0.2, \
    share_axes=True):
    '''
    Plot an array as a series of image panels.
    
    Parameters
    ----------
    array : array_like
      shape = n_panels, n_rows, n_cols
    nrows : int
      number of rows to plot panels in
    panel_labels : list of strings
      labels to give each panel
    extra_col : float
      "pad" around colour range
    '''
    if fig == None:
        fig = plt.figure()
    n_panels = array.shape[0]
    ncols = n_panels / nrows if ((n_panels % nrows) == 0) \
        else (n_panels / nrows) + 1
    grid = AxesGrid(fig, 111, nrows_ncols = (nrows, ncols),
                    axes_pad = 0.05, share_all=share_axes,
                    cbar_mode='single', cbar_location='right', cbar_size='15%')
    for i in xrange(n_panels):
        vmin = np.nanmin(array[0]) * (1 - extra_col)
        vmax = np.nanmax(array[0]) * (1 + extra_col)
        im = grid[i].imshow(array[i], cmap=mpl.cm.jet, vmin=vmin, vmax=vmax)
        if panel_labels != None:
            grid[i].set_title(panel_labels[i], size='small')
    plt.colorbar(im, cax=grid.cbar_axes[0])
    cax = grid.cbar_axes[0]
    cax.axis["right"].toggle(ticks=True, ticklabels=True, label=True)
    #cax.set_ylabel("")
    return grid

