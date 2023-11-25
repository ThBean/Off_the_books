# -*- coding:ISO-8859-1 -*-
import ast
import os
import random
from pathlib import Path

# import Modules.TextHandler as text_handler

'''
  ____
//@  @\\
|| �  || hes called jeff
 \\___//
 
Users is structured as so
{
Name: [password,PubKey(in str)]
}

'''
path = str(Path(__file__).parent)
if os.name.lower() == "windows":
    f = open(path+"\\Users","r")
else:
    f = open(path + "/Users", "r")

Users = ast.literal_eval(f.read())#get and convert dictionary
f.close()

def add_user(Name,PubKey):#to check
    if Name not in Users.keys():# see if they already exist (if not)
        Users[Name] = PubKey
        if os.name.lower() == "windows":
            f = open(path+"\\Users","w")
        else:
            f = open(path + "/Users", "w")
        f.write(str(Users))#write in case of a crash
        f.close()
        return True
    else: #if they already exist
        return False#tell them no

def change_name(OName,NName,password,PubKey):
    if OName not in Users.keys():# see if they already exist (if not)
        if Users[OName][0] == password and PubKey==Users[OName][1]:#make sure they are who they say they are. PubKey is a second layer
            del Users[OName] # delete ol data
            Users[NName]=[password,PubKey]#before you say im bieng lazy by getting the pub key i could use pop insted to get the value and then use that            

            if os.name.lower() == "windows":
                f = open(path+"\\Users","w")
            else:
                f = open(path + "/Users", "w")
            f.write(str(Users))#write in case of a crash
            f.close()
            return True#tell them its good
        
    return False#this wont run unless the afermentioned returned isnt true

