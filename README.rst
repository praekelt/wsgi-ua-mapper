User Agent Mapper
=================

WSGI handler for mapping a request's user agent to an appropriate template level.

.. contents:: Contents

Overview
--------

This project contains a WSGI handler that maps the HTTP request's user agent to an appropriate template level. The handler simply returns the
template level.

The mapping uses the WURFL API and XML file to look up the device capabilities associated with the user agent. Mappings are cached using memcached.

Requirements
------------

#. pywurfl
#. python-memcached

Usage
-----

To use the user agent mapper, subclass ``UAMapper`` and override its ``map`` function. An instance of this subclass will then serve as the WSGI handler.

ua_mapper.wsgi
**************

The basic WSGI handler.

ua_mapper.wsgi.UAMapper
~~~~~~~~~~~~~~~~~~~~~~~

The WSGI handler base class that performs user agent mapping. It uses ``wurfl`` to map a user agent to a specific device.

map(self, device) 
+++++++++++++++++
This method must be overridden to perform a custom mapping. The base method simply returns 'medium' or 'high' depending on the resolution of the device.

ua_mapper.updatewurfl
*********************

A utility script that downloads the latest WURFL XML file, parses the XML and outputs ``wurfl``. ``wurfl`` contains the mapping of user agents to devices.
This script requires the ``wurfl2python`` module.

