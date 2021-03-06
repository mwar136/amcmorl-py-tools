import numpy as np
from multiregress import *

test_dir = '/home/amcmorl/lib/python-lib/tests/'

def test_multiregress():
    data = np.loadtxt(test_dir + 'box16.1_air_pollution.txt',
                      usecols=range(1,8))
    Y = data[...,0]
    X = data[...,1:3]
    coefs, ses = multiregress(X,Y)
    supplied_coefs = np.array((77.231, -1.0480, 0.0243))
    assert np.all((coefs - supplied_coefs) < 1e-2)
    supplied_ses = np.array((0.37327, 0.0047880))
    assert np.all((ses - supplied_ses) < 1e-4)
    print "multiregress ok"

def test_rsq():
    data = np.loadtxt(test_dir + 'box16.1_air_pollution.txt',
                      usecols=range(1,8))
    Y = data[:,0]
    X = data[:,1:3]
    print X.shape, Y.shape
    calc_rsq = rsq(X, Y)
    supplied_rsq = 0.5162
    assert np.abs(calc_rsq - supplied_rsq) < 0.5162
    print 'rsq okay'

def test_rsq_from_b():
    data = np.loadtxt(test_dir + 'box16.1_air_pollution.txt',
                      usecols=range(1,8))
    Y = data[:,0]
    X = data[:,1:3]
    b = multiregress(X,Y)
    calc_rsq = rsq_from_b(X, Y, b)
    supplied_rsq = 0.5162
    assert np.abs(calc_rsq - supplied_rsq) < 0.5162
    print 'rsq_from_coeffs okay'
