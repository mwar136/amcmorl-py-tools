import numpy as np
from numpy import cos, sin, array, dot

from warnings import warn
warn("This module is deprecated. Use vecgeom package instead.")

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
    '''
    Returns unit length vector in same direction as vec

    Parameters
    ----------
    vec : sequence
      vector to normalize
    axis : int, optional
      axis along which to normalize, defaults to last
    '''
    return np.apply_along_axis(_unitvec, axis, arr)

def angle_between(a, b):
    '''returns the angle (in rads) between 2 vectors'''

    costheta = np.dot( a, b ) / (norm( a ) * norm( b ))
    theta = np.arccos( costheta )
    return theta

def pt_nearest(pt, offs, dir):
    '''returns point ''new'' on line in direction ''dir'' through ''offs''
    nearest to point ''pt'' '''
    return offs + np.cross(dir, pt - offs) * dir

def rotate_about_centre(v, c, th):
    '''returns vector v after rotation about centre c
    angle th is given in rads'''
    v = np.asarray(v)
    c = np.asarray(c)
    
    rotation_matrix = np.array([(np.cos(th), np.sin(th)), \
                               (-np.sin(th), np.cos(th))])
    return np.dot(rotation_matrix, v - c) + c

def rotate_about_origin_3d(vector, normal, theta):
    '''rotates the vector v around the normal vector n through angle th'''
    x, y, z = vector
    u, v, w = normal
    dt = u*x + v*y + w*z
    lns = u**2 + v**2 + w**2
    ln = np.sqrt(lns)
    return np.array(( \
        (u * dt \
         + (x * (v**2 + w**2) - u * (v*y + w*z)) * cos(theta) \
         + ln * (-w*y + v*z) * sin(theta)) / lns,                      
        (v * dt \
         + (y * (u**2 + w**2) - v * (u*x + w*z)) * cos(theta) \
         + ln * (w*x - u*z) * sin(theta)) / lns,
        (w * dt \
         + (z * (u**2 + v**2) - w * (u*x + v*y)) * cos(theta) \
         + ln * (-v*x + u*y) * sin(theta)) / lns \
        ))

def rotate_by_angles(vector, theta, phi, reverse_order=False, fixlen=False):
    '''Gives vector after rotation about theta, phi.

    Parameters
    ----------
    vector : array_like, shape (3,)
      axial components of vector
    theta : scalar
      angle of rotation to z axis
    phi : scalar
      angle of rotation in x-y plane, CCW from x axis
    reverse_order : bool
      perform the phi rotation first? Normally, theta rotation is first.

    Returns
    -------
    rotated vector : array_like, shape (3,)
      axial components of rotated vector

    Notes
    -----
    Theta and phi are relative to (0,0,1).
    This performs two rotations:
      theta, about the y-axis; followed by phi, about the z-axis.
      '''
    t, ph = theta, phi
    A = np.array(([cos(t) * cos(ph), cos(t) * sin(ph), -sin(t)],
                  [-sin(ph),         cos(ph),          0],
                  [sin(t) * cos(ph), sin(t) * sin(ph), cos(t)]))
    if not reverse_order:
        A = A.T
    return np.dot(A, vector)

def Rx(theta):
    '''
    Construct rotation matrix for rotation about x.

    Parameters
    ----------
    theta : float
      angle in radians

    Returns
    -------
    rotation_matrix : ndarray
      3x3 rotation matrix
    '''
    t = theta
    return array([[1,      0,       0],
                  [0, cos(t), -sin(t)],
                  [0, sin(t),  cos(t)]])

def Ry(theta):
    '''
    Construct rotation matrix for rotation about y.

    Parameters
    ----------
    theta : float
      angle in radians

    Returns
    -------
    rotation_matrix : ndarray
      3x3 rotation matrix
    '''
    t = theta
    return array([[ cos(t), 0, sin(t)],
                  [ 0,      1,      0],
                  [-sin(t), 0, cos(t)]])

def Rz(theta):
    '''
    Construct rotation matrix for rotation about z.

    Parameters
    ----------
    theta : float
      angle in radians

    Returns
    -------
    rotation_matrix : ndarray
      3x3 rotation matrix
    '''
    t = theta
    return array([[cos(t), -sin(t), 0],
                  [sin(t),  cos(t), 0],
                  [0,            0, 1]])

def ypr2mat(ypr):
    '''
    Construct rotation matrix from yaw, pitch, roll.

    Parameters
    ----------
    ypr : array_like
      shape (3,),  yaw, pitch and roll angles

    Returns
    -------
    rotation_matrix : ndarray
      shape (3,3) rotation matrix
    '''
    return dot(dot(Rx(ypr[0]), Ry(ypr[1])), Rz(ypr[2]))
    
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

def axis_angle2mat(axis, angle):
    '''
    Construct rotation matrix from axis of rotation and angle.
    
    Parameters
    ----------
    axis : array_like
      vector of axis of rotation
    angle : float
      amount to rotate in radians
    '''
    axis = unitvec(axis)
    if np.rank(axis) > 1:
        raise ValueError('axis should be 1-d only')
    nd = axis.shape[0]
    xm = cross_matrix(axis)
    tp = tensor_product(axis, axis)
    c, s = cos(angle), sin(angle)
    I = np.identity(nd)
    return I * c + s * xm + (1 - c) * tp
    
def rotmat_between_two_vecs(u, v):
    '''
    Calculate the rotation matrix to transform from one vector `u`
    to another 'v'.
    
    Parameters
    ----------
    u, v : array_like
      1-d vectors
      
    Returns
    -------
    r : ndarray
      rotation matrix
    '''
    u = unitvec(u)
    v = unitvec(v)
    # if vectors are parallel, return Indentity
    if np.all(u == v):
        return np.identity(u.shape[0])
    axis = np.cross(u, v)
    angle = np.arccos(np.dot(u,v))
    return axis_angle2mat(axis, angle)
