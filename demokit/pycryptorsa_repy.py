# -*- coding: utf-8 -*-
### Automatically generated by repyhelper.py ### /chalmers/users/isaker/Distributed/Distributed/demokit/pycryptorsa.repy

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
  pycrypto.repy

<Started>
  2009-01

<Author>
  Modified by Anthony Honstain from the following code:
    PyCrypto which is authored by Dwayne C. Litzenberger
    
<Purpose>
  This file provides the encryption functionality for rsa.repy. 
  This code has been left as close to origional as possible with
  the notes about changes made to enable for easier modification
  if pycrypto is updated. 
  
  It contains:
    pubkey.py
    RSA.py 
    _RSA.py
    _slowmath.py
    number.py

"""

repyhelper.translate_and_import('random.repy')

#
#   pubkey.py : Internal functions for public key operations
#
#  Part of the Python Cryptography Toolkit
#
# Distribute and use freely; there are no restrictions on further
# dissemination and usage except those imposed by the laws of your
# country of residence.  This software is provided "as is" without
# warranty of fitness for use or suitability for any purpose, express
# or implied. Use at your own risk or not at all.
#

"""
<Modified>
  Anthony
  
  Apr 7:
    Modified behavior of _verify to maintain backwards compatibility.
  Apr 18:
    Adjusted sign to return a long instead of bytes.
    Adjusted verify to accept a long instead of bytes.
  Apr 27:
    Modified encrypt to return a long.
    Modified decrypt to accept a long as its cipher text argument.
    Large change, dropped out behavior for taking tuples, since
    it will never be used in this way for RSA, pubkey has that 
    behavior because of DSA and ElGamal.
    
  NEW ARGUEMENT TYPE AND RETURN TYPE OF
  ENCRYPT DECRYPT SIGN and VERIFY:
  
           Argument Type        Return Type
  --------------------------------------------
  encrypt  |  byte                (long,)
  decrypt  |  long                byte
  sign     |  byte                (long,)
  verify   |  long                byte  

