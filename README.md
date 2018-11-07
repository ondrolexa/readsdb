# ReadSDB plugin for QGIS 3

QGIS plugin to plot data from SDB structural database on map or on the stereonet.

The plugin reads data from SDB structural database (SQLite3 database created by [PySDB manager](https://github.com/ondrolexa/pysdb)).
The plugin cosists of following functionalities:
1) Read data based on several criteria, inluding active selection in localities layer.
2) Can automatically correct symbol rotation according to grid convergence and magnetic declination (using NOAA data).
3) Contains basic set of svg symbols used by structural geologists.
4) Plot selected data on Stereonet using [APSG](https://github.com/ondrolexa/apsg) python package for structural geologists.

Installation instructions and further funcionalities are under active developement.

#### Dependency requirements

**Note**:All dependencies must be installed within QGIS 3 python environment_

  - **`Numpy`**
  - **`Scipy`**
  - **`Matplotlib`**
  - **`APSG`** >= 0.6.0 version

### Screenshot

![](help/source/images/readsdb_ani.gif)
