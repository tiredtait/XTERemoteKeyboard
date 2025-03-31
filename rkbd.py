#!/usr/bin/env python3
import curses
import keymouse
import sys
import os
import traceback

################################################################################
# Remote Keyboard V 0.5
# Released under the BSD licence
#
# Designed so that I could use my Cyberdeck as a keyboard without worrying about 
# cables or waiting for the KVM to switch back and forth.  Requires xte which is
# part of the xautomate package.
# 
# Note that Ctrl and Alt are always sent as key modifiers, not as standalone key
# strokes, so Ctrl clicking is not possible with this software
# 
################################################################################


#Use for testing
import time

# Some times curses returns a character, sometimes it returns a number, this
# function makes sure it always returns the int
def safeord(x):
    if x.__class__ is int:
        return x
    else:
        return ord(x)


#List of characters that are known to be directly supported and can be passed
#straight from curses input to the keyboard library's output
Passthrough = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-_\"'<>?|;:<>,./[([{)}]!@#$ ^*`~&=+%"

#List of characters that have to be altered.  Hash is what Curses spits out, contents is#what xde reads
Specials = {
        "\n": "Return", #return
        chr(9): "Tab", #return
        330: "Delete",
        263: "BackSpace",
        262: "Home",
        360: "End",
        260: "Left",
        259: "Up",
        261: "Right",
        258: "Down",
        339: "Page_Up",
        338: "Page_Down",
        265: "F1",
        266: "F2",
        267: "F3",
        268: "F4",
        269: "F5",
        270: "F6",
        271: "F7",
        272: "F8",
        273: "F9",
        274: "F10",
        275: "F11",
        276: "F12",
        #: "Control_L",
        "\x1b": "#Alt_R",
        "\\": "\\"

}

#Similar to above, but using ord to get the ascii code
NumSpecials = {
        9: "Tab"
}
#esc passes through


def Keyboard(Display):
    Keyer = keymouse.KeyMouse(Display, "/tmp/streamlog")

    #Set up the ncurses environment
    StdCurse = curses.initscr()
    curses.noecho()
    curses.cbreak()
    StdCurse.keypad(True)
    curses.raw()
    
    StdCurse.refresh()
    
    #Want to fix what curses did to the screen if something breaks
    try:
        while True:
            x = StdCurse.get_wch()
            if x == 275: #Exit button pressed
                curses.nocbreak()
                StdCurse.keypad(False)
                curses.echo()
                curses.endwin()
                Keyer.Exit()
                return(x)
            #Clear the screen
            StdCurse.erase()

            #Curses handles things a bit counterintuitively.  Some keys show up
            #as the ascii equivalent, others as numerical key codes, alt as a
            #two key combination, escape, annoyingly, as just the alt modifier
            #with no second code, and control + key as it's own set of codes

            if str(x) in Passthrough: #Standard charcter pressed, throw it 
                                      #straight to the keyboard
                StdCurse.addstr(0,0, "Latest: '%s', %s, %s" % (x, x.__repr__(), safeord(x)))
                Keyer.Key(x)
            elif x in Specials: #Needs a bit of conversion before we output
                StdCurse.addstr(0,0, "Special: %s, %s, %s" % (x, Specials[x], safeord(x) ))
                Keyer.Key(Specials[x])
            else: #Covers control keys and tabs
                StdCurse.addstr(0,0, "Other: %s, %s, %s" % (x, x.__repr__(), safeord(x) ))

                if(safeord(x) in NumSpecials):#Just tab, may edit
                    StdCurse.addstr(1,0, "NumSpec: %s" % NumSpecials[ord(x)])
                    Keyer.Key(NumSpecials[ord(x)])

                #Control keys
                elif(safeord(x) >= 1 and safeord(x) <= 26): #1-26 is ctrl a-ctrl-z
                    Keyer.Key("#Control_R")
                    Keyer.Key(chr(ord(x) - 1 + ord('a')))

                #Not any key i'm aware of, if this comes up send me a messsage
                else:
                    StdCurse.addstr(1,0, "Mystery: %s" % x)

    except Exception as E:
        #clear up the terminal from the curses takeover
        curses.nocbreak()
        StdCurse.keypad(False)
        curses.echo()
        curses.endwin()
        Keyer.Exit()
        print(traceback.print_tb(E.__traceback__))
        print(E)
        print("exeption: %s, %s, %s" % (x, x.__repr__(), safeord(x) ))
        return(E)

#debug function, prints out the latest character that was pressed
def TestChr():
    StdCurse = curses.initscr()
    curses.noecho()
    curses.cbreak()
    StdCurse.keypad(True)
    curses.raw()
    
    StdCurse.refresh()
    while True:
        x = StdCurse.get_wch()
        print(x)
        print(x.__repr__())
        time.sleep(1)
    curses.nocbreak()
    StdCurse.keypad(False)
    curses.echo()
    curses.endwin()


if __name__ == "__main__":
    if len(sys.argv) == 2: #only command line argument is the x11 display variable
                           #if no argument is given, check the environment to see
                           #what the current display is, if that doesn't work it 
                           #defaults to :0.0
        Display=sys.argv[1]
    elif "DISPLAY" in os.environ: 
        Display = os.environ["DISPLAY"]
    else:
        Display=":0.0" #Default displayZ
    Keyboard(Display)