"""

# Anthony stage1
#__revision__ = "$Id$"

# Anthony stage 2, allusage of types.StringType or types.TupleType
# were replaced with type("") and type((1,1))
#import types

# Anthony stage 2, removed the warning completely
#import warnings

# Anthony stage1
#from number import *
#import number  #stage 2

# Basic public key class
class pubkey_pubkey:
    def __init__(self):
        pass

    # Anthony - removed because we are not using pickle
    #def __getstate__(self):
    #    """To keep key objects platform-independent, the key data is
    #    converted to standard Python long integers before being
    #    written out.  It will then be reconverted as necessary on
    #    restoration."""
    #    d=self.__dict__
    #    for key in self.keydata:
    #        if d.has_key(key): d[key]=long(d[key])
    #    return d
    #
    #def __setstate__(self, d):
    #    """On unpickling a key object, the key data is converted to the big
    #    number representation being used, whether that is Python long
    #    integers, MPZ objects, or whatever."""
    #    for key in self.keydata:
    #        if d.has_key(key): self.__dict__[key]=bignum(d[key])

    def encrypt(self, plaintext, K):
        """encrypt(plaintext:string|long, K:string|long) : tuple
        Encrypt the string or integer plaintext.  K is a random
        parameter required by some algorithms.
        """
        # Anthony - encrypt now simply returns the ciphertext
        # as a long.
        wasString=0
        if isinstance(plaintext, type("")):
            # Anthony stage1 added number.bytes_to_long(
            plaintext=number_bytes_to_long(plaintext) ; wasString=1
        #if isinstance(K, type("")):
        #    # Anthony stage1 added number.bytes_to_long(
        #    K=number_bytes_to_long(K)
        ciphertext=self._encrypt(plaintext, K)
        # Anthony stage1 added number.long_to_bytes(
        #if wasString: return tuple(map(number_long_to_bytes, ciphertext))
        #else: return ciphertext
        return ciphertext

    def decrypt(self, ciphertext):
        """decrypt(ciphertext:tuple|string|long): string
        Decrypt 'ciphertext' using this key.
        """
        # Anthony - decrypt now accepts the arguement ciphertext
        # as a long.
        #wasString=0
        #if not isinstance(ciphertext, type((1,1))):
        #    ciphertext=(ciphertext,)
        #if isinstance(ciphertext[0], type("")):
        #    # Anthony stage1 added number.bytes_to_long
        #    ciphertext=tuple(map(number_bytes_to_long, ciphertext)) ; wasString=1
        plaintext=self._decrypt(ciphertext)
        ## Anthony stage1 added number.long_to_bytes(
        #if wasString: return number_long_to_bytes(plaintext)
        #else: return plaintext
        return number_long_to_bytes(plaintext)

    def sign(self, M, K):
        """sign(M : string|long, K:string|long) : tuple
        Return a tuple containing the signature for the message M.
        K is a random parameter required by some algorithms.
        """
        if (not self.has_private()):
            raise error, 'Private key not available in this object'
        # Anthony stage1 added number.bytes_to_long(
        if isinstance(M, type("")): M=number_bytes_to_long(M)
        if isinstance(K, type("")): K=number_bytes_to_long(K)
        # Anthony - modified to provide backwards compatability - required for
        # pycrypto unittest.
        #return self._sign(M, K)
        # Anthony - Apr18 adjusted to return a long instead of bytes
        #return (number_long_to_bytes(self._sign(M, K)[0]),)
        return (self._sign(M, K)[0], )

    def verify(self, signature):    
    # Anthony - modified to provide backwards compatability - required for 
    # pycrypto unittest.
    #def verify (self, M, signature):
    #    """verify(M:string|long, signature:tuple) : bool
    #    Verify that the signature is valid for the message M;
    #    returns true if the signature checks out.
    #    """
    #    ## Anthony stage1 added number.bytes_to_long(
    #    if isinstance(M, type("")): M=number_bytes_to_long(M)
    #    return self._verify(M, signature)
    
        # Anthony - Apr18 adjusted to return a long instead of bytes    
        #return number_long_to_bytes(self._verify(number_bytes_to_long(signature)))
        return number_long_to_bytes(self._verify(signature))
        
    # Anthony stage 2, removing warnings import.
    # alias to compensate for the old validate() name
    #def validate (self, M, signature):
    #    warnings.warn("validate() method name is obsolete; use verify()",
    #                  DeprecationWarning)

    def blind(self, M, B):
        """blind(M : string|long, B : string|long) : string|long
        Blind message M using blinding factor B.
        """
        wasString=0
        if isinstance(M, type("")):
            # Anthony stage1 added number.bytes_to_long(
            M=number_bytes_to_long(M) ; wasString=1
        # Anthony stage1 added number.bytes_to_long(
        if isinstance(B, type("")): B=number_bytes_to_long(B)
        blindedmessage=self._blind(M, B)
        # Anthony stage1 added number.long_to_bytes(
        if wasString: return number_long_to_bytes(blindedmessage)
        else: return blindedmessage

    def unblind(self, M, B):
        """unblind(M : string|long, B : string|long) : string|long
        Unblind message M using blinding factor B.
        """
        wasString=0
        if isinstance(M, type("")):
            # Anthony stage1 added number.bytes_to_long(
            M=number_bytes_to_long(M) ; wasString=1
        # Anthony stage1 added number.bytes_to_long(
        if isinstance(B, type("")): B=number_bytes_to_long(B)
        unblindedmessage=self._unblind(M, B)
        # Anthony stage1 added number.long_to_bytes(
        if wasString: return number_long_to_bytes(unblindedmessage)
        else: return unblindedmessage


    # The following methods will usually be left alone, except for
    # signature-only algorithms.  They both return Boolean values
    # recording whether this key's algorithm can sign and encrypt.
    def can_sign (self):
        """can_sign() : bool
        Return a Boolean value recording whether this algorithm can
        generate signatures.  (This does not imply that this
        particular key object has the private information required to
        to generate a signature.)
        """
        return 1

    def can_encrypt (self):
        """can_encrypt() : bool
        Return a Boolean value recording whether this algorithm can
        encrypt data.  (This does not imply that this
        particular key object has the private information required to
        to decrypt a message.)
        """
        return 1

    def can_blind (self):
        """can_blind() : bool
        Return a Boolean value recording whether this algorithm can
        blind data.  (This does not imply that this
        particular key object has the private information required to
        to blind a message.)
        """
        return 0

    # The following methods will certainly be overridden by
    # subclasses.

    def size (self):
        """size() : int
        Return the maximum number of bits that can be handled by this key.
        """
        return 0

    def has_private (self):
        """has_private() : bool
        Return a Boolean denoting whether the object contains
        private components.
        """
        return 0

    def publickey (self):
        """publickey(): object
        Return a new key object containing only the public information.
        """
        return self
    
    # Anthony - removed, not using pickle
    #def __eq__ (self, other):
    #    """__eq__(other): 0, 1
    #    Compare us to other for equality.
    #    """
    #    return self.__getstate__() == other.__getstate__()
        # -*- coding: utf-8 -*-
