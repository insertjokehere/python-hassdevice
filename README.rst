========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/python-hassdevice/badge/?style=flat
    :target: https://readthedocs.org/projects/python-hassdevice
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/insertjokehere/python-hassdevice.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/insertjokehere/python-hassdevice

.. |requires| image:: https://requires.io/github/insertjokehere/python-hassdevice/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/insertjokehere/python-hassdevice/requirements/?branch=master

.. |codecov| image:: https://codecov.io/github/insertjokehere/python-hassdevice/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/insertjokehere/python-hassdevice

.. |version| image:: https://img.shields.io/pypi/v/hassdevice.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/hassdevice

.. |commits-since| image:: https://img.shields.io/github/commits-since/insertjokehere/python-hassdevice/v0.0.2.svg
    :alt: Commits since latest release
    :target: https://github.com/insertjokehere/python-hassdevice/compare/v0.0.2...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/hassdevice.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/hassdevice

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/hassdevice.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/hassdevice

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/hassdevice.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/hassdevice


.. end-badges

A library for building MQTT devices for HomeAssistant

* Free software: Apache Software License 2.0

Installation
============

::

    pip install hassdevice

Documentation
=============

https://python-hassdevice.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
