#/* 
#* SPDX-License-Identifier: Apache-2.0
#* Copyright 2019 Western Digital Corporation or its affiliates.
#* 
#* Licensed under the Apache License, Version 2.0 (the "License");
#* you may not use this file except in compliance with the License.
#* You may obtain a copy of the License at
#* 
#* http:*www.apache.org/licenses/LICENSE-2.0
#* 
#* Unless required by applicable law or agreed to in writing, software
#* distributed under the License is distributed on an "AS IS" BASIS,
#* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#* See the License for the specific language governing permissions and
#* limitations under the License.
#*/

import os
import importlib

STR_DEMOS_FOLDER = "demos"
STR_DEMO_MODULE = "demos.demo_"
STR_DEMO_CLASS = "demo"
STR_NEW_LINE = "\n"
STR_COMMENT = "#"
STR_CONFIG_FILE = "configure.txt"
STR_DEMO_MODULE_PREFIX = "demo_"
STR_DEMO_MODULE_SUFFIX = ".py"
STR_CONFIG_HEADER =  "##### This file is auto-generated by the build system. #####\n"
STR_CONFIG_HEADER += "#####         Please dont edit it manually.            #####"
STR_DEMO ="demo"
STR_TOOLCHAIN = "toolchain"
STR_SCONS_TOOLCHAIN = "scons-tools"
INT_DEMO_INDEX = 0
INT_TOOLCHAIN_INDEX = 1
INT_NUM_OF_CONFIGS = 2
STR_COMRV_DEMO = "comrv"
STR_COMRV_TC = "llvm"
STR_BITMANIP_DEMO = "bit_manipulation"
STR_BITMANIP_TC = "llvm-bitmanip"



class clsGenerate(object):
  def __init__(self):
    self.strConfigs = ""
    self.listDemos = []
    self.listToolchain = []

  def setDemo(self):
    listConfigs = []
    self.getConfigure()
    listConfigs = self.fnParseConfig()
    # if somehow the demo has not been set correctly break the build
    if len(listConfigs) != INT_NUM_OF_CONFIGS:
      print "No demo has been selected!"
      print "Please run the config.sh from the build folder."
      exit(1)

    print "Setting Demo to => %s (%s)" % (listConfigs[INT_DEMO_INDEX], listConfigs[INT_TOOLCHAIN_INDEX])
    # import the demo class accordig to the configure 
    strModuleName = STR_DEMO_MODULE + listConfigs[INT_DEMO_INDEX]
    mdlDemo = importlib.import_module(strModuleName)
    objClass = getattr(mdlDemo, STR_DEMO_CLASS)
    objDemo = objClass()
    objDemo.toolchain = listConfigs[INT_TOOLCHAIN_INDEX]
    objDemo.toolchainPath = os.path.join(STR_SCONS_TOOLCHAIN, listConfigs[INT_TOOLCHAIN_INDEX])
    return objDemo
    
  def fnParseConfig(self):
    listConfigs = []
    listLines = self.strConfigs.split(STR_NEW_LINE)
    for strLine in listLines:
      if strLine.startswith(STR_COMMENT):
        continue
      elif strLine.startswith(STR_DEMO):
        strArg = strLine.replace(STR_DEMO, '', 1)
        listConfigs.append(strArg)
        continue
      elif strLine.startswith(STR_TOOLCHAIN):
        strArg = strLine.replace(STR_TOOLCHAIN, '', 1)
        listConfigs.append(strArg)
        continue
    
    return listConfigs
    
  def getConfigure(self):
    # if he configure file does not exist break the build
    if not os.path.isfile(STR_CONFIG_FILE):
      print "No configure file has been found!"
      print "Please run the config.sh from the build folder."
      exit(1)

    # read the configure file from he build folder and grab its info
    f = open(STR_CONFIG_FILE, "r")
    self.strConfigs = f.read()
    f.close()
    
  def scanDemos(self):
    # scan the build/demo folder and grab all the files with pattern "demo_xxxx.py
    listFiles = os.listdir(os.path.join(os.getcwd(), STR_DEMOS_FOLDER))
    for strFile in sorted(listFiles):
      if strFile.startswith(STR_DEMO_MODULE_PREFIX) and strFile.endswith(STR_DEMO_MODULE_SUFFIX):
        self.listDemos.append(strFile.replace(STR_DEMO_MODULE_PREFIX, "").replace(STR_DEMO_MODULE_SUFFIX, "")) 

  def scanToolchains(self):
    # scan the build/toolchain folder and grab all the folders
    listDirs = os.listdir(os.path.join(os.getcwd(), STR_TOOLCHAIN, STR_SCONS_TOOLCHAIN))
    for strDir in sorted(listDirs):
      self.listToolchain.append(strDir) 
        
  def pickItem(self, strListName, listItems):
    # list all the demos found in the build/demos folder and wait for the user to pick one
    for strItem in sorted(listItems):
      print "%s: %s" % (listItems.index(strItem), strItem)
    
    # @todo: get demo name from argument/argument file in the future
    while(True):
      strItem = raw_input("Please select a %s: " %strListName)
      if not strItem.isdigit():
        print "Please enter an index!"
      elif int(strItem) > (len(listItems) - 1):
        print "Selected index out of range!"
      else:
        break
    return int(strItem)

  def setConfig(self):
    strConfiguration = STR_CONFIG_HEADER
    self.scanDemos()
    self.scanToolchains()
    intItemDemo = self.pickItem(STR_DEMO, self.listDemos)
    strConfiguration += "\n" + STR_DEMO + self.listDemos[intItemDemo]
    
    if self.listDemos[intItemDemo].find(STR_COMRV_DEMO) > -1:
      intItemTool = self.listToolchain.index(STR_COMRV_TC)
      print "\nAuto select toolchain ---> %s can only work with %s " % (self.listDemos[intItemDemo], STR_COMRV_TC)
    elif  self.listDemos[intItemDemo].find(STR_BITMANIP_DEMO) > -1:
      intItemTool = self.listToolchain.index(STR_BITMANIP_TC)
      print "\nAuto select toolchain ---> %s can only work with %s " % (self.listDemos[intItemDemo], STR_BITMANIP_TC)
    else:
      intItemTool = self.pickItem(STR_TOOLCHAIN, self.listToolchain)
    strConfiguration += "\n" + STR_TOOLCHAIN + self.listToolchain[intItemTool]

    print "\nSelected:"
    print "demo      = %s" % self.listDemos[intItemDemo]
    print "toolcahin = %s" % self.listToolchain[intItemTool]
    # save the configureation in the configure file in the build folder
    f  = open(STR_CONFIG_FILE, "w")
    f.write(strConfiguration)
    f.close()

if __name__ == "__main__":
  objConfigure= clsGenerate()
  objConfigure.setConfig()

