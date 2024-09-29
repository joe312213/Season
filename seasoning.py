# basic cryptography lib, using a rotation of Ceasar ciphers 
# defined by the ascii codes of a string key
# use varied keys of > ~12 characters to reduce effectiveness of frequency analysis
#
# usage: 
# sn = Season(password, mode)
# enc = sn.season(msg)
# ...
# dec = sn.unseason(enc)
# 
# optional parameter mode can be set to 'heavy' to pseudo-randomly pad the key
# to reduce effectiveness of frequency analysis based code breaking
# should have no effect on speed
# 
# optional parameter salt can be set to a string or list of integers to 
# add some variation to the key and to store it in non-plain text
#

# CC Joe Hudson 2024

class Season:

    def __init__(self, spice="season", mode='light', salt='', bin=False):
        self.heavy = False if mode == 'light' else True
        self.spice = []      
        self.spicepos = 0
        self.msgpos = 0
        self.dir = 1
        self.msg = []
        self.swin = 6
        self.swinsize = (1 << (7 * self.swin))
        self.pchar = chr(0)  # use DEL (127) instead of NULL?
        self.bin = True if bin else False
        self.salt = None
        if len(salt) > 14 :
            if isinstance(salt, list) and isinstance(salt[0], int):
                self.salt = list(map(lambda x: int(x)%128, salt)) # ensure all elements can be cast to int and confine to max 127
            elif isinstance(salt, str):                
                self.salt = list(map(ord, list(salt)))
        if not self.salt or (self.salt[:-1] == self.salt[1:]): # should have some variation in the salt
            self.salt = [7,10,1,5,60,42,91,67,8,3,36,55,22,29,84] 
        self._newspice(spice) # turns key string into list of acsii codes  
    def __str__(self):
        return self.spice

    def seasonmode(self):
        return 'heavy' if self.heavy else 'light'
        
    def resetpos(self):
        self.spicepos = 0
        self.msgpos = 0

    # convert a string key to a list of ascii code values
    def _newspice(self, spice):
        if not self.heavy :
            self.spice = list(map(ord, list(spice)))
        else:
            self._heavyspice(spice)

    # repeatable shuffle of char code list
    def _shuffle(self, lst, n=1):
        lss = len(lst)
        for _ in range(n):
            for i in range(lss):
                j = (i + (lst[i] + lst[(i+1) % lss]) * lst[(i+2) % lss]) % lss
                lst[i], lst[j] = lst[j], lst[i]
        return lst

    # repeatable shuffle of char list
    def _shufflechar(self, lst, n=1):

        lss = len(lst)
        for _ in range(n):
            for i in range(lss):
                j = (i + (ord(lst[i]) + ord(lst[(i+1) % lss])) * ord(lst[(i+2) % lss])) % lss
                lst[i], lst[j] = lst[j], lst[i]
        return lst


    # shuffle and pad out key to variable length (min 27 chars) pseudo-random sequence
    def _heavyspice(self, spice):
        sl = len(spice)
        
        shufspice = list(spice)
      
        shufspice = self._shufflechar(shufspice)

        lsalt = len(self.salt)
        cp = int(26/sl + 1) # internal key will be min 27 chars long
        self.spice = [None]*(sl * cp)
        nl = len(self.spice)
        for i in range(nl):
            self.spice[i] = (ord(shufspice[i % sl]) + self.salt[i % lsalt] + int(i/sl)) % 128

        self.spice = self._shuffle(self.spice)

    # encrypt, with an optional new key
    def season(self, msg, spice = ''):
        self.dir = 1
        if spice:
            self._newspice(spice)
        return self._season(msg)
    
    # decrypt, with an optional new key
    def unseason(self, msg, spice = ''):
        self.dir = 0
        if spice:
            self._newspice(spice)
        return self._season(msg)

    # encrypts/decrypts whole messages
    def _season(self, msg):
        self.resetpos()
        self.msg = msg
        if self.heavy :
            return ''.join(self._heavyseason())
        else :
            return ''.join(self.__season())

    def _getspiceord(self):
        ret = self.spice[self.spicepos]
        self.spicepos = (self.spicepos + 1) % len(self.spice) # rotate the Ceasar cipher
        return ret
    
    # do some ascii modulo arithmetic (essentially the Ceasar cipher)
    def seasonchar(self, sord, mchar):
        mc = ord(mchar)
          # mod div ascii values from 32 (space) to 126 (~)
        return chr((mc + sord - 32) % 95 + 32)
        

    def unseasonchar(self, sord, mchar):
        mc = ord(mchar)
          # mod div ascii values from 32 (space) to 126 (~)
        return chr((mc - sord - 32) % 95 + 32)


    def __season(self):
        
        l = len(self.msg)
        sn = [None]*l

        if self.dir:
            for i in range(l):
                sn[i] = self.seasonchar(self._getspiceord(), self.msg[i])
            self.msgpos += l
        else:
            for i in range(l):
                sn[i] = self.unseasonchar(self._getspiceord(), self.msg[i])
            self.msgpos += l

        self.msg = None
        return sn