#
#  PublicKey/RSA.py : RSA public key primitive
#
# Copyright (C) 2008  Dwayne C. Litzenberger <dlitz@dlitz.net>
#
# =======================================================================
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# =======================================================================

"""RSA public-key cryptography algorithm."""

"""
<Modified>  
  Anthony 
  Feb 9:
    removed the import of Crypto.Util.python_compat, dont need 
    to support python 2.1 ..
  
    Removed _fastmath import and Crypto Random
  
  Feb 15:
    removed code that set a Random function.
    
  Apr 7:
    Modified behavior of _verify to maintain backwars compatibility.
  Apr 27:
    Modified decrypt to accept a long as its cipher text argument.
    Large change, dropped out behavior for taking tuples, since
    it will never be used in this way for RSA, pubkey has that 
    behavior because of DSA and ElGamal.
  Oct 5 2009:
    Modified RSA-RSAobj.__init__ to correctly reload the required
    key values, the code was using getattr but this is no longer
    allowed by repy.
  
"""
# Anthony stage 1
#__revision__ = "$Id$"

# Anthony stage 2
#__all__ = ['generate', 'construct', 'error']

# Anthony
#from Crypto.Util.python_compat import *

# Anthony removing all imports for stage 2
#import _RSA    
#import _slowmath
#import pubkey

# Anthony - not porting Random package yet.
#from Crypto import Random

# Anthony
#try:
#    from Crypto.PublicKey import _fastmath
#except ImportError:
#    _fastmath = None

