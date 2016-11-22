# -*- coding: utf-8 -*-
### Automatically generated by repyhelper.py ### /chalmers/users/isaker/Distributed/Distributed/demokit/advertise.repy

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
<Program Name>
  advertise.repy

<Started>
  October 14, 2008

<Author>
  Justin Cappos

<Purpose>
  Module which allows clients to send advertise queries to various servers.
"""

repyhelper.translate_and_import('listops.repy')
repyhelper.translate_and_import('centralizedadvertise.repy')
repyhelper.translate_and_import('centralizedadvertise_v2.repy')
repyhelper.translate_and_import('DORadvertise.repy')
repyhelper.translate_and_import('parallelize.repy')
repyhelper.translate_and_import('udpcentralizedadvertise.repy')


# All the names of services we can support.
# As of January 2012, openDHT is no longer a default service.
_advertise_all_services = ("central", "central_v2")


nodemanager_announce_context = {}
for service in _advertise_all_services:
  nodemanager_announce_context["skip" + service] = 0
  nodemanager_announce_context["previous" + service + "skip"] = 1
nodemanager_announce_context_lock = getlock()


# an exception to indicate an error occured while advertising
class AdvertiseError(Exception):
  pass




def _try_advertise_announce(args):
  """
  <Purpose>
    Helper function to be used in parallel with other advertise requests. 
    This is the function we pass to parallelize to perform simultaneous 
    queries.

  <Arguments>
    args (tuple)
      A tuple containing the following:
        which_service (string)
          The service we should use to advertise, such as "central" or "DOR".
        key (string)
          The advertisement key. For most nodes, this will be a public key.
        value (string)
          The advertisement value to be assigned to key.
        ttlval (int)
          Time To Live for this advertisement, in seconds.
        exceptions (List reference, should literally be [''])
          An empty list reference which will be have exception data in its zero 
          index if something goes wrong. Due to this method's parallelized nature, 
          we cannot simply return this data; it is not invoked by this module.
        finishedref (List with boolean in zero index)
          This function sets finishedref[0] = true when it has completed 
          successfully. This is used as a flag so that we know when to return 
          advertise data to the client later.

  <Exceptions>
    AdvertiseError
      If an invalid service type is specified, this exception will be raised.
    ValueError
      Too many, or too few values passed in the args tuple.

  <Side Effects>
    Contingent on the side effects of the modules invoked for different 
    services, this consumes an outsocket and insocket on use. Therefore, 
    invoking too many instances of these in parallel can lead to crashing 
    if the application exceeds its allotted socket count.

    The number of sockets permitted to an application is determined by 
    its associated restrictions file.

  <Returns>
    None
  """
  # ValueError if there are too many or too few values.
  which_service, key, value, ttlval, exceptions, finishedref = args

  if which_service not in _advertise_all_services:
    raise AdvertiseError("Incorrect service type used in internal function _try_advertise_announce.")

  try:
    if which_service == "central":
      centralizedadvertise_announce(key, value, ttlval)
    elif which_service == "central_v2":
      v2centralizedadvertise_announce(key, value, ttlval)
    elif which_service == "DOR":
      DORadvertise_announce(key, value, ttlval)
    elif which_service == "UDP":
      udpcentralizedadvertise_announce(key, value, ttlval)
    else:
      # This should be redundant with the previous explicit AdvertiseError.
      # One cannot (usually) be too careful.
      raise AdvertiseError("Did not understand service type.")

    finishedref[0] = True     # Indicate that this instance has finished.
    
    nodemanager_announce_context_lock.acquire()
    try:
      nodemanager_announce_context["previous" + which_service + "skip"] = 1
    finally:
      nodemanager_announce_context_lock.release()

  except Exception, e:
    nodemanager_announce_context_lock.acquire()
    try:
      exceptions[0] += 'announce error (type: ' + which_service + '): ' + str(e)
      nodemanager_announce_context["skip" + which_service] = \
          nodemanager_announce_context["previous" + which_service + "skip"] + 1
      nodemanager_announce_context["previous" + which_service + "skip"] = \
          min(nodemanager_announce_context["previous" + which_service + "skip"] * 2, 16)
    finally:
      nodemanager_announce_context_lock.release()





def advertise_announce(key, value, ttlval, concurrentevents=4, \
    graceperiod=10, timeout=60):
  """
  <Purpose>
    Announce (PUT) a key : value pair to all default advertise services.

  <Arguments>
    key (string)
      The key for our advertise dictionary entry.

    value (string)
      The value for our advertise dictionary entry.

    ttlval (int)
      Time in seconds to persist the associated key<->value pair.
    
    concurrentevents (int) (optional)
      How many services to announce on in parallel.

    graceperiod (float) (optional)
      Amount of time to wait before returning, provided at least one of the 
      parallel attempts has finished.

      Note that even when this method returns, parallelized announce attempts may
      still be running. These will terminate in relatively short order, but be 
      aware of this. It could be a problem, for example, if you tried to set graceperiod 
      very low to send rapid-fire queries to the advertise servers. This would 
      probably cause you to exceed your allotted outsockets. (This is only 
      possible if your timeout value is greater than your graceperiod value.)

      In short, graceperiod is a "soft" timeout. Provided at least one query has 
      been confirmed, the method will return after graceperiod seconds at most.
      If none return, this could run all the way till timeout.

    timeout (int) (optional)
      Absolute allowed time before returning. Provided the method has not 
      returned by now, successful or not, it will terminate after timeout seconds.

  <Exceptions>
    AdvertiseError if something goes wrong.

  <Side Effects>
    Spawns as many worker events as concurrentevents specifies, limited by the
    number of services available (currently 2). Each worker event consumes one 
    insocket and one outsocket until it is finished.

  <Returns>
    None.
  """
  # convert different types to strings to avoid type conversion errors #874
  key = str(key)
  value = str(value)

  # Wrapped in an array so we can modify the reference (python strings are immutable).
  exceptions = [''] # track exceptions that occur and raise them at the end

  parallize_worksets = []
  start_time = getruntime()

  onefinished = [False]

  # Populate parallel jobs list.
  for service_type in _advertise_all_services:
    if nodemanager_announce_context["skip" + service_type] == 0:
      parallize_worksets.append((service_type, key, value, ttlval, \
          exceptions, onefinished))
    else:
      nodemanager_announce_context_lock.acquire()
      try:
        nodemanager_announce_context["skip" + service_type] = \
            nodemanager_announce_context["skip" + service_type] - 1
      finally:
        nodemanager_announce_context_lock.release()

  # Begin parallel jobs, instructing parallelize to run no more than 
  # concurrentevents at once.
  ph = parallelize_initfunction(parallize_worksets, _try_advertise_announce, \
      concurrentevents=concurrentevents)

  # Once we have either timed out or exceeded graceperiod with at least one 
  # service reporting, return whatever data we have. Remaining threads will 
  # be forsaken and allowed to terminate at their leisure.
  while not parallelize_isfunctionfinished(ph):
    sleep(0.015)
    if getruntime() - start_time > timeout or \
        (getruntime() - start_time > graceperiod and onefinished[0]):
      parallelize_abortfunction(ph)
      break

  # This does not terminate all parallel threads; do not assume it does.
  parallelize_closefunction(ph)

  # check to see if any successfully returned 
  if onefinished == [False]:
    raise AdvertiseError("None of the advertise services could be contacted")

  # if we got an error, indicate it
  if exceptions[0] != '':
    raise AdvertiseError(str(exceptions))

  return None




def _try_advertise_lookup(args):
  """
  <Purpose>
    Helper function for advertise lookups. This is the instance function for 
    parallel lookups which is passed to and managed by parallelize. Each 
    execution of this method will perform one lookup and return whatever 
    it is able to get.

  <Arguments>
    args (4-tuple)
      which_service (string)
        The service on which to perform a lookup. This must match one of the 
        values in _advertise_all_services.
      key (string)
        The key to retrieve a value for.
      maxvals (int)
        The maximum number of entries to retrieve from the server.
      finishedref (Array reference with a boolean at index zero)
        The state of the function instance. If it completes successfully,
        this boolean will be set to True.
  """
  which_service, key, maxvals, finishedref = args

  if which_service not in _advertise_all_services:
    raise AdvertiseError("Incorrect service type used in internal function _try_advertise_lookup.")

  try:
    if which_service == "central":
      results = centralizedadvertise_lookup(key, maxvals)
    elif which_service == "central_v2":
      results = v2centralizedadvertise_lookup(key, maxvals)
    elif which_service == "DOR":
      results = DORadvertise_lookup(key, maxvals=maxvals)
    elif which_service == "UDP":
      results = udpcentralizedadvertise_lookup(key, maxvals)
    else:
      raise AdvertiseError("Did not understand service type!")

    finishedref[0] = True
    return results
  
  except Exception, e:
    return []




def advertise_lookup(key, maxvals=100, lookuptype=None, \
    concurrentevents=4, graceperiod=10, timeout=60):
  """
  <Purpose>
    Lookup (GET) (a) value(s) stored at the given key in the central advertise
    server, central advertise server V2, DOR, UDP, or all.

  <Arguments>
    key
      The key used to lookup values.

    maxvals (optional, defaults to 100):
      Maximum number of values to return.

    lookuptype (optional, defaults to ['central', 'central_v2', 'DOR', 'UDP']):
      Which services to employ looking up values.
    
    concurrentevents (optional, defaults to 2):
      How many services to lookup on in parallel.

    graceperiod (optional, defaults to 10):
      After this many seconds (can be a float or int type), return the
      results if one service was reached successfully.

    timeout (optional, defaults to 60):
      After this many seconds (can be a float or int type), give up.

  <Exceptions>
    AdvertiseError if something goes wrong.

  <Side Effects>
    Spawns as many worker events as concurrentevents specifies, limited by the
    number of services in lookuptype.

  <Returns>
    All unique values stored at the key.
  """
  # convert different types to strings to avoid type conversion errors #874
  key = str(key)

  # As of January 2012, DHT is no longer a default service.
  if lookuptype is None:
    lookuptype = _advertise_all_services

  parallel_worksets = []
  start_time = getruntime()

  onefinished = [False]

  # Populate parallel jobs list.
  for servicetype in lookuptype:
    if servicetype == "central":
      parallel_worksets.append(("central", key, maxvals, onefinished))
    elif servicetype == "central_v2":
      parallel_worksets.append(("central_v2", key, maxvals, onefinished))
    elif servicetype == "DOR":
      parallel_worksets.append(("DOR", key, maxvals, onefinished))
    elif servicetype == "UDP":
      parallel_worksets.append(("UDP", key, maxvals, onefinished))
    else:
      raise AdvertiseError("Incorrect service type '" + servicetype + "' passed to advertise_lookup().")

  # Start parallel jobs.
  ph = parallelize_initfunction(parallel_worksets, _try_advertise_lookup, \
      concurrentevents=concurrentevents)

  # Wait until either timeout or graceperiod with at least one service 
  # success, and then continue.
  while not parallelize_isfunctionfinished(ph):
    sleep(0.015)
    if getruntime() - start_time > timeout or \
        (getruntime() - start_time > graceperiod and onefinished[0]):
      parallelize_abortfunction(ph)
      break

  parallel_results = parallelize_getresults(ph)['returned']
  results = []

  # Construct a list of return results
  for parallel_result in parallel_results:
    junk, return_value = parallel_result
    results += return_value

  parallelize_closefunction(ph)

  # Filter results and return.
  return listops_uniq(results)

### Automatically generated by repyhelper.py ### /chalmers/users/isaker/Distributed/Distributed/demokit/advertise.repy
