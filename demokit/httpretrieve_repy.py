# -*- coding: utf-8 -*-
### Automatically generated by repyhelper.py ### /chalmers/users/vikbergl/distributedGit/Distributed/demokit/httpretrieve.repy

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
  httpretrieve.repy

<Started>
  August 19, 2009

<Authors>
  Yafete Yemuru
  Conrad Meyer
  
<Purpose>
  Provides a method for retrieving content from web servers using the HTTP
  protocol. The content can be accessed as a file like object, or saved to
  a file or returned as a string.
"""



repyhelper.translate_and_import('urlparse.repy')
repyhelper.translate_and_import('sockettimeout.repy')
repyhelper.translate_and_import('urllib.repy')



class HttpConnectionError(Exception):
  """
  Error indicating that the web server has unexpectedly dropped the
  connection.
  """




class HttpBrokenServerError(Exception):
  """
  Error indicating that the web server has sent us complete garbage instead
  of something resembling HTTP.
  """




def httpretrieve_open(url, querydata=None, postdata=None,\
    httpheaders=None, proxy=None, timeout=None):
  """
  <Purpose>
     Returns a file-like object that can be used to read the content from
     an HTTP server. Follows 3xx redirects.

  <Arguments>
    url:
           The URL to perform a GET or POST request on.
    postdata (optional):
           A dictionary of form data or a string to POST to the server.
           Passing a non-None value results in a POST request being sent
           to the server.
    querydata (optional):
           A dictionary of form data or a string to send as the query
           string to the server.

           If postdata is omitted, the URL is retrieved with GET. If
           both postdata and querydata are omitted, there is no query
           string sent in the request.

           For both querydata and postdata, strings are sent *unmodified*.
           This means you probably should encode them first, with
           urllib_quote().
    httpheaders (optional):
           A dictionary of supplemental HTTP request headers to add to the
           request.
    proxy (optional):
           A proxy server 2-tuple to bind to: ('host', port).       
    timeout (optional):
           A timeout for establishing a connection to the web server,
           sending headers, and reading the response headers.

           If excluded or None, never times out.

  <Exceptions>
    ValueError if given an invalid URL, or malformed limit or timeout
      values. This is also raised if the user attempts to call a method
      on the file-like object after closing it.

    HttpConnectionError if opening the connection fails, or if the
      connection is closed by the server before we expect.

    SocketTimeoutError if the timeout is exceeded.

    HttpBrokenServerError if the response or the Location response header
      is malformed.

  <Side Effects>
    None

  <Returns>
    Returns a file-like object which can be used to read the body of
    the response from the web server. The protocol version spoken by the
    server, status code, and response headers are available as members of
    the object.
  """

  starttimefloat = getruntime()

  # Check if the URL is valid and get host, path, port and query
  parsedurldict = urlparse_urlsplit(url)
  hoststr = parsedurldict['hostname']
  pathstr = parsedurldict['path']
  portint = parsedurldict.get('port')
  portint = portint or 80

  if parsedurldict['scheme'] != 'http':
    raise ValueError("URL doesn't seem to be for the HTTP protocol.")
  if hoststr is None:
    raise ValueError("Missing hostname.")
  if parsedurldict['query'] is not None and parsedurldict['query'] != "":
    raise ValueError("URL cannot include a query string.")

  # Typical HTTP sessions consist of (optionally, a series of pairs of) HTTP
  # requests followed by HTTP responses. These happen serially.

  # JAC: Set this up so that we can raise the right error if the 
  # timeout_openconn doesn't work.
  sockobj = None

  # Open connection to the web server
  try:
    if proxy is not None:
      # if there is a proxy, open a connection with the proxy instead of the actual server
      # use the timeout we are given (or none)
      sockobj = timeout_openconn(proxy[0], proxy[1], timeout=timeout)  
    else:
      # if there is no proxy open a connection with server directly
      # use the timeout we are given (or none)
      sockobj = timeout_openconn(hoststr, portint, timeout=timeout)

  except Exception, e:
    # If a socket object was created, we want to clean in up.
    if sockobj:
      sockobj.close()

    if repr(e).startswith("timeout("):
      raise HttpConnectionError("Socket timed out connecting to host/port.")
    raise

  try:
    # Builds the HTTP request:
    httprequeststr = _httpretrieve_build_request(hoststr, portint, pathstr, \
        querydata, postdata, httpheaders, proxy)

    # Send the full HTTP request to the web server.
    _httpretrieve_sendall(sockobj, httprequeststr)

    # Now, we're done with the HTTP request part of the session, and we need
    # to get the HTTP response.

    # Check if we've timed out (if the user requested a timeout); update the
    # socket timeout to reflect the time taken sending the request.
    if timeout is None:
      sockobj.settimeout(0)
    elif getruntime() - starttimefloat >= timeout:
      raise SocketTimeoutError("Timed out")
    else:
      sockobj.settimeout(timeout - (getruntime() - starttimefloat))

    # Receive the header lines from the web server (a series of CRLF-terminated
    # lines, terminated by an empty line, or by the server closing the
    # connection.
    headersstr = ""
    while not headersstr.endswith("\r\n\r\n"):
      try:
        # This should probably be replaced with page-sized reads in the future,
        # but for now, the behavior is at least correct.
        headersstr += sockobj.recv(1)
      except Exception, e:
        if str(e) == "Socket closed":
          break
        else:
          raise

    httpheaderlist = headersstr.split("\r\n")
    # Ignore (a) trailing blank line(s) (for example, the response header-
    # terminating blank line).
    while len(httpheaderlist) > 0 and httpheaderlist[-1] == "":
      httpheaderlist = httpheaderlist[:-1]

    # Get the status code and status message from the HTTP response.
    statuslinestr, httpheaderlist = httpheaderlist[0], httpheaderlist[1:]

    # The status line should be in the form: "HTTP/1.X NNN SSSSS", where
    # X is 0 or 1, NNN is a 3-digit status code, and SSSSS is a 'user-friendly'
    # string representation of the status code (may contain spaces).
    statuslinelist = statuslinestr.split(' ', 2)

    if len(statuslinelist) < 3:
      raise HttpBrokenServerError("Server returned garbage for HTTP " + \
        "response (status line missing one or more fields).")

    if not statuslinelist[0].startswith('HTTP'):
      raise HttpBrokenServerError("Server returned garbage for HTTP " + \
          "response (invalid response protocol in status line).")

    friendlystatusstr = statuslinelist[2]
    try:
      statusint = int(statuslinelist[1])
    except ValueError, e:
      raise HttpBrokenServerError("Server returned garbage for HTTP " + \
        "response (status code isn't integer).")

    httpheaderdict = _httpretrieve_parse_responseheaders(httpheaderlist)

    # If we got any sort of redirect response, follow the redirect. Note: we
    # do *not* handle the 305 status code (use the proxy as specified in the
    # Location header) at all; I think this is best handled at a higher layer
    # anyway.
    if statusint in (301, 302, 303, 307):
      sockobj.close()
      try:
        redirecturlstr = httpheaderdict["Location"][0]
      except (KeyError, IndexError), ke:
        # When a server returns a redirect status code (3xx) but no Location
        # header, some clients, e.g. Firefox, just show the response body
        # as they would normally for a 2xx or 4xx response. So, I think we
        # should ignore a missing Location header and just return the page
        # to the caller.
        pass
      else:
        # If the server did send a redirect location, let's go there.
        return httpretrieve_open(redirecturlstr)

    # If we weren't requested to redirect, and we didn't, return a read-only
    # file-like object (representing the response body) to the caller.
    return _httpretrieve_filelikeobject(sockobj, httpheaderdict, \
        (statuslinelist[0], statusint, friendlystatusstr))
  
  except:
    # If any exception occured after the socket was open, we want to make
    # sure that the socket is cleaned up if it is still open before we
    # raise the exception.
    if sockobj:
      sockobj.close()

    raise



def httpretrieve_save_file(url, filename, querydata=None, postdata=None, \
    httpheaders=None, proxy=None, timeout=None):
  """
  <Purpose>
    Perform an HTTP request, and save the content of the response to a
    file.

  <Arguments>
    filename:
           The file name to save the response to.
    Other arguments:
           See documentation for httpretrieve_open().

  <Exceptions>
    This function will raise any exception raised by Repy file objects
    in opening, writing to, and closing the file.

    This function will all also raise any exception raised by
    httpretrieve_open(), for the same reasons.

  <Side Effects>
    Writes the body of the response to 'filename'.

  <Returns>
    None
  """

  # Open the output file object and http file-like object.
  outfileobj = open(filename, 'w')
  httpobj = httpretrieve_open(url, querydata=querydata, postdata=postdata, \
      httpheaders=httpheaders, proxy=proxy, timeout=timeout)

  # Repeatedly read from the file-like HTTP object into our file, until the
  # response is finished.
  responsechunkstr = None
  while responsechunkstr != '':
    responsechunkstr = httpobj.read(4096)
    outfileobj.write(responsechunkstr)

  outfileobj.close()
  httpobj.close()




def httpretrieve_get_string(url, querydata=None, postdata=None, \
    httpheaders=None, proxy=None, timeout=30):
  """
  <Purpose>
    Performs an HTTP request on the given URL, using POST or GET,
    returning the content of the response as a string. Uses
    httpretrieve_open.

  <Arguments>
    See httpretrieve_open.

  <Exceptions>
    See httpretrieve_open.

  <Side Effects>
    None.

  <Returns>
    Returns the body of the HTTP response (no headers).
  """

  # Open a read-only file-like object for the HTTP request.
  httpobj = httpretrieve_open(url, querydata=querydata, postdata=postdata, \
      httpheaders=httpheaders, proxy=proxy, timeout=timeout)

  # Read all of the response and return it.
  try:
    return httpobj.read()
  finally:
    httpobj.close()




class _httpretrieve_filelikeobject:
  # This class implements a file-like object used for performing HTTP
  # requests and retrieving responses.

  def __init__(self, sock, headers, httpstatus):
    # The socket-like object connected to the HTTP server. Headers have
    # already been read.
    self._sockobj = sock

    # If this is set, the close() method has already been called, so we
    # don't accept future reads.
    self._fileobjclosed = False

    # This flag is set if we've finished recieving the entire response
    # from the server.
    self._totalcontentisreceived = False

    # This integer represents the number of bytes read so far.
    self._totalread = 0

    # This is the dictionary of HTTP response headers associated with this
    # file-like object.
    self.headers = headers

    # The HTTP status tuple of this response, e.g. ("HTTP/1.0", 200, "OK")
    self.httpstatus = httpstatus



  def read(self, limit=None, timeout=None):
    """
    <Purpose>
      Behaves like Python's file.read(), with the potential to raise
      additional informative exceptions.

    <Arguments>
      limit (optional):
            The maximum amount of data to read. If omitted or None, this
            reads all available data.

    <Exceptions>
      See file.read()'s documentation, as well as that of
      httpretrieve_open().

    <Side Effects>
      None.

    <Returns>
      See file.read().
    """

    # Raise an error if the caller has already close()d this object.
    if self._fileobjclosed:
      raise ValueError("I/O operation on closed file")

    # If we've finished reading everything we can from the server, return the
    # empty string.
    if self._totalcontentisreceived:
      return ''

    lefttoread = None
    if limit is not None:
      lefttoread = limit

      # Sanity check type/value of limit.
      if type(limit) is not int:
        raise TypeError("Expected an integer or None for read() limit")
      elif limit < 0:
        raise ValueError("Expected a non-negative integer for read() limit")

    if timeout is None:
      self._sockobj.settimeout(0)
    else:
      self._sockobj.settimeout(timeout)

    # Try to read up to limit, or until there is nothing left.
    httpcontentstr = ''
    while True:
      try:
        contentchunkstr = self._sockobj.recv(lefttoread or 4096)
      except Exception, e:
        if str(e) == "Socket closed":
          self._totalcontentisreceived = True
          break
        else:
          raise
      
      httpcontentstr += contentchunkstr
      self._totalread += len(contentchunkstr)
      if limit is not None:
        if len(contentchunkstr) == lefttoread:
          break
        else:
          lefttoread -= len(contentchunkstr)
      if contentchunkstr == "":
        self._totalcontentisreceived = True
        break

    return httpcontentstr



  def close(self):
    """
    <Purpose>
      Close the file-like object.

    <Arguments>
      None

    <Exceptions>
      None

    <Side Effects>
      Disconnects from the HTTP server.

    <Returns>
      Nothing
    """
    self._fileobjclosed = True
    self._sockobj.close()




def _httpserver_put_in_headerdict(res, lastheader, lastheader_str):
  # Helper function that tries to put the header into a dictionary of lists,
  # 'res'.
  if lastheader is not None:
    if lastheader not in res:
      res[lastheader] = []
    res[lastheader].append(lastheader_str.strip())




def _httpretrieve_parse_responseheaders(headerlines):
  # Parse rfc822-style headers (this could be abstracted out to an rfc822
  # library that would be quite useful for internet protocols). Returns
  # a dictionary mapping headers to arrays of values. E.g.:
  #
  # Foo: a
  # Bar:
  #   b
  # Bar: c
  #
  # Becomes: {"Foo": ["a"], "Bar": ["b", "c"]}

  # These variables represent the key and value of the last header we found,
  # unless we are parsing the very first header. E.g., if we've just read:
  #   Content-Type: text/html
  # Then, lastheaderkeystr == "Content-Type",
  # lastheadervaluestr == "text/html"

  lastheaderkeystr = None
  lastheadervaluestr = ""

  resdict = {}
  
  if len(headerlines) == 0:
    return {}

  try:
    # Iterate over the request header lines:
    for i in range(len(headerlines)):
      # Lines with leading non-CRLF whitespace characters are part of the
      # previous line (see rfc822 for details).
      if headerlines[i][0] in (" ", "\t") and lastheaderkeystr is not None:
        lastheadervaluestr += headerlines[i]
      else:
        _httpserver_put_in_headerdict(resdict, lastheaderkeystr, lastheadervaluestr)
        lastheaderkeystr, lastheadervaluestr = headerlines[i].split(":", 1)

    # Add the last line to the result dictionary.
    _httpserver_put_in_headerdict(resdict, lastheaderkeystr, lastheadervaluestr)

    return resdict

  except IndexError, idx:
    raise HttpBrokenServerError("Server returned garbage for HTTP" + \
        " response. Bad headers.")




def _httpretrieve_build_request(host, port, path, querydata, postdata, \
    httpheaders, proxy):
  # Builds an HTTP request from these parameters, returning it as
  # a string.

  # Sanity checks:
  if path == "":
    raise ValueError("Invalid path -- empty string.")
  if postdata is not None and type(postdata) not in (str, dict):
    raise TypeError("Postdata should be a dict of form-data or a string")
  if querydata is not None and type(querydata) not in (str, dict):
    raise TypeError("Querydata should be a dict of form-data or a string")
  if httpheaders is not None and type(httpheaders) is not dict:
    raise TypeError("Expected HTTP headers as a dictionary.")

  # Type-conversions:
  if type(querydata) is dict:
    querydata = urllib_quote_parameters(querydata)
  elif querydata is None:
    querydata = ""

  if type(postdata) is dict:
    postdata = urllib_quote_parameters(postdata)

  # Default to GET, unless the caller specifies a message body to send.
  methodstr = "GET"
  if postdata is not None:
    methodstr = "POST"

  # Encode the path and querystring part of the request.
  resourcestr = querydata
  if querydata != "":
    resourcestr = "?" + resourcestr

  # Encode the HTTP request line and headers:
  if proxy is not None:
    # proxy exists thus the request header should include the original requested url  
    requeststr = methodstr + ' http://' + host + ':' + str(port) + path + resourcestr + ' HTTP/1.0\r\n'
  else:
    # there is no proxy; send normal http request   
    requeststr = methodstr + ' ' + path + resourcestr + ' HTTP/1.0\r\n'

  # Make sure there is an httpheaders dict
  if httpheaders is None:
    httpheaders = {}

  # Most servers require a 'Host' header for normal functionality
  # (especially in the case of multiple domains being hosted on a
  # single server). Let's add it to be sure.
  if "Host" not in httpheaders:
    requeststr += "Host: " + host + ':' + str(port) + "\r\n"

  # Add httpheaders's contents to the request string    
  for key, val in httpheaders.items():
    requeststr += key + ": " + str(val) + '\r\n'


  # Affix post-data related headers and content:
  if methodstr == "POST":
    requeststr += 'Content-Length: ' + str(len(postdata)) + '\r\n'

  # The empty line terminates HTTP headers.
  requeststr += '\r\n'

  # If we're a POST request, affix any requested data to the message body.
  if methodstr == "POST":
    requeststr += postdata

  return requeststr




def _httpretrieve_sendall(sockobj, datastr):
  # Helper function that attempts to dump all of the data in datastr to the
  # socket sockobj (data is any arbitrary bytes).
  while len(datastr) > 0:
    datastr = datastr[sockobj.send(datastr):]

### Automatically generated by repyhelper.py ### /chalmers/users/vikbergl/distributedGit/Distributed/demokit/httpretrieve.repy
