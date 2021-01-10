=======================================
About Speleo-OWDL (= One-Way Data link)
=======================================

The name of this project comes directly from a reference to the Cold War period.

        *A numbers station, also known as a one-way voice link (OWVL), is a special type of unusual radio broadcast, generally on the Short Wave (SW) radio bands, reading out incomprehensible lists of (spoken) numbers or morse coded messages. The most common type features a female voice, reading long strings of numbers, generally in groups of five, often preceeded by a preamble and/or a series of musical notes. In most cases, such stations carry OTP encrypted messages.* [#]_

We speleologists are passionate about the events that take place in the caves and want to observe them as closely as possible, even when weather conditions prevent it. This piece of software is basically a data scrapper.

The Cavelink system, created by Felix Ziegler, offers interesting answers:

1. various sensors can be placed in the cave
2. radio transmitters allow information to be transferred in real time

We do not use short waves (HF [#]_) like OWVL transmitters, but VLF (= Very Low Frequency). And we transmit data, not voice anymore.
So, I diverted the reference of OWVL to OWDL.


The Speleo-OWDL project allows to retrieve information from the caves, but also rainfall data by using the API provided by NetAtmo. Thanks to these Unofficial Informants [#]_ of their collaboration.
Finally, the data is used to correlate events using Grafana.

The aim of this tool is to :

1. Fetch data from cavelink sensors and/or NetAtmo rain gauges

2. Prepare them as a batch of measurements

3. Store them in a TSDB, influxDB.

============
Installation
============

This repository is a Python package. You can install it on your Linux system with the command:

.. code:: python

  python3 setup.py install

You will then call the tool as a command line.

=====
Usage
=====

.. code:: bash

  speleowdl --help


==========
Parameters
==========

-c, --configuration  Path to configuration file
-s, --sensors        Path to the file describbing the sensors
--collect            Type of data to collect (weather | speleo | all)
                     where weather stands for NetAtmo
                     and speleo represents cavelink data.


Configuration file
""""""""""""""""""

The configuration file is INI formatted. Here is the example of `configuration file <https://github.com/SebastienPittet/speleo-OWDL/blob/master/speleOWDL/config.ini>`_.


Sensors file
""""""""""""
This file is JSON formatted, see `my own example <https://github.com/SebastienPittet/speleo-OWDL/blob/master/speleOWDL/sensors.json>`_.
It has to follow the following structure, with the fields :

For Cavelink sensors:
^^^^^^^^^^^^^^^^^^^^

:active: True or False. Used to disable a sensor.
:description: Allows you to have a readable explanation of this sensor.
:url: Cavelink URL
:table: Used to insert data in influxDB
:tags: A list of tags. Will be inserted in the measurements.
:type: The value 'cavelink' identify the sensor and calls the right lib


For NetAtmo sensors:
^^^^^^^^^^^^^^^^^^^

:active: True or False. Used to disable a sensor.
:description: Allows you to have a readable explanation of this sensor.
:table: Used to insert data in influxDB
:tags: A list of tags. Will be inserted in the measurements-
:type: The value 'netatmo' allows the code to use NetAtmo API
:unit: Specify the unit of the sensor (inserted in the table)
:latitude: Coordinate of the netAtmo station.
:longitude: Coordinate of the netAtmo station.


Exemple
^^^^^^^

.. code:: bash

  speleowdl --collect all --configuration ./config.ini --sensors sensors.json
  speleowdl --collect speleo --configuration ./config.ini --sensors sensors.json
  speleowdl --collect weather --configuration ./config.ini --sensors sensors.json


=========
Footnotes
=========

.. [#] https://www.cryptomuseum.com/spy/owvl/index.htm
.. [#] https://en.wikipedia.org/wiki/Shortwave_radio
.. [#] https://en.wikipedia.org/wiki/Unofficial_collaborator
