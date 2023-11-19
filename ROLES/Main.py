from re import X
from cryptography.fernet import Fernet
from pathlib import Path

file=Path().resolve()

def load_key():
    return open("key.key", "rb").read()

def write_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)

def Encrypt(msg,key):
    
    f = Fernet(load_key())
    
    encrypted = f.encrypt(msg.encode())
    print(str(file)+"\\ROLES\\Text.txt")
    Text = list(open(str(file)+"\\ROLES\\Text.txt","r",encoding='ISO 8859-1').read())
    
    positions = []#[["letter","orgPos","new pos"]]
    
    EPos = 0
    for i in encrypted.decode():
        try:
            TPos = Text.index(i)
            if TPos != -1:
                Text.pop(TPos)
                i = [i,EPos,TPos]
                
                x = 0
                positions.append(i)
                for l in positions:
                    if x != 0:
                        if l[2] >= i[2]:#go until i find somthing bigger (title of my sextape)
                            print(i)
                            positions.insert(x,i)
                            break
                    x += 1
                   

        except ValueError:
            print(i)
        EPos+=1
        
    outS = ""
    outN = ""
    for o in positions:
        outS = outS + o[0]
        outN = outN +"#"+str(o[1])
    out = outS +"\n"*10+ outN
    
    return out
    

print(Encrypt("Hello world",0))