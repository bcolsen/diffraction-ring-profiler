**A program for extracting electron diffraction ring pattern profiles, 
comparing simulation and making figures.**

Produced by [Dr. David Mitlin's Research Group](http://www.mitlingroup.com/) 
from the Department of Chemical and Materials Engineering at the Univerity of Alberta

If you found this program helpful in your research, please cite it by using a line similar to:

"TEM diffraction patterns were analysed with Diffraction Ring Profiler, 
which was developed for phase identification in complex microstructures`[cite]`"

Then cite [doi:10.1021/jp205052f](http://dx.doi.org/10.1021/jp205052f):

<pre>
High rate electrochemical capacitors from three-dimensional arrays of vanadium nitride-functionalized carbon nanotubes,<br>
L Zhang, CMB Holt, EJ Luber, BC Olsen, H Wang, M Danaie, X Cui, X Tan, V Lui, WP Kalisvaart and D Mitlin,<br>
Journal of Physical Chemistry C, 115 (2011) 24381-24393, doi:10.1021/jp205052f</pre>

## Installation

### Windows

There are zipped executables available in the release section at:

[https://github.com/bcolsen/diffraction-ring-profiler/releases](https://github.com/bcolsen/diffraction-ring-profiler/releases)

### All Systems

Install the Anconda Python 3.5(or greater) Distribution:(It's big(450mb) but it's full of great science tools) 

[Download Anaconda](https://www.continuum.io/downloads)

Open a terminal(Windows use the "Anaconda Prompt") and type:

`conda install -c newville wxpython-phoenix`

To Run:

`python diffraction_ring_profiler.py`

## Cctbx Cif Crystal File Profile Simulations

You can now use cctbx to simulate diffraction profiles from .cif crystal files.

Download the latest cctbx binaries from here:

[Download CCTBX](http://cci.lbl.gov/cctbx_build/)

Then extract the folder to your user directory (eg. C:\Users\<user_name>\ or /home/<user_name>/) 

## Documentation

The are instuctions on the Wiki with screenshots:

[How-to](https://github.com/bcolsen/diffraction-ring-profiler/wiki/How-to-&-Screenshots)

## Screen Shots

![Screen Shot](https://raw.githubusercontent.com/wiki/bcolsen/diffraction-ring-profiler/images/screen16.png)