class RSA_RSAobj(pubkey_pubkey):
    keydata = ['n', 'e', 'd', 'p', 'q', 'u']

    def __init__(self, implementation, key):        
        self.implementation = implementation
        self.key = key
    
    # Anthony - these were assigned in place of the behavior provided
    # by the __getattr__ function which is not supported in repy. 
    # Anthony Oct 5 2009: Modified again because getattr was no
    # longer allowed by repy.   
        try:
            self.n = self.key.n
        except AttributeError:
            pass
        try:
            self.e = self.key.e
        except AttributeError:
            pass
        try:
            self.d = self.key.d
        except AttributeError:
            pass
        try:
            self.p = self.key.p
        except AttributeError:
            pass
        try:
            self.q = self.key.q
        except AttributeError:
            pass
        try:
            self.u = self.key.u
        except AttributeError:
            pass
        
          
    # Anthony - not allowed in repy 
    #def __getattr__(self, attrname):
    #    if attrname in self.keydata:
    #        # For backward compatibility, allow the user to get (not set) the
    #        # RSA key parameters directly from this object.
    #        return getattr(self.key, attrname)
    #    else:
    #        raise AttributeError("%s object has no %r attribute" % (self.__class__.__name__, attrname,))

    def _encrypt(self, c, K):
        return (self.key._encrypt(c),)

    def _decrypt(self, c):
        #(ciphertext,) = c
        #(ciphertext,) = c[:1]  # HACK - We should use the previous line
                               # instead, but this is more compatible and we're
                               # going to replace the Crypto.PublicKey API soon
                               # anyway.
        #return self.key._decrypt(ciphertext)
        return self.key._decrypt(c)

    def _blind(self, m, r):
        return self.key._blind(m, r)

    def _unblind(self, m, r):
        return self.key._unblind(m, r)

    def _sign(self, m, K=None):
        return (self.key._sign(m),)
        
    def _verify(self, sig):
    # Anthony - modified to provide backwards compatability
    #def _verify(self, m, sig):
    #    #(s,) = sig
    #    (s,) = sig[:1]  # HACK - We should use the previous line instead, but
    #                    # this is more compatible and we're going to replace
    #                    # the Crypto.PublicKey API soon anyway.
    #    # Anthony - modified to provide backwars compatability
    #    return self.key._verify(m, s)
        return self.key._verify(sig)

    def has_private(self):
        return self.key.has_private()

    def size(self):
        return self.key.size()

    def can_blind(self):
        return True

    def can_encrypt(self):
        return True

    def can_sign(self):
        return True

    def publickey(self):
        return self.implementation.construct((self.key.n, self.key.e))

    # Anthony - removing this functionality, not allowed in repy
    """
    def __getstate__(self):
        d = {}
        for k in self.keydata:
            try:
                d[k] = getattr(self.key, k)
            except AttributeError:
                pass
        return d

    def __setstate__(self, d):
        if not hasattr(self, 'implementation'):
            self.implementation = RSAImplementation()
        t = []
        for k in self.keydata:
            if not d.has_key(k):
                break
            t.append(d[k])
        self.key = self.implementation._math.rsa_construct(*tuple(t))

    def __repr__(self):
        attrs = []
        for k in self.keydata:
            if k == 'n':
                attrs.append("n(%d)" % (self.size()+1,))
            elif hasattr(self.key, k):
                attrs.append(k)
        if self.has_private():
            attrs.append("private")
        return "<%s @0x%x %s>" % (self.__class__.__name__, id(self), ",".join(attrs))
    """
class RSA_RSAImplementation(object):
    def __init__(self, **kwargs):
        
      
        #Anthony - removed this code, never going to use fast_math
        # 
        ## 'use_fast_math' parameter:
        ##   None (default) - Use fast math if available; Use slow math if not.
        ##   True - Use fast math, and raise RuntimeError if it's not available.
        ##   False - Use slow math.
        #use_fast_math = kwargs.get('use_fast_math', None)
        #if use_fast_math is None:   # Automatic
        #    if _fastmath is not None:
        #        self._math = _fastmath
        #    else:
        #        self._math = _slowmath
        #
        #elif use_fast_math:     # Explicitly select fast math
        #    if _fastmath is not None:
        #        self._math = _fastmath
        #    else:
        #        raise RuntimeError("fast math module not available")
        #
        #else:   # Explicitly select slow math
        #    self._math = _slowmath
        
        #Anthony - added to set _slowmath by default.
        # stage 2, there is no add _slowmath module to the object
        # since we no longer can choose _fastmath
        #self._math = _slowmath
        
        # Anthony stage 2
        #self.error = self._math.error
        self.error = _slowmath_error

        # 'default_randfunc' parameter:
        #   None (default) - use Random.new().read
        #   not None       - use the specified function
        self._default_randfunc = kwargs.get('default_randfunc', None)
        self._current_randfunc = None

    def _get_randfunc(self, randfunc):
        # Anthony - Adjusting to get a random function working
        #if randfunc is not None:
        #    return randfunc
        #elif self._current_randfunc is None:
        #    self._current_randfunc = Random.new().read
        return self._current_randfunc

    def generate(self, bits, randfunc=None, progress_func=None):
        rf = self._get_randfunc(randfunc)
        obj = _RSA_generate_py(bits, rf, progress_func)    # TODO: Don't use legacy _RSA module
        key = _slowmath_rsa_construct(obj.n, obj.e, obj.d, obj.p, obj.q, obj.u)
        return RSA_RSAobj(self, key)

    def construct(self, tup):
        key = _slowmath_rsa_construct(*tup)
        return RSA_RSAobj(self, key)

# Anthony these will not be used in repy.
#_impl = RSAImplementation()
#generate = _impl.generate
#construct = _impl.construct
#error = _impl.error




