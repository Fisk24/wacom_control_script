# Logger Modual By: Michael Fisk
import os, time, sys, traceback, string
logname    = "output.log"
enableTear = True
teartext   = '''
================================================================
################################################################
================================================================
'''
def legalize(x):
    # *NEW* Easy How To Install Brutal Doom V19 With Extras 11/05/13
    ILLEGAL = [ ["<3", "[HEART EMOTICION]"], 
                ['\u2013', "-"], 
                ['\u2665', ""],
                ['\u2640', "O+"] ]

    for i in ILLEGAL:
        x = x.replace(i[0], i[1])
    x = x.strip()
    return x

def getLogFileName():
    return logname

def setLogFileName(name):
    global logname
    logname = str(name)

def out(tex, wrt=True, file=logname, doTime=True):
    localtime = time.asctime( time.localtime(time.time()) )
    try:
        text = legalize(str(tex))
        if wrt:
            print(text)
        with open(file, mode='a') as log:
            if doTime:
                log.write(localtime+ " : " + text + "\n")
            else:
                log.write(text+"\n")
            
    except Exception as e:
        print("Error in logger.out()... Something unforseen fucked up!")
        print(e)

def report(file=logname):
    with open(file, mode='a') as log:
        traceback.print_exc(file=log)
        traceback.print_exc(file=sys.stdout)

def tear(line=teartext):
    out(tex=line, wrt=False, doTime=False)