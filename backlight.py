#!/usr/bin/env python3
from tkinter import *
import sys
import os
import collections
import subprocess

wmi_location = "/sys/devices/platform/clevo_wmi/kbled"
wmi_install_location = "clevo_wmi_code"
wmi_url = "git://git.code.sf.net/p/clevo-wmi/code"

full_wmi_install_location = os.path.join(os.path.dirname(__file__),
                                         wmi_install_location)

COLORMAP = collections.OrderedDict()
COLORMAP["black"]       = "000"
COLORMAP["white"]       = "111"
COLORMAP["lime green"]  = "100"
COLORMAP["red"]         = "010"
COLORMAP["blue"]        = "001"
COLORMAP["yellow"]      = "110"
COLORMAP["magenta"]     = "011"
COLORMAP["aqua"]        = "101"

class ColoredRectangleButton(Canvas):
  colors = []
  defaultWidth = 60
  defaultHeight = 60
  def __init__(self,master,clickCallback,width=defaultWidth,height=defaultHeight,
                                         color="red"):
    Canvas.__init__(self,master,width=width,height=height)
    self.color = color;
    self.create_rectangle(0, 0, width, height, fill=color)
    self.clickCallback = clickCallback
    self.bind("<Button-1>", self.onClick)
  def onClick(self,event):
    # self.configure(highlightbackground="black",highlightthickness="5")
    self.clickCallback(self.color)

class PartialKeyboardController(Frame):

  """
  Controls a third of the keyboard.
  """
  def __init__(self,master,side):
    """
    Parameters:
    master - The container element.
    side - A string of either left, right, or middle.
    """
    Frame.__init__(self,master)
    index = 0
    for color in COLORMAP.keys():
      ColoredRectangleButton(self,self.onColorChosen,color=color)\
      .grid(row=int(index/4), column=index%4, padx=5, pady=5)
      index+=1
    self.side = side
  def onColorChosen(self,color):
    try:
      fd = os.open(wmi_location+"/"+self.side,os.O_WRONLY)
      os.write(fd,bytes(COLORMAP[color]+"\n", 'UTF-8'))

    except PermissionError:
      sys.exit("needs to be run as root!")
    except FileNotFoundError:
      raise ValueError("side needs to either left, right, or middle")
    else:
      os.close(fd)

class BrightnessController(Scale):
  def __init__(self,master):
    Scale.__init__(self,master,from_=10, to=0,
                               orient="vertical",
                               command=self.updateValue)
    try:
      f = open(wmi_location+"/brightness","r")
      self.set(int(f.readline()))
    except PermissionError:
      sys.exit("needs to be run as root!")
    else:
      f.close()
  def updateValue(self,event):
    try:
      fd = os.open(wmi_location+"/brightness",os.O_WRONLY)
      os.write(fd,bytes(str(self.get())+"\n", 'UTF-8'))
    except PermissionError:
      sys.exit("needs to be run as root!")
    else:
      os.close(fd)

def initView(master):
  master.wm_title("Keyboard Color Picker")
  master.geometry('+40+80')
  BrightnessController(root).grid(row=0,column=0,rowspan=3)
  Label(master,text="Choose Left Color").grid(row=0,column=1)
  PartialKeyboardController(master,"left").grid(row=1, column=1, padx=10)
  Label(master,text="Choose Middle Color").grid(row=0,column=2)
  PartialKeyboardController(master,"middle").grid(row=1, column=2, padx=10)
  Label(master,text="Choose Right Color").grid(row=0,column=3)
  PartialKeyboardController(master,"right").grid(row=1, column=3, padx=10)

def installWMI():
  if os.path.isdir(wmi_location):
    return
  else:
    print("Installing WMI")
    if not os.path.isdir(wmi_install_location):
      cloneStatus = subprocess.call(["git","clone",wmi_url,full_wmi_install_location])
      if cloneStatus == 127:
        sys.exit("needs git to clone wmi")
      elif cloneStatus != 0:
        sys.exit("error cloning wmi")
    r = subprocess.call(["make","-C",full_wmi_install_location])
    if r != 0:
      sys.exit("error making wmi")
    r = subprocess.call(["insmod",full_wmi_install_location+"/clevo_wmi.ko"])
    if r != 0:
      sys.exit("error installing wmi")
    return

# make sure user is root
if os.geteuid() != 0:
  sys.exit('needs to be run as root!')

installWMI()
root = Tk()
initView(root)
root.mainloop()