#
#   RSA.py : RSA encryption/decryption
#
#  Part of the Python Cryptography Toolkit
#
# Distribute and use freely; there are no restrictions on further
# dissemination and usage except those imposed by the laws of your
# country of residence.  This software is provided "as is" without
# warranty of fitness for use or suitability for any purpose, express
# or implied. Use at your own risk or not at all.
#


# Anthony, not allowed for REPY
#__revision__ = "$Id$"

"""
<Modified> 
  Anthony - Feb 24 
  full conversion to stage2 repy port
  
  Anthony - Jun 1
  _RSA_generate_py will no longer generate a p and q such that 
  GCD( e, (p-1)(q-1)) != 1. The old behavior resulted in an invalid
  key when d was computed (it resulted in d = 1).

"""

# Anthony stage2
#import pubkey
#import number

def _RSA_generate_py(bits, randfunc, progress_func=None):
    """generate(bits:int, randfunc:callable, progress_func:callable)

    Generate an RSA key of length 'bits', using 'randfunc' to get
    random data and 'progress_func', if present, to display
    the progress of the key generation.
    
    <Modified>
      Anthony - Because e is fixed, it is possible that a p or q
      is generated such that (p-1)(q-1) is not relatively prime to e.
      A check after p and q are generated will result in p and q
      discarded if either (p-1) or (q-1) is congruent to 0 modulo e.
      
    """
    obj=_RSA_RSAobj()

    # Generate the prime factors of n
    if progress_func:
        progress_func('p,q\n')
        
    p = q = 1L
    while number_size(p*q) < bits:
        # Note that q might be one bit longer than p if somebody specifies an odd
        # number of bits for the key. (Why would anyone do that?  You don't get
        # more security.)
        
        # Anthony stage1 - because pubkey is not using a 
        # 'from number import *' we will call getPrime from
        # number instead
        #p = pubkey.getPrime(bits/2, randfunc)
        #q = pubkey.getPrime(bits - (bits/2), randfunc)
        p = number_getPrime(bits/2, randfunc)
        q = number_getPrime(bits - (bits/2), randfunc)
        
        # Anthony - This is an new modification to the scheme, it is
        # very unlikely that p-1 or q-1 will be a multiple of 65537.
        if ((p - 1) % 65537 == 0) or ((q - 1) % 65537 == 0):
          p = q = 1L


    # p shall be smaller than q (for calc of u)
    if p > q:
        (p, q)=(q, p)
    obj.p = p
    obj.q = q

    if progress_func:
        progress_func('u\n')
        
    # Anthony stage1 - pubkey no longer imports inverse()   
    obj.u = number_inverse(obj.p, obj.q)
    obj.n = obj.p*obj.q

    obj.e = 65537L
    if progress_func:
        progress_func('d\n')
    # Anthony stage1 - pubkey no longer imports inverse()    
    obj.d=number_inverse(obj.e, (obj.p-1)*(obj.q-1))

    assert bits <= 1+obj.size(), "Generated key is too small"
    
    return obj

class _RSA_RSAobj(pubkey_pubkey):

    def size(self):
        """size() : int
        Return the maximum number of bits that can be handled by this key.
        """
        return number_size(self.n) - 1

#
#   number.py : Number-theoretic functions
#
#  Part of the Python Cryptography Toolkit
#
# Distribute and use freely; there are no restrictions on further
# dissemination and usage except those imposed by the laws of your
# country of residence.  This software is provided "as is" without
# warranty of fitness for use or suitability for any purpose, express
# or implied. Use at your own risk or not at all.
#

# Anthony
#__revision__ = "$Id$"

# Anthony - no globals
#bignum = long

# New functions
# Anthony stage 1 - since its not called locally might as well remove it
#from _number_new import *

# Anthony stage2 random will be the repy package we use for random
# number untill we are able complete the port. For stage1 I will
# be using python's random.random(). Now stage2 using repy's random

# Commented out and replaced with faster versions below
## def long2str(n):
##     s=''
##     while n>0:
##         s=chr(n & 255)+s
##         n=n>>8
##     return s

