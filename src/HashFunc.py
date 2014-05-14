#
#**************************************************************************
#*                                                                        *
#*          General Purpose Hash Function Algorithms Library              *
#*                                                                        *
#* Author: Arash Partow - 2002                                            *
#* URL: http://www.partow.net                                             *
#* URL: http://www.partow.net/programming/hashfunctions/index.html        *
#*                                                                        *
#* Copyright notice:                                                      *
#* Free use of the General Purpose Hash Function Algorithms Library is    *
#* permitted under the guidelines and in accordance with the most current *
#* version of the Common Public License.                                  *
#* http://www.opensource.org/licenses/cpl1.0.php                          *
#*                                                                        *
#**************************************************************************
#

from Crypto.Hash import SHA224
from Crypto.Hash import HMAC
from Crypto.Hash import MD5
from Crypto.Hash import MD4
from Crypto.Hash import RIPEMD
from Crypto.Hash import SHA256
from random import choice

from Crypto.Util import number


def Hash1(key):
    
    h = HMAC.new(str(14))
    h.update(key)
    v = number.bytes_to_long(h.digest())
    return v
    
def Hash2(key):
    h = SHA224.new()
    h.update(key)
    v = number.bytes_to_long(h.digest())
    return v


def Hash3(key):
    h = MD5.new()
    h.update(key)
    v = number.bytes_to_long(h.digest())
    return v

def Hash4(key):
    h = RIPEMD.new()
    h.update(key)
    v = number.bytes_to_long(h.digest())
    return v    


def Hash5(key):
    h = SHA256.new()
    h.update(key)
    v = number.bytes_to_long(h.digest())
    return v   


def Hash6(key):
    h = MD4.new()
    h.update(key)
    v = number.bytes_to_long(h.digest())
    return v