# heavy mode: group 6 char blocks of message and rotate by 6 char blocks of key, 
# extend range of key char vals to non-printable chars and map to blocks 
# of 7 bits using binary math. this will create a 6x7 = 42bit mapping 
# space, up from 7 bits for message character sequences. this would mean 
# chars in message as the same offset relative to multiples of the key 
# length no longer map to the same char. The mapping would depend on 
# each individual 6 char block of the message, having the same relative 
# offset to multiples of the key length 

    # gets the next 6 char block of the key
    def _heavyspiceord(self, win):
        slen = len(self.spice)
        
        if self.spicepos + win <= slen :
            ni = self.spicepos + win
            hord = self.spice[self.spicepos : ni]
            self.spicepos = ni % slen
        else :
            e = ni % slen
            hord = self.spice[self.spicepos : ] + self.spice[ : e]
            self.spicepos = e
        return hord
    
    # convert a block of 7 bit char codes to a single number
    def _winnum(self, ords):
        num = 0
        for ord in ords :
            num <<= 7
            num += ord
        return num
    
    # convert a number to a block of swin, 7 bit chars codes
    def _numwin(self, num):
        win = [0]*self.swin
        for i in range(self.swin-1,-1,-1):
            win[i] = num & 127
            num >>= 7
        return win
    
    # convert a number to a block of w, 7 bit chars
    def _numwinr(self, num, w):
        win = [0]*w
        for i in range(w-1,-1,-1):
            win[i] = num & 127
            num >>= 7
        return win
        
    # convert a string to a list of ascii codes
    def _winords(self, strw):
        return list(map(ord, list(strw)))

    # (en/de)crypt an swin size char block of message
    def _heavyseasonwin(self, sords, strw):
        snum = self._winnum(sords)
        mnum = self._winnum(self._winords(strw))

        rnum = (mnum + snum)%self.swinsize if self.dir else (mnum - snum)%self.swinsize
        return list(map(chr, self._numwin(rnum)))

    # (en/de)crypt an w size char block of message    
    def _heavyseasonwinr(self, sords, strw, w):
        wsize = 1 << (7*w)
        snum = self._winnum(sords)
        mnum = self._winnum(self._winords(strw))

        rnum = (mnum + snum)%wsize if self.dir else (mnum - snum)%wsize
        return list(map(chr, self._numwinr(rnum, w)))

    def _heavyseason(self):
        l = len(self.msg)
        sn = [None]*l
        wr = l % self.swin

        lw = l - wr

        wl = self.swin
        for i in range(0, lw, wl):    
            sords = self._heavyspiceord(wl)
            strw = self.msg[i:i+wl]
            sn[i:i+wl] = self._heavyseasonwin(sords, strw)
        if lw != l :
            sords = self._heavyspiceord(wr)
            strw = self.msg[lw:lw+wr]
            sn[lw:lw+wr] = self._heavyseasonwinr(sords, strw, wr)

        return sn
            
