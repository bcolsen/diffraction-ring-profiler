# How to + Screenshots #

## The Main Screen(Pattern Diplay) ##

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen01.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen01.png)

### Basic Toolbar ###

|Name|Location|Description|
|:---|:-------|:----------|
|Home Button|![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/home.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/home.png)|Returns to the initial zoom|
|Back Button|![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/back.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/back.png)|Returns to the previous zoom|
|Forward Button|![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/forward.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/forward.png)|Returns to the next zoom|
|Pan Tool|![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/pan.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/pan.png)|Left-click and drag pans the pattern/Right-click and drag zooms the pattern|
|Zoom Tool|![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/zoom.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/zoom.png)|Left-click and drag makes zoom-in box/Right-click and drag makes zoom-out box|
|Configure subplots Button|![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/subplot.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/subplot.png)|Adjust the space on the outside of the figure axes Button|
|Save|![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/save.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/save.png)|Saves the figure(.pdf(vector) and .png(raster) work well, .emf doesn't work)|

### Main Screen Toolbar ###

|Name|Location|Description|
|:---|:-------|:----------|
|Mark Rings Tool|![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/circle.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/circle.png)|Click 3-ponts on a ring to measure the d-spacing and mark the center|
|Mark Spots Tool|![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/points.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/points.png)|Click 2-points to measure the distance in d-space|
|Profile Button|![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/profile.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/profile.png)|Opens the profile screen with the calculated pattern profile|
|Undo Button|![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/undo.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/undo.png)|Removes marks made on the figure one by one|

### Main Screen Menu ###

|Location|Description|
|:-------|:----------|
|Pattern -> Open|Opens a diffraction pattern image or .dm3 file|
|Pattern -> Exit|Exits the program and closes all profile and ring figure windows|
|Edit -> Undo|Removes marks made on the figure one by one|
|Edit -> Preferences|Used to set the Accelerating Voltage, Camera length and Resolution of the pattern|
|Tools -> Calibrate|Calculation the resolution of the pattern by comparing up to 4 marked ring with know d-spacings.  The default d-spacings are for Au.|
|Tools -> Profile|Opens the profile screen with the calculated pattern profile|
|Help -> About|Show the About box|


### Main Screen Howto ###

Open a TEM ring pattern using Pattern -> Open. Almost any image file or .dm3 file is compatible. Use the Zoom tool to make the rings larger:

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen02.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen02.png)

Use the Mark Rings tool and click 3 points on a ring to mark it.  You must mark at least one ring to make a profile or calibrate your detector.  The gamma slider at the bottom can help when marking dim rings:

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen03.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen03.png)

Set your accelerating voltage, camera length and resolution of your TEM in the Edit -> Preferences dialogue.  If you don't know your resolution of your detector, Mark a few rings and open the Tools -> Calibration dialogue. Input the known d-spacings(the defaults are for gold) for the rings you marked and click calibrate and then close the dialogue:

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen04.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen04.png)

Click the Profile button or select Tools -> Profile to get the profile of the ring pattern in the Profile Screen:


---


## Profile Screen ##

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen05.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen05.png)

### Profile Screen Toolbar ###

|Name|Location|Description|
|:---|:-------|:----------|
|Label Peaks Tool|![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/circle.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/circle.png)|Click on a peak to mark and measure the maxima|
|Clear Profiles Button|![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/points.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/points.png)|Clears the profile visualizations and peak labels|
|Undo Button|![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/profile.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/profile.png)|Goes back to the previous profile|

### Profile Screen Menu ###

