from numpy import *
import scipy as sp
import scipy.ndimage

import Image

import matplotlib.pyplot as plt

def plot_polar_pattern(data, origin, boxs, rdf, drdf):
    """Plots an image reprojected into polar coordinages with the origin
    at "origin" (a tuple of (x0, y0), defaults to the center of the image)"""
    
    origin =  [origin[1], origin[0]]
    
    polar_grid, r, theta, pmrdf, psrdf = reproject_image_into_polar(data, origin, boxs)
    
    a = 0.1	
    log_pattern = rot90(log(1+a*polar_grid))
    
    rdf = array(rdf)
    drdf = array(drdf)
    print pmrdf.shape, psrdf.max()
    dpmrdf = linspace(drdf.min(), drdf.max(), pmrdf.shape[0])
    print dpmrdf.shape
    
    rdf /= rdf.max()
    pmrdf /= pmrdf.max()
    psrdf /= psrdf.max()
    
    plt.figure()
    plt.plot(drdf, rdf, c='b', alpha=1, linewidth=2)
    plt.plot(dpmrdf, pmrdf, c='r', alpha=1, linewidth=2)
    plt.plot(dpmrdf, psrdf, c='g', alpha=1, linewidth=2)
    plt.imshow(log_pattern, cmap='binary', extent=(drdf.min(), drdf.max(), rdf.min(), rdf.max()+rdf.max()*.2), origin='lower')
    plt.axis('auto')
    plt.title('Diffraction Pattern Intensity Profile')
    plt.xlabel('Scattering Vector (1/A)')
    plt.ylabel('Intensity')
    plt.yticks([])
    plt.xlim(0, drdf.max())
    plt.ylim(0, rdf.max()+rdf.max()*.2)
    #plt.ylim(plt.ylim()[::-1])
#    plt.xlabel('R Coordinate (pixels)')
#    plt.title('Pattern in Polar Coordinates')
    plt.show()
    plt.savefig('polar.png', dpi=600, format='png')
    
def reproject_image_into_polar(data, origin, boxs):
    """Reprojects a 2D numpy array ("data") into a polar coordinate system.
    "origin" is a tuple of (x0, y0) and defaults to the center of the image."""
        
    Cr = around(origin)
    print origin
    #print Cr[0]-boxs,Cr[0]+boxs,Cr[1]-boxs,Cr[1]+boxs

    #data = data[int(Cr[0]-boxs):int(Cr[0]+boxs),int(Cr[1]-boxs):int(Cr[1]+boxs)]
        
    ny, nx = data.shape[:2]
    print data.shape[:2], boxs
    
    #plt.figure()
    #plt.imshow(data,cmap='gray')
    
    #origin = (nx//2, ny//2)
    origin = origin[::-1]
    print origin
	
    # Determine that the min and max r and theta coords will be...
    x, y = index_coords(data, origin=origin)
    r, theta = cart2polar(x, y)
    
    # Make a regular (in polar space) grid based on the min and max r & theta
    r_i = linspace(0, boxs-1, nx)
    theta_i = linspace(theta.min(), theta.max(), ny)
    theta_grid, r_grid = meshgrid(theta_i, r_i)

    # Project the r and theta grid back into pixel coordinates
    xi, yi = polar2cart(r_grid, theta_grid)
    xi += origin[0] # We need to shift the origin back to 
    yi += origin[1] # back to the lower-left corner...
    xi, yi = xi.flatten(), yi.flatten()
    coords = vstack((xi, yi)) # (map_coordinates requires a 2xn array)
	
    #print coords.shape
	
    # Reproject each band individually and the restack
    # (uses less memory than reprojection the 3-dimensional array in one step)
    bands = []
    band = data.T
    zi = sp.ndimage.map_coordinates(band, coords, order=1)
    bands = (zi.reshape((nx, ny)))
    output = bands
    pmrdf, psrdf, prrdf= polar_mean(output)
    return output[:,-boxs/2-boxs/3:-boxs/2+boxs/8], r_i, theta_i, pmrdf, psrdf, prrdf #[:,-boxs/2-boxs/2.5:-boxs/2+boxs/2.5]

def index_coords(data, origin):
    """Creates x & y coords for the indicies in a numpy array "data".
    "origin" defaults to the center of the image. Specify origin=(0,0)
    to set the origin to the lower left corner of the image."""
    ny, nx = data.shape[:2]
    origin_x, origin_y = origin
    x, y = meshgrid(arange(nx), arange(ny))
    x -= origin_x
    y -= origin_y
    return x, y
    
def cart2polar(x, y):
    r = sqrt(x**2 + y**2)
    theta = arctan2(y, x)
    return r, theta

def polar2cart(r, theta):
    x = r * cos(theta)
    y = r * sin(theta)
    return x, y
    
def polar_mean(output):
    #print output.shape[:2]
    pr, pt = output.shape[:2]
    
    #print output[:50,:250], output[-50:,:250]
    out_mean = output.mean(axis=1)
    ptv = []
    
    index = (output[:,:50]>out_mean[50]).nonzero()
    #print index, len(index), len(index[0])
    #print output[50].shape, output[50], out_mean[50]*.5
    
    for i in range(pr):
        index = (output[i]>out_mean[i]*.4).nonzero()
        #print len(index)
        ptv += [float(len(index[0]))]
        
    #print output[:50,:250], output[-50:,:250]
    
    #print len(ptv),ptv
    ptv = array(ptv)
    ptv[ptv==0]=1
    #print len(ptv),ptv
    
    out_median = median(output, axis=1)
    
    return out_mean, output.sum(axis=1)/ptv, out_median

