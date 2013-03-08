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
    r_i = arange(boxs) #linspace(0, boxs, nx)
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
    bands = (zi.reshape((boxs, ny)))
    output = bands
    print output.shape[:2]
    #plt.figure()
    #plt.imshow(output)
    #plt.show()
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
    
def make_profile_rings(pro_intens, basis, origin, boxs, is_linear = 0):
    
    print origin
    #print Cr[0]-boxs,Cr[0]+boxs,Cr[1]-boxs,Cr[1]+boxs

    #data = data[int(Cr[0]-boxs):int(Cr[0]+boxs),int(Cr[1]-boxs):int(Cr[1]+boxs)]
    
    #nx = 2*len(pro_base)
    #print nx, boxs
    
    if is_linear:
        print origin, boxs
        origin = (len(basis), len(basis))
        pro_base_l = basis
        pro_intens_l = pro_intens
        img_size = boxs*2 #-9
        lin_index = linspace(0,2*len(basis),img_size)-len(basis)
        
    else:
        theta_2 = basis
        origin = (len(theta_2), len(theta_2))
        print origin
        
        pro_base = (2*sin(((theta_2/180)*pi)/2.))/.5
        
        pro_base_concat = concatenate((-pro_base[:0:-4],pro_base[::4]))
        pro_base_concat = (pro_base_concat/pro_base.max()) * len(pro_base)
        img_size = len(pro_base_concat)
        
    #    plt.figure()
    #    plt.plot(pro_base, pro_intens, 'r')

        pro_base_l = linspace(0,max(pro_base),len(pro_base))
        
    #    plt.plot(pro_base_l, pro_intens, 'b')

        pro_intens_l = interp(pro_base_l, pro_base, pro_intens)
        
    #    plt.plot(pro_base_l, pro_intens_l, 'g.')
    #    
    #    plt.figure()
    #    plt.plot(pro_base_concat)
    
        lin_index = linspace(0,2*len(pro_base),img_size)-len(pro_base)
    
#    plt.plot(lin_index)
	
    # make a polar grid
    origin_x, origin_y = origin
#    x, y = meshgrid(pro_base_concat, pro_base_concat)
    #x -= origin_x
    #y -= origin_y
#    r, theta = cart2polar(x, y)
    
    x_l,y_l = meshgrid(lin_index,lin_index)
    r_l, theta_l = cart2polar(x_l, y_l)
    
#    print r, r.max()
#    plt.figure()
#    plt.imshow(r, cmap='gray')
#    plt.figure()
#    #plt.plot(r[r.shape[0]//2])
#    #plt.plot(r_l[r_l.shape[0]//2])
#    plt.plot(-(r[r.shape[0]//2]-r_l[r_l.shape[0]//2]))
    
    #plt.show()
    
    # Make a regular (in polar space) grid based on the min and max r & theta
#    r_i = linspace(0, boxs-1, nx)
#    theta_i = linspace(0, 2*pi, nx)
#    theta_grid, r_grid = meshgrid(theta_i, r_i)

    # Project the r and theta grid back into pixel coordinates
    #xi, yi = polar2cart(r_grid, theta_grid)
    #xi += origin[0] # We need to shift the origin back to 
    #yi += origin[1] # back to the lower-left corner...
    #xi, yi = xi.flatten(), yi.flatten()
    r_l = r_l.flatten()
    coords = vstack((r_l, zeros(len(r_l)))) # (map_coordinates requires a 2xn array)
    
    print coords
	
    #print coords.shape
	
    # Reproject each band individually and the restack
    # (uses less memory than reprojection the 3-dimensional array in one step)
    bands = []
    band = array([pro_intens_l,ones(len(pro_intens_l))]).T
    zi = sp.ndimage.map_coordinates(band, coords, order=2)
    bands = (zi.reshape((img_size, img_size)))
    output = bands
    #pmrdf, psrdf, prrdf= polar_mean(output)
    
    #plt.figure()
    #plt.imshow(output, cmap='gray')
    #plt.plot(origin[0]/4,origin[1]/4,'+')
    #plt.show()
    
    return output

if __name__ == "__main__":
    data = loadtxt("../tem/temfig/au_pro.txt")
    
    theta_2 = data[:,0]
    
    intensity = data[:,1]
    intensity /= intensity.max()

    print data.shape, len(theta_2), len(intensity)
    
    make_profile_rings(intensity, theta_2, (100,100), 200)
    