|Location|Description|
|:-------|:----------|
|Profile -> Import GDIS Simulation|Overlays a GDIS powder diffraction simulation with a wavlength of 0.5 and U,V,W set to 0.  This makes shows peak centers and intensities|
|Profile -> Import GDIS Profile Sim|Overlays a GDIS powder diffraction simulation with a wavlength of 0.5, U,V,W set to 0.8 and pseudo-viogt mixing to 0.8.  This makes shows a profile simulation that has broadening.|
|Profile -> Import DM Simulation|Overlays a Desktop Microscopist ring simulation on the current profile.  The simulation is in the form of a .tiff screenshot of the program with the camera length set to 400cm & 200kV accelerating voltage|
|Edit -> Undo Profile|Goes back to the previous profile|
|Edit -> Simulation Labels|A dialogue that allows the peaks to be labelled with hkl indexes.  It also set the colour as well as the legend label and relative intensity. You can have up to 3 peak simulations|
|Edit -> Profile Preferences|A dialogue to change the scatting vector limit(x-max) and Polar Pattern background image preferences|
|Edit -> Clear Profiles|Clears the profile visualizations and peak labels|
|Edit -> Remove Simulation|Removes the last peak simulation|
|Tools -> Background Subtract|Fits a 3-points point power law to the main beam falloff by selecting 3-point that lie on the falloff.  The fit curve is then subtracted from the profile.  The background subtraction is lost when subsequently performing a polar pattern or recenter|
|Tools -> Recenter(Shapen Peaks)|This tool to refines the center of the ring pattern by finding the center where the peak at your first marked ring(on the main screen) is the sharpest.  Polar pattern must be redone after recentering the pattern.|
|Tools -> Polar Pattern|Makes an interpolated polar transformed image of the ring pattern resulting in straight vertical lines.  A new profile is made based on the average of that image.|
|Tools -> Beam Stop Correction|Implements polar pattern profile that has outliers removed. This is designed to remove the affect of the beam stop on the intensity|
|Tools -> Remove Spots|Implements polar pattern with the median instead of the mean.  This removes single crystal peaks from the profile.|
|Tools -> Make Ring Figure|Open the ring figure screen.|

### Profile Howto ###

Use the Tools -> Recenter(Sharpen Peaks) tool to refine the center of the rings by finding the center where the peak at your first marked ring is the sharpest:

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen06.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen06.png)

Use the visualization to confirm the result(the thick black line is the sharpest) and then clear the visualization by clicking the Clear Profiles button:

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen07.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen07.png)

Use Tools -> Polar Pattern to make a linearized ring pattern and an interpolated profile(use clear profiles to remove previous profiles):

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen08.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen08.png)

Select Tools -> Background Subtract and click 5-points on the main beam falloff (try picking three points near the beam and 2 on the tail) to fit a curve and subtract it from the profile(use clear profiles to remove previous profiles):

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen09.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen09.png)

Open the Profile Preferences dialogue by selecting Edit -> Profiles Preferences. Set the Scattering Vector Limit to 1.2 to change the x scale maximum of the graph (latex rendering only from source):

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen10.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen10.png)

Open the included GDIS peak simulation au\_peak.txt by selecting Profile -> Open GDIS Simulation.  The GDIS must be set to electron and wavelength of 0.5 without peak broadening:

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen11.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen11.png)

Open the Simulation Label dialogue by selecting Edit -> Simulation Label.  You can have up to 3 peak simulations.

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen12.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen12.png)

The labels are displayed on the simulations:

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen13.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen13.png)

Open the included GDIS profile simulation au\_pro.txt by selecting Profile -> Open GDIS Profile Sim.  The GDIS must be set to electron and wavelength of 0.5 with peak broadening around 0.6:

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen14.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen14.png)

Make a Ring Figure with Tools -> Make a Ring Figure.  If you subtracted you background from your profile, the background will be subtracted from your original pattern.  Drag the labels to reposition:

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen15.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen15.png)


Works on Linux:

On Ubuntu 10.10+:

```
$ sudo apt-get install python python-matplotlib python-scipy python-numpy python-imaging python-wxgtk2.8
```

On Ubuntu 10.04(32 or 64):

```
$ sudo apt-get install python python-matplotlib python-scipy python-numpy python-imaging python-wxgtk2.8
```

As well as install these two packages:

if 32 bit:

https://launchpad.net/~tukss/+archive/ppa/+files/python-matplotlib-data_1.0.1-1%7Etux1%7Etux1lucid1_all.deb
https://launchpad.net/~tukss/+archive/ppa/+files/python-matplotlib_1.0.1-1%7Etux1%7Etux1lucid1_i386.deb

if 64 bit:

https://launchpad.net/~tukss/+archive/ppa/+files/python-matplotlib-data_1.0.1-1%7Etux1%7Etux1lucid1_all.deb
https://launchpad.net/~tukss/+archive/ppa/+files/python-matplotlib_1.0.1-1%7Etux1%7Etux1lucid1_amd64.deb

To Run:

```
$ python diffraction_ring_profiler.py
```

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen16.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/screen16.png)