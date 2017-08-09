# Diffraction Ring Profiler

### A program for extracting electron diffraction ring pattern profiles, comparing simulation and making figures.

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

### Windows (executable):

1. Download the latest cctbx binaries from here:
   
   [Download CCTBX](http://cci.lbl.gov/cctbx_build/)

   Then extract the folder to your user directory (eg. C:\Users\\<user_name>\ or /home/<user_name>/)
   
   This is needed to simulate diffraction profiles from .cif crystal files.

2. Download the latest executable from:

   https://github.com/bcolsen/diffraction-ring-profiler/releases

3. Double click the executable

### Windows & OSX & Linux (Using Anaconda):

1. Download the latest cctbx binaries from here:

   [Download CCTBX](http://cci.lbl.gov/cctbx_build/)

   Then extract the folder to your user directory (eg. C:\Users\\<user_name>\ or /home/<user_name>/) 

2. Install the Anaconda Python 3.6 Distribution:(It's big(450mb) but it's full of great science tools) 

   [Download Anaconda](https://www.continuum.io/downloads)

3. Open a terminal(Windows use the "Anaconda Prompt") and type:

   ```
   conda install -c conda-forge wxpython`
   ```

4. Download the latest source from:

   https://github.com/bcolsen/diffraction-ring-profiler/releases

5. Extract the source to your user directory (eg. C:\Users\\<user_name>\ or /home/<user_name>/).

6. Change to that directory in the terminal and run:

   ```
   python diffraction_ring_profiler.py
   ```

### On Ubuntu 16.04+:

```
$ sudo apt-get install python3 python3-matplotlib python3-scipy python3-numpy python3-imaging
$ sudo pip3 install wxpython
```

## Requirements:

* python >= 3.4
* matplotlib >= 2.0
* scipy
* numpy 
* python imaging library(PIL or pillow)


## Documentation

The are instuctions on the Wiki with screenshots:

[How-to](https://github.com/bcolsen/diffraction-ring-profiler/wiki/How-to-&-Screenshots)

## Screen Shot

![Screen Shot](https://raw.githubusercontent.com/wiki/bcolsen/diffraction-ring-profiler/images/screen16.png)
