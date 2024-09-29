import seasoning as sn
import unittest


msg = "{'some':'json','to':'test'}"

class TestSeasoningMethods(unittest.TestCase):

    def test_init(self):
        s = sn.Season("Spicy Tomato")
        self.assertEqual(s.spice, [83, 112, 105, 99, 121, 32, 84, 111, 109, 97, 116, 111])

    def test_seasonchar(self):
        s = sn.Season("Spicy Tomato")
        sp = s.seasonchar(50, ' ')
        
        usp = s.unseasonchar(50, sp)
        self.assertEqual(sp, 'R')
        self.assertEqual(usp, ' ')
        
        z = s.seasonchar(25, 'z')        
        uz = s.unseasonchar(25, z)
        self.assertEqual(z, '4')
        self.assertEqual(uz, 'z')

    def test_season(self):
        s = sn.Season("Spicy Tomato")
        msg = "{'some':'json','to':'test'}"

        enc = s.season(msg)
        
        dec = s.unseason(enc)
        print("\nkey (light mode):", ''.join(map(chr,s.spice)))
        print("\nstring:", msg, "encoded as:", enc, "\nciphertext:", enc, "decoded as:", dec)

        self.assertTrue(enc[3] != enc[11])
        self.assertEqual(msg, dec)

# heavy mode tests

    def test_shuffle(self):
        print("\nHeavy mode: shuffle and salt\n")
        s = sn.Season("Spicy Tomato", 'heavy')
        msg = "{'some':'json','to':'test'}"        

        print("salt:", s.salt)
        t1 = "123456789"
        t2 = "Spicy Tomato"
        t3 = "987654321"
        tlist1 = list("123456789")

        tlist2 = [ord(c) for c in list(t1)]

        tlist3 = [ord(c) for c in list(t2)]
        tlist4 = [ord(c) for c in list(t3)]

        tl1s = s._shufflechar(tlist1)
        tl2s = map(chr, s._shuffle(tlist2))
        tl3s = map(chr, s._shuffle(tlist3))
        tl4s = map(chr, s._shuffle(tlist4))

        print(f'chars: {t1}, shufflechar: \t', *tl1s)
        print(f'chars: {t1}, shuffled:    \t', *tl2s)
        print(f'chars: {t2}, shuffled:    \t', *tl3s)
        print(f'chars: {t3}, shuffled:    \t', *tl4s)

    def test_winnum(self):
        print("\nHeavy mode: winnum and numwin\n")
        s = sn.Season("Spicy Tomato", 'heavy')
        msg = "{'some':'json','to':'test'}"

        ordstr = "Spicy Tomato"
        ords = [ord(c) for c in ordstr]
        numords = s._winnum(ords)
        print(f'_winnum: {numords}, for ords', *ords, "chars: ", ordstr)

        reords = s._numwinr(numords, len(ords))
        reostr = ''.join(map(chr, reords))
        print(f'_numwinr: {reostr}')

        self.assertEqual(ordstr, reostr)

    def test_heavyseasonwin(self):
        print("\nHeavy mode: heavyseasonwin\n")

        s = sn.Season("Spicy Tomato", 'heavy')
        msg = "{'some':'json','to':'test'}"

        ordstr = "Spicy Tomato"     
        ords = [ord(c) for c in ordstr]

        s.dir = 1
        encl = s._heavyseasonwin(ords, msg[:s.swin])
        print(f'_heavyseasonwin encrypted window: {encl}, plaintext window: {msg[:s.swin]}')

        s.dir = 0
        decl = ''.join(s._heavyseasonwin(ords, encl))
        print(f'_heavyseasonwin decrypted window: {decl}\nplaintext window:\t\t{msg[:s.swin]}')

        self.assertEqual(msg[:s.swin], decl)
        self.assertEqual(len(encl), s.swin)

    def test_heavyseason(self):
        s = sn.Season("Spicy Tomato", 'heavy')
        msg = "{'some':'json','to':'test'}"

        enc = s.season(msg)
        
        dec = s.unseason(enc)

        print("\nkey (heavy mode):", ''.join(map(chr,s.spice)))
        print("\nstring:", msg, "encoded as:", enc, "\nciphertext:", enc, "decoded as:", dec)

        self.assertEqual(msg, dec)

        msg = "{'some':'json','to':'test different'}"

        enc = s.season(msg)
        
        dec = s.unseason(enc)

        print("\nkey (heavy mode):", ''.join(map(chr,s.spice)))
        print("\nstring:", msg, "encoded as:", enc, "\nciphertext:", enc, "decoded as:", dec)

        self.assertEqual(msg, dec)



if __name__ == '__main__':
    unittest.main()


