# Introduction #

In this section we'll see how to make the GDIS simulation files included with Diffraction Ring Profiler.

GDIS(Graphical Display Interface for Structures) can simulate electron powder diffraction from CIF files.

GDIS Home Page: http://gdis.sourceforge.net/

CIF files for crystals are commonly available and can be created with Crystal Maker or Vesta.  In this section we'll use Vesta which is avalable for download from the JP-minerals website.

Vesta Home Page: http://jp-minerals.org/vesta/en/

# Vesta #

If you already have a CIF file for your structure then you can skip to the section about GDIS.

To make the crystal structure you need to know the space group and lattice parameters of your structure.  Click File -> New structure and go to the Unit cell tab then enter the space group and lattice parameters of your structure. Gold is cubic Fm-3m with a 4.0782 Å lattice parameter:

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/vesta01.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/vesta01.png)

In the structure parameter tab make a new atom of Au and place it in the 0,0,0 symmetry location.

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/vesta02.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/vesta02.png)

The resulting structure will look like this:

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/vesta03.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/vesta03.png)

Then click File -> Export Data... and then save the structure as a .cif file.

# GDIS #

Open your Au CIF file that was made in the previous step or with another software package with GDIS by clicking File -> Open.. and selecting the file. It will open to look like this.

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/gdis01.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/gdis01.png)

Then click on the this bottom to simulate a diffraction.

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/gdis02.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/gdis02.png)

Match the dialogue to the one below to get a peak simulation.

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/gdis03.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/gdis03.png)

The resulting graph should match the one below.  The graph data can be exported by using File -> Export -> Graph Data.  Save the file with a .txt extension.

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/gdis04.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/gdis04.png)

Match the dialogue to the one below to get a profile simulation.  You can adjust the parameters to match the broadening typically seen in your sample.

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/gdis05.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/gdis05.png)

The resulting graph should match the one below.  The graph data can be exported by using File -> Export -> Graph Data.  Save the file with a .txt extension.

![http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/gdis06.png](http://wiki.diffraction-ring-profiler.googlecode.com/hg/images/gdis06.png)

These two .txt files can be used with Diffraction Ring Profiler to match diffraction ring pattern peak positions and profiles to the simulated ideal crystal structure.