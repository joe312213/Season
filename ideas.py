import matplotlib.pyplot as plt
import matplotlib as mpl
import random

# 'rz mapping' function is part of encryption approach
# determin mapping variables based on some encryption config:
swin = 8 # 8 is a reasonable default. number of symbols per window being (en)coded at a time
symbits = 8 # number of bits per symbol being (en)coded, e.g. 8 for extended ascii or ISO/IEC 8859-1
setsize = 1 << (swin*symbits) # the size of the range of values we're making a mapping for.

# mapping vars
r1 = setsize - 1
s = 1 << 24 # 128 is reasonable default. must be power of 2  - if input value changes by 1, output mapping changes by this value (usually). also the number of mapping zones 
sl = s.bit_length() - 1 # log2(s)   - pre-comp used for optimization of mapping algorithm 
rsize = setsize >> sl # number of values within each mapping range  - pre-comp used for optimization of mapping algorithm 
# rsize will be power of 2, providing s <= 2^symbits
rsizel = rsize.bit_length() - 1


# 'range z mapping' 
# take an n bit number q and map it to another n bit number r 
# such that small changes in q result in big changes in r
# (and larger changes in q result in smaller changes in r, because it needs to remain 1-to-1 reversible mapping)
# e.g. an 8 bit mapping where input change of 1 results in output changing by 2, we split the mapping into 2 regions:
# 0 - 0, 1 - 2, 2 - 4, 3 - 6, .. 127 - 254 | 128 - 1, 129 - 3, 130 - 5, .. 255 - 255
# so
# n < 128 -> m = 2n,  n >= 128 -> m = 2(n-127) - 1 = 2n - 255
# or for a change of 1 to 8 we end up with 8 zones:
# 0 - 0, 1 - 8, 2 - 16, 3 - 24 .. 31 - 248 | 32 - 1, 33 - 9, 34 - 17 .. 63 - 249 | 64 - 2, 65 - 10 .. 95 - 250 |  
# n -> 8n   |   n -> 8n - 1023  |   n -> 8n - 2046   |   n -> 8n - 3069   |   n -> 8n - ...
# n -> 8n   |   n -> 8n - 255  |   n -> 8n - 510   |   n -> 8n - 765   |   n -> 8n - 1020   |   n -> 8n - 1275   ...
# or
# n -> 8n   |   n -> 8n - r1 |  n -> 8n - r2 | n -> 8n - r3  ... n -> 8n - r7
# where
# s = scale factor within zone
# r0 = 0, r1 = nmax - 1, r2 = 2*r1, r3 = 3*r1 ..
# rsize = nmax/s
# zone z of n = floor(n/(rsize))
# r[z] = r1(n >> log2(rsize))
# r[z] = r1(n >> rsizel)
# but also
# r1 = nmax - 1,  r2 = nmax >> 1 - 2,  r3 = nmax >> 2 - nmax - 3,  r4 = nmax >> 3 - nmax >> 2 - 4,  r5 = nmax >> 4 -  .. hmm, not sure useful, just use a multiply

# number of buckets = s
# q = sn - r[z]
# q = sn - r1(n >> rzr1)
# so, reversing the mapping:-
# first finding the mapping zone from q:
# z = q % s
# r[z] = r1*z
# n = (q + r[z])/s

# where nmax and s are powers of 2, shift operations can replace some division and multiplication.

# win is a essentially number containing a set of (en/de)ciphered symbols 
def rzmap(win):
    rz = r1*(win >> rsizel) # find zone offset, divide by number of mapping zones to find zone, then mult by r1
    return (win << sl) - rz

# reverse the mapping
def rzunmap(win):
    rz = r1*(win % s)
    return (win + rz) >> sl




# plot it

# but before we do, do we need to use a sample of a huge number space?
step = 1
maxsamples = 1024
if setsize > maxsamples :
    avstep = (setsize >> 10) + 1 # shift right 10 is dividing by 1024
    minstep = 1
    maxstep = avstep*2 - 1
    x = 0
    n = [0]*maxsamples
    i = 1
    while x < setsize and i < 1024:
        step  = random.randrange(minstep,maxstep)
        x += step
        n[i] = x
        i += 1
    if x >= setsize:        
        n[i-1] = setsize - 1
    if i < 1024:
        n = n[:i]
else:
    n = list(range(setsize))

q = list(map(rzmap, n))
# and back again...
n2 = list(map(rzunmap, q))


mpl.rc('lines', linewidth=0.5, linestyle='dashed', marker='o', markersize=3, markerfacecolor='blue')

fig, (there, andback) = plt.subplots(2, sharex=True, sharey=True)
dispsize = setsize
if setsize > (1 << 32) :
    dispsize = "2^" + str(setsize.bit_length() - 1)
fig.suptitle(f'Showing the operation of the rz map function for:\nsetsize: {dispsize}, rz scale factor: {s:.4g}, zone size: {rsize:.4g}')
fig.set_figheight(9)
there.set_title("rzmap")
there.set_xlabel("n")
there.set_ylabel("q")
there.set_aspect('equal', adjustable='box')
there.plot(n, q)
andback.set_title("rzunmap")
andback.set_xlabel("q")
andback.set_ylabel("n")
andback.plot(q, n2)
andback.set_aspect('equal', adjustable='box')

txt = f"average sample step size: {avstep:.4g}\n"
a = set(n)
b = set(n2)
ndiff = (a | b) - (a & b) 
if len(ndiff) : 
    txt += "mapping error, all input values not reversed on reverse mapping"
    print("in n but not n2:\n", a - b)
    print("in n2 but not n:\n", b - a)
else:
    txt += "success! mapping is reversible"

fig.text(.5, .02, txt, ha='center')

plt.show()

