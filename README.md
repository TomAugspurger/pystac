## PySTAC
![Build Status](https://github.com/stac-utils/pystac/workflows/CI/badge.svg?branch=develop)
[![PyPI version](https://badge.fury.io/py/pystac.svg)](https://badge.fury.io/py/pystac)
[![Documentation](https://readthedocs.org/projects/pystac/badge/?version=latest)](https://pystac.readthedocs.io/en/latest/)
[![codecov](https://codecov.io/gh/stac-utils/pystac/branch/main/graph/badge.svg)](https://codecov.io/gh/stac-utils/pystac)
[![Gitter chat](https://badges.gitter.im/azavea/pystac.svg)](https://gitter.im/azavea/pystac)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

PySTAC is a library for working with [SpatialTemporal Asset Catalog](https://stacspec.org) in Python 3.

## Installation

PySTAC has a single dependency (`python-dateutil`).
PySTAC can be installed from pip or the source repository.

```bash
> pip install pystac
```

if you'd like to enable the validation feature utilizing the [jsonschema](https://pypi.org/project/jsonschema/) project, install with the optional `validation` requirements:


```bash
> pip install pystac[validation]
```

From source repository:

```bash
> git clone https://github.com/stac-utils/pystac.git
> cd pystac
> pip install .
```


#### Versions
To install a specific versions of STAC, install the matching version of pystac.

```bash
> pip install pystac==0.5.*
```

The table below shows the corresponding versions between pystac and STAC:

| pystac | STAC  |
| ------ | ----- |
| 1.x    | 1.0.x |
| 0.5.x  | 1.0.0-beta.* |
| 0.4.x  | 0.9.x |
| 0.3.x  | 0.8.x |

## Documentation

See the [documentation page](https://pystac.readthedocs.io/en/latest/) for the latest docs.

## Developing

See [contributing docs](docs/contributing.rst)

## Running the quickstart and tutorials

There is a quickstart and tutorials written as jupyter notebooks in the `docs/tutorials` folder.
To run the notebooks, run a jupyter notebook with the `docs` directory as the notebook directory:

```
> PYTHONPATH=`pwd`:$PYTHONPATH jupyter notebook --ip 0.0.0.0 --port 8888 --notebook-dir=docs
```

You can then navigate to the notebooks and execute them.

Requires [Jupyter](https://jupyter.org/) be installed.
