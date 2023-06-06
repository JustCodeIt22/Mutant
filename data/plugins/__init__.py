import os
# from FileManager import *

# For Dynamically importing the plugins
pwd = os.getcwd()
plugins = os.listdir(pwd + "\\data\\plugins")[:-2]
for plugs in plugins:
    path = "data.plugins." + plugs
    globals()[path] = __import__(path)
    print(plugs)
