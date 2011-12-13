import numpy as np
from numpy import cos, sin, array, dot

def vec2str(vec, dp=2):
    vec = np.asarray(vec)
    if np.rank(vec) != 1:
        raise(ValueError("vec must be rank 1"))
    l = vec.size
    fstr = " ".join(["%5." + "%d" % dp + "f"] * l)
    return fstr % (tuple(vec))

def norm(vec, axis=None):
    '''
    Return length of vector
    '''
    vec = np.asarray(vec)
    return np.sqrt(np.sum(vec**2, axis=axis))

def perpz(vec):
    '''returns the unit length vector perpendicular
    to vec and lying in the x-y plane (i.e. z = 0).

    Works for 2 and 3-D vectors.
    '''
    try:
        assert ((len(vec) >= 2) & (len(vec) <= 3))
    except AssertionError:
        print "Perpz is only defined for 2 and 3-D vectors."

    if len(vec) == 3:
        return unitvec( (vec[1], -vec[0], 0) )
    else:
        return unitvec( (vec[1], -vec[0]) )

def _unitvec(vec):
    '''returns the unit length vector
    in the same direction as vec'''
    vec = np.asarray(vec)
    return vec / np.sqrt(np.sum(vec ** 2))

def unitvec(arr, axis=-1):
    return np.apply_along_axis(_unitvec, axis, arr)
    
def cross_matrix(v):
    '''
    Returns the skew-symmetric matrix of a vector, defined as:
        [0 -a3 a2
        a3 0 -a1
        -a2 a1 0]
    '''
    return np.array([[0,    -v[2],  v[1]],
                     [v[2],     0, -v[0]],
                     [-v[1], v[0],  0   ]])

def tensor_product(u, v):
    '''
    Returns the tensor product of two vectors.
    '''
    return u[None] * v[:,None]