## import types
## def str2long(s):
##     if type(s)!=types.StringType: return s   # Integers will be left alone
##     return reduce(lambda x,y : x*256+ord(y), s, 0L)

def number_size (N):
    """size(N:long) : int
    Returns the size of the number N in bits.
    """
    bits, power = 0,1L
    while N >= power:
        bits += 1
        power = power << 1
    return bits

#def number_getRandomNumber(N, randfunc=None):
#    """getRandomNumber(N:int, randfunc:callable):long
#    Return an N-bit random number.
#
#    If randfunc is omitted, then Random.new().read is used.
#    
#    Anthony - This function is not called by anything.
#    """
#    
#    # Anthony stage1 - This code has been removed because we
#    # are not using the pycrypto PRNG
#    """
#    if randfunc is None:
#        _import_Random()
#        randfunc = Random.new().read
#
#    S = randfunc(N/8)
#    odd_bits = N % 8
#    if odd_bits != 0:
#        char = ord(randfunc(1)) >> (8-odd_bits)
#        S = chr(char) + S
#    value = bytes_to_long(S)
#    value |= 2L ** (N-1)                # Ensure high bit is set
#    assert size(value) >= N
#    return value
#    """
#    # Anthony stage2 repy random is included
#    return random_randint(2**(N-1), 2**N - 1)
  

def number_GCD(x,y):
    """GCD(x:long, y:long): long
    Return the GCD of x and y.
    """
    x = abs(x) ; y = abs(y)
    while x > 0:
        x, y = y % x, x
    return y

def number_inverse(u, v):
    """inverse(u:long, u:long):long
    Return the inverse of u mod v.
    """
    u3, v3 = long(u), long(v)
    u1, v1 = 1L, 0L
    while v3 > 0:
        q=u3 / v3
        u1, v1 = v1, u1 - v1*q
        u3, v3 = v3, u3 - v3*q
    while u1<0:
        u1 = u1 + v
    return u1

# Given a number of bits to generate and a random generation function,
# find a prime number of the appropriate size.

def number_getPrime(N, randfunc=None):
    """getPrime(N:int, randfunc:callable):long
    Return a random N-bit prime number.

    If randfunc is omitted, then Random.new().read is used.
    """
    # Anthony stage1 removing existing random package
    #if randfunc is None:
    #    _import_Random()
    #    randfunc = Random.new().read

    # Anthony stage2 - using repy random for now
    # for N-bit number, max will be (2^N) - 1
    # and min will be 2^(N-1)
    # This will use a bitwise OR to ensure the number is odd
    #origional: number=getRandomNumber(N, randfunc) | 1
    
    # Anthony - changed this again, now that random.repy
    # includes a function to get a random N bit number
    # that can be used instead.
    #number = random_randint(2**(N-1), 2**N - 1) | 1
    number = random_nbit_int(N) | 1
    
    number |= 2L ** (N-1) # ensure high bit is set 
    
    while (not number_isPrime(number, randfunc=randfunc)):
        number=number+2
    return number

def number_isPrime(N, randfunc=None):
    """isPrime(N:long, randfunc:callable):bool
    Return true if N is prime.

    If randfunc is omitted, then Random.new().read is used.
    """
    
    # Anthony stage1 removing the existing random package
    # does not appear that this code is even used in this method.
    """
    _import_Random()
    if randfunc is None:
        randfunc = Random.new().read

    randint = StrongRandom(randfunc=randfunc).randint
    """
    
    sieve = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59,
       61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127,
       131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193,
       197, 199, 211, 223, 227, 229, 233, 239, 241, 251]
 
    if N == 1:
        return 0
    if N in sieve:
        return 1
    for i in sieve:
        if (N % i)==0:
            return 0
    
    # Anthony - not going to use _fastmath ever
    # Use the accelerator if available
    #if _fastmath is not None:
    #    return _fastmath.isPrime(N)

    # Compute the highest bit that's set in N
    N1 = N - 1L
    n = 1L
    while (n<N):
        n=n<<1L
    n = n >> 1L

    # Rabin-Miller test
    for c in sieve[:7]:
        a=long(c) ; d=1L ; t=n
        while (t):  # Iterate over the bits in N1
            x=(d*d) % N
            if x==1L and d!=1L and d!=N1:
                return 0  # Square root of 1 found
            if N1 & t:
                d=(x*a) % N
            else:
                d=x
            t = t >> 1L
        if d!=1L:
            return 0
    return 1

