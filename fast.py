import numpy as np
from scipy import weave

def histogram(values, bins=10, range=None):
    '''
    Faster version of numpy.histogram. Depends on `values` being sorted in
    ascending order prior to entry, and has no capacity for weights or
    normalization.

    Parameters
    ----------
    values : array_like
      Input data. The histogram is computed over the flattened array.
    bins : int or sequence of scalars, optional
      If `bins` is an int, it defines the number of equal-width
      bins in the given range (10, by default). If `bins` is a sequence,
      it defines the bin edges, including the rightmost edge, allowing
      for non-uniform bin widths.
    range : (float, float), optional
      The lower and upper range of the bins.  If not provided, range
      is simply ``(a.min(), a.max())``.  Values outside the range are
      ignored.

    Returns
    -------
    hist : array
      The values of the histogram. See `normed` and `weights` for a
      description of the possible semantics.
    bin_edges : array of dtype float
      Return the bin edges ``(length(hist)+1)``.
    '''
    values = np.asarray(values)
        
    # define bins, size N
    if (range is not None):
        mn, mx = range
        if (mn > mx):
            raise AttributeError(
                'max must be larger than min in range parameter.')

    if not np.iterable(bins):
        if range is None:
            range = (values.min(), values.max())
        mn, mx = [mi+0.0 for mi in range]
        if mn == mx:
            mn -= 0.5
            mx += 0.5
        bins = np.linspace(mn, mx, bins+1, endpoint=True)
    else:
        bins = np.asarray(bins)
        if (np.diff(bins) < 0).any():
            raise AttributeError(
                'bins must increase monotonically.')
    
    # define n, empty array of size N+1
    count = np.zeros(bins.size - 1, int)
    nvalues = values.size
    nbins = bins.size

    if values.size == 0:
        raise AttributeError(
            'a must contain some data')
    
    if values[-1] < bins[0]:
        raise AttributeError(
            'last element of a must be smaller than first element of bins')
    
    code = \
        '''
    int lb, rb;

    if (values(0) >= bins(0)) {
        rb = 0;
    } else {
        lb = 0;
        rb = nvalues + 1;
        while(lb < rb - 1) {
            if (values((lb + rb) / 2) < bins(0)) {
                lb = (lb + rb) / 2;
            } else {
                rb = (lb + rb) / 2;
            }
        }
    }

    // Sweep through the values, counting, until they get too big
    lb = 0;
    while ((rb < nvalues) && (values(rb) < bins(nbins-1))) {
        // Advance the edge caret until the current value is in the current bin
        while (bins(lb+1) <= values(rb)) {
            lb++;
        }
        // Increment the current bin
        count(lb)++;
        // Increment the value caret
        rb++;
    }
    // Make last bin closed on RHS, i.e. include last value if equal
    if (bins(nbins-1) == values(rb)) {
        count(nbins-2)++;
    }
    '''
    weave.inline(code, ['count', 'values', 'bins', 'nvalues', 'nbins'],
                 type_converters=weave.converters.blitz)
    return count, bins

def indices3d(vol_size):
    '''Returns the equivalent of n.indices for 3-D only.
    Gives a ~6x speed up.
    '''
    xsz = vol_size[0]
    ysz = vol_size[1]
    zsz = vol_size[2]
    assert( len(vol_size) == 3 )
    assert( type(xsz) == int )
    assert( type(ysz) == int )
    assert( type(zsz) == int )
    code = '''
    #line 14
    int i,j,k;
    npy_int dims[4] = {3,xsz,ysz,zsz};
    long *curpos;
    PyArrayObject* ar =
      (PyArrayObject *)PyArray_ZEROS(4, &dims[0], NPY_LONG, 0);
    for (i = 0; i<xsz; i++)
        for (j = 0; j<ysz; j++)
            for (k = 0; k<zsz; k++)
            {
                curpos = (long *)PyArray_GETPTR4(ar, 0, i, j, k);
                *curpos = i;
                curpos = (long *)PyArray_GETPTR4(ar, 1, i, j, k);
                *curpos = j;
                curpos = (long *)PyArray_GETPTR4(ar, 2, i, j, k);
                *curpos = k;
                
            }
    return_val = PyArray_Return(ar);
    '''
    return weave.inline( code, ['xsz','ysz','zsz'] ) 
