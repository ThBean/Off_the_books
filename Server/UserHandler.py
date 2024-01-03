# -*- coding:ISO-8859-1 -*-
import ast
import os
from pathlib import Path

'''
  ____
//@  @\\
|| ¬  || hes called jeff
 \\___//
 
Users is structured as so
{
Name: [password,PubKey(in str)]
}

'''
path = str(Path(__file__).parent)
if os.name.lower() == "windows":
    f = open(path + "\\Users", "r")
else:
    f = open(path + "/Users", "r")

Users = ast.literal_eval(f.read())  # get and convert dictionary
f.close()


def AddUser(Name, PubKey):  # to check
    if Name not in Users.keys():  # see if they already exist (if not)
        Users[Name] = PubKey
        if os.name.lower() == "windows":
            ff = open(path + "\\Users", "w")
        else:
            ff = open(path + "/Users", "w")
        ff.write(str(Users))  # write in case of a crash
        ff.close()
        return True
    else:  # if they already exist
        return False  # tell them no


def ChangeName(OName, NName, password, PubKey):
    if OName not in Users.keys():  # see if they already exist (if not)
        if Users[OName][0] == password and PubKey == Users[OName][1]:  # make sure they are who they say they are. PubKey is a second layer
            del Users[OName]  # delete ol data
            Users[NName] = [password,
                            PubKey]  # before you say im being lazy by getting the pub key I could use pop instead to
            # get the value and then use that

            if os.name.lower() == "windows":
                fff = open(path + "\\Users", "w")
            else:
                fff = open(path + "/Users", "w")
            fff.write(str(Users))  # write in case of a crash
            fff.close()
            return True  # tell them its good

    return False  # this won't run unless the aforementioned returned isn't true
