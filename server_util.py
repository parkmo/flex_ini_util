#!/usr/bin/python3
#-*- coding: utf-8 -*-
import configparser
from optparse import OptionParser
import os
import sys
import getpass

g_szVersion = "0.7"
g_OptParser = OptionParser(version="%%prog %s" % (g_szVersion))

class CVimCrypt:
  def __init__(self, szFilename,szPassword):
    self.m_szFilename = szFilename
    self.m_szPassword = szPassword
  def runCmd(self, szCmd):
    fpPopen = os.popen(szCmd)
    szData=fpPopen.read()
    fpPopen.close()
    return szData
  def getPlainText(self):
    szData = self.runCmd("echo '%s'|vim -es '+%%print' '+:q!' %s" % ( self.m_szPassword, self.m_szFilename) )
    return szData

class CServerManager:
   def __init__(self, szData):
     self.m_szOrgData = szData
     self.m_config = configparser.RawConfigParser()
     try:
       self.m_config.read_string(szData)
     except:
       v_print (4, "Error: read ini file.")
       sys.exit(0)
     self.m_szSecName = None
   def setSection(self, szSectionName):
     if szSectionName in self.m_config.sections():
       self.m_szSecName = szSectionName
     else:
       print("Error: no %s exist" % (szSectionName))
       sys.exit(0)
   def getConfigInfoBySection(self, szSection, szKey):
     szValue = None
     try:
       szValue = self.m_config[szSection][szKey]
     except:
       pass
     return szValue
   def getConfigInfo(self, szKey):
     return self.getConfigInfoBySection('config',szKey)
   def getValueFromSection(self, szKey):
     szTergetSecName = self.m_szSecName
     globalSplit = szKey.split(":")
     if ( len(globalSplit) > 1 ): # Need Global Access
       szTergetSecName = globalSplit[0]
       szKey = globalSplit[1]
     try:
       szValue = self.m_config[szTergetSecName][szKey]
     except:
       try:
         szValue = self.m_config['config'][szKey]
       except:
         szValue = szKey
     return szValue
   def getMessageCallback(self, szOrgMessage, cbfProc):
     SplitedMsg=szOrgMessage.split("${")
     szRetMessage = SplitedMsg[0] # pre string
     for InnerMsg in SplitedMsg[1:]:
       szTmpRigtTrimed = InnerMsg.split("}")
       if ( len(szTmpRigtTrimed) < 2 ):
         szRetMessage += "${" + szTmpRigtTrimed[0]
         return szRetMessage
       szFieldname= szTmpRigtTrimed[0]
       szValue = str(cbfProc(szFieldname))
       szRetMessage += szValue
       szRetMessage += szTmpRigtTrimed[1]
     return szRetMessage
   def runCommandOne(self, szKey):
     szBaseCmd=self.getConfigInfo(szKey)
     if ( szBaseCmd is None ):
       print("Error: [config] [%s] is not exist" % (szKey))
       sys.exit(0)
     v_print (2, szBaseCmd)
     szOrgCmd = ""
     szOutCmd = szBaseCmd
     while szOrgCmd != szOutCmd:
       szOrgCmd=szOutCmd
       szOutCmd = self.getMessageCallback(szOrgCmd, self.getValueFromSection)
     v_print (3, szOutCmd)
     os.system(szOutCmd)
   def runCommand(self, szKey):
     loop_index=1
     if (self.m_szSecName == "loop"): # Loop Section
       szBaseCmd = self.getConfigInfoBySection(self.m_szSecName, szKey)
       if ( szBaseCmd is None ):
         print("Error: [config] [%s] is not exist" % (szKey))
         sys.exit(0)
       self.m_config['config'][szKey] = szBaseCmd
       self.m_config['config']['loop.total']=str(len(self.m_config.sections())-2) # config, loop
       for szCurSecName in self.m_config.sections():
         self.setSection(szCurSecName)
         if ( szCurSecName == "loop" or szCurSecName == "config"):
           continue
         self.m_config['config']['loop.index']=str(loop_index)
         self.m_config['config']['loop.section']=self.m_szSecName
         loop_index += 1
         self.runCommandOne(szKey)
       pass
     else:
       self.runCommandOne(szKey)

def _v_print(*verb_args):
  if verb_args[0] > (3 - g_verbosity):
    print (verb_args[1])
  else:
    _v_print = lambda *a: None  # do-nothing function

def main():
  g_OptParser.add_option("-c", "--cmd", dest="cmd",
    help="set command in [config] section")
  g_OptParser.add_option("-s", "--server", dest="servername",
    help="set setver name in [xxx] section") #, default="")
  g_OptParser.add_option("-v", '--verbosity', action="count", dest="verbosity", default=0,
    help="verbose")
  g_OptParser.add_option("-C", '--config', dest="cfg_inifile", default="serverlst.ini",
    metavar="FILE", help="config ini filename")
  (options, args) = g_OptParser.parse_args()
  global g_verbosity, v_print
  g_verbosity = options.verbosity
  v_print = _v_print
  # Read Password
  szPassword = getpass.getpass("Enter Password:", stream=sys.stdout)
  mVC = CVimCrypt(options.cfg_inifile, szPassword)
  szData = mVC.getPlainText()
  serman = CServerManager(szData)
  serman.setSection(options.servername)
  serman.runCommand(options.cmd)

if __name__ == "__main__":
  main()