# Small primes used for checking primality; these are all the primes
# less than 256.  This should be enough to eliminate most of the odd
# numbers before needing to do a Rabin-Miller test at all.


# Improved conversion functions contributed by Barry Warsaw, after
# careful benchmarking



def number_long_to_bytes(n, blocksize=0):
    """long_to_bytes(n:long, blocksize:int) : string
    Convert a long integer to a byte string.

    If optional blocksize is given and greater than zero, pad the front of the
    byte string with binary zeros so that the length is a multiple of
    blocksize.
    
    Anthony - THIS WILL STRIP OFF LEADING '\000' of a string!
           comes in '\000\xe8\...' and will come out of
           long_to_bytes as '\xe8\..'   
    
    """
    s = ''
    n = long(n)
    tmp = 0
    #pack = struct.pack
    while n > 0:
        # Anthony removed the use of struct module
        #s = pack('>I', n & 0xff ff ff ffL) + s
        s = "%s%s" % (chr(n & 0xFF), s)
        n = n >> 8
    # strip off leading zeros
    for i in range(len(s)):
        if s[i] != '\000':
            break
    else:
        # only happens when n == 0
        s = '\000'
        i = 0
        
    s = s[i:]    
    # add back some pad bytes.  this could be done more efficiently w.r.t. the
    # de-padding being done above, but sigh...    
    if blocksize > 0 and len(s) % blocksize:
        s = (blocksize - len(s) % blocksize) * '\000' + s
    return s

def number_bytes_to_long(s):
    """bytes_to_long(string) : long
    Convert a byte string to a long integer.

    This is (essentially) the inverse of long_to_bytes().
    """
    
    acc = 0L
    length = len(s)
    if length % 4:
        extra = (4 - length % 4)
        s = '\000' * extra + s
        length = length + extra
    
    for i in range(0, length):
        # Anthony - replaced struct module functionality.
        #acc = (acc << 32) + unpack('>I', s[i:i+4])[0]
        acc = (acc << 8) 
        acc = acc + ord(s[i])
    return acc


# For backwards compatibility...
# Anthony Feb 14 
# removed long2str str2long and _import_Random()
"""
import warnings
def long2str(n, blocksize=0):
    warnings.warn("long2str() has been replaced by long_to_bytes()")
    return long_to_bytes(n, blocksize)
def str2long(s):
    warnings.warn("str2long() has been replaced by bytes_to_long()")
    return bytes_to_long(s)

def _import_Random():
    # This is called in a function instead of at the module level in order to avoid problems with recursive imports
    global Random, StrongRandom
    from Crypto import Random
    from Crypto.Random.random import StrongRandom
"""# -*- coding: utf-8 -*-
#
#  PubKey/RSA/_slowmath.py : Pure Python implementation of the RSA portions of _fastmath
#
# Copyright (C) 2008  Dwayne C. Litzenberger <dlitz@dlitz.net>
#
# =======================================================================
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# =======================================================================

"""Pure Python implementation of the RSA-related portions of Crypto.PublicKey._fastmath."""

"""
<Modified> 
  Anthony - Feb 9 2009
    removed the import of Crypto.Util.python_compat, dont need 
    to support python 2.1 ..
  Anthony - April 7 2009
    Changed return of _verify to coincide with seattle's origional rsa behavior.
  Anthony - April 30 2009
    Changed _slowmath_rsa_construct to allow user to create
    a _slowmath_RSAKey without a public key
  Anthony - May 9 2009
    Modified _slowmath_rsa_construct to allow type int in 
    addition to long.
  Anthony - Oct 5 2009
    Modified _slowmath_RSAKey.has_private and  _slowmath_RSAKey.has_public
    to no longer use hasattr because repy no longer allows hasattr.
    The code was borrowed from the fix for RSA.py (Note: RSA.py is
    lumped together with the other modules to get pycryptorsa.repy
    before distribution.
"""

