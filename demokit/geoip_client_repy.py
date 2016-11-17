# -*- coding: utf-8 -*-
### Automatically generated by repyhelper.py ### /home/apotekaren/Desktop/distributed/demokit/geoip_client.repy

### THIS FILE WILL BE OVERWRITTEN!
### DO NOT MAKE CHANGES HERE, INSTEAD EDIT THE ORIGINAL SOURCE FILE
###
### If changes to the src aren't propagating here, try manually deleting this file. 
### Deleting this file forces regeneration of a repy translation


from repyportability import *
import repyhelper
mycontext = repyhelper.get_shared_context()
callfunc = 'import'
callargs = []

"""
<Author>
  Evan Meagher

<Start Date>
  Nov 26, 2009

<Description>
  XMl-RPC client for remote GeoIP server. Given an IP:port of a GeoIP
  XML-RPC server, allows location lookup of hostnames and IP addresses.

<Usage>
  client = geoip_client(server_address)

  Where server_address is the ip address of a remote GeoIP XMl-RPC server.
"""

repyhelper.translate_and_import('parallelize.repy')
repyhelper.translate_and_import('xmlrpc_client.repy')


"""
Initialize global GeoIP XML-RPC client object to None
Note: client is stored in wrapper list to avoid using mycontext dict
"""
geoip_clientlist = []



def geoip_init_client(url=["http://geoipserver.poly.edu:12679", "http://geoipserver2.poly.edu:12679"]):
  """
  <Purpose>
    Create a new GeoIP XML-RPC client object.
  
  <Arguments>
    url
      List of URLs (protocol://ip:port) of GeoIP XML-RPC server.

  <Exceptions>
    None.

  <Side Effects>
    Inserts GeoIP XML-RPC client as first element of global
    geoip_clientlist.

  <Returns>
    None.
      
  """
  # Empty the global list.
  del geoip_clientlist[:]

  # Store XML-RPC client globally in list to avoid using mycontext dict
  for cururl in url:
    geoip_clientlist.append(xmlrpc_client_Client(cururl))


def _isvalid_IP(addr):
  # Helper method that is used to validate IPv4 addresses for thier correct
  # format. The only accepted format is the dotted decimal,i.e. 'x.x.x.x'.
  # This is because the backend GeoIP server only accepts this format.
  # This method returns a Bool for validated IP address.

  # split the IP address, so that I can check for each number if it falls
  # within the range of 0-255.
  decimallist = addr.split('.')

  # First, I need to check if there are 4 decimal numbers for IP address.
  if len(decimallist) != 4:
    return False

  # Make sure the numbers in IP address are sent as decimals that fall in the
  # range of 0-255.
  try:
    # If any of the decimal is not within the range, return False.
    for eachdecimal in decimallist:
      if not (0 <= int(eachdecimal) < 256):
        return False

  # This is used to catch any values sent other than numbers to base 10
  # to int().
  except ValueError:
    return False

  # finally, return the result.
  return True


def geoip_record_by_addr(addr, graceperiod=2, timeout=5):
  """
  <Purpose>
    Request location data of provided IP address from GeoIP XML-RPC server

  <Arguments>
    addr
      IP address of which to look up location.
    timeout
      How long we should wait for a response.

  <Exceptions>
    None.

  <Side Effects>
    None.

  <Returns>
    Dictionary of location data of provided IP address.
  """
  
  # Keep track of when we started.
  start_time = getruntime()

  # A list that keeps track of whether at least one of the geoip servers have
  # returned the result.
  one_finished_instance=[False]

  # a client-side check to validate IP, before sending to PyGeoIP server.
  # Not doing this check, will return bogus information from server.
  if not _isvalid_IP(addr):
    raise ValueError('Not a valid IPv4 address.')

  parallel_handle = parallelize_initfunction(geoip_clientlist, _try_geoip_addr_lookup, 5, addr, timeout, one_finished_instance)

  while not parallelize_isfunctionfinished(parallel_handle):
    sleep(0.01)
    if (getruntime() - start_time > graceperiod) and one_finished_instance:
      parallelize_abortfunction(parallel_handle)
      break  

  # If we did not get any successful lookup, then raise error.
  if not one_finished_instance[0]:
    raise Exception("Unable to contact the geoip server.")

  # Lookup the results for geoip.
  junk, result = parallelize_getresults(parallel_handle)['returned'][0]

  # This does not terminate all parallel threads; do not assume it does.
  parallelize_closefunction(parallel_handle)

  # If we found no suitable result.
  if not result:
    raise Exception("Unable to contact the geoip server.")

  if 'faultCode' in result:
    raise Exception(result['faultString'])

  return result






