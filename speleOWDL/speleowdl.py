# encoding=utf-8

# Collect data and store it to influxDB.

# Author : Sebastien Pittet, https://sebastien.pittet.org

import configparser
import logging
import os
import sys
import json
from cavelink import cavelink
import pyatmo
import click
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime

__version__ = "0.0.2"

@click.command()
@click.option('--collect',
             type=click.Choice(['speleo', 'weather', 'all']),
             required=True,
             show_default=True,
             default='all',
             help='Specify the type of data to collect.'
             )

@click.option('-c', '--configuration', type=click.Path(exists=True,
                                                       file_okay=True,
                                                       dir_okay=False,
                                                       readable=True,
                                                       resolve_path=True),
                required=False,
                show_default=True,
                default='config.ini',
                help='Path to the mandatory configuration file.')

@click.option('-s', '--sensors', type=click.Path(exists=True,
                                                 file_okay=True,
                                                 dir_okay=False,
                                                 readable=True,
                                                 resolve_path=True),
                required=False,
                show_default=True,
                default='sensors.json',
                help='Path to the mandatory sensors file, JSON formatted.')


def main(collect, configuration, sensors):
    """
    Fetch cavelink and weather data to store them to influxDB.
    
    A config file is mandatory to ensure proper data manipulation
    and storage in the database.

    A sensors file (JSON formatted) is mandatory to input a list
    of sensors to collect data from.

    Please specify the data type you are interested in.
    """

    click.secho('Executing speleo %s' % __version__, fg='yellow')

    configuration_file = configuration
    sensors_file = sensors

    # Load the Logging configuration from config.ini file
    # Parse the config file content
    config = configparser.ConfigParser()
    config.read(configuration_file)

    # Configure logging
    loglevel = config.get('logging','loglevel')

    # Create Logger and set log level (parent)
    logger = logging.getLogger()
    LogLevel = getattr(logging, loglevel.upper(), None)
    logger.setLevel(LogLevel)

    # Create a Console Handler and add it to parent logger
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(LogLevel)
    logger.addHandler(consoleHandler)

    # Specify the log format
    formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')
    consoleHandler.setFormatter(formatter)

    logging.info('============= [ START ] =============')
    logging.info('Configuration file = %s' % (configuration_file))
    click.secho('Configuration file = %s' % (configuration_file), fg='yellow')
        
    # get the list of sensors and details
    logging.info('Sensors definition file = %s' % (sensors_file))
    click.secho('Sensors definition file = %s' % (sensors_file), fg='yellow')

    # get nb_rows to be queried from config file
    nb_rows = config.get('cavelink', 'rows')
    logging.info('Config file: fetching %s last record(s) from cavelink.' % (nb_rows))
    click.secho('Config file: fetching %s last record(s) from cavelink.' % (nb_rows), fg='green')

    # get information to interact with NetAtmo
    netatmo_client_id     = config.get('netatmo', 'CLIENT_ID')
    netatmo_client_secret = config.get('netatmo', 'CLIENT_SECRET')
    netatmo_username      = config.get('netatmo', 'USERNAME')
    netatmo_password      = config.get('netatmo', 'PASSWORD')

    # get tolerance/margin for coordinate system, to be passed to NetAtmo
    margin = config.get('netatmo', 'margin')
    margin = float(margin)

    # get params to connect the influxDB database
    influxDB_url = config.get('database', 'influxDB_url')
    influxDB_token = config.get('database', 'influxDB_token')
    influxDB_org = config.get('database', 'influxDB_org')
    influxDB_bucket = config.get('database', 'influxDB_bucket')


    # read sensors definition file
    with open(sensors_file, 'r') as f:
        sensors = json.load(f)
    
    logging.info('Found %d sensor(s) in %s.' % (len(sensors), sensors_file))
    click.secho('Found %d sensor(s) in %s.' % (len(sensors), sensors_file), fg='green')

    # Filtering sensors list. Keeping only those to process 
    if collect == 'speleo':
        active_sensors = [s for s in sensors if s['active'].lower() == "true" and s['type'].lower() == 'cavelink']
    elif collect == 'weather':
        active_sensors = [s for s in sensors if s['active'].lower() == "true" and s['type'].lower() == 'netatmo']
    else:
        # collect = all
        active_sensors = [s for s in sensors if s['active'].lower() == "true"]

    logging.info('Found %s active sensor(s) of type: "%s"' % (len(active_sensors), collect))
    click.secho('Found %s active sensor(s) of type: "%s".' % (len(active_sensors), collect), fg='green')

    # Login at Netatmo
    authorization = pyatmo.ClientAuth(clientId = netatmo_client_id,
                                      clientSecret = netatmo_client_secret,
                                      username = netatmo_username,
                                      password = netatmo_password)
      
    measurements = []  # create a list of measurements to be written to influxDB

    # Parse a list of dict (sensors, from sensors file)
    # for each sensor, we generate a 'measurement'
    with click.progressbar(active_sensors, label='Collecting data') as bar:
        for sensor in bar:
            
            if sensor['type'] == 'cavelink':

                # get URL from definition file, specified in config file
                webpage = sensor['url']
                logging.debug('url selected: %s' % (webpage))

                logging.info('Querying %s rows of %s' % (nb_rows, sensor['description']))
                s = cavelink.Sensor(webpage, nb_rows)
                cl = json.loads(s.getJSON('epoch'))

                logging.debug('%s records received for sensor : %s' % (len(cl['measures']), sensor['description']))
                logging.debug('Records recevied: %s' % (cl['measures']))

                for timestamp in cl['measures']:
                    valuetype = sensor['tags']['sensor']
                    measurement = {}
                    measurement['measurement'] = sensor['table']
                    measurement['tags'] = sensor['tags']
                    measurement['tags']['unit']= cl['sensor']['unit']
                    measurement['time'] = int(timestamp) * 1_000_000_000 # nanoseconds
                    measurement['fields'] = {}
                    measurement['fields'][valuetype] = cl['measures'][timestamp]
                    
                    # Append a measurement to the list
                    measurements.append(measurement)

                # in case of debug, show only the last measurment of the sensor
                logging.debug(measurement)
                
            elif sensor['type'] == 'netatmo':
            
                # get netatmo station's location from definition file
                latitude = float(sensor['latitude'])
                longitude = float(sensor['longitude'])
                
                logging.info('Netatmo: %s at %s' % (sensor['description'], sensor['address']))
                logging.debug('Gather netatmo data for location: Lat %s and Lon %s' % (latitude, longitude))
                
                try:
                    netatmo = pyatmo.PublicData(authorization,
                                            LAT_NE = latitude + margin,
                                            LON_NE = longitude + margin,
                                            LAT_SW = latitude - margin,
                                            LON_SW = longitude - margin
                                            )
                    logging.debug('Found %s netatmo in area.' % netatmo.CountStationInArea())
                except:
                    e = sys.exc_info()[0]
                    logging.debug(e)
                
                for pluvioId in netatmo.get60minRain().keys():
                    measurement = {}
                    measurement['measurement'] = sensor['table']
                    measurement['tags'] = sensor['tags']
                    measurement['tags']['unit'] = sensor['unit']
                    measurement['time'] = netatmo.getTimeForRainMeasures()[pluvioId] * 1_000_000_000 # nanoseconds
                    measurement['fields'] = {}
                    measurement['fields']['value'] = float(netatmo.get60minRain()[pluvioId])
                    measurement['tags']['location'] = netatmo.getLocations()[pluvioId]
                    
                    logging.debug('Id Pluviomètre: %s' % pluvioId)
                    logging.debug('Location: %s' % netatmo.getLocations()[pluvioId])
                    logging.debug('Live rain: %s' % netatmo.getLive()[pluvioId])
                    logging.debug('Last hour rain: %s' % netatmo.get60minRain()[pluvioId])
                    logging.debug('Last day rain: %s' % netatmo.get24hRain()[pluvioId])
                    logging.debug('Time at last rain: %s' % netatmo.getTimeForRainMeasures()[pluvioId])
                
                    # Append a measurement to the list
                    measurements.append(measurement)

    # Post the measurements in batch to influxDB, if not empty
    if measurements:

        # login to influxDB
        client = InfluxDBClient(url=influxDB_url, token=influxDB_token)

        # write measurements in batch
        write_api = client.write_api(write_options=SYNCHRONOUS)
        write_api.write(influxDB_bucket, influxDB_org, measurements)

        logging.info('%s measurements written in DB.' % len(measurements))
        click.secho('%s measurements written in DB.' % len(measurements), fg='green')
    else:
        logging.info('No measurement to write.')
        click.secho('No measurement to write.', fg='red')
