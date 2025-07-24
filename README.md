# ReadSDB plugin for QGIS 3

QGIS plugin to plot data from SDB structural database on the map or stereonet.

The plugin reads data from SDB structural database (SQLite3 database created by [PySDB manager](https://github.com/ondrolexa/pysdb)).
The plugin provides the following functionalities:
1) Read data based on several criteria, including active selection in localities layer.
2) Can automatically correct symbol rotation according to grid convergence and magnetic declination (using NOAA data).
3) Contains a basic set of SVG symbols used by structural geologists.
4) Plot selected data on Stereonet using [APSG](https://github.com/ondrolexa/apsg) python package for structural geologists.

### Install instructions

Download the [ReadSDB plugin](https://github.com/ondrolexa/readsdb/archive/master.zip) from GitHub and unzip into the `python/plugins` folder of the active user profile. The location of profile folder could be find using the menu **Settings ► User Profiles ► Open Active Profile Folder**.

#### Dependency requirements

**Note**:All dependencies must be installed within QGIS3 python environment:

  - `numpy`
  - `scipy`
  - `matplotlib`
  - `pandas`
  - `sqlalchemy`
  - `apsg >= 1.3`

On Debian-like Linux distros use apt:

    sudo apt install python3-pip python3-numpy python3-matplotlib python3-scipy python3-pandas python3-sqlalchemy

and install APSG using pip into user space:

    pip install --user apsg

For Ubuntu 23.04 and later Canonical blocked installing or uninstalling pip packages. One possibility is to force pip to install apsg:

    pip install --user apsg --break-system-packages

On Windows, numpy, matplotlib, scipy and pandas are already installed with QGIS, so we need to install apsg. Open Python console in QGIS and run following commands:

    >>> import pip
    >>> pip.main(['install', '--no-deps', '--user', 'apsg'])

Restart QGIS and enjoy!

### Screenshot

![](help/source/images/readsdb_ani.gif)
