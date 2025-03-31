from subprocess import Popen, PIPE

#These need to be written as str not key
XKeySym = """&%!"#$\\\'()*+,-./:;<=>?@[]^_`{|}~ABCDEFGHIJKLMNOPQRSTUVWXYZ"""



class KeyMouse():
    """Offers an interface for Keyboard/mouse interaction.  Designed to send single
keystrokes, relative and absolute mouse positions, and Keyup/Keydown signals
At present, uses xte and pipes to handle X I/O"""
    ########################################################################
    # Starts the pipe (saved as xte) 
    ########################################################################
    def __init__(self, Display = ":0.0", LogFile = False):
        """Display is the x screen to use, default uses the DISPLAY system variable"""
        if Display:
                self.xte = Popen(['xte','-x', Display], stdin=PIPE)
        else:
                self.xte = Popen(['xte'], stdin=PIPE)
        if LogFile:
            self.log = open(LogFile, "w")
            self.log.write("xte stream logfile")
        else:
            self.log = False
        self.StickyKeys=[]
        self.OneShotStickyKeys=[]
    
    def Key(self, Key):
        """Sends a keystroke to the target window.  Available keystrokes are:
a-z, 1-0, `~!@#$%^&*()_+-=[]{}\|,.<>/?
F1,F2,F3,... F12
Home
Left
Up
Right
Down
Page_Up
Page_Down
End
Return
BackSpace
Tab
Escape
Delete
Control_L
Alt_L
Control_R
Alt_R
Shift_L
Shift_R

Note that case is important in the multi-character keystroke commands

Adding a # to the beginning of a keystroke makes it "sticky", and it will stay 
pressed until the next keystroke is is entered. so Key("#Alt_L") followed by 
Key("Tab") Key("Tab") will send Alt-Tab, Tab. 

If a stickey is entered, then entered again, it disables the sticky.  


Adding a "$" to the beginning of the keystroke makes it stick until the keystroke is sent again, with or without the "$"

Returns the key or combination of keys pressed, of the format "<sticky>-<sticky>-...<stiky>-Key
"""
        #Setting a one-shot sticky
        if Key[0] == "#" and len(Key) > 1:
            Key = Key[1:]
            if Key in self.OneShotStickyKeys:#Remove if pressed twice
                self.OneShotStickyKeys.remove(Key)
                return False
            else:#Flag it as sticky and send
                self.OneShotStickyKeys.append(Key) 
                self.SendKeyDown(Key)
            return Key

        #Setting/unsetting a perma sickey key
        elif Key[0] == "$" and len(Key) > 1:
            Key = Key[1:]
            if Key in self.StickyKeys: #Second time, remove key
                self.SendKeyUp(Key)
                self.StickyKeys.remove(Key)
            else: #first time, add key
                self.SendKeyDown(Key)
                self.StickyKeys.append(Key)
        #Regular key
        else: 
            if Key in self.StickyKeys or Key in self.OneShotStickyKeys:
                #Currently pressed sticky key
                if Key in self.StickyKeys:
                    self.SendKeyStroke(Key)
                    self.StickyKeys.remove(Key)
                elif Key in self.OneShotStickyKeys:
                    self.SendKeyUp(Key)
                    self.OneShotStickyKeys.remove(Key)
            else:
                self.SendKeyStroke(Key)
                #building return line
                Keys = ""
                for ii in self.OneShotStickyKeys + self.StickyKeys:
                    Keys+="<%s>-" % ii
                Keys += Key
                #Now to remove the oneshot stickies
                for ii in self.OneShotStickyKeys:
                    self.SendKeyUp(ii)
                    self.OneShotStickyKeys.remove(ii)
        return Keys

    def Exit(self):
        """terminates the keyer when you are done with it"""
        self.xte.terminate()
        self.log.close()



    ####################################################################################
    # These functions deal with the raw IO to the xde app and shouldn't generally be
    # used
    ####################################################################################
    def XteWrite(self, Str):
        self.xte.stdin.write(bytes(Str, "utf-8"))
        self.xte.stdin.flush()
        if self.log:
            self.log.write(str(Str))
            self.log.flush()
    def SendKeyStroke(self, Key):
        if Key in XKeySym:
            #Key = XKeySym[Key]
            self.XteWrite("str %s\n" % Key)
        else:
            self.XteWrite("key %s\n" % Key)
    def SendKeyDown(self, Key):
        self.XteWrite("keydown %s\n" % Key)
    def SendKeyUp(self, Key):
        self.XteWrite("keyup %s\n" % Key)
    def SendShiftKey(self, Key):
        self.SendKey("$Shift_L")
        return self.SendKey(Key)
    def MouseClick(self, Bttn):
        self.XteWrite("mouseclick %s\n" % Bttn)
    def MouseMoveXY(self, X, Y):
        self.XteWrite("mousermove %s %s\n" % (X, Y))
    def MouseMoveX(self, X):
        return self.MouseMoveXY(self, X, 0)
    def MouseMoveY(self, Y):
        return self.MouseMoveXY(self, 0, Y)

