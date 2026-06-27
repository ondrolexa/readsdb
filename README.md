# readsdb - QGIS Plugin

QGIS plugin to plot data from SDB structural database on the map or stereonet.

The plugin reads data from SDB structural database (SQLite3 database created by [PySDB manager](https://github.com/ondrolexa/pysdb)).
The plugin provides the following functionalities:
1) Read data based on several criteria, including active selection in localities layer.
2) Can automatically correct symbol rotation according to grid convergence and magnetic declination (using NOAA data).
3) Contains a basic set of SVG symbols used by structural geologists.
4) Plot selected data on Stereonet using [APSG](https://github.com/ondrolexa/apsg) python package for structural geologists.

### Documentation

The documentation is located in `docs` subfolder, written in Markdown using [myst-parser](https://myst-parser.readthedocs.io/), structured in two main parts, Usage and Contribution, generated using Sphinx (have a look to [the configuration file](./docs/conf.py)) and is automatically generated through the CI and published on Pages: <https://github.com/ondrolexa/readsdb/pages> (see [post generation steps](#2-build-the-documentation-locally) below).

----

## License

Distributed under the terms of the [`MIT` license](LICENSE).
