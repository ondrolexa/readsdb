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

  - `Numpy`
  - `Scipy`
  - `Matplotlib`
  - `apsg >= 1.0`

On Debian-like Linux distros use apt

    sudo apt install python3-pip python3-numpy python3-matplotlib python3-scipy

and install APSG in QGIS 3 Python console

    >>> import subprocess
    >>> subprocess.check_output(['pip3', 'install', '--no-deps', '--user', 'apsg'])

On Windows, numpy, matplotlib and scipy is already installed with QGIS, so open Python console

    >>> import pip
    >>> pip.main(['install', '--no-deps', '--user', 'apsg'])

Restart QGIS and enjoy!

On Debian-like Linux distros use apt

    $ sudo apt install python3-numpy3-pip python3-numpy python3-matplotlib python3-scipy

and install APSG in QGIS 3 Python console

    >>> import subprocess
    >>> subprocess.check_output(['pip3', 'install', '--no-deps', '--user', 'apsg'])

On Windows, numpy, matplotlib and scipy is already installed with QGIS, so open Python console

    >>> import pip
    >>> pip.main(['install', '--no-deps', '--user', 'apsg'])

Restart QGIS and enjoy!

### Screenshot

![](help/source/images/readsdb_ani.gif)
