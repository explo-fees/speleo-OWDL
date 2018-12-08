=======================================
About Speleo-OWDL (= One-Way Data link)
=======================================

The name of this project comes directly from a reference to the Cold War period.

        *A numbers station, also known as a one-way voice link (OWVL), is a special type of unusual radio broadcast, generally on the Short Wave (SW) radio bands, reading out incomprehensible lists of (spoken) numbers or morse coded messages. The most common type features a female voice, reading long strings of numbers, generally in groups of five, often preceeded by a preamble and/or a series of musical notes. In most cases, such stations carry OTP encrypted messages.* [#]_

We speleologists are passionate about the events that take place in the caves and want to observe them as closely as possible, even when weather conditions prevent it.

The Cavelink system, created by Felix Ziegler, offers interesting answers:

1. various sensors can be placed in the cave
2. radio transmitters allow information to be transferred in real time

We do not use short waves (SW) like OWVL transmitters, but VLF (= Very Low Frequency). And we transmit data, not voice anymore.
So, I diverted the reference of OWVL to OWDL.


The Speleo-OWDL project allows to retrieve information from the caves, but also rainfall data by using the API provided by NetAtmo. Thanks to these Unofficial Informats of their collaboration.
Finally, the data is used to correlate events using TICK-stack, Telegram, InfluxDB, Chronograph, Kapacitor.

The aim of this tool is to :

1. Fetch data from cavelink sensors and/or NetAtmo rain gauges

2. Prepare them as a batch of measurements

3. Store them in a TSDB, influxDB.

============
Installation
============

Explain here the ...sadf

.. code:: python

  def my_function():
      "just a test"
      print 8/2


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

The configuration file is INI formatted. Here are the options:



Sensors file
""""""""""""
This file is JSON formatted.
It has to follow the following structure.


Exemple
^^^^^^^


.. [#] https://www.cryptomuseum.com/spy/owvl/index.htm