# Anthony removing globals, looks like this one can go.
#__revision__ = "$Id$"

# Anthony stage 2
#__all__ = ['rsa_construct']

# Anthony - see above for reason
#from Crypto.Util.python_compat import *

# Anthony Stage 1
#from number import size, inverse

# Anthony stage 2
#import number

class _slowmath_error(Exception):
    pass

class _slowmath_RSAKey(object):
    def _blind(self, m, r):
        # compute r**e * m (mod n)
        return m * pow(r, self.e, self.n)

    def _unblind(self, m, r):
        # compute m / r (mod n)
        
        # Anthony stage 1
        return number_inverse(r, self.n) * m % self.n

    def _decrypt(self, c):
        # compute c**d (mod n)
        if not self.has_private():
            raise _slowmath_error("No private key")
        return pow(c, self.d, self.n) # TODO: CRT exponentiation

    def _encrypt(self, m):
        # compute m**d (mod n)
        if not self.has_public():
            raise _slowmath_error("No public key")
        return pow(m, self.e, self.n)

    def _sign(self, m):   # alias for _decrypt
        if not self.has_private():
            raise _slowmath_error("No private key")
        return self._decrypt(m)

    # Anthony - modified to provide backwards compatability with
    # existing procedure. Pycrypto returned a boolean, and the
    # existing repy code requires the encryped signature.
    def _verify(self, sig):
        if not self.has_public():
            raise _slowmath_error("No public key")
    #def _verify(self, m, sig):       
    #    return self._encrypt(sig) == m
        return self._encrypt(sig)

    def has_private(self):
        # Anthony because repy builds private keys that
        # do no have public key data, an additional requirement
        # was added.
        #return hasattr(self, 'd')
        
        # Anthony Oct 5 2009: This is no longer supported under repy
        #return hasattr(self, 'd') and hasattr(self, 'n')
        has_n = False
        has_d = False
        try:
            self.n
            has_n = True
        except AttributeError:
            pass
          
        try:
            self.d
            has_d = True
        except AttributeError:
            pass
        
        return has_d and has_n
      
    def has_public(self):
        # Anthony because repy builds private keys that
        # do no have public key data, an additional requirement
        # was added.
        
        # Anthony Oct 5 2009: This is no longer supported under repy
        #return hasattr(self, 'n') and hasattr(self, 'e') 
        has_n = False
        has_e = False
        try:
            self.n
            has_n = True
        except AttributeError:
            pass
          
        try:
            self.e
            has_e = True
        except AttributeError:
            pass
          
        return has_e and has_n
 

    def size(self):
        """Return the maximum number of bits that can be encrypted"""
        # Anthony stage 2
        return number_size(self.n) - 1

# Anthony - changed to allow user to create a private key
# without the public keys
def _slowmath_rsa_construct(n=None, e=None, d=None, p=None, q=None, u=None):
#def _slowmath_rsa_construct(n, e, d=None, p=None, q=None, u=None):
    """Construct an RSAKey object"""
    # Anthony - changed to allow user to create a private key
    # without the public keys
    #assert isinstance(n, long)
    #assert isinstance(e, long)
    # Anthony - modified May 9 to allow type int for each arguement.
    assert isinstance(n, (int, long, type(None)))
    assert isinstance(e, (int, long, type(None)))
    assert isinstance(d, (int, long, type(None)))
    assert isinstance(p, (int, long, type(None)))
    assert isinstance(q, (int, long, type(None)))
    assert isinstance(u, (int, long, type(None)))
    obj = _slowmath_RSAKey()
    # Anthony - changed to allow user to create a private key
    # without the public keys
    #obj.n = n
    #obj.e = e
    if n is not None: obj.n = n
    if e is not None: obj.e = e
    if d is not None: obj.d = d
    if p is not None: obj.p = p
    if q is not None: obj.q = q
    if u is not None: obj.u = u
    return obj

### Automatically generated by repyhelper.py ### /chalmers/users/isaker/Distributed/Distributed/demokit/pycryptorsa.repy
