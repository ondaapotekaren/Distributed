# -*- coding: utf-8 -*-
### Automatically generated by repyhelper.py ### /Users/isakeriksson/Documents/Skola/TDA596/Distributed/demokit/rsa.repy

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
  rsa.repy

<Started>
  2008-04-23

<Author>
  Modified by Anthony Honstain from the following code:
    PyCrypto which is authored by Dwayne C. Litzenberger
    
    Seattle's origional rsa.repy which is Authored by:
      Adapted by Justin Cappos from the version by:
        author = "Sybren Stuvel, Marloes de Boer and Ivo Tamboer"

<Purpose>
  This is the main interface for using the ported RSA implementation.
    
<Notes on port>
  The random function can not be defined with the initial construction of
  the RSAImplementation object, it is hard coded into number_* functions.
    
"""

repyhelper.translate_and_import('random.repy')
repyhelper.translate_and_import('pycryptorsa.repy')
    
     
        
def rsa_gen_pubpriv_keys(bitsize):
  """
  <Purpose>
    Will generate a new key object with a key size of the argument
    bitsize and return it. A recommended value would be 1024.
   
  <Arguments>
    bitsize:
           The number of bits that the key should have. This
           means the modulus (publickey - n) will be in the range
           [2**(bitsize - 1), 2**(bitsize) - 1]           

  <Exceptions>
    None

  <Side Effects>
    Key generation will result in call to metered function for
    random data.

  <Return>
    Will return a key object that rsa_encrypt, rsa_decrypt, rsa_sign,
    rsa_validate can use to preform their tasts.
  """

  rsa_implementation = RSA_RSAImplementation()
  
  # The key returned is of type RSA_RSAobj which is derived 
  # from pubkey_pubkey, and wraps a _slowmath_RSAKey object
  rsa_key = rsa_implementation.generate(bitsize)
  
  return ({'e':rsa_key.e, 'n':rsa_key.n },
          {'d':rsa_key.d, 'p':rsa_key.p, 'q':rsa_key.q })
  


def _rsa_keydict_to_keyobj(publickey = None, privatekey = None):
  """
  <Purpose>
    Will generate a new key object using the data from the dictionary
    passed. This is used because the pycrypto scheme uses
    a key object but we want backwards compatibility which
    requires a dictionary. 
  
  <Arguments>
    publickey:
              Must be a valid publickey dictionary of 
              the form {'n': 1.., 'e': 6..} with the keys
              'n' and 'e'.
    privatekey:
               Must be a valid privatekey dictionary of 
               the form {'d':1.., 'p':1.. 'q': 1..} with
               the keys 'd', 'p', and 'q'
  <Exceptions>
    TypeError if neither argument is provided.
    ValueError if public or private key is invalid.
    
  <Side Effects>
    None  
    
  <Return>
    Will return a key object that rsa_encrypt, rsa_decrypt, rsa_sign,
    rsa_validate will use.
  """
  if publickey is not None:
    if not rsa_is_valid_publickey(publickey):
      raise ValueError, "Invalid public key"
  
  if privatekey is not None:    
    if not rsa_is_valid_privatekey(privatekey):
      raise ValueError, "Invalid private key"
    
  if publickey is None and privatekey is None:
    raise TypeError("Must provide either private or public key dictionary")

  if publickey is None: 
    publickey = {}
  if privatekey is None: 
    privatekey = {}
  
  n = None 
  e = None
  d = None
  p = None
  q = None
  
  if 'd' in privatekey: 
    d = long(privatekey['d'])
  if 'p' in privatekey: 
    p = long(privatekey['p'])
  if 'q' in privatekey: 
    q = long(privatekey['q'])  
  
  if 'n' in publickey: 
    n = long(publickey['n'])
  # n is needed for a private key even thought it is not
  # part of the standard public key dictionary.
  else: n = p*q  
  if 'e' in publickey: 
    e = long(publickey['e'])
  
  rsa_implementation = RSA_RSAImplementation()
  rsa_key = rsa_implementation.construct((n,e,d,p,q))
  
  return rsa_key


def rsa_encrypt(message, publickey):
  """
  <Purpose>
    Will use the key to encrypt the message string.
    
    If the string is to large to be encrypted it will be broken 
    into chunks that are suitable for the keys modulus, 
    by the _rsa_chopstring function.
  
  <Arguments>
    message:
            A string to be encrypted, there is no restriction on size.
      
    publickey:
              Must be a valid publickey dictionary of 
              the form {'n': 1.., 'e': 6..} with the keys
              'n' and 'e'.
      
  <Exceptions>
    ValueError if public key is invalid.
    
    _slowmath_error if the key object lacks a public key 
    (elements 'e' and 'n').
  

  <Side Effects>
    None
    
  <Return>
    Will return a string with the cypher text broken up and stored 
    in the seperate integer representation. For example it might
    be similar to the string " 1422470 3031373 65044827" but with
    much larger integers.
  """
  
  # A key object is created to interact with the PyCrypto
  # encryption suite. The object contains key data and
  # the necessary rsa functions.
  temp_key_obj = _rsa_keydict_to_keyobj(publickey)
  
  return _rsa_chopstring(message, temp_key_obj, temp_key_obj.encrypt)



def rsa_decrypt(cypher, privatekey):
  """
  <Purpose>
    Will use the private key to decrypt the cypher string.
    
    
    If the plaintext string was to large to be encrypted it will 
    use _rsa_gluechops and _rsa_unpicklechops to reassemble the
    origional plaintext after the individual peices are decrypted. 
  
  <Arguments>
    cypher:
           The encrypted string that was returned by rsa_encrypt.
           Example:
             Should have the form " 142247030 31373650 44827705"
    
    privatekey:
               Must be a valid privatekey dictionary of 
               the form {'d':1.., 'p':1.. 'q': 1..} with
               the keys 'd', 'p', and 'q'
    
  <Exceptions>
    ValueError if private key is invalid.
    
    _slowmath_error if the key object lacks a private key 
    (elements 'd' and 'n').
      
  <Return>
    This will return the plaintext string that was encrypted
    with rsa_encrypt.
  
  """
    
  # A key object is created to interact with the PyCrypto
  # encryption suite. The object contains key data and
  # the necessary rsa functions.
  temp_key_obj = _rsa_keydict_to_keyobj(privatekey = privatekey)  
  
  return _rsa_gluechops(cypher, temp_key_obj, temp_key_obj.decrypt)
  


def rsa_sign(message, privatekey):
  """
  <Purpose>
    Will use the key to sign the plaintext string.
        
  <None>
    If the string is to large to be encrypted it will be broken 
    into chunks that are suitable for the keys modulus, 
    by the _rsa_chopstring function. 
  
  <Arguments>
    message:
            A string to be signed, there is no restriction on size.
      
    privatekey:
               Must be a valid privatekey dictionary of 
               the form {'d':1.., 'p':1.. 'q': 1..} with
               the keys 'd', 'p', and 'q'
      
  <Exceptions>
    ValueError if private key is invalid.
    
    _slowmath_error if the key object lacks a private key 
    (elements 'd' and 'n').

  <Side Effects>
    None
    
  <Return>
    Will return a string with the cypher text broken up and stored 
    in the seperate integer representation. For example it might
    be similar to the string " 1422470 3031373 65044827" but with
    much larger integers.
    
  """
  
  # A key object is created to interact with the PyCrypto
  # encryption suite. The object contains key data and
  # the necessary rsa functions.
  temp_key_obj = _rsa_keydict_to_keyobj(privatekey = privatekey) 
  
  return _rsa_chopstring(message, temp_key_obj, temp_key_obj.sign)



def rsa_verify(cypher, publickey):
  """
  <Purpose>
    Will use the private key to decrypt the cypher string.
    
    
    If the plaintext string was to large to be encrypted it will 
    use _rsa_gluechops and _rsa_unpicklechops to reassemble the
    origional plaintext after the individual peices are decrypted. 
  
  <Arguments>
    cypher:
           The signed string that was returned by rsa_sign.
           
           Example:
             Should have the form " 1422470 3031373 65044827"
    
    publickey:
              Must be a valid publickey dictionary of 
              the form {'n': 1.., 'e': 6..} with the keys
              'n' and 'e'.
    
  <Exceptions>
    ValueError if public key is invalid.
    
    _slowmath_error if the key object lacks a public key 
    (elements 'e' and 'n').    
    
  <Side Effects>
    None
    
  <Return>
    This will return the plaintext string that was signed by
    rsa_sign.
    
  """
  
  # A key object is created to interact with the PyCrypto
  # encryption suite. The object contains key data and
  # the necessary rsa functions.  
  temp_key_obj = _rsa_keydict_to_keyobj(publickey)
  
  return _rsa_gluechops(cypher, temp_key_obj, temp_key_obj.verify)  
  


def _rsa_chopstring(message, key, function):
  """
  <Purpose>
    Splits 'message' into chops that are at most as long as 
    (key.size() / 8 - 1 )bytes. 
    
    Used by 'encrypt' and 'sign'.
    
  <Notes on chopping>
    If a 1024 bit key was used, then the message would be
    broken into length x, where 1<= x <= 126.
    (1023 / 8) - 1 = 126
    After being converted to a long, the result would
    be at most 1009 bits and at least 9 bits.
    
      maxstring = chr(1) + chr(255)*126
      minstring = chr(1) + chr(0)
      number_bytes_to_long(maxstring) 
      => 2**1009 - 1
      number_bytes_to_long(minstring)
      => 256
    
    Given the large exponent used by default (65537)
    this will ensure that small message are okay and that
    large messages do not overflow and cause pycrypto to 
    silently fail (since its behavior is undefined for a 
    message greater then n-1 (where n in the key modulus).   
    
    WARNING: key.encrypt could have undefined behavior
    in the event a larger message is encrypted.
  
  """
  
  msglen = len(message)
  
  # the size of the key in bits, minus one
  # so if the key was a 1024 bits, key.size() returns 1023
  nbits = key.size() 
  
  # JAC: subtract a byte because we're going to add an extra char on the front
  # to properly handle leading \000 bytes and ensure no loss of information.
  nbytes = int(nbits / 8) - 1
  blocks = int(msglen / nbytes)
  
  if msglen % nbytes > 0:
    blocks += 1

  # cypher will contain the integers returned from either
  # sign or encrypt.
  cypher = []
    
  for bindex in range(blocks):
    offset = bindex * nbytes
    block = message[offset:offset+nbytes]
    # key.encrypt will return a bytestring
    # IMPORTANT: The block is padded with a '\x01' to ensure
    # that no information is lost when the key transforms the block
    # into its long representation prior to encryption. It is striped
    # off in _rsa_gluechops.
    # IMPORTANT: both rsa_encrypt and rsa_sign which use _rsa_chopstring
    # will pass the argument 'function' a reference to encrypt or
    # sign from the baseclass publickey.publickey, they will return
    # the cypher as a tuple, with the first element being the desired
    # integer result.  
    # Example result :   ( 1023422341232124123212 , )
    # IMPORTANT: the second arguement to function is ignored
    # by PyCrypto but required for different algorithms.
    cypher.append( function(chr(1) + block, '0')[0])

  return _rsa_picklechops(cypher)



def _rsa_gluechops(chops, key, function):
  """
  Glues chops back together into a string. Uses _rsa_unpicklechops to
  get a list of cipher text blocks in byte form, then key.decrypt
  is used and the '\x01' pad is striped.
  
  Example 
    chops=" 126864321546531240600979768267740190820"
    after _rsa_unpicklechops(chops)
    chops=['\x0b\xed\xf5\x0b;G\x80\xf4\x06+\xff\xd3\xf8\x1b\x8f\x9f']
  
  Used by 'decrypt' and 'verify'.
  """
  message = ""

  # _rsa_unpicklechops returns a list of the choped encrypted text
  # Will be a list with elements of type long
  chops = _rsa_unpicklechops(chops)    
  for cpart in chops:
    # decrypt will return the plaintext message as a bytestring   
    message += function(cpart)[1:] # Remove the '\x01'
        
  return message



def _rsa_picklechops(chops):
  """previously used to pickles and base64encodes it's argument chops"""
  
  retstring = ''
  for item in chops:  
    # the elements of chops will be of type long
    retstring = retstring + ' ' + str(item)
  return retstring



def _rsa_unpicklechops(string):
  """previously used to base64decode and unpickle it's argument string"""
  
  retchops = []
  for item in string.split():
    retchops.append(long(item))
  return retchops



def rsa_is_valid_privatekey(key):
  """
  <Purpose>
     This tries to determine if a key is valid.   If it returns False, the
     key is definitely invalid.   If True, the key is almost certainly valid
  
  <Arguments>
    key:
        A dictionary of the form {'d':1.., 'p':1.. 'q': 1..} 
        with the keys 'd', 'p', and 'q'    
                  
  <Exceptions>
    None

  <Side Effects>
    None
    
  <Return>
    If the key is valid, True will be returned. Otherwise False will
    be returned.
     
  """
  # must be a dict
  if type(key) is not dict:
    return False

  # missing the right keys
  if 'd' not in key or 'p' not in key or 'q' not in key:
    return False

  # has extra data in the key
  if len(key) != 3:
    return False

  for item in ['d', 'p', 'q']:
    # must have integer or long types for the key components...
    if type(key[item]) is not int and type(key[item]) is not long:
      return False

  if number_isPrime(key['p']) and number_isPrime(key['q']):
    # Seems valid...
    return True
  else:
    return False



def rsa_is_valid_publickey(key):
  """
  <Purpose>
    This tries to determine if a key is valid.   If it returns False, the
    key is definitely invalid.   If True, the key is almost certainly valid
  
  <Arguments>
    key:
        A dictionary of the form {'n': 1.., 'e': 6..} with the 
        keys 'n' and 'e'.  
                  
  <Exceptions>
    None

  <Side Effects>
    None
    
  <Return>
    If the key is valid, True will be returned. Otherwise False will
    be returned.
    
  """
  # must be a dict
  if type(key) is not dict:
    return False

  # missing the right keys
  if 'e' not in key or 'n' not in key:
    return False

  # has extra data in the key
  if len(key) != 2:
    return False

  for item in ['e', 'n']:
    # must have integer or long types for the key components...
    if type(key[item]) is not int and type(key[item]) is not long:
      return False

  if key['e'] < key['n']:
    # Seems valid...
    return True
  else:
    return False
  
  

def rsa_publickey_to_string(publickey):
  """
  <Purpose>
    To convert a publickey to a string. It will read the
    publickey which should a dictionary, and return it in
    the appropriate string format.
  
  <Arguments>
    publickey:
              Must be a valid publickey dictionary of 
              the form {'n': 1.., 'e': 6..} with the keys
              'n' and 'e'.
    
  <Exceptions>
    ValueError if the publickey is invalid.

  <Side Effects>
    None
    
  <Return>
    A string containing the publickey. 
    Example: if the publickey was {'n':21, 'e':3} then returned
    string would be "3 21"
  
  """
  if not rsa_is_valid_publickey(publickey):
    raise ValueError, "Invalid public key"

  return str(publickey['e'])+" "+str(publickey['n'])


def rsa_string_to_publickey(mystr):
  """
  <Purpose>
    To read a private key string and return a dictionary in 
    the appropriate format: {'n': 1.., 'e': 6..} 
    with the keys 'n' and 'e'.
  
  <Arguments>
    mystr:
          A string containing the publickey, should be in the format
          created by the function rsa_publickey_to_string.
          Example if e=3 and n=21, mystr = "3 21"
          
  <Exceptions>
    ValueError if the string containing the privateky is 
    in a invalid format.

  <Side Effects>
    None
    
  <Return>
    Returns a publickey dictionary of the form 
    {'n': 1.., 'e': 6..} with the keys 'n' and 'e'.
  
  """
  if len(mystr.split()) != 2:
    raise ValueError, "Invalid public key string"
  
  return {'e':long(mystr.split()[0]), 'n':long(mystr.split()[1])}



def rsa_privatekey_to_string(privatekey):
  """
  <Purpose>
    To convert a privatekey to a string. It will read the
    privatekey which should a dictionary, and return it in
    the appropriate string format.
  
  <Arguments>
    privatekey:
               Must be a valid privatekey dictionary of 
               the form {'d':1.., 'p':1.. 'q': 1..} with
               the keys 'd', 'p', and 'q'    
                  
  <Exceptions>
    ValueError if the privatekey is invalid.

  <Side Effects>
    None
    
  <Return>
    A string containing the privatekey. 
    Example: if the privatekey was {'d':21, 'p':3, 'q':7} then returned
    string would be "21 3 7"
  
  """
  if not rsa_is_valid_privatekey(privatekey):
    raise ValueError, "Invalid private key"

  return str(privatekey['d'])+" "+str(privatekey['p'])+" "+str(privatekey['q'])



def rsa_string_to_privatekey(mystr):
  """
  <Purpose>
    To read a private key string and return a dictionary in 
    the appropriate format: {'d':1.., 'p':1.. 'q': 1..} 
    with the keys 'd', 'p', and 'q' 
  
  <Arguments>
    mystr:
          A string containing the privatekey, should be in the format
          created by the function rsa_privatekey_to_string.
          Example mystr = "21 7 3"
             
  <Exceptions>
    ValueError if the string containing the privateky is 
    in a invalid format.

  <Side Effects>
    None
    
  <Return>
    Returns a privatekey dictionary of the form 
    {'d':1.., 'p':1.. 'q': 1..} with the keys 'd', 'p', and 'q'.
  
  """
  if len(mystr.split()) != 3:
    raise ValueError, "Invalid private key string"
  
  return {'d':long(mystr.split()[0]), 'p':long(mystr.split()[1]), 'q':long(mystr.split()[2])}



def rsa_privatekey_to_file(key,filename):
  """
  <Purpose>
    To write a privatekey to a file. It will convert the
    privatekey which should a dictionary, to the appropriate format
    and write it to a file, so that it can be read by
    rsa_file_to_privatekey.
  
  <Arguments>
    privatekey:
               Must be a valid privatekey dictionary of 
               the form {'d':1.., 'p':1.. 'q': 1..} with
               the keys 'd', 'p', and 'q'
    filename:
             The string containing the name for the desired
             publickey file.
                  
  <Exceptions>
    ValueError if the privatekey is invalid.

    IOError if the file cannot be opened.

  <Side Effects>
    file(filename, "w") will be written to.
    
  <Return>
    None
  
  """
  
  if not rsa_is_valid_privatekey(key):
    raise ValueError, "Invalid private key"

  fileobject = file(filename,"w")
  fileobject.write(rsa_privatekey_to_string(key))
  fileobject.close()



def rsa_file_to_privatekey(filename):
  """
  <Purpose>
    To read a file containing a key that was created with 
    rsa_privatekey_to_file and return it in the appropriate 
    format: {'d':1.., 'p':1.. 'q': 1..} with the keys 'd', 'p', and 'q' 
  
  <Arguments>
    filename:
             The name of the file containing the privatekey.
             
  <Exceptions>
    ValueError if the file contains an invalid private key string.
    
    IOError if the file cannot be opened.

  <Side Effects>
    None
    
  <Return>
    Returns a privatekey dictionary of the form 
    {'d':1.., 'p':1.. 'q': 1..} with the keys 'd', 'p', and 'q'.
  
  """
  fileobject = file(filename,'r')
  privatekeystring = fileobject.read()
  fileobject.close()

  return rsa_string_to_privatekey(privatekeystring)



def rsa_publickey_to_file(publickey, filename):
  """
  <Purpose>
    To write a publickey to a file. It will convert the
    publickey which should a dictionary, to the appropriate format
    and write it to a file, so that it can be read by
    rsa_file_to_publickey.
  
  <Arguments>
    publickey:
              Must be a valid publickey dictionary of 
              the form {'n': 1.., 'e': 6..} with the keys
              'n' and 'e'.
    filename:
             The string containing the name for the desired
             publickey file.
         
  <Exceptions>
    ValueError if the publickey is invalid.
    
    IOError if the file cannot be opened.

  <Side Effects>
    file(filename, "w") will be written to.
    
  <Return>
    None
  
  """
  
  if not rsa_is_valid_publickey(publickey):
    raise ValueError, "Invalid public key"

  fileobject = file(filename,"w")
  fileobject.write(rsa_publickey_to_string(publickey))
  fileobject.close()



def rsa_file_to_publickey(filename):
  """
  <Purpose>
    To read a file containing a key that was created with 
    rsa_publickey_to_file and return it in the appropriate 
    format:  {'n': 1.., 'e': 6..} with the keys 'n' and 'e'.
  
  <Arguments>
    filename:
             The name of the file containing the publickey.
             
  <Exceptions>
    ValueError if the file contains an invalid public key string.
    
    IOError if the file cannot be opened.

  <Side Effects>
    None
    
  <Return>
    Returns a publickey dictionary of the form 
    {'n': 1.., 'e': 6..} with the keys 'n' and 'e'.
  
  """
  fileobject = file(filename,'r')
  publickeystring = fileobject.read()
  fileobject.close()

  return rsa_string_to_publickey(publickeystring)


def rsa_matching_keys(privatekey, publickey):
  """
  <Purpose>
    Determines if a pair of public and private keys match and allow 
    for encryption/decryption.
  
  <Arguments>
    privatekey: The private key*
    publickey:  The public key*
    
    * The dictionary structure, not the string or file name
  <Returns>
    True, if they can be used. False otherwise.
  """
  # We will attempt to encrypt then decrypt and check that the message matches
  testmessage = "A quick brown fox."
  
  # Encrypt with the public key
  encryptedmessage = rsa_encrypt(testmessage, publickey)

  # Decrypt with the private key
  try:
    decryptedmessage = rsa_decrypt(encryptedmessage, privatekey)
  except TypeError:
    # If there was an exception, assume the keys are to blame
    return False
  except OverflowError:
    # There was an overflow while decrypting, blame the keys
    return False  
  
  # Test for a match
  return (testmessage == decryptedmessage)

### Automatically generated by repyhelper.py ### /Users/isakeriksson/Documents/Skola/TDA596/Distributed/demokit/rsa.repy