def _try_geoip_addr_lookup(geoip_client, addr, timeout, one_finished_instance):
  """
  <Purpose>
    The purpose of this function is to try and do a geoip lookup
    by address.
  """

  # Lookup the request and update the one_finished_instance, indicating
  # that at least one lookup was successful.

  # a client-side check to validate IP, before sending to PyGeoIP server.
  # Not doing this check, will return bogus information from server.
  if not _isvalid_IP(addr):
    raise ValueError('Not a valid IPv4 address.')

  result = geoip_client.send_request("record_by_addr", (addr, ), timeout)
  one_finished_instance[0] = True
  return result





def geoip_record_by_name(name, graceperiod=2, timeout=5):
  """
  <Purpose>
    Request location data of provided hostname from GeoIP XML-RPC server

  <Arguments>
    name
      Hostname of which to look up location.
    timeout
      How long we should wait for a response.

  <Exceptions>
    None.

  <Side Effects>
    None.

  <Returns>
    Dictionary of location data of provided hostname.
  """

  # Keep track of when we started.
  start_time = getruntime()

  # A list that keeps track of whether at least one of the geoip servers have
  # returned the result.
  one_finished_instance=[False]

  parallel_handle = parallelize_initfunction(geoip_clientlist, _try_geoip_name_lookup, 5, name, timeout, one_finished_instance)

  while not parallelize_isfunctionfinished(parallel_handle):
    sleep(0.01)
    if (getruntime() - start_time > graceperiod) and one_finished_instance:
      parallelize_abortfunction(parallel_handle)
      break  

  # If we did not get any successful lookup, then raise error.
  if not one_finished_instance[0]:
    raise Exception("Unable to contact the geoip server.")

  # Lookup the results for geoip.
  junk, result = parallelize_getresults(parallel_handle)['returned'][0]

  # This does not terminate all parallel threads; do not assume it does.
  parallelize_closefunction(parallel_handle)

  # If we found no suitable result.
  if not result:
    raise Exception("Unable to contact the geoip server.")

  return result

  


def _try_geoip_name_lookup(geoip_client, name, timeout, one_finished_instance):
  """
  <Purpose>
    The purpose of this function is to try and do a geoip lookup
    by record.
  """

  # Lookup the request and update the one_finished_instance, indicating
  # that at least one lookup was successful.
  result = geoip_client.send_request("record_by_name", (name, ), timeout)
  one_finished_instance[0] = True
  return result



def geoip_location_str(location_dict):
  """
  <Purpose>
    Pretty-prints a location specified by location_dict as a comma-separated
    list. Prints location info as specifically as it can, according to the
    format 'CITY, STATE/PROVINCE, COUNTRY'.

    location_dict['city'], location_dict['region_name'], and
    location_dict['country_name'] are added if defined, and
    location_dict['region_name'] is added if the location is in the US or
    Canada.
      
  <Arguments>
    location_dict
      Dictionary of location information, as returned by a call to
      geoip_record_by_addr or geoip_record_by_name.
      
  <Exceptions>
    None.

  <Side Effects>
    None.

  <Returns>
    A string representation of a location.
  """

  location_str = ""
  if 'city' in location_dict and location_dict['city'] is not None:
    location_str = location_str + location_dict['city'] + ", "

  if 'country_name' in location_dict:
    # If location is in the US or Canada, include the state/province
    if location_dict['country_name'] in ['United States', 'Canada']:
      if 'region_name' in location_dict and location_dict['region_name'] is not None:
        location_str = location_str + location_dict['region_name'] + ", "
    location_str = location_str + location_dict['country_name']

  return location_str

### Automatically generated by repyhelper.py ### /home/apotekaren/Desktop/distributed/demokit/geoip_client.repy