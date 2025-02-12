#! /usr/bin/env python
""" 
        utility routines for FourierOpticsJHU2018
	anand@stsci.edu 2018

"""

import sys, os, time
import numpy as np
import scipy
from astropy.io import fits


def parabola2d(x,y, **kwargs):
	cx = kwargs['cx']
	cy = kwargs['cy'] 
	return ((x-cx)*(x-cx) + (y-cy)*(y-cy))

def makedisk(s, ctr=None, radius=None):
    return make_ellipse(s, ctr=ctr, ellpars = (radius,radius,0.0))

def centerpoint(s):
    """ 
        correct for Jinc, hex transform, 'ff' fringes to place peak in
            central pixel (odd array) 
            pixel corner (even array)
    """
    return (0.5*s[0] - 0.5,  0.5*s[1] - 0.5)

def makegauss(s, ctr=None, sigma=None):
    # choose a pixel-centric center default for odd-sizes, pixelcornercentric for even
    if ctr is None:
        ctr = (s/2.0, s/2.0)
	
    xx = np.linspace(-ctr[0]+0.5, s-ctr[0]-0.5, s) 
    yy = np.linspace(-ctr[1]+0.5, s-ctr[1]-0.5, s)
    (x,y) = np.meshgrid(xx, yy.T)
    gauss = np.exp(-0.5*x*x/sigma - 0.5*y*y/sigma)
    return gauss


def make_ellipse(s, ctr=None, ellpars = None):
    """
    rotated ellipse function using Alex' modern array index use

    s = integer, number of pixels on a side of square array
    ellpars = (semimajor, semiminor, rotation in degrees)
    s = 20: default ctr is [10.5,10.5] in DS9, i.e. a pixel corner (even case)
    s = 21: [11.0, 11.0] in DS9, i.e. central pixel is center of ellipse
    semimajor is horiz in DS9
    rot = 30: CCW rotation, semimajor points to 2 o'clock
    """
    # choose a pixel-centric center default for odd-sizes, pixelcornercentric for even
    if ctr is None:
        ctr = (s/2.0, s/2.0)
	
    # print "s", s, "ctr", ctr
    xx = np.linspace(-ctr[0]+0.5, s-ctr[0]-0.5, s) 
    yy = np.linspace(-ctr[1]+0.5, s-ctr[1]-0.5, s)
    (x,y) = np.meshgrid(xx, yy.T)
	
    deg = -np.pi/180.0    # minus sign seen here ... any reason?  anand
    semimajor, semiminor, theta = ellpars
    esq = (x*np.cos(theta/deg) - y*np.sin(theta/deg))**2 / semimajor**2 + \
          (y*np.cos(theta/deg) + x*np.sin(theta/deg))**2 / semiminor**2
    array = np.zeros((s,s))
    array[esq<1] = 1
    return array

def centerpoint(s):
    """ 
       s is integer scalar size of square array
       central pixel (odd array) 
       pixel corner (even array)
    """
    if hasattr(s, '__iter__'): return (0.5*s[0] - 0.5,  0.5*s[1] - 0.5)
    else: return (0.5*s - 0.5,  0.5*s - 0.5)

def kwave2d(x,y, **kwargs):
    """
    Create a cosine ripple (amplitude 1) in the array oriented so the
    ridges run at "angle" degrees from the first axis of a 2D array.

    Usage example... the example written here was not tested by running it:

    array = np.zeros((100,100))
    diam_pupil = 50.0
    nwaves = 4
    spatialwavelen = diam_pupil / nwaves

    center = centerpoint(array.shape[0]) # returns (center_x,center_y)
    
    # 0 offset gets cosine wave, 90 gets sine wave (origin at array center)
    offset = offset * np.pi/180.0 # 0 offset gets cos wave, 90 gets sine wave

    khat = np.array((np.sin(angle*np.pi/180.0), 
                     np.cos(angle*np.pi/180.0))) # unit vector

    kwavedata = np.fromfunction(kwave2d, array.shape,
                                spatialwavelen=spatialwavelen,
                                center=center,
                                offset=offset,
                                khat=khat)
    """
    spatialwavelen = kwargs["spatialwavelen"]
    center = kwargs["center"]
    offset = kwargs["offset"]
    khat = kwargs["khat"] # unit vector
    argu  = 2.0 * np.pi * (khat[0] * (x - center[0])  +  khat[1] * (y - center[1])) /  \
        spatialwavelen - offset
    return np.cos(argu)

def tilt_(x,y,**kwargs):
    tilt2d = kwargs["tilt"]
    return tilt2d[0]*x + tilt2d[1]*y

def tiltarray(arrayshape, tilt):
    """
    return tilted eg phase array
    If you need to make it zero-men do so outside this routine.
    Recall that piston (addition of a constant phase) makes no
    difference to the physics of a wave when you use this as a
    phase array.
    """
    """ tilt is a tuple (a,b) """
    return np.fromfunction(tilt_, arrayshape, tilt=tilt)

def phasearrays(npup, tiltlist):
    """
    return list of tilted eg phase array
    """
    phaselist = []
    for t in tiltlist:
        phaselist.append(tiltarray((npup,npup), t))
    return phaselist

def Jinc(x, y, c=None, scale=1.0): # LG++
    """  Uses pixel coords entirely.  Mathematical, not optical function.
         To get eg first zero at 12.2 pixels use scale=0.1, viz.  Jinc(x,y,scale=0.1)
    """
    rho = np.pi * np.sqrt(pow((x-c[0])/scale,2) + pow((y-c[1])/scale,2))
    J = 2.0 * scipy.special.jv(1, rho) / rho
    nanposition=np.where(np.isnan(J)) # Are we hitting a division by zero?
    if len(nanposition[0] == 0):  J[nanposition] = 1.0
    return J



