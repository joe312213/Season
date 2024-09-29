# use this code as a starting point for your program,

import seasoning as sn
from pathlib import Path
from datetime import datetime


again = True

while again:
    seasoning = None
    encrypted = False

    path = input("enter path to file: ")
    p = Path(path)    
    if p.suffix == '.enc': # encrypted dictionary
        password = input("enter decryption password: ")
        encrypted = True
    else:
        password = input("enter new password for encrypting: ")
    
    seasoning = sn.Season(password)
    
    f = None
    try:
        # Open file in read and write mode
        f = open(str(p), 'r+')  
        if encrypted:
            enc = f.read()
            print("encrypted text read from file:", enc)
            txt = seasoning.unseason(enc) # decrypt the data
        else: # rename the file so the extension is .enc
            txt = f.read()
            print("read plain text from file:", txt)
            f.close()
            encp = Path(p.parent, p.stem + '.enc')
            if not encp.is_file(): 
                # e.g. text.txt becomes text.enc
                p.rename(encp)  # if encp doesn't already exist, rename p  
            f = open(str(encp), 'r+')
            
        now = datetime.now()
        formatted = now.strftime("%Y-%m-%d %H:%M:%S")

        txt += "current date and time: "+formatted+"\n"
        
        print("modified file plain text:", txt)
        
        f.seek(0)
        
        # now encrypt the data
        enc = seasoning.season(txt)
        
        print("encrypted text to be saved:", enc)
        
        f.write(enc)
        
        f.truncate() 
    except IOError as e:
        print("An error occurred:", e)
        ans = input("would you like to try again? [y|n] ")
        if ans != 'y' :
            again = False

    finally:

        if f: 
            f.close()

        if input("go again? [y|n]: ") != 'y':
            again = False
        
