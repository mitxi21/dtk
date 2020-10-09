# MIT License
# 
# Copyright (c) 2019
# Miguel Perales - miguelperalesbermejo@gmail.com 
# Jose Manuel Caballero - jcaballeromunoz4@gmail.com
# Jose Antonio Martin - ja.martin.esteban@gmail.com
# Miguel Diaz - migueldiazgil92@gmail.com
# Jesus Blanco Garrido - jesusblancogarrido@gmail.com
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import datetime
import json
import os
import platform
import shutil
import subprocess
import threading

import dtkglobal
import wx
import wx.lib.scrolledpanel as scrolled
import zipfile

import wx.lib.agw.ultimatelistctrl as ULC #Accelerate Integration
import wx.lib.agw.hyperlink as hl

MODULE_NAME_COL=0
DESCRIPTION_COL=1
MODULE_KEY_COL=2
DEPENDENCIES_COL=3
ADDITIONAL_INFO_COL=4

class ScriptDataPanel(wx.Panel):
    def __init__(self, parent):
        super(ScriptDataPanel, self).__init__(parent)
        self.logList = dict()
        self.stop = False
        self.InitUI()

    def InitUI(self):
        self.mainSizer = wx.GridBagSizer(1, 1)

        self.fileNameLbl = wx.StaticText(self, label="File")
        self.fileNameLbl.ToolTip = "File to add to workspace."
        #Accelerate Integration
        self.fileNameTextCtrl = wx.TextCtrl(self,style=wx.TE_READONLY)
        self.fileNameTextCtrl.ToolTip = "File to add to workspace."

        self.btnUploadFile = wx.Button(self, label="Browse")
        #Accelerate Integration
        #self.btnUploadFile.Bind(wx.EVT_BUTTON, self.UploadFile)
        self.btnUploadFile.Hide()

        self.scriptFileNameLbl = wx.StaticText(self, label="Script File")
        self.scriptFileNameLbl.ToolTip = "File to load script."
        #Accelerate Integration
        self.scriptFileNameTextCtrl = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.scriptFileNameTextCtrl.ToolTip = "File to load script."

        self.btnUploadScript = wx.Button(self, label="Browse")
        #Accelerate Integration
        #self.btnUploadScript.Bind(wx.EVT_BUTTON, self.UploadScript)
        self.btnUploadScript.Hide()

        self.clearLogsLbl = wx.StaticText(self, label="Clear Logs")
        self.clearLogsLbl.ToolTip = "Clear log output and asynchronous jobs."
        self.clearLogsCheckBox = wx.CheckBox(self)
        self.clearLogsCheckBox.ToolTip = "Clear log output and asynchronous jobs."
        self.clearLogsCheckBox.SetValue(True)

        self.scriptLbl = wx.StaticText(self, label="Script Text")
        self.scriptLbl.ToolTip = "Script Text."
        self.scriptTextCtrl = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_AUTO_URL | wx.HSCROLL)
        self.scriptTextCtrl.ToolTip = "Script Text."

        self.btnRunScript = wx.Button(self, label="Run Script")
        self.btnRunScript.Bind(wx.EVT_BUTTON, self.RunScriptButton)

        self.consoleOutputLbl = wx.StaticText(self, label="Log")
        self.consoleOutputLbl.ToolTip = "Console output log."
        self.consoleOutputTextCtrl = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_AUTO_URL | wx.HSCROLL
        )
        self.consoleOutputTextCtrl.ToolTip = "Console output log."

        self.btnStop = wx.Button(self, label="Stop")
        self.btnStop.Bind(wx.EVT_BUTTON, self.StopButton)

        self.btnRefreshLog = wx.Button(self, label="Refresh Log")
        self.btnRefreshLog.Bind(wx.EVT_BUTTON, self.RefreshLog)

        row = 0
        col = 0
        spanV = 10
        spanH = 50

        self.firstSizer = wx.GridBagSizer(1, 1)
        self.firstSizer.Add(self.fileNameLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)

        self.fileNameSizer = wx.GridBagSizer(1, 1)
        self.fileNameSizer.Add(
            self.fileNameTextCtrl, pos=(0, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5
        )
        self.fileNameSizer.Add(self.btnUploadFile, pos=(0, 1), flag=wx.TOP | wx.BOTTOM | wx.RIGHT, border=5)
        self.fileNameSizer.AddGrowableCol(0)
        self.fileNameSizer.SetEmptyCellSize((0, 0))
        self.firstSizer.Add(
            self.fileNameSizer,
            pos=(row, 1),
            span=(0, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=0,
        )

        row += 1
        self.firstSizer.Add(
            self.scriptFileNameLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )

        self.scriptFileSizer = wx.GridBagSizer(1, 1)
        self.scriptFileSizer.Add(
            self.scriptFileNameTextCtrl, pos=(0, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5
        )
        self.scriptFileSizer.Add(self.btnUploadScript, pos=(0, 1), flag=wx.TOP | wx.BOTTOM | wx.RIGHT, border=5)
        self.scriptFileSizer.AddGrowableCol(0)
        self.scriptFileSizer.SetEmptyCellSize((0, 0))
        self.firstSizer.Add(
            self.scriptFileSizer,
            pos=(row, col + 1),
            span=(0, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=0,
        )
        row += 1
        self.checkSizer = wx.GridBagSizer(1, 1)
        self.checkSizer.Add(self.clearLogsLbl, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.checkSizer.Add(self.clearLogsCheckBox, pos=(0, 1), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.checkSizer.AddGrowableCol(1)
        self.checkSizer.SetEmptyCellSize((0, 0))

        self.firstSizer.Add(self.checkSizer, pos=(row, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=0)
        row += 1
        self.firstSizer.Add(self.scriptLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        row += 1
        self.firstSizer.Add(
            self.scriptTextCtrl,
            pos=(row, col),
            span=(spanV, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )

        self.firstSizer.AddGrowableCol(1)
        self.firstSizer.AddGrowableRow(row)

        self.logSizer = wx.GridBagSizer(1, 1)
        row = 0
        self.logSizer.Add(self.consoleOutputLbl, pos=(row, 0), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        row += 1
        self.logSizer.Add(
            self.consoleOutputTextCtrl,
            pos=(row, 0),
            span=(10, 40),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )

        self.logSizer.AddGrowableCol(0)
        self.logSizer.AddGrowableRow(row)

        self.mainSizer.Add(
            self.firstSizer, pos=(0, 0), span=(0, 5), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5
        )
        self.mainSizer.Add(self.btnRunScript, pos=(1, 4), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.logSizer, pos=(2, 0), span=(0, 5), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5
        )
        self.mainSizer.Add(self.btnStop, pos=(3, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)
        self.mainSizer.Add(self.btnRefreshLog, pos=(3, 4), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)

        self.mainSizer.AddGrowableCol(0)
        self.mainSizer.AddGrowableRow(2)
        self.SetSizer(self.mainSizer)

    def StopButton(self, event):
        self.stop = True
        self.SetButtonState(True)

    def SetButtonState(self, state):
        if state:
            self.btnRunScript.Enable()
            self.btnRefreshLog.Enable()
        else:
            self.btnRunScript.Disable()
            self.btnRefreshLog.Disable()

    #Accelerate Integration
    def UploadFile(self):
        postMasterDataFolder = os.path.join(os.path.expanduser("~"), ".dtkconfig", "AccelerateDeployConfiguration", dtkglobal.postMasterDataFolder)
        if not os.path.exists(postMasterDataFolder):
            self.consoleOutputTextCtrl.AppendText("Post Master Data Script cannot be loaded...")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return

        self.consoleOutputTextCtrl.AppendText("Loading Accelerate Post Master Data Script & Files...")
        self.consoleOutputTextCtrl.AppendText(os.linesep)

        deployUrl = os.path.join(self.Parent.Parent.Parent.Parent.currentWorkspace, "deploy")
        deployDataUrl = os.path.join(deployUrl, "data")

        if not os.path.exists(deployDataUrl):
            os.makedirs(deployDataUrl)

        self.fileNameTextCtrl.Clear()
        pathnames = os.listdir(postMasterDataFolder)
        for pathname in pathnames:
            self.fileNameTextCtrl.AppendText(os.path.join(postMasterDataFolder,pathname))
            self.fileNameTextCtrl.AppendText(";")
            shutil.copy(os.path.join(postMasterDataFolder,pathname), deployDataUrl)
            self.consoleOutputTextCtrl.AppendText(
                "File copied into workspace data folder: " + dtkglobal.PathLeaf(os.path.join(postMasterDataFolder,pathname))
            )
            self.consoleOutputTextCtrl.AppendText(os.linesep)

        """
        if len(self.Parent.Parent.Parent.Parent.currentWorkspace) == 0:
            dlg = wx.MessageDialog(self, "Workspace not set yet.", "DTK - Deploy", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        deployUrl = os.path.join(self.Parent.Parent.Parent.Parent.currentWorkspace, "deploy")
        deployDataUrl = os.path.join(deployUrl, "data")

        dlg = wx.FileDialog(
            self,
            "Select file(s)",
            wildcard="All files (*.*)|*.*",
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE,
        )

        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        pathnames = dlg.GetPaths()
        self.fileNameTextCtrl.Clear()
        for pathname in pathnames:
            self.fileNameTextCtrl.AppendText(pathname)
            self.fileNameTextCtrl.AppendText(";")
            shutil.copy(pathname, deployDataUrl)
            self.consoleOutputTextCtrl.AppendText(
                "File copied into workspace data folder: " + dtkglobal.PathLeaf(pathname)
            )
            self.consoleOutputTextCtrl.AppendText(os.linesep)
        """

    #Accelerate Integration
    def UploadScript(self):

        postMasterDataScript = os.path.join(os.path.expanduser("~"), ".dtkconfig", "AccelerateDeployConfiguration", dtkglobal.postMasterDataFolder,dtkglobal.postMasterDataScript)
        if not os.path.exists(postMasterDataScript):
            self.consoleOutputTextCtrl.AppendText("Post Master Data Script cannot be loaded...")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return

        deployUrl = os.path.join(self.Parent.Parent.Parent.Parent.currentWorkspace, "deploy")
        deployDataUrl = os.path.join(deployUrl, "data")

        if not os.path.exists(deployDataUrl):
            os.makedirs(deployDataUrl)

        self.scriptFileNameTextCtrl.Clear()
        self.scriptFileNameTextCtrl.AppendText(postMasterDataScript)
        fileScript = open(postMasterDataScript, "r", encoding="utf8")
        self.scriptTextCtrl.Clear()
        self.scriptTextCtrl.AppendText(fileScript.read())
        self.consoleOutputTextCtrl.AppendText("Script loaded: " + dtkglobal.PathLeaf(postMasterDataScript))
        self.consoleOutputTextCtrl.AppendText(os.linesep)

        self.consoleOutputTextCtrl.AppendText("Success!!!")
        self.consoleOutputTextCtrl.AppendText(os.linesep)  

        """
        dlg = wx.FileDialog(
            self, "Select script file", wildcard="All files (*.*)|*.*", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        )

        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        pathname = dlg.GetPath()
        self.scriptFileNameTextCtrl.Clear()
        self.scriptFileNameTextCtrl.AppendText(pathname)
        fileScript = open(pathname, "r", encoding="utf8")
        self.scriptTextCtrl.AppendText(fileScript.read())
        self.consoleOutputTextCtrl.AppendText("Script loaded: " + dtkglobal.PathLeaf(pathname))
        self.consoleOutputTextCtrl.AppendText(os.linesep)
        """

    def RunScriptButton(self, event):
        self.stop = False
        deployUrl = os.path.join(self.Parent.Parent.Parent.Parent.currentWorkspace, "deploy")
        deployDataUrl = os.path.join(deployUrl, "data")
        deployStageUrl = os.path.join(deployUrl, "stage")
        orgName = self.Parent.Parent.Parent.Parent.organizationComboBox.GetValue()
        targetName = self.Parent.Parent.Parent.Parent.sandboxTypeTargetComboBox.GetValue()
        if len(orgName) == 0:
            dlg = wx.MessageDialog(self, "Please select an organization.", "DTK - Deploy", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(targetName) == 0:
            dlg = wx.MessageDialog(self, "Please select a target.", "DTK - Deploy", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if not os.path.exists(deployUrl):
            os.makedirs(deployUrl)
        if not os.path.exists(deployDataUrl):
            os.makedirs(deployDataUrl)
        if not os.path.exists(deployStageUrl):
            os.makedirs(deployStageUrl)

        if self.clearLogsCheckBox.GetValue():
            self.consoleOutputTextCtrl.Clear()
            self.consoleOutputTextCtrl.AppendText("Workspace: " + self.Parent.Parent.Parent.Parent.currentWorkspace)
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            self.logList.clear()

        scriptUrl = os.path.join(deployDataUrl, "defaultScript.txt")
        self.scriptTextCtrl.SaveFile(scriptUrl)
        self.SetButtonState(False)
        thread = threading.Thread(target=self.ProcessScript, args=(deployDataUrl, scriptUrl, deployStageUrl))
        thread.setDaemon(True)
        thread.start()

    def ProcessScript(self, deployDataUrl, scriptUrl, deployStageUrl):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        # deployType = self.deploymentTypeComboBox.GetValue()
        orgName = self.Parent.Parent.Parent.Parent.organizationComboBox.GetValue()
        sdbxNameSource = "Config"
        #Accelerate Integration
        """if dtkglobal.advSetting:
            sdbxNameSource = self.Parent.Parent.Parent.Parent.sandboxTypeSourceTextCtrl.GetValue()"""
        #Accelerate Integration
        sdbxName = self.Parent.Parent.Parent.Parent.sandboxTypeTargetComboBox.GetValue()
        sourceName = orgName + "_" + sdbxNameSource
        if "_" in sdbxNameSource:
            sourceName = sdbxNameSource
        targetName = self.Parent.Parent.Parent.Parent.currentTarget
        scriptFile = open(scriptUrl, "r", encoding="utf8")
        scriptFull = scriptFile.read()
        if "SOURCE" in scriptFull and len(sdbxNameSource) == 0:
            dlg = wx.MessageDialog(self, "Please select a Source.", "DTK - Deploy", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if "TARGET" in scriptFull and len(sdbxName) == 0:
            dlg = wx.MessageDialog(self, "Please select a Target.", "DTK - Deploy", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        scriptFile.close()
        i = 1
        scriptFile = open(scriptUrl, "r", encoding="utf8")
        for line in scriptFile:
            if self.stop:
                self.consoleOutputTextCtrl.AppendText("Process stopped.")
                self.consoleOutputTextCtrl.AppendText(os.linesep)
                return
            lineStr = line.strip("\r\n")
            lineSplit = lineStr.split("|")
            if len(lineSplit) > 0:
                if lineSplit[0] == "CMDEXECUTE":
                    self.ProcessCommandScriptLine(
                        lineSplit, lineStr, targetName, sourceName, deployDataUrl, i, deployStageUrl
                    )
                if lineSplit[0] == "FILE":
                    self.ProcessFileScriptLine(
                        lineSplit, lineStr, targetName, sourceName, deployDataUrl, i, deployStageUrl
                    )
                if (lineSplit[0] == "SOURCE" or lineSplit[0] == "TARGET") and (lineSplit[1] != "DEPLOYZIP" and lineSplit[1] != "DEPLOYFOLDER"):
                    self.ProcessDataScriptLine(
                        lineSplit, lineStr, targetName, sourceName, deployDataUrl, i, deployStageUrl
                    )
                if (lineSplit[0] == "SOURCE" or lineSplit[0] == "TARGET") and (lineSplit[1] == "DEPLOYZIP" or lineSplit[1] == "DEPLOYFOLDER"):
                    self.ProcessMetadataScriptLine(
                        lineSplit, lineStr, targetName, sourceName, deployDataUrl, i, deployStageUrl
                    )
        i += 1
        scriptFile.close()
        wx.CallAfter(self.SetButtonState, True)
        
    def ProcessCommandScriptLine(
        self, lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl
    ):
        error, errorMsg, cmd = dtkglobal.ProcessCommandScriptLine(
            lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl
        )
        if self.stop:
            return
        if error:
            self.consoleOutputTextCtrl.AppendText(errorMsg)
            self.consoleOutputTextCtrl.AppendText(os.linesep)
        else:
            proc = subprocess.Popen(cmd, shell=True, text=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            try:
                for line in proc.stdout:
                    self.consoleOutputTextCtrl.AppendText(line)
                self.consoleOutputTextCtrl.AppendText(os.linesep)
            except:
                self.consoleOutputTextCtrl.AppendText("Error processing stdout...")
                self.consoleOutputTextCtrl.AppendText(os.linesep)

    def ProcessFileScriptLine(
        self, lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl
    ):
        error, errorMsg, returnMsg = dtkglobal.ProcessFileScriptLine(
            lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl
        )
        if self.stop:
            return
        if error:
            self.consoleOutputTextCtrl.AppendText(errorMsg)
            self.consoleOutputTextCtrl.AppendText(os.linesep)
        else:
            self.consoleOutputTextCtrl.AppendText(returnMsg)
            self.consoleOutputTextCtrl.AppendText(os.linesep)

    def ProcessDataScriptLine(
        self, lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl
    ):
        error, errorMsg, target, pathString, cmd = dtkglobal.ProcessDataScriptLine(
            lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl
        )
        if self.stop:
            return
        if error:
            self.consoleOutputTextCtrl.AppendText(errorMsg)
            self.consoleOutputTextCtrl.AppendText(os.linesep)
        else:
            self.RunDataCmd(lineSplit, lineStr, target, pathString, cmd)

    def ProcessMetadataScriptLine(
        self, lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl
    ):  
        deployType = None,
        orgName = None,
        sdbxName = None,
        deployUrl = None,
        deployMetadataUrl = None,
        confirmDeploy = None,
        generateManifest = None,
        ignoreErrors = False,
        ignoreWarnings = False,
        specifiedTests = None,
        gitUrl = None,
        gitBranch = None,
        metadataGitFolder = None,
        metadataFolderSource = None,
        preScriptFile = None,
        scriptFile = None,
        zipFileUrlSource = None,
        zipFileUrlWorkspace = None
        preScriptFileWorkspace = None,
        scriptFileWorkspace = None,
        metadataTypes = None,

        error, errorMsg, target, pathString, cmd = dtkglobal.ProcessMetadataScriptLine(
            lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl
        )

        
        if self.stop:
            return
        if error:
            self.consoleOutputTextCtrl.AppendText(errorMsg)
            self.consoleOutputTextCtrl.AppendText(os.linesep)
        else:
            if lineSplit[1] == "DEPLOYZIP":
                fileTarget = lineSplit[2]
                testLevel = lineSplit[3]
                checkOnly = False
                if lineSplit[4] == "YES":
                    checkOnly = True
                ignoreWarnings = False
                if lineSplit[5] == "YES":
                    ignoreWarnings = True
                ignoreErrors = False
                if lineSplit[6] == "YES":
                    ignoreErrors = True
                waitParam = lineSplit[7]
                deployType = "Zip"
                zipFileUrlWorkspace = pathString
                fromScript = True
                self.RunDeploy(
                        deployType,
                        orgName,
                        sdbxName,
                        targetName,
                        deployUrl,
                        deployMetadataUrl,
                        deployDataUrl,
                        deployStageUrl,
                        checkOnly,
                        ignoreWarnings,
                        ignoreErrors,
                        confirmDeploy,
                        generateManifest,
                        testLevel,
                        specifiedTests,
                        gitUrl,
                        gitBranch,
                        metadataGitFolder,
                        metadataFolderSource,
                        preScriptFile,
                        scriptFile,
                        zipFileUrlSource,
                        zipFileUrlWorkspace,
                        preScriptFileWorkspace,
                        scriptFileWorkspace,
                        metadataTypes,
                        fromScript,
                        waitParam,
                    
                    )

    def OnText(self, text):
        self.consoleOutputTextCtrl.AppendText(text)
    
    def RunDeploy(
        self,
        deployType,
        orgName,
        sdbxName,
        targetName,
        deployUrl,
        deployMetadataUrl,
        deployDataUrl,
        deployStageUrl,
        checkOnly,
        ignoreWarnings,
        ignoreErrors,
        confirmDeploy,
        generateManifest,
        testLevel,
        specifiedTests,
        gitUrl,
        gitBranch,
        metadataGitFolder,
        metadataFolderSource,
        preScriptFile,
        scriptFile,
        zipFileUrlSource,
        zipFileUrlWorkspace,
        preScriptFileWorkspace,
        scriptFileWorkspace,
        metadataTypes,
        fromScript,
        waitParam,
    ):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        cmd = [
            "sfdx",
            "force:mdapi:deploy",
            "--apiversion",
            dtkglobal.defaultApiVersion,
            "-u",
            targetName,
            "-l",
            testLevel,
            "-w",
            waitParam
        ]
        if (platform.system() != "Windows"):
            cmd = ["/usr/local/bin/sfdx" + " " + "force:mdapi:deploy" + " " + "--apiversion" + " " + dtkglobal.defaultApiVersion + " " + "-u" + " " + targetName + " " + "-l" + " " +  testLevel + " " + "-w" + " " +  waitParam]
        if checkOnly:
            cmd.append("-c")
        if ignoreWarnings:
            cmd.append("-g")
        if ignoreErrors:
            cmd.append("-o")
        if testLevel == "RunSpecifiedTests":
            cmd.append("-r")
            cmd.append(specifiedTests)
        if deployType == "Zip":
            cmd.append("-f")
            cmd.append(zipFileUrlWorkspace)
        if deployType == "Folder" or deployType == "Git":
            cmd.append("-d")
            cmd.append(deployMetadataUrl)
        os.environ["SFDX_USE_PROGRESS_BAR"] = "false"
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
        )
        for line in proc.stdout:
            lineStr = line.decode()
            if "jobid:  " in lineStr:
                lineSplit = lineStr.split("jobid: ")
                if len(lineSplit) > 1:
                    logEntry = {}
                    logEntry["type"] = "Deploy"
                    logEntry["file"] = zipFileUrlWorkspace
                    logEntry["scriptLine"] = ""
                    jobIdStrip = lineSplit[1].strip("\r\n")
                    jobIdStrip = jobIdStrip.strip()
                    logEntry["jobid"] = jobIdStrip
                    logEntry["batchid"] = ""
                    logEntry["targetname"] = targetName
                    logEntry["pathname"] = deployMetadataUrl
                    self.logList[jobIdStrip] = logEntry
            wx.CallAfter(self.OnText, lineStr)
        
    def RunDataCmd(self, lineSplit, lineStr, target, pathString, cmd):
        if self.stop:
            return
        wx.CallAfter(self.OnText, os.linesep)
        wx.CallAfter(self.OnText, "Processing: " + lineStr)
        wx.CallAfter(self.OnText, os.linesep)
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
        )
        WINDOWS_LINE_ENDING = b'\r\n'
        UNIX_LINE_ENDING = b'\n'
        if "SOQLQUERY" in lineSplit:
            fileOutput = open(pathString, "w", encoding="utf8")
            for line in proc.stdout:
                lnStr = line.decode()
                if "Querying Data" not in lnStr:
                    if "sfdx-cli update available from" not in lnStr:
                        fileOutput.write(lnStr)
            fileOutput.close()
            fileRead = open(pathString, "rb")
            content = fileRead.read()
            content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)
            fileRead.close()
            fileOutput = open(pathString, "wb")
            fileOutput.write(content)
            fileOutput.close()
            wx.CallAfter(self.OnText, "Exported data to " + pathString + "\n")
        else:
            for line in proc.stdout:
                lnStr = line.decode()
                if "force:data:bulk:status" in lnStr:
                    lnSplit = lnStr.split("-i ")
                    if len(lnSplit) > 1:
                        lineSplitAgain = lnSplit[1].split(" -b ")
                        if len(lineSplitAgain) > 1:
                            logEntry = {}
                            logEntry["type"] = "Bulk"
                            logEntry["file"] = ""
                            logEntry["scriptLine"] = lineStr
                            jobIdStrip = lineSplitAgain[0].strip("\r\n")
                            jobIdStrip = jobIdStrip.strip()
                            logEntry["jobid"] = jobIdStrip
                            batchIdStrip = lineSplitAgain[1].strip("\r\n")
                            batchIdStrip = batchIdStrip.strip()
                            logEntry["batchid"] = batchIdStrip
                            logEntry["targetname"] = target
                            logEntry["pathname"] = pathString
                            self.logList[jobIdStrip] = logEntry
                wx.CallAfter(self.OnText, line)
        wx.CallAfter(self.SetButtonState, True)

    def RefreshLog(self, event):
        self.stop = False
        if len(self.logList) == 0:
            return
        self.consoleOutputTextCtrl.AppendText(
            "----------------------------------------------------------------------------------"
        )
        self.consoleOutputTextCtrl.AppendText(os.linesep)
        self.consoleOutputTextCtrl.AppendText(
            "Refresh log started at: " + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        )
        self.consoleOutputTextCtrl.AppendText(os.linesep)
        waitMinutes = "0"
        self.SetButtonState(False)
        thread = threading.Thread(target=self.RunRefreshLog, args=(waitMinutes))
        thread.setDaemon(True)
        thread.start()

    def RunRefreshLog(self, waitMinutes):
        for jobId in self.logList:
            if self.stop:
                self.consoleOutputTextCtrl.AppendText("Process stopped.")
                self.consoleOutputTextCtrl.AppendText(os.linesep)
                return
            log = self.logList[jobId]
            type, file, scriptLine, jobId, batchId, targetName, pathName = (
                log["type"],
                log["file"],
                log["scriptLine"],
                log["jobid"],
                log["batchid"],
                log["targetname"],
                log["pathname"],
            )
            if type == "Retrieve":
                cmd = [
                    "sfdx",
                    "force:mdapi:retrieve:report",
                    "--apiversion",
                    dtkglobal.defaultApiVersion,
                    "-u",
                    targetName,
                    "-i",
                    jobId,
                    "-r",
                    pathName,
                    "-w",
                    waitMinutes,
                ]
                if (platform.system() != "Windows"):
                    cmd = ["/usr/local/bin/sfdx" + " " + "force:mdapi:retrieve:report" + " " +  "--apiversion" + " " + dtkglobal.defaultApiVersion + " " + "-u" + " " + targetName + " " + "-i" + " " + jobId + " " + "-r"+ " " + pathName + " " + "-w" + " " + waitMinutes]
                proc = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
                )
                # zipToExtract = self.unZipRetrievedCheckBox.GetValue()
                zipToExtract = False
                zipReady = False
                zipUrl = ""
                for line in proc.stdout:
                    lineStr = line.decode()
                    wx.CallAfter(self.OnText, line)
                    if zipToExtract:
                        if "Wrote retrieve zip to " in lineStr:
                            lineSplit = lineStr.split("Wrote retrieve zip to ")
                            if len(lineSplit) > 1:
                                zipUrl = lineSplit[1]
                                zipUrl = zipUrl.strip("\r\n")
                                zipUrl = zipUrl.rstrip(".")
                                zipReady = True
                if zipToExtract and zipReady:
                    wx.CallAfter(self.Unzip, zipUrl)
            if type == "Deploy":
                cmd = [
                    "sfdx",
                    "force:mdapi:deploy:report",
                    "--apiversion",
                    dtkglobal.defaultApiVersion,
                    "-u",
                    targetName,
                    "-i",
                    jobId,
                ]
                if (platform.system() != "Windows"):
                    cmd = ["/usr/local/bin/sfdx" + " " + "force:mdapi:deploy:report" + " " + "--apiversion" + " " + dtkglobal.defaultApiVersion + " " + "-u" + " " + targetName + " " + "-i" + " " + jobId]
                proc = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
                )
                self.consoleOutputTextCtrl.AppendText(os.linesep)
                self.consoleOutputTextCtrl.AppendText("Metadata Deployment:")
                for line in proc.stdout:
                    wx.CallAfter(self.OnText, line)
            if type == "Bulk":
                cmd = [
                    "sfdx",
                    "force:data:bulk:status",
                    "--apiversion",
                    dtkglobal.defaultApiVersion,
                    "-u",
                    targetName,
                    "-i",
                    jobId,
                    "-b",
                    batchId,
                ]
                if (platform.system() != "Windows"):
                    cmd = ["/usr/local/bin/sfdx" + " " + "force:data:bulk:status" + " " + "--apiversion"+ " " + dtkglobal.defaultApiVersion+ " " +"-u" + " " + targetName + " " + "-i" + " " + jobId + " " + "-b" + " " + batchId]
                self.consoleOutputTextCtrl.AppendText(os.linesep)
                self.consoleOutputTextCtrl.AppendText("Script Line: " + scriptLine)
                proc = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
                )
                for line in proc.stdout:
                    wx.CallAfter(self.OnText, line)
        wx.CallAfter(self.SetButtonState, True)

class DeployMetadataPanel(wx.Panel):
    def __init__(self, parent, deployType):
        super(DeployMetadataPanel, self).__init__(parent)
        self.logList = dict()
        self.stop = False
        self.InitUI(deployType)

    def InitUI(self, deployType):
        self.mainSizer = wx.GridBagSizer(1, 1)
        self.deployTypeSelected = deployType

        # if dtkglobal.advSetting:
        self.deploymentTypeLbl = wx.StaticText(self, label="Deployment Type")
        self.deploymentTypeLbl.ToolTip = "Deployment Type: Git, Zip, Folder."
        self.deploymentTypeComboBox = wx.ComboBox(self, style=wx.CB_READONLY)
        self.deploymentTypeComboBox.ToolTip = "Deployment Type: Git, Zip, Folder."
        self.deploymentTypeComboBox.Items = dtkglobal.acceleratedeploymentTypes
        self.deploymentTypeComboBox.Bind(wx.EVT_COMBOBOX, self.ChangeDeploymentType)
        self.deploymentTypeComboBox.SetValue(self.deployTypeSelected)

        #Accelerate Integration
        self.gitUrlLbl = wx.StaticText(self, label = "Accelerate Git URL")
        self.gitUrlLbl.ToolTip = "Git URL where Accelerate configuration is"
        self.gitUrlTextCtrl = wx.TextCtrl(self, value = "", style = wx.CB_READONLY)
        self.gitUrlTextCtrl.ToolTip = "Git URL where Accelerate configuration is"
        self.organizationGitUrlLbl = wx.StaticText(self, label = "Organization Git URL")
        self.organizationGitUrlLbl.ToolTip = "Organization Git URL where Accelerate configuration is going to be pushed"
        self.organizationGitUrlTextCtrl = wx.TextCtrl(self, value = "", style = wx.CB_READONLY)
        self.organizationGitUrlTextCtrl.ToolTip = "Organization Git URL where Accelerate configuration is going to be pushed"
        """self.gitUrlComboBox = wx.ComboBox(self, style=wx.CB_READONLY)
        self.gitUrlComboBox.ToolTip = "Git Url set on Organization."
        self.gitUrlComboBox.Bind(wx.EVT_COMBOBOX, self.ChangeGitUrl)"""
        #Accelerate Integration

        self.gitBranchFilterLbl = wx.StaticText(self, label="Git Branch Filter")
        self.gitBranchFilterLbl.ToolTip = "Filter branch by this, wildcards allowed."
        self.gitBranchFilterTextCtrl = wx.TextCtrl(self)
        self.gitBranchFilterTextCtrl.ToolTip = "Filter branch by this, wildcards allowed."

        self.btnFilterBranch = wx.Button(self, label="Filter")
        self.btnFilterBranch.Bind(wx.EVT_BUTTON, self.ChangeGitUrl)

        #Accelerate Integration
        self.gitBranchLbl = wx.StaticText(self, label="Accelerate Git Branch")
        self.gitBranchLbl.ToolTip = "Git branch where the Accelerate version is going to be applied from"
        self.gitBranchTextCtrl = wx.TextCtrl(self, value = "", style = wx.CB_READONLY)
        self.gitBranchTextCtrl.ToolTip = "Git branch where the Accelerate version is going to be applied from"
        """self.gitBranchComboBox = wx.ComboBox(self, style=wx.CB_READONLY)
        self.gitBranchComboBox.ToolTip = "Git branch where the Accelerate version is going to be applied from" #Accelerate Integration
        self.gitBranchComboBox.Enable(False)"""
        #Accelerate Integration

        self.metadataGitFolderLbl = wx.StaticText(self, label="Accelerate Metadata Git Folder") #Accelerate Integration
        self.metadataGitFolderLbl.ToolTip = "Specifies the folder in the git repository containing the metadata to be deployed" #Accelerate Integration
        self.metadataGitFolderTextCtrl = wx.TextCtrl(self, value = "sfdc\src\\", style = wx.CB_READONLY) #Accelerate Integration
        self.metadataGitFolderTextCtrl.ToolTip = "Specifies the folder in the git repository containing the metadata to be deployed" #Accelerate Integration

        self.zipFileLbl = wx.StaticText(self, label="Zip File")
        self.zipFileLbl.ToolTip = (
            "Zip file to be deployed. It needs to be a valid metadata zip file containing a manifest."
        )
        self.zipFileTextCtrl = wx.TextCtrl(self)
        self.zipFileTextCtrl.ToolTip = (
            "Zip file to be deployed. It needs to be a valid metadata zip file containing a manifest."
        )

        self.btnZipFile = wx.Button(self, label="Browse")
        self.btnZipFile.Bind(wx.EVT_BUTTON, self.SelectZipFile)

        self.metadataFolderLbl = wx.StaticText(self, label="Metadata Folder")
        self.metadataFolderLbl.ToolTip = "Specifies the folder containing the metadata to be deployed. Manifest package will be overwritten" #Accelerate Integration
        self.metadataFolderTextCtrl = wx.TextCtrl(self)
        self.metadataFolderTextCtrl.ToolTip = "Specifies the folder containing the metadata to be deployed. Manifest package will be overwritten" #Accelerate Integration

        self.btnMetadataFolder = wx.Button(self, label="Browse")
        self.btnMetadataFolder.Bind(wx.EVT_BUTTON, self.SelectMetadataFolder)

        self.preScriptFolderLbl = wx.StaticText(self, label="PreDeploy Script File") #Accelerate Integration
        self.preScriptFolderLbl.ToolTip = "Script file to be executed before metadata deployment" #Accelerate Integration
        self.preScriptFolderTextCtrl = wx.TextCtrl(self, value = "", style = wx.CB_READONLY) #Accelerate Integration
        self.preScriptFolderTextCtrl.ToolTip = "Script file to be executed before metadata deployment" #Accelerate Integration

        self.scriptFolderLbl = wx.StaticText(self, label="PostDeploy Script File") #Accelerate Integration
        self.scriptFolderLbl.ToolTip = "Script file to be executed after metadata deployment" #Accelerate Integration
        self.scriptFolderTextCtrl = wx.TextCtrl(self, value = "", style = wx.CB_READONLY) #Accelerate Integration
        self.scriptFolderTextCtrl.ToolTip = "Script file to be executed after metadata deployment" #Accelerate Integration

        self.btnPreScriptFolder = wx.Button(self, label="Browse")
        self.btnPreScriptFolder.Bind(wx.EVT_BUTTON, self.selectPreScriptFolder)

        self.btnScriptFolder = wx.Button(self, label="Browse")
        self.btnScriptFolder.Bind(wx.EVT_BUTTON, self.SelectScriptFolder)

        #Accelerate Integration
        self.moduleWidget = wx.ListCtrl(self, size = wx.Size(510,-1), style = wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES)
        self.moduleWidget.EnableCheckBoxes(True)

        self.moduleWidget.Bind(wx.EVT_LIST_ITEM_CHECKED,self.OnListItemChecked)
        
        self.moduleWidget.InsertColumn(MODULE_NAME_COL, 'Module Name', width = 150)
        self.moduleWidget.InsertColumn(DESCRIPTION_COL, 'Description', width = 290)
        self.moduleWidget.InsertColumn(MODULE_KEY_COL, 'Module Key', width = -2)
        self.moduleWidget.InsertColumn(DEPENDENCIES_COL, 'Dependencies', width = -2)
        self.moduleWidget.InsertColumn(ADDITIONAL_INFO_COL, 'Additional Info', width = 150)
        #Accelerate Integration

        self.metadataTemplateLbl = wx.StaticText(self, label="Metadata Template")
        self.metadataTemplateLbl.ToolTip = "Template to autoselect Metadata Types."
        self.metadataTemplateComboBox = wx.ComboBox(self, style=wx.CB_READONLY)
        self.metadataTemplateComboBox.ToolTip = "Template to autoselect Metadata Types."
        self.metadataTemplateComboBox.Items = dtkglobal.metadataTemplates
        self.metadataTemplateComboBox.Bind(wx.EVT_COMBOBOX, self.ChangeMetadataTemplate)

        self.metadataTypesLbl = wx.StaticText(self, label="Metadata Types")
        self.metadataTypesLbl.ToolTip = "List of Metadata Types."
        self.metadataTypesListBox = wx.ListBox(self, style=wx.LB_MULTIPLE)
        self.metadataTypesListBox.ToolTip = "List of Metadata Types."
        self.metadataTypesListBox.Items = dtkglobal.metadataTypes
        self.metadataTypesListBox.Bind(wx.EVT_LISTBOX, self.ShowSelectedMetadataList)

        self.selectedMetadataTypesLbl = wx.StaticText(self, label="Selected Metadata Types")
        self.selectedMetadataTypesLbl.ToolTip = "Selected Metadata Types."
        self.selectedMetadataTypesTextCtrl = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_AUTO_URL | wx.VSCROLL | wx.TE_WORDWRAP
        )
        self.selectedMetadataTypesTextCtrl.ToolTip = "Selected Metadata Types."

        #Accelerate Integration
        self.btnCheckAll = wx.Button(self, label="Check All")
        self.btnCheckAll.Bind(wx.EVT_BUTTON, self.CheckAll)
        self.btnUnCheckAll = wx.Button(self, label="Uncheck All")
        self.btnUnCheckAll.Bind(wx.EVT_BUTTON, self.UnCheckAll)

        self.pushToGitLbl = wx.StaticText(self, label = "Push to Organization Git")
        self.pushToGitLbl.ToolTip = "If checked, Accelerate configuration will be pushed to your organization Git in a new branch"
        self.pushToGitCheckBox = wx.CheckBox(self)
        self.pushToGitCheckBox.Value = True
        self.pushToGitCheckBox.ToolTip = "If checked, Accelerate configuration will be pushed to your organization Git in a new branch"
        #Accelerate Integration

        self.checkOnlyLbl = wx.StaticText(self, label="Check Only")
        self.checkOnlyLbl.ToolTip = "If checked the deployment will be only validated. No changes will be applied."
        self.checkOnlyCheckBox = wx.CheckBox(self)
        self.checkOnlyCheckBox.ToolTip = "If checked the deployment will be only validated. No changes will be applied."

        self.ignoreWarningsLbl = wx.StaticText(self, label="Ignore Warnings")
        self.ignoreWarningsLbl.ToolTip = (
            "Deployment will ignore warnings if checked. Otherwise the deployment will fail if any warning occurs."
        )
        self.ignoreWarningsCheckBox = wx.CheckBox(self)
        self.ignoreWarningsCheckBox.ToolTip = (
            "Deployment will ignore warnings if checked. Otherwise the deployment will fail if any warning occurs."
        )

        self.ignoreErrorsLbl = wx.StaticText(self, label="Ignore Errors")
        self.ignoreErrorsLbl.ToolTip = (
            "Deployment will ignore errors if checked. Otherwise the deployment will fail if any error occurs."
        )
        self.ignoreErrorsCheckBox = wx.CheckBox(self)
        self.ignoreErrorsCheckBox.ToolTip = (
            "Deployment will ignore errors if checked. Otherwise the deployment will fail if any error occurs."
        )
        if not dtkglobal.advSetting:
            self.ignoreErrorsCheckBox.SetValue(False)
            self.ignoreErrorsCheckBox.Enable(False)

        self.generateManifestLbl = wx.StaticText(self, label="Generate Manifest")
        self.generateManifestLbl.ToolTip = "Auto generate xml manifest depending on the metdata types selected."
        self.generateManifestCheckBox = wx.CheckBox(self)
        self.generateManifestCheckBox.ToolTip = "Auto generate xml manifest depending on the metdata types selected."
        self.generateManifestCheckBox.Value = True

        self.confirmDeployLbl = wx.StaticText(self, label="Confirm Deploy")
        self.confirmDeployLbl.ToolTip = "Confirm deployment, if unchecked only the pull will be done from git branch."
        self.confirmDeployCheckBox = wx.CheckBox(self)
        self.confirmDeployCheckBox.ToolTip = (
            "Confirm deployment, if unchecked only the pull will be done from git branch."
        )
        self.confirmDeployCheckBox.Value = True

        self.clearLogsLbl = wx.StaticText(self, label="Clear Logs")
        self.clearLogsLbl.ToolTip = "Clear log output and asynchronous jobs."
        self.clearLogsCheckBox = wx.CheckBox(self)
        self.clearLogsCheckBox.ToolTip = "Clear log output and asynchronous jobs."
        self.clearLogsCheckBox.SetValue(True)

        self.waitParamLbl = wx.StaticText(self, label="Wait time")
        self.waitParamLbl.ToolTip = "Wait time for SFDX Deploy (minutes)."
        self.waitParamNumCtrl = wx.TextCtrl(self, size = (-1,-1),style = wx.TE_RIGHT)
        self.waitParamNumCtrl.ToolTip = "Wait time for SFDX Deploy. DTK will wait for the input minutes. If the deploy finishes before, then DTK wil stop waiting. For Unlimited waiting use '-1'"
        self.waitParamNumCtrl.SetValue('-1')

        self.testLevelsLbl = wx.StaticText(self, label="Test Levels")
        self.testLevelsLbl.ToolTip = """Specifies which level of deployment tests to run. Valid values are:

        NoTestRun—No tests are run. This test level applies only to deployments to development environments, such as sandbox, Developer Edition, or trial orgs. This test level is the default for development environments.

        RunSpecifiedTests—Runs only the tests that you specify in the --runtests option. Code coverage requirements differ from the default coverage requirements when using this test level. Executed tests must comprise a minimum of 75% code coverage for each class and trigger in the deployment package. This coverage is computed for each class and trigger individually and is different than the overall coverage percentage.

        RunLocalTests—All tests in your org are run, except the ones that originate from installed managed packages. This test level is the default for production deployments that include Apex classes or triggers.

        RunAllTestsInOrg—All tests in your org are run, including tests of managed packages.

        If this field is blank the default test level used is NoTestRun."""
        self.testLevelsComboBox = wx.ComboBox(self, style=wx.CB_READONLY)
        self.testLevelsComboBox.ToolTip = """Specifies which level of deployment tests to run. Valid values are:

        NoTestRun—No tests are run. This test level applies only to deployments to development environments, such as sandbox, Developer Edition, or trial orgs. This test level is the default for development environments.

        RunSpecifiedTests—Runs only the tests that you specify in the --runtests option. Code coverage requirements differ from the default coverage requirements when using this test level. Executed tests must comprise a minimum of 75% code coverage for each class and trigger in the deployment package. This coverage is computed for each class and trigger individually and is different than the overall coverage percentage.

        RunLocalTests—All tests in your org are run, except the ones that originate from installed managed packages. This test level is the default for production deployments that include Apex classes or triggers.

        RunAllTestsInOrg—All tests in your org are run, including tests of managed packages.

        If this field is blank the default test level used is NoTestRun."""
        self.testLevelsComboBox.Items = dtkglobal.testLevels
        self.testLevelsComboBox.SetStringSelection("NoTestRun")
        self.testLevelsComboBox.Bind(wx.EVT_COMBOBOX, self.ChangeTestLevels)

        self.specifiedTestsLbl = wx.StaticText(self, label="Specified Tests")
        self.specifiedTestsLbl.ToolTip = (
            "Lists the Apex classes containing the deployment tests to run. Separate classes names by comma."
        )
        self.specifiedTestTextCtrl = wx.TextCtrl(self)
        self.specifiedTestTextCtrl.ToolTip = (
            "Lists the Apex classes containing the deployment tests to run. Separate classes names by comma."
        )

        self.btnDeploy = wx.Button(self, label="Deploy")
        self.btnDeploy.Bind(wx.EVT_BUTTON, self.DeployButton)

        self.consoleOutputLbl = wx.StaticText(self, label="Log")
        self.consoleOutputLbl.ToolTip = "Console output log."
        self.consoleOutputTextCtrl = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_AUTO_URL | wx.HSCROLL
        )
        self.consoleOutputTextCtrl.ToolTip = "Console output log."

        self.btnStop = wx.Button(self, label="Stop")
        self.btnStop.Bind(wx.EVT_BUTTON, self.StopButton)

        self.btnRefreshLog = wx.Button(self, label="Refresh Log")
        self.btnRefreshLog.Bind(wx.EVT_BUTTON, self.RefreshLog)
        
        #Accelerate Integration
        self.btnRefreshLog.Hide()
        #End Accelerate Integration

        row = 0
        col = 0
        spanV = 5
        spanH = 5

        self.typeSizer = wx.GridBagSizer(1, 1)

        if dtkglobal.advSetting:
            self.typeSizer.Add(
                self.deploymentTypeLbl,
                pos=(row, col),
                flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
                border=5,
            )
            col += 1
            self.typeSizer.Add(
                self.deploymentTypeComboBox,
                pos=(row, col),
                span=(0, spanH + 15),
                flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
                border=5,
            )
            self.typeSizer.AddGrowableCol(col)

        self.typeSizer.AddGrowableRow(row)
        self.typeSizer.SetEmptyCellSize((0, 0))

        row = 0
        col = 0
        self.deploySizer = wx.GridBagSizer(1, 1)
        self.deploySizer.Add(
            self.gitUrlLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5
        )
        self.deploySizer.Add(
            #self.gitUrlComboBox,
            self.gitUrlTextCtrl,
            pos=(row, col + 1),
            span=(0, spanH + 15),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )
        row += 1
        self.deploySizer.Add(
            self.gitBranchFilterLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5
        )

        self.filterBranchSizer = wx.GridBagSizer(1, 1)
        self.filterBranchSizer.Add(
            self.gitBranchFilterTextCtrl,
            pos=(0, 0),
            span=(0, 10),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )
        self.filterBranchSizer.Add(self.btnFilterBranch, pos=(0, 11), flag=wx.TOP | wx.BOTTOM | wx.RIGHT, border=5)
        self.filterBranchSizer.AddGrowableCol(0)
        self.filterBranchSizer.SetEmptyCellSize((0, 0))
        self.deploySizer.Add(
            self.filterBranchSizer,
            pos=(row, col + 1),
            span=(0, spanH + 15),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=0,
        )
        row += 1
        self.deploySizer.Add(
            self.gitBranchLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5
        )
        self.deploySizer.Add(
            #self.gitBranchComboBox,
            self.gitBranchTextCtrl,
            pos=(row, col + 1),
            span=(0, spanH + 15),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )
        row += 1
        self.deploySizer.Add(
            self.metadataGitFolderLbl,
            pos=(row, col),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )
        self.deploySizer.Add(
            self.metadataGitFolderTextCtrl,
            pos=(row, col + 1),
            span=(0, spanH + 15),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )
        row += 1

        self.deploySizer.Add(
            self.zipFileLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5
        )
        self.zipFileSizer = wx.GridBagSizer(1, 1)
        self.zipFileSizer.Add(
            self.zipFileTextCtrl, pos=(0, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5
        )
        self.zipFileSizer.Add(self.btnZipFile, pos=(0, 1), flag=wx.TOP | wx.BOTTOM | wx.RIGHT, border=5)
        self.zipFileSizer.AddGrowableCol(0)
        self.zipFileSizer.SetEmptyCellSize((0, 0))
        self.deploySizer.Add(
            self.zipFileSizer,
            pos=(row, col + 1),
            span=(0, spanH + 15),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=0,
        )
        row += 1
        self.deploySizer.Add(
            self.metadataFolderLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5
        )
        self.metadataFolderSizer = wx.GridBagSizer(1, 1)
        self.metadataFolderSizer.Add(
            self.metadataFolderTextCtrl, pos=(0, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5
        )
        self.metadataFolderSizer.Add(self.btnMetadataFolder, pos=(0, 1), flag=wx.TOP | wx.BOTTOM | wx.RIGHT, border=5)
        self.metadataFolderSizer.AddGrowableCol(0)
        self.metadataFolderSizer.SetEmptyCellSize((0, 0))
        self.deploySizer.Add(
            self.metadataFolderSizer,
            pos=(row, col + 1),
            span=(0, spanH + 15),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=0,
        )
        row += 1
        self.deploySizer.Add(self.preScriptFolderLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM , border=5)        
        row += 1
        self.deploySizer.Add(self.scriptFolderLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM , border=5)


        self.preScriptFolderSizer = wx.GridBagSizer(1, 1)
        self.scriptFolderSizer = wx.GridBagSizer(1, 1)
        self.organizationGitSizer = wx.GridBagSizer(1, 1) #Accelerate Integration

        self.preScriptFolderSizer.Add(
            self.preScriptFolderTextCtrl, pos=(0, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5
        )
        self.preScriptFolderSizer.Add(self.btnPreScriptFolder, pos=(0, 1), flag=wx.TOP | wx.BOTTOM | wx.RIGHT, border=5)
        self.scriptFolderSizer.Add(
            self.scriptFolderTextCtrl, pos=(1, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5
        )
        self.scriptFolderSizer.Add(self.btnScriptFolder, pos=(1, 1), flag=wx.TOP | wx.BOTTOM | wx.RIGHT, border=5)
        self.preScriptFolderSizer.AddGrowableCol(0)
        self.scriptFolderSizer.AddGrowableCol(0)
        self.preScriptFolderSizer.SetEmptyCellSize((0, 0))
        self.scriptFolderSizer.SetEmptyCellSize((0, 0))
        self.deploySizer.Add(
            self.preScriptFolderSizer,
            pos=(row-1, col + 1),
            span=(1, spanH + 15),
            flag=wx.EXPAND | wx.TOP | wx.BOTTOM | wx.RIGHT,
            border=0,
        )
        self.deploySizer.Add(
            self.scriptFolderSizer,
            pos=(row, col + 1),
            span=(1, spanH + 15),
            flag=wx.EXPAND | wx.TOP | wx.BOTTOM | wx.RIGHT,
            border=0,
        )
        

        #Accelerate Integration
        self.deploySizer.Add(self.organizationGitUrlLbl, pos = (row+1, col), flag = wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM, border = 5)
        self.organizationGitSizer.Add(self.organizationGitUrlTextCtrl, pos = (1,0), flag = wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM | wx.RIGHT, border = 5) #Accelerate Integration
        self.organizationGitSizer.AddGrowableCol(0)
        self.organizationGitSizer.SetEmptyCellSize((0, 0))
        self.deploySizer.Add(self.organizationGitSizer, pos = (row+1, col + 1), span = (1, spanH + 15), flag = wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM | wx.RIGHT, border = 0)
        #Accelerate Integration

        self.deploySizer.AddGrowableCol(col + 1)
        self.deploySizer.SetEmptyCellSize((0, 0))

        #Accelerate Integration
        self.moduleSizer = wx.GridBagSizer(1, 1)
        self.btnCheckSizer = wx.GridBagSizer(1, 1)
        col = 0
        row = 0
        self.moduleSizer.Add(self.moduleWidget, pos = (row,col), span = (0, spanH + 15), flag = wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border = 5)
        row += 1
        self.moduleSizer.Add(self.btnCheckSizer, pos = (row,col), flag = wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT | wx.ALIGN_LEFT, border = 1)
        self.btnCheckSizer.Add(self.btnCheckAll, pos = (row-1,col), flag = wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT | wx.ALIGN_LEFT, border = 1)
        self.btnCheckSizer.Add(self.btnUnCheckAll, pos=(row-1, col + 1), flag = wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT | wx.ALIGN_LEFT, border = 1)

        self.moduleSizer.Add(self.pushToGitLbl, pos = (row, col + 17), flag = wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT | wx.ALIGN_RIGHT, border = 5)
        self.moduleSizer.Add(self.pushToGitCheckBox, pos = (row, col + 18), span = (0,0), flag = wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border = 5)

        row += 1
        self.moduleSizer.Add(self.checkOnlyLbl, pos = (row, col + 17), flag = wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT | wx.ALIGN_RIGHT, border = 5)
        self.moduleSizer.Add(self.checkOnlyCheckBox, pos=(row, col + 18), span=(0, 0), flag = wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border = 5)
        row += 1
        self.moduleSizer.Add(self.clearLogsLbl, pos = (row, col + 17), flag = wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_RIGHT, border = 5)
        self.moduleSizer.Add(self.clearLogsCheckBox, pos=(row, col + 18), span=(0, 0), flag = wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border = 5)

        row += 1
        self.moduleSizer.Add(self.generateManifestLbl, pos = (row, col + 17), flag = wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_RIGHT, border = 5)
        self.moduleSizer.Add(self.generateManifestCheckBox, pos=(row, col + 18), span=(0, 0), flag = wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border = 5)

        #Accelerate Integration

        self.optionsSizer = wx.GridBagSizer(1, 1)

        self.metadataSizer = wx.GridBagSizer(1, 1)
        self.selectedMetadataSizer = wx.GridBagSizer(1, 1)
        col = 0
        row = 0
        self.metadataSizer.Add(
            self.testLevelsLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.metadataSizer.Add(
            self.testLevelsComboBox, pos=(row, col + 1), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        row += 1
        self.metadataSizer.Add(
            self.specifiedTestsLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.metadataSizer.Add(
            self.specifiedTestTextCtrl, pos=(row, col + 1), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        row += 1
        self.metadataSizer.Add(
            self.metadataTemplateLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.metadataSizer.Add(
            self.metadataTemplateComboBox, pos=(row, col + 1), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        row += 1
        self.metadataSizer.Add(
            self.metadataTypesLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.metadataSizer.Add(
            self.metadataTypesListBox, pos=(row, col + 1), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )

        self.metadataSizer.AddGrowableCol(col + 1)
        self.metadataSizer.AddGrowableRow(row)
        self.metadataSizer.SetEmptyCellSize((0, 0))

        row = 0
        col = 0
        self.selectedMetadataSizer.Add(
            self.selectedMetadataTypesLbl, pos=(row, col), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        row += 1
        self.selectedMetadataSizer.Add(
            self.selectedMetadataTypesTextCtrl,
            pos=(row, col),
            span=(1, 2),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )
        self.selectedMetadataSizer.AddGrowableRow(1)
        self.selectedMetadataSizer.AddGrowableCol(0)
        self.selectedMetadataSizer.SetEmptyCellSize((0, 0))

        self.checkBoxesOptionsSizer = wx.GridBagSizer(1, 1)
        col = 0
        row = 0
        #Accelerate Integration
        """self.checkBoxesOptionsSizer.Add(
            self.checkOnlyLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.checkBoxesOptionsSizer.Add(self.checkOnlyCheckBox, pos = (row, col + 1), span=(0, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)""" #Accelerate Integration
        row += 1
        self.checkBoxesOptionsSizer.Add(
            self.ignoreWarningsLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.checkBoxesOptionsSizer.Add(
            self.ignoreWarningsCheckBox,
            pos=(row, col + 1),
            span=(0, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )
        row += 1
        self.checkBoxesOptionsSizer.Add(
            self.ignoreErrorsLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.checkBoxesOptionsSizer.Add(
            self.ignoreErrorsCheckBox,
            pos=(row, col + 1),
            span=(0, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )
        row += 1
        self.checkBoxesOptionsSizer.Add(
            self.confirmDeployLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.checkBoxesOptionsSizer.Add(
            self.confirmDeployCheckBox,
            pos=(row, col + 1),
            span=(0, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )
        row += 1
        #Accelerate Integration
        """
        self.checkBoxesOptionsSizer.Add(
            self.generateManifestLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.checkBoxesOptionsSizer.Add(
            self.generateManifestCheckBox,
            pos=(row, col + 1),
            span=(0, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )
        row += 1
        self.checkBoxesOptionsSizer.Add(self.clearLogsLbl, pos=(row, col), flag=wx.TOP | wx.LEFT | wx.RIGHT , border=5)
        self.checkBoxesOptionsSizer.Add(self.clearLogsCheckBox, pos=(row, col + 1), span = (0, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)""" #Accelerate Integration

        self.checkBoxesOptionsSizer.SetEmptyCellSize((0, 0))
        self.waitTimeSizer = wx.GridBagSizer(1, 1)
        self.waitTimeSizer.Add(self.waitParamLbl, pos=(0, 0))
        self.waitTimeSizer.Add(
            self.waitParamNumCtrl, pos=(0, 2))

        col = 0
        row = 0
        self.optionsSizer.Add(
            self.metadataSizer, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.optionsSizer.Add(
            self.selectedMetadataSizer, pos=(row, col + 1), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.optionsSizer.Add(
            self.checkBoxesOptionsSizer, pos=(row, col + 3), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )

        self.moduleSizer.AddGrowableCol(1)
        self.moduleSizer.AddGrowableCol(0)
        self.moduleSizer.AddGrowableCol(2)
        self.moduleSizer.AddGrowableRow(row)
        self.moduleSizer.SetEmptyCellSize((0, 0))

        self.optionsSizer.AddGrowableCol(1)
        self.optionsSizer.AddGrowableCol(0)
        self.optionsSizer.AddGrowableCol(2)
        self.optionsSizer.AddGrowableRow(row)
        self.optionsSizer.SetEmptyCellSize((0, 0))

        self.logSizer = wx.GridBagSizer(1, 1)
        row = 0
        self.logSizer.Add(self.consoleOutputLbl, pos=(row, 0), span=(0, 2), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        row += 1
        self.logSizer.Add(
            self.consoleOutputTextCtrl,
            pos=(row, 0),
            span=(10, 40),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )

        self.logSizer.AddGrowableCol(0)
        self.logSizer.AddGrowableRow(row)
        row = 0
        self.btnDeploySizer= wx.GridBagSizer(1,1)
        self.btnDeploySizer.Add(
                self.waitTimeSizer,
                pos=(row,0),
                flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT | wx.ALIGN_RIGHT,
                border=10,
        )
        self.btnDeploySizer.Add(self.btnDeploy, pos=(row, 1), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT | wx.ALIGN_RIGHT, border=10)
        
        row = 0
        self.mainSizer.Add(
            self.typeSizer,
            pos=(row, 0),
            span=(0, 5),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )
        row += 1
        self.mainSizer.Add(
            self.deploySizer,
            pos=(row, 0),
            span=(0, 5),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )
        row += 1
        self.mainSizer.Add(self.moduleSizer, pos = (row, 0), span = (0, 5), flag = wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border = 5)
        row += 1
        self.mainSizer.Add(
            self.optionsSizer,
            pos=(row, 0),
            span=(0, 5),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )
        row += 1
        self.mainSizer.Add(
            self.btnDeploySizer, pos=(row, 4), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT | wx.ALIGN_RIGHT
        )
        row += 1
        self.mainSizer.Add(
            self.logSizer, pos=(row, 0), span=(0, 5), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5
        )
        row += 1
        self.mainSizer.Add(self.btnStop, pos=(row, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.btnRefreshLog, pos=(row, 4), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT | wx.ALIGN_RIGHT, border=10
        )

        self.specifiedTestsLbl.Hide()
        self.specifiedTestTextCtrl.Hide()

        if not dtkglobal.advSetting:
            self.deploymentTypeLbl.Hide()
            self.deploymentTypeComboBox.Hide()

        #Accelerate Integration
        if self.deployTypeSelected == "Zip":

            self.selectedMetadataTypesLbl.Hide()
            self.selectedMetadataTypesTextCtrl.Hide()
            self.gitBranchLbl.Hide()
            #self.gitBranchComboBox.Hide()
            self.gitBranchTextCtrl.Hide()
            self.gitBranchFilterLbl.Hide()
            self.btnFilterBranch.Hide()
            self.gitUrlLbl.Hide()
            #self.gitUrlComboBox.Hide()
            self.gitUrlTextCtrl.Hide() #Accelerate Integration
            self.gitBranchFilterTextCtrl.Hide()
            self.metadataFolderLbl.Hide()
            self.metadataFolderTextCtrl.Hide()

            self.generateManifestLbl.Hide()
            self.generateManifestCheckBox.Hide()
            self.confirmDeployLbl.Hide()
            self.confirmDeployCheckBox.Hide()

            self.metadataTemplateLbl.Hide()
            self.metadataTemplateComboBox.Hide()
            self.metadataTypesLbl.Hide()
            self.metadataTypesListBox.Hide()

            self.metadataFolderLbl.Hide()
            self.metadataFolderTextCtrl.Hide()
            self.btnMetadataFolder.Hide()

        #Accelerate Integration
        if self.deployTypeSelected == "Git":
            self.gitBranchFilterLbl.Hide()
            self.gitBranchFilterTextCtrl.Hide()
            self.btnFilterBranch.Hide()

            self.btnPreScriptFolder.Hide()
            self.btnScriptFolder.Hide()

            self.testLevelsLbl.Hide()
            self.testLevelsComboBox.Hide()

            self.metadataTemplateLbl.Hide()
            self.metadataTemplateComboBox.Hide()

            self.metadataTypesLbl.Hide()
            self.metadataTypesListBox.Hide()

            self.selectedMetadataTypesLbl.Hide()
            self.selectedMetadataTypesTextCtrl.Hide()

            self.ignoreWarningsLbl.Hide()
            self.ignoreWarningsCheckBox.Hide()

            self.ignoreErrorsLbl.Hide()
            self.ignoreErrorsCheckBox.Hide()

            self.confirmDeployLbl.Hide()
            self.confirmDeployCheckBox.Hide()

            self.generateManifestLbl.Hide()
            self.generateManifestCheckBox.Hide()

            self.waitParamLbl.Hide()
            self.waitParamNumCtrl.Hide()

            self.zipFileLbl.Hide()
            self.zipFileTextCtrl.Hide()
            self.btnZipFile.Hide()

            self.metadataFolderLbl.Hide()
            self.metadataFolderTextCtrl.Hide()
            self.btnMetadataFolder.Hide()

        #Accelerate Integration
        if self.deployTypeSelected == "Folder":
            self.gitBranchLbl.Hide()
            #self.gitBranchComboBox.Hide()
            self.gitBranchTextCtrl.Hide()
            self.gitBranchFilterLbl.Hide()
            self.btnFilterBranch.Hide()
            self.gitUrlLbl.Hide()
            #self.gitUrlComboBox.Hide()
            self.gitUrlTextCtrl.Hide()
            self.gitBranchFilterTextCtrl.Hide()
            self.metadataFolderLbl.Hide()
            self.metadataFolderTextCtrl.Hide()

            self.metadataTemplateLbl.Hide()
            self.metadataTemplateComboBox.Hide()

            self.metadataTypesLbl.Hide()
            self.metadataTypesListBox.Hide()

            self.selectedMetadataTypesLbl.Hide()
            self.selectedMetadataTypesTextCtrl.Hide()

            self.confirmDeployLbl.Hide()
            self.confirmDeployCheckBox.Hide()

            self.generateManifestLbl.Hide()
            self.generateManifestCheckBox.Hide()

            self.zipFileLbl.Hide()
            self.zipFileTextCtrl.Hide()
            self.btnZipFile.Hide()

        self.mainSizer.AddGrowableCol(0)
        self.mainSizer.AddGrowableRow(row - 1)
        self.mainSizer.SetEmptyCellSize((0, 0))
        self.Layout()
        self.Fit()
        self.SetSizer(self.mainSizer)
        self.LoadAccelerateSettings() #Accelerate Integration

    #Accelerate Integration
    def LoadAccelerateSettings(self):
        self.gitUrlTextCtrl.SetValue(dtkglobal.accelerateGitURL)
        self.gitBranchTextCtrl.SetValue(dtkglobal.accelerateGitBranch)
        self.metadataGitFolderTextCtrl.SetValue(dtkglobal.accelerateMetadataGitFolder)
        self.preScriptFolderTextCtrl.SetValue(dtkglobal.acceleratePreDeployScriptFile)
        self.scriptFolderTextCtrl.SetValue(dtkglobal.acceleratePostDeployScriptFile)
        index = 0
        for module in dtkglobal.accelerateModulesAvailable:
            numCol = 0
            for settingModule in module:
                if (settingModule == "ModuleName"):
                    self.moduleWidget.InsertItem(index, module[settingModule])
                else:
                    self.moduleWidget.SetItem(index, numCol, module[settingModule])
                numCol += 1
            
            if index % 2:
                self.moduleWidget.SetItemBackgroundColour(index, wx.Colour(242,238,238,0))

            index += 1
        index += 1
    #Accelerate Integration
    def CheckAll(self, event):
        for row in range(self.moduleWidget.GetItemCount()):
            self.moduleWidget.CheckItem(row,True)
        self.consoleOutputTextCtrl.AppendText("All modules have been checked.")
        self.consoleOutputTextCtrl.AppendText(os.linesep)

    def UnCheckAll(self, event):
        for row in range(self.moduleWidget.GetItemCount()):
            self.moduleWidget.CheckItem(row,False)
        self.consoleOutputTextCtrl.AppendText("All modules have been unchecked.")
        self.consoleOutputTextCtrl.AppendText(os.linesep)

    def OnListItemChecked (self,event):
        dependentModules = self.moduleWidget.GetItemText(event.Index,col=DEPENDENCIES_COL)
        if (dependentModules != ""):
            ltsModules = dependentModules.split(";")
            for Module in ltsModules:
                for row in range(self.moduleWidget.GetItemCount()):
                    if (self.moduleWidget.GetItemText(row,col=MODULE_KEY_COL) == Module and not self.moduleWidget.IsItemChecked(self.moduleWidget.GetItem(row).GetId())):
                        self.moduleWidget.CheckItem(row,True)
                        self.consoleOutputTextCtrl.AppendText("Dependent module has been included ("+self.moduleWidget.GetItemText(row,col=MODULE_NAME_COL)+").")
                        self.consoleOutputTextCtrl.AppendText(os.linesep)

    def GetModulesChecked(self):
        selection = ""
        for row in range(self.moduleWidget.GetItemCount()):
            if (self.moduleWidget.IsItemChecked(self.moduleWidget.GetItem(row).GetId())):
                selection = selection + self.moduleWidget.GetItemText(row,col=MODULE_KEY_COL) + ","
        if (selection != ""):
            selection = selection[:-1]
        return selection
    
    def StopButton(self, event):
        self.stop = True
        self.SetButtonState(True)

    def SetButtonState(self, state):
        if state:
            self.btnDeploy.Enable()
            self.btnRefreshLog.Enable()
        else:
            self.btnDeploy.Disable()
            self.btnRefreshLog.Disable()

    def ChangeDeploymentType(self, event):
        self.deployTypeSelected = self.deploymentTypeComboBox.GetValue()
        if self.deployTypeSelected == "Git":
            self.gitBranchLbl.Show()
            #Accelerate Integration self.gitBranchComboBox.Show()
            self.gitBranchTextCtrl.Show()
            #Accelerate Integration self.gitBranchFilterLbl.Show()
            #Accelerate Integration self.btnFilterBranch.Show()
            self.gitUrlLbl.Show()
            #Accelerate Integration self.gitUrlComboBox.Show()
            self.gitUrlTextCtrl.Show()
            #Accelerate Integration self.gitBranchFilterTextCtrl.Show()
            self.metadataGitFolderLbl.Show()
            self.metadataGitFolderTextCtrl.Show()

            #Accelerate Integration
            self.btnPreScriptFolder.Hide()
            self.btnScriptFolder.Hide()
            self.preScriptFolderTextCtrl.SetValue(dtkglobal.acceleratePreDeployScriptFile)
            self.scriptFolderTextCtrl.SetValue(dtkglobal.acceleratePostDeployScriptFile)

            self.generateManifestCheckBox.Value = True
            self.generateManifestLbl.Hide()
            self.generateManifestCheckBox.Hide()
            """self.generateManifestLbl.Show()
            self.generateManifestCheckBox.Show()
            self.confirmDeployLbl.Show()
            self.confirmDeployCheckBox.Show()

            self.metadataTemplateLbl.Show()
            self.metadataTemplateComboBox.Show()
            self.metadataTypesLbl.Show()
            self.metadataTypesListBox.Show()

            self.selectedMetadataTypesLbl.Show()
            self.selectedMetadataTypesTextCtrl.Show()"""
            
            self.zipFileLbl.Hide()
            self.zipFileTextCtrl.Hide()
            self.btnZipFile.Hide()

            self.metadataFolderLbl.Hide()
            self.metadataFolderTextCtrl.Hide()
            self.btnMetadataFolder.Hide()
            self.Layout()

        if self.deployTypeSelected == "Zip":
            #Accelerate Integration
            self.btnPreScriptFolder.Show()
            self.btnScriptFolder.Show()
            self.preScriptFolderTextCtrl.Clear()
            self.scriptFolderTextCtrl.Clear()

            self.zipFileLbl.Show()
            self.zipFileTextCtrl.Show()
            self.btnZipFile.Show()

            self.gitBranchLbl.Hide()
            #Accelerate Integration self.gitBranchComboBox.Hide()
            self.gitBranchTextCtrl.Hide() #Accelerate Integration
            self.gitBranchFilterLbl.Hide()
            self.btnFilterBranch.Hide()
            self.gitUrlLbl.Hide()
            #Accelerate Integration self.gitUrlComboBox.Hide()
            self.gitUrlTextCtrl.Hide()
            self.gitBranchFilterTextCtrl.Hide()
            self.metadataGitFolderLbl.Hide()
            self.metadataGitFolderTextCtrl.Hide()

            self.generateManifestLbl.Hide()
            self.generateManifestCheckBox.Hide()
            self.confirmDeployLbl.Hide()
            self.confirmDeployCheckBox.Hide()

            self.metadataTemplateLbl.Hide()
            self.metadataTemplateComboBox.Hide()
            self.metadataTypesLbl.Hide()
            self.metadataTypesListBox.Hide()

            self.selectedMetadataTypesLbl.Hide()
            self.selectedMetadataTypesTextCtrl.Hide()

            self.metadataFolderLbl.Hide()
            self.metadataFolderTextCtrl.Hide()
            self.btnMetadataFolder.Hide()
            self.Layout()

        if self.deployTypeSelected == "Folder":
            #Accelerate Integration
            self.btnPreScriptFolder.Show()
            self.btnScriptFolder.Show()

            self.metadataFolderLbl.Show()
            self.metadataFolderTextCtrl.Show()
            self.btnMetadataFolder.Show()

            #Accelerate Integration
            self.preScriptFolderTextCtrl.Clear()
            self.scriptFolderTextCtrl.Clear()
            self.generateManifestLbl.Show()
            self.generateManifestCheckBox.Show()
            """self.generateManifestLbl.Show()
            self.generateManifestCheckBox.Show()
            self.confirmDeployLbl.Show()
            self.confirmDeployCheckBox.Show()

            self.metadataTemplateLbl.Show()
            self.metadataTemplateComboBox.Show()
            self.metadataTypesLbl.Show()
            self.metadataTypesListBox.Show()"""

            self.gitBranchLbl.Hide()
            #Accelerate Integration self.gitBranchComboBox.Hide()
            self.gitBranchTextCtrl.Hide()
            self.gitBranchFilterLbl.Hide()
            self.btnFilterBranch.Hide()
            self.gitUrlLbl.Hide()
            #Accelerate Integration self.gitUrlComboBox.Hide()
            self.gitUrlTextCtrl.Hide()
            self.gitBranchFilterTextCtrl.Hide()
            self.metadataGitFolderLbl.Hide()
            self.metadataGitFolderTextCtrl.Hide()

            #Accelerate Integration self.selectedMetadataTypesLbl.Show()
            #Accelerate Integration self.selectedMetadataTypesTextCtrl.Show()

            self.zipFileLbl.Hide()
            self.zipFileTextCtrl.Hide()
            self.btnZipFile.Hide()
            self.Layout()

    def DeployButton(self, event):
        if len(self.Parent.Parent.Parent.Parent.currentWorkspace) == 0:
            dlg = wx.MessageDialog(self, "Workspace not set yet.", "DTK - Deploy", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.stop = False

        #Accelerate Integration: Deploy Settings
        moduleList = self.GetModulesChecked()
        organizationGitURL = self.organizationGitUrlTextCtrl.GetValue()
        activationModuleScriptUrl = os.path.join(os.path.join(os.path.expanduser("~"), ".dtkconfig"), "AccelerateDeployConfiguration")
        gitUrl = self.organizationGitUrlTextCtrl.GetLineText(0)
        pushToGit = self.pushToGitCheckBox.GetValue()
        metadataTypes = dtkglobal.metadataTypes
        #End Accelerate Integration

        deployType = self.deploymentTypeComboBox.GetValue()
        orgName = self.Parent.Parent.Parent.Parent.organizationComboBox.GetValue()
        sdbxName = self.Parent.Parent.Parent.Parent.sandboxTypeTargetComboBox.GetValue()
        targetName = self.Parent.Parent.Parent.Parent.currentTarget
        deployUrl = os.path.join(self.Parent.Parent.Parent.Parent.currentWorkspace, "deploy")
        deployMetadataUrl = os.path.join(deployUrl, "metadata")
        deployDataUrl = os.path.join(deployUrl, "data")
        deployStageUrl = os.path.join(deployUrl, "stage")
        checkOnly = self.checkOnlyCheckBox.GetValue()
        ignoreWarnings = self.ignoreWarningsCheckBox.GetValue()
        ignoreErrors = self.ignoreErrorsCheckBox.GetValue()
        confirmDeploy = self.confirmDeployCheckBox.GetValue()
        generateManifest = self.generateManifestCheckBox.GetValue()
        testLevel = self.testLevelsComboBox.GetValue()
        specifiedTests = self.specifiedTestTextCtrl.GetLineText(0)
        #Accelerate Integration:  gitUrl = self.gitUrlComboBox.GetValue() 
        #Accelerate Integration:  gitBranch = self.gitBranchComboBox.GetValue()
        gitBranch = self.gitBranchTextCtrl.GetLineText(0)
        metadataGitFolder = self.metadataGitFolderTextCtrl.GetLineText(0)
        preScriptFile = self.preScriptFolderTextCtrl.GetLineText(0)
        scriptFile = self.scriptFolderTextCtrl.GetLineText(0)
        zipFileUrlSource = self.zipFileTextCtrl.GetLineText(0)
        zipFileUrlWorkspace = ""
        preScriptFileSource = self.preScriptFolderTextCtrl.GetLineText(0)
        scriptFileSource = self.scriptFolderTextCtrl.GetLineText(0)
        preScriptFileWorkspace = os.path.join(deployStageUrl, preScriptFileSource)
        scriptFileWorkspace = os.path.join(deployStageUrl, scriptFileSource)
        if len(preScriptFileSource) == 0:
            preScriptFileWorkspace = deployStageUrl
        if len(scriptFileSource) == 0:
            scriptFileWorkspace = deployStageUrl
        metadataFolderSource = self.metadataFolderTextCtrl.GetLineText(0)
        #Accelerate Integration:  metadataTypes = self.metadataTypesListBox.GetSelections()
        waitParam = self.waitParamNumCtrl.GetLineText(0)
        fromScript = False

        #Accelerate Integration: Preparing ORG Git URL
        gitPreffix = ''
        gitSuffix = ''
        gitUser = ''
        gitPass = ''
        gitFinalUrl = ''
        gitUrlSplit = gitUrl.split("//")
        if len(gitUrlSplit) > 1:
            gitPreffix = gitUrlSplit[0] + "//"
            gitSuffix = gitUrlSplit[1]
            gitUser = dtkglobal.orgDict[orgName]["gituser"]
            gitPass = dtkglobal.Decode(gitUser, dtkglobal.orgDict[orgName]["gitpass"])
            gitFinalUrl = gitPreffix + gitUser + ":" + gitPass + "@" + gitSuffix

        if len(orgName) == 0:
            dlg = wx.MessageDialog(self, "Please select an organization.", "DTK - Deploy", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(targetName) == 0:
            dlg = wx.MessageDialog(self, "Please select a target.", "DTK - Deploy", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if not os.path.exists(deployUrl):
            os.makedirs(deployUrl)
        if os.path.exists(deployMetadataUrl):
            shutil.rmtree(deployMetadataUrl, onerror=dtkglobal.RemoveReadonly)
        if not os.path.exists(deployMetadataUrl):
            os.makedirs(deployMetadataUrl)
        if os.path.exists(deployDataUrl):
            shutil.rmtree(deployDataUrl, onerror=dtkglobal.RemoveReadonly)
        if not os.path.exists(deployDataUrl):
            os.makedirs(deployDataUrl)
        if os.path.exists(deployStageUrl):
            shutil.rmtree(deployStageUrl, onerror=dtkglobal.RemoveReadonly)
        if not os.path.exists(deployStageUrl):
            os.makedirs(deployStageUrl)

        if deployType == "Zip":
            if not os.path.exists(zipFileUrlSource):
                dlg = wx.MessageDialog(self, "Zip file not found.", "DTK - Deploy", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
            if self.clearLogsCheckBox.GetValue():
                self.consoleOutputTextCtrl.Clear()
                self.consoleOutputTextCtrl.AppendText("Workspace: " + self.Parent.Parent.Parent.Parent.currentWorkspace)
                self.consoleOutputTextCtrl.AppendText(os.linesep)
                self.logList.clear()
            self.consoleOutputTextCtrl.AppendText("Start deployment...")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            self.SetButtonState(False)
            thread = threading.Thread(
                target=self.DeployZip,
                args=(
                    deployType,
                    orgName,
                    sdbxName,
                    targetName,
                    deployUrl,
                    deployMetadataUrl,
                    deployDataUrl,
                    deployStageUrl,
                    checkOnly,
                    ignoreWarnings,
                    ignoreErrors,
                    confirmDeploy,
                    generateManifest,
                    testLevel,
                    specifiedTests,
                    gitUrl,
                    gitBranch,
                    metadataGitFolder,
                    metadataFolderSource,
                    preScriptFile,
                    scriptFile,
                    zipFileUrlSource,
                    zipFileUrlWorkspace,
                    preScriptFileWorkspace,
                    scriptFileWorkspace,
                    metadataTypes,
                    fromScript,
                    waitParam,
                    moduleList,
                    organizationGitURL,
                    activationModuleScriptUrl,
                    pushToGit,
                    gitFinalUrl
                ),
            )
            thread.setDaemon(True)
            thread.start()
        if deployType == "Git":
            if len(metadataTypes) == 0:
                dlg = wx.MessageDialog(
                    self,
                    "No metadata types selected. Are you sure you want to continue with the deployment?",
                    "DTK - Deploy",
                    wx.YES_NO | wx.ICON_WARNING,
                )
                result = dlg.ShowModal()
                if result == wx.ID_NO:
                    dlg.Destroy()
                    return
            if (len(gitUrl) == 0 and pushToGit):
                dlg = wx.MessageDialog(self, "No target git repository selected to push the changes.", "DTK - Deploy", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return

            if len(gitBranch) == 0:
                dlg = wx.MessageDialog(self, "No git branch selected.", "DTK - Deploy", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
            if self.clearLogsCheckBox.GetValue():
                self.consoleOutputTextCtrl.Clear()
                self.consoleOutputTextCtrl.AppendText("Workspace: " + self.Parent.Parent.Parent.Parent.currentWorkspace)
                self.consoleOutputTextCtrl.AppendText(os.linesep)
                self.logList.clear()

            self.consoleOutputTextCtrl.AppendText("Start deployment...")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            self.SetButtonState(False)
            thread = threading.Thread(
                target=self.RetrieveGitBranch,
                args=(
                    deployType,
                    orgName,
                    sdbxName,
                    targetName,
                    deployUrl,
                    deployMetadataUrl,
                    deployDataUrl,
                    deployStageUrl,
                    checkOnly,
                    ignoreWarnings,
                    ignoreErrors,
                    confirmDeploy,
                    generateManifest,
                    testLevel,
                    specifiedTests,
                    gitUrl,
                    gitBranch,
                    metadataGitFolder,
                    metadataFolderSource,
                    preScriptFile,
                    scriptFile,
                    zipFileUrlSource,
                    zipFileUrlWorkspace,                        
                    preScriptFileWorkspace,
                    scriptFileWorkspace,
                    metadataTypes,
                    gitUser,
                    gitPass,
                    gitFinalUrl,
                    fromScript,
                    waitParam,
                    moduleList,
                    organizationGitURL,
                    activationModuleScriptUrl,
                    pushToGit
                ),
            )
            thread.setDaemon(True)
            thread.start()
        if deployType == "Folder":
            if len(metadataTypes) == 0:
                dlg = wx.MessageDialog(self, "No metadata types selected.", "DTK - Deploy", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return
            if self.clearLogsCheckBox.GetValue():
                self.consoleOutputTextCtrl.Clear()
                self.consoleOutputTextCtrl.AppendText("Workspace: " + self.Parent.Parent.Parent.Parent.currentWorkspace)
                self.consoleOutputTextCtrl.AppendText(os.linesep)
                self.logList.clear()

            self.consoleOutputTextCtrl.AppendText("Start deployment...")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            self.SetButtonState(False)
            thread = threading.Thread(
                target=self.DeployFolder,
                args=(
                    deployType,
                    orgName,
                    sdbxName,
                    targetName,
                    deployUrl,
                    deployMetadataUrl,
                    deployDataUrl,
                    deployStageUrl,
                    checkOnly,
                    ignoreWarnings,
                    ignoreErrors,
                    confirmDeploy,
                    generateManifest,
                    testLevel,
                    specifiedTests,
                    gitUrl,
                    gitBranch,
                    metadataGitFolder,
                    metadataFolderSource,
                    preScriptFile,
                    scriptFile,
                    zipFileUrlSource,
                    zipFileUrlWorkspace,
                    preScriptFileWorkspace,
                    scriptFileWorkspace,
                    metadataTypes,
                    fromScript,
                    waitParam,
                    moduleList,
                    organizationGitURL,
                    activationModuleScriptUrl,
                    pushToGit,
                    gitFinalUrl
                ),
            )
            thread.setDaemon(True)
            thread.start()

    def DeployFolder(
        self,
        deployType,
        orgName,
        sdbxName,
        targetName,
        deployUrl,
        deployMetadataUrl,
        deployDataUrl,
        deployStageUrl,
        checkOnly,
        ignoreWarnings,
        ignoreErrors,
        confirmDeploy,
        generateManifest,
        testLevel,
        specifiedTests,
        gitUrl,
        gitBranch,
        metadataGitFolder,
        metadataFolderSource,
        preScriptFile,
        scriptFile,
        zipFileUrlSource,
        zipFileUrlWorkspace,
        preScriptFileWorkspace,
        scriptFileWorkspace,
        metadataTypes,
        fromScript,
        waitParam,
        moduleList,
        organizationGitURL,
        activationModuleScriptUrl,
        pushToGit,
        gitFinalUrl
    ):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        # if os.path.exists(deployStageUrl):
        #     shutil.rmtree(deployStageUrl, onerror=dtkglobal.RemoveReadonly)
        if not os.path.exists(deployStageUrl):
           os.makedirs(deployStageUrl)
        # if os.path.exists(deployMetadataUrl):
        #     shutil.rmtree(deployMetadataUrl, onerror=dtkglobal.RemoveReadonly)
        if not os.path.exists(deployMetadataUrl):
            os.makedirs(deployMetadataUrl)
        dtkglobal.CopyDir(metadataFolderSource, deployStageUrl)
        if generateManifest:
            self.consoleOutputTextCtrl.AppendText("Generating manifest file...")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            thread = threading.Thread(
                target=self.GenerateManifestFirst,
                args=(
                    deployType,
                    orgName,
                    sdbxName,
                    targetName,
                    deployUrl,
                    deployMetadataUrl,
                    deployDataUrl,
                    deployStageUrl,
                    checkOnly,
                    ignoreWarnings,
                    ignoreErrors,
                    confirmDeploy,
                    generateManifest,
                    testLevel,
                    specifiedTests,
                    gitUrl,
                    gitBranch,
                    metadataGitFolder,
                    metadataFolderSource,
                    preScriptFile,
                    scriptFile,
                    zipFileUrlSource,
                    zipFileUrlWorkspace,
                    preScriptFileWorkspace,
                    scriptFileWorkspace,
                    metadataTypes,
                    fromScript,
                    waitParam,
                    moduleList,
                    organizationGitURL,
                    activationModuleScriptUrl,
                    pushToGit,
                    gitFinalUrl
                ),
            )
            thread.setDaemon(True)
            thread.start()
        else:
            dtkglobal.CopyDir(deployStageUrl, deployMetadataUrl)
            if confirmDeploy:
                self.NewThreadRunDeploy(
                    deployType,
                    orgName,
                    sdbxName,
                    targetName,
                    deployUrl,
                    deployMetadataUrl,
                    deployStageUrl,
                    deployDataUrl,
                    checkOnly,
                    ignoreWarnings,
                    ignoreErrors,
                    confirmDeploy,
                    generateManifest,
                    testLevel,
                    specifiedTests,
                    gitUrl,
                    gitBranch,
                    metadataGitFolder,
                    metadataFolderSource,
                    preScriptFile,
                    scriptFile,
                    zipFileUrlWorkspace,
                    preScriptFileWorkspace,
                    scriptFileWorkspace,
                    metadataTypes,
                    fromScript,
                    waitParam,
                    moduleList,
                    organizationGitURL,
                    activationModuleScriptUrl,
                    pushToGit,
                    gitFinalUrl
                )

    def DeployZip(
        self,
        deployType,
        orgName,
        sdbxName,
        targetName,
        deployUrl,
        deployMetadataUrl,
        deployDataUrl,
        deployStageUrl,
        checkOnly,
        ignoreWarnings,
        ignoreErrors,
        confirmDeploy,
        generateManifest,
        testLevel,
        specifiedTests,
        gitUrl,
        gitBranch,
        metadataGitFolder,
        metadataFolderSource,        
        preScriptFile,
        scriptFile,
        zipFileUrlSource,
        zipFileUrlWorkspace,
        preScriptFileWorkspace,
        scriptFileWorkspace,
        metadataTypes,
        fromScript,
        waitParam,
        moduleList,
        organizationGitURL,
        activationModuleScriptUrl,
        pushToGit,
        gitFinalUrl
    ):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        # if os.path.exists(deployMetadataUrl):
        #     shutil.rmtree(deployMetadataUrl, onerror=dtkglobal.RemoveReadonly)
        if not os.path.exists(deployMetadataUrl):
            os.makedirs(deployMetadataUrl)
        shutil.copy(zipFileUrlSource, deployMetadataUrl)
        zipFileUrlWorkspace = os.path.join(deployMetadataUrl, dtkglobal.PathLeaf(zipFileUrlSource))
        self.NewThreadRunDeploy(
            deployType,
            orgName,
            sdbxName,
            targetName,
            deployUrl,
            deployMetadataUrl,
            deployDataUrl,
            deployStageUrl,
            checkOnly,
            ignoreWarnings,
            ignoreErrors,
            confirmDeploy,
            generateManifest,
            testLevel,
            specifiedTests,
            gitUrl,
            gitBranch,
            metadataGitFolder,
            metadataFolderSource,
            preScriptFile,
            scriptFile,
            zipFileUrlSource,
            zipFileUrlWorkspace,
            preScriptFileWorkspace,
            scriptFileWorkspace,
            metadataTypes,
            fromScript,
            waitParam,
            moduleList,
            organizationGitURL,
            activationModuleScriptUrl,
            pushToGit,
            gitFinalUrl
        )

    def RetrieveGitBranch(
        self,
        deployType,
        orgName,
        sdbxName,
        targetName,
        deployUrl,
        deployMetadataUrl,
        deployDataUrl,
        deployStageUrl,
        checkOnly,
        ignoreWarnings,
        ignoreErrors,
        confirmDeploy,
        generateManifest,
        testLevel,
        specifiedTests,
        gitUrl,
        gitBranch,
        metadataGitFolder,
        metadataFolderSource,
        preScriptFile,
        scriptFile,
        zipFileUrlSource,
        zipFileUrlWorkspace,
        preScriptFileWorkspace,
        scriptFileWorkspace,
        metadataTypes,
        gitUser,
        gitPass,
        gitFinalUrl,
        fromScript,
        waitParam,
        moduleList,
        organizationGitURL,
        activationModuleScriptUrl,
        pushToGit
    ):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        # if os.path.exists(deployStageUrl):
        #     shutil.rmtree(deployStageUrl, onerror=dtkglobal.RemoveReadonly)
        if not os.path.exists(deployStageUrl):
            os.makedirs(deployStageUrl)
        # if os.path.exists(deployMetadataUrl):
        #     shutil.rmtree(deployMetadataUrl, onerror=dtkglobal.RemoveReadonly)
        if not os.path.exists(deployMetadataUrl):
            os.makedirs(deployMetadataUrl)
        outputFileUrl = os.path.join(self.Parent.Parent.Parent.Parent.currentWorkspace, "tmp", "git.tmp")
        #Accelerate Integration: Use Accelerate repository to get the configuration UPDATE WITH GLOBAL PARAMETER
        accelerateGitURL = dtkglobal.gitPreffix + dtkglobal.accelerateGitUser + ":" + dtkglobal.accelerateGitPassword + "@" + dtkglobal.gitSuffix
        cmd = ["git", "clone", "--single-branch", "--branch", gitBranch, accelerateGitURL, deployStageUrl]
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
        )
        for line in proc.stdout:
            wx.CallAfter(self.OnText, line)
        if generateManifest:
            thread = threading.Thread(
                target=self.GenerateManifestFirst,
                args=(
                    deployType,
                    orgName,
                    sdbxName,
                    targetName,
                    deployUrl,
                    deployMetadataUrl,
                    deployDataUrl,
                    deployStageUrl,
                    checkOnly,
                    ignoreWarnings,
                    ignoreErrors,
                    confirmDeploy,
                    generateManifest,
                    testLevel,
                    specifiedTests,
                    gitUrl,
                    gitBranch,
                    metadataGitFolder,
                    metadataFolderSource,
                    preScriptFile,
                    scriptFile,
                    zipFileUrlSource,
                    zipFileUrlWorkspace,
                    preScriptFileWorkspace,
                    scriptFileWorkspace,
                    metadataTypes,
                    fromScript,
                    waitParam,
                    moduleList,
                    organizationGitURL,
                    activationModuleScriptUrl,
                    pushToGit,
                    gitFinalUrl
                ),
            )
            thread.setDaemon(True)
            thread.start()
        else:
            shutil.copytree(deployStageUrl, deployMetadataUrl)
            if confirmDeploy:
                self.NewThreadRunDeploy(
                    deployType,
                    orgName,
                    sdbxName,
                    targetName,
                    deployUrl,
                    deployMetadataUrl,
                    deployDataUrl,
                    deployStageUrl,
                    checkOnly,
                    ignoreWarnings,
                    ignoreErrors,
                    confirmDeploy,
                    generateManifest,
                    testLevel,
                    specifiedTests,
                    gitUrl,
                    gitBranch,
                    metadataGitFolder,
                    metadataFolderSource,
                    preScriptFile,
                    scriptFile,
                    zipFileUrlSource,
                    zipFileUrlWorkspace,
                    preScriptFileWorkspace,
                    scriptFileWorkspace,
                    metadataTypes,
                    fromScript,
                    waitParam,
                    moduleList,
                    organizationGitURL,
                    activationModuleScriptUrl,
                    pushToGit,
                    gitFinalUrl
                )

    def GenerateManifestFirst(
        self,
        deployType,
        orgName,
        sdbxName,
        targetName,
        deployUrl,
        deployMetadataUrl,
        deployDataUrl,
        deployStageUrl,
        checkOnly,
        ignoreWarnings,
        ignoreErrors,
        confirmDeploy,
        generateManifest,
        testLevel,
        specifiedTests,
        gitUrl,
        gitBranch,
        metadataGitFolder,
        metadataFolderSource,
        preScriptFile,
        scriptFile,
        zipFileUrlSource,
        zipFileUrlWorkspace,
        preScriptFileWorkspace,
        scriptFileWorkspace,
        metadataTypes,
        fromScript,
        waitParam,
        moduleList,
        organizationGitURL,
        activationModuleScriptUrl,
        pushToGit,
        gitFinalUrl
    ):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        # if os.path.exists(deployMetadataUrl):
        #     shutil.rmtree(deployMetadataUrl, onerror=dtkglobal.RemoveReadonly)
        if not os.path.exists(deployMetadataUrl):
            os.makedirs(deployMetadataUrl)
        outputFileUrl = os.path.join(self.Parent.Parent.Parent.Parent.currentWorkspace, "tmp")
        if not os.path.exists(outputFileUrl):
            os.makedirs(outputFileUrl)
        outputFileUrl = os.path.join(self.Parent.Parent.Parent.Parent.currentWorkspace, "tmp", "describeMetadata.tmp")
        thread = threading.Thread(
            target=self.DescribeMetadata,
            args=(
                deployType,
                orgName,
                sdbxName,
                targetName,
                deployUrl,
                deployMetadataUrl,
                deployDataUrl,
                deployStageUrl,
                checkOnly,
                ignoreWarnings,
                ignoreErrors,
                confirmDeploy,
                generateManifest,
                testLevel,
                specifiedTests,
                gitUrl,
                gitBranch,
                metadataGitFolder,
                metadataFolderSource,
                preScriptFile,
                scriptFile,
                zipFileUrlSource,
                zipFileUrlWorkspace,
                preScriptFileWorkspace,
                scriptFileWorkspace,
                metadataTypes,
                outputFileUrl,
                fromScript,
                waitParam,
                moduleList,
                organizationGitURL,
                activationModuleScriptUrl,
                pushToGit,
                gitFinalUrl
            ),
        )
        thread.setDaemon(True)
        thread.start()

    def DescribeMetadata(
        self,
        deployType,
        orgName,
        sdbxName,
        targetName,
        deployUrl,
        deployMetadataUrl,
        deployDataUrl,
        deployStageUrl,
        checkOnly,
        ignoreWarnings,
        ignoreErrors,
        confirmDeploy,
        generateManifest,
        testLevel,
        specifiedTests,
        gitUrl,
        gitBranch,
        metadataGitFolder,
        metadataFolderSource,
        preScriptFile,
        scriptFile,
        zipFileUrlSource,
        zipFileUrlWorkspace,
        preScriptFileWorkspace,
        scriptFileWorkspace,
        metadataTypes,
        outputFileUrl,
        fromScript,
        waitParam,
        moduleList,
        organizationGitURL,
        activationModuleScriptUrl,
        pushToGit,
        gitFinalUrl
    ):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        cmd = [
            "sfdx",
            "force:mdapi:describemetadata",
            "--apiversion",
            dtkglobal.defaultApiVersion,
            "-u",
            targetName,
            "-f",
            outputFileUrl,
        ]
        if (platform.system() != "Windows"):
            cmd = ["/usr/local/bin/sfdx" + " " + "force:mdapi:describemetadata" + " " + "--apiversion" + " " + dtkglobal.defaultApiVersion + " " + "-u" + " " + targetName + " " + "-f" + " " + outputFileUrl]
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
        )
        for line in proc.stdout:
            wx.CallAfter(self.OnText, line)
        thread = threading.Thread(
            target=self.GenerateManifestSecond,
            args=(
                deployType,
                orgName,
                sdbxName,
                targetName,
                deployUrl,
                deployMetadataUrl,
                deployDataUrl,
                deployStageUrl,
                checkOnly,
                ignoreWarnings,
                ignoreErrors,
                confirmDeploy,
                generateManifest,
                testLevel,
                specifiedTests,
                gitUrl,
                gitBranch,
                metadataGitFolder,
                metadataFolderSource,
                preScriptFile,
                scriptFile,
                zipFileUrlSource,
                zipFileUrlWorkspace,
                preScriptFileWorkspace,
                scriptFileWorkspace,
                metadataTypes,
                outputFileUrl,
                fromScript,
                waitParam,
                moduleList,
                organizationGitURL,
                activationModuleScriptUrl,
                pushToGit,
                gitFinalUrl
            ),
        )
        thread.setDaemon(True)
        thread.start()

    def GenerateManifestSecond(
        self,
        deployType,
        orgName,
        sdbxName,
        targetName,
        deployUrl,
        deployMetadataUrl,
        deployDataUrl,
        deployStageUrl,
        checkOnly,
        ignoreWarnings,
        ignoreErrors,
        confirmDeploy,
        generateManifest,
        testLevel,
        specifiedTests,
        gitUrl,
        gitBranch,
        metadataGitFolder,
        metadataFolderSource,
        preScriptFile,
        scriptFile,
        zipFileUrlSource,
        zipFileUrlWorkspace,
        preScriptFileWorkspace,
        scriptFileWorkspace,
        metadataTypes,
        outputFileUrl,
        fromScript,
        waitParam,
        moduleList,
        organizationGitURL,
        activationModuleScriptUrl,
        pushToGit,
        gitFinalUrl
    ):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        fileOutput = open(outputFileUrl, "r", encoding="utf8")
        describeMetadataDict = json.loads(fileOutput.read())
        manifestFileUrl = os.path.join(deployMetadataUrl, "package.xml")
        tempStageUrl = deployStageUrl
        if deployType == "Git":
            tempStageUrl = os.path.join(deployStageUrl, metadataGitFolder)
        manifestFile = open(manifestFileUrl, "wb")
        strContent = '<?xml version="1.0" encoding="UTF-8"?>\n'
        strContent += '<Package xmlns="http://soap.sforce.com/2006/04/metadata">\n'
        metadataTypesSelected = []
        oneIncluded = False
        metadataTypesSelected = metadataTypes
        for item in describeMetadataDict["metadataObjects"]:
            if self.stop:
                self.consoleOutputTextCtrl.AppendText("Process stopped.")
                self.consoleOutputTextCtrl.AppendText(os.linesep)
                return
            if not "xmlName" in item:
                self.OnText("Metadata describe problem. Process aborted.")
                self.consoleOutputTextCtrl.AppendText(os.linesep)
                self.SetButtonState(True)
                return
            if item["xmlName"] in metadataTypesSelected:
                metadataTypePath = os.path.join(tempStageUrl, item["directoryName"])
                deployMetadataTypePath = os.path.join(deployMetadataUrl, item["directoryName"])
                if os.path.exists(metadataTypePath):
                    oneIncluded = True
                    dtkglobal.CopyDir(metadataTypePath, deployMetadataTypePath)
                    strContent += "\t<types>\n"
                    strContent += "\t\t<members>*</members>\n"
                    strContent += "\t\t<name>" + item["xmlName"] + "</name>\n"
                    strContent += "\t</types>\n"
                else:
                    self.consoleOutputTextCtrl.AppendText(
                        item["xmlName"] + ": " + metadataTypePath + " doesn't exist, skipped."
                    )
                    self.consoleOutputTextCtrl.AppendText(os.linesep)
        if not oneIncluded:
            self.OnText("No metadata selected to deploy.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            self.SetButtonState(True)
            return
        strContent += "\t<version>" + dtkglobal.defaultApiVersion + "</version>\n"
        strContent += "</Package>\n"
        bynaryContent = strContent.encode()
        manifestFile.write(bynaryContent)
        manifestFile.close()
        wx.CallAfter(self.OnText, "Manifest file generated.")
        wx.CallAfter(self.OnText, os.linesep)
        #Accelerate Integration
        if confirmDeploy:
            self.ActivateAccelerateModules(
                deployType,
                orgName,
                sdbxName,
                targetName,
                deployUrl,
                deployMetadataUrl,
                deployDataUrl,
                deployStageUrl,
                checkOnly,
                ignoreWarnings,
                ignoreErrors,
                confirmDeploy,
                generateManifest,
                testLevel,
                specifiedTests,
                gitUrl,
                gitBranch,
                metadataGitFolder,
                metadataFolderSource,
                preScriptFile,
                scriptFile,
                zipFileUrlSource,
                zipFileUrlWorkspace,
                preScriptFileWorkspace,
                scriptFileWorkspace,
                metadataTypes,
                fromScript,
                waitParam,
                moduleList,
                organizationGitURL,
                activationModuleScriptUrl,
                pushToGit,
                gitFinalUrl
            )
    #Accelerate Integration
    def ActivateAccelerateModules(
        self,
        deployType,
        orgName,
        sdbxName,
        targetName,
        deployUrl,
        deployMetadataUrl,
        deployDataUrl,
        deployStageUrl,
        checkOnly,
        ignoreWarnings,
        ignoreErrors,
        confirmDeploy,
        generateManifest,
        testLevel,
        specifiedTests,
        gitUrl,
        gitBranch,
        metadataGitFolder,
        metadataFolderSource,
        preScriptFile,
        scriptFile,
        zipFileUrlSource,
        zipFileUrlWorkspace,
        preScriptFileWorkspace,
        scriptFileWorkspace,
        metadataTypes,
        fromScript,
        waitParam,
        moduleList,
        organizationGitURL,
        activationModuleScriptUrl,
        pushToGit,
        gitFinalUrl
    ):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return

        activationModuleScriptFileUrl = os.path.join(activationModuleScriptUrl, dtkglobal.activationScriptName)

        if (os.path.exists(activationModuleScriptFileUrl) and os.path.exists(deployMetadataUrl)):
            if (moduleList!=""):
                if (platform.system() == "Windows"):
                    cmd = ["powershell", activationModuleScriptFileUrl, deployMetadataUrl, moduleList]
                    proc = subprocess.Popen(
                        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
                    )
                    try:
                        for line in proc.stdout:
                            wx.CallAfter(self.OnText, line)
                    except:
                        self.consoleOutputTextCtrl.AppendText("Executed Succesfully")
                        self.consoleOutputTextCtrl.AppendText(os.linesep)
                else:
                    #IMPLEMENT ACTIVATION SCRIPT FOR OTHER SYSTEMS.
                    self.consoleOutputTextCtrl.AppendText("Modules activation function is available only on Windows platforms for the moment.")
                    self.consoleOutputTextCtrl.AppendText(os.linesep)
                    return
            else:
                self.consoleOutputTextCtrl.AppendText("No Modules will be activated.")
                self.consoleOutputTextCtrl.AppendText(os.linesep)
        else:
            self.consoleOutputTextCtrl.AppendText("Activation Script not found or metadata folder does not exists.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)

        if confirmDeploy:
            self.NewThreadRunDeploy(
                deployType,
                orgName,
                sdbxName,
                targetName,
                deployUrl,
                deployMetadataUrl,
                deployDataUrl,
                deployStageUrl,
                checkOnly,
                ignoreWarnings,
                ignoreErrors,
                confirmDeploy,
                generateManifest,
                testLevel,
                specifiedTests,
                gitUrl,
                gitBranch,
                metadataGitFolder,
                metadataFolderSource,
                preScriptFile,
                scriptFile,
                zipFileUrlSource,
                zipFileUrlWorkspace,
                preScriptFileWorkspace,
                scriptFileWorkspace,
                metadataTypes,
                fromScript,
                waitParam,
                moduleList,
                organizationGitURL,
                activationModuleScriptUrl,
                pushToGit,
                gitFinalUrl
            )


    def NewThreadRunDeploy(
        self,
        deployType,
        orgName,
        sdbxName,
        targetName,
        deployUrl,
        deployMetadataUrl,
        deployDataUrl,
        deployStageUrl,
        checkOnly,
        ignoreWarnings,
        ignoreErrors,
        confirmDeploy,
        generateManifest,
        testLevel,
        specifiedTests,
        gitUrl,
        gitBranch,
        metadataGitFolder,
        metadataFolderSource,
        preScriptFile,
        scriptFile,
        zipFileUrlSource,
        zipFileUrlWorkspace,
        preScriptFileWorkspace,
        scriptFileWorkspace,
        metadataTypes,
        fromScript,
        waitParam,
        moduleList,
        organizationGitURL,
        activationModuleScriptUrl,
        pushToGit,
        gitFinalUrl
    ):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        thread = threading.Thread(
            target=self.RunDeploy,
            args=(
                deployType,
                orgName,
                sdbxName,
                targetName,
                deployUrl,
                deployMetadataUrl,
                deployDataUrl,
                deployStageUrl,
                checkOnly,
                ignoreWarnings,
                ignoreErrors,
                confirmDeploy,
                generateManifest,
                testLevel,
                specifiedTests,
                gitUrl,
                gitBranch,
                metadataGitFolder,
                metadataFolderSource,
                preScriptFile,                
                scriptFile,
                zipFileUrlSource,
                zipFileUrlWorkspace,
                preScriptFileWorkspace,
                scriptFileWorkspace,
                metadataTypes,
                fromScript,
                waitParam,
                moduleList,
                organizationGitURL,
                activationModuleScriptUrl,
                pushToGit,
                gitFinalUrl
            ),
        )
        thread.setDaemon(True)
        thread.start()

    def RunDeploy(
        self,
        deployType,
        orgName,
        sdbxName,
        targetName,
        deployUrl,
        deployMetadataUrl,
        deployDataUrl,
        deployStageUrl,
        checkOnly,
        ignoreWarnings,
        ignoreErrors,
        confirmDeploy,
        generateManifest,
        testLevel,
        specifiedTests,
        gitUrl,
        gitBranch,
        metadataGitFolder,
        metadataFolderSource,
        preScriptFile,
        scriptFile,
        zipFileUrlSource,
        zipFileUrlWorkspace,
        preScriptFileWorkspace,
        scriptFileWorkspace,
        metadataTypes,
        fromScript,
        waitParam,
        moduleList,
        organizationGitURL,
        activationModuleScriptUrl,
        pushToGit,
        gitFinalUrl
    ):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        if not fromScript:
            preScriptProcessed = False
            if os.path.exists(preScriptFile) and preScriptFile != deployStageUrl:
                shutil.copy(preScriptFile, deployDataUrl)
                self.ProcessScript(deployDataUrl, preScriptFile, deployStageUrl,moduleList,organizationGitURL,activationModuleScriptUrl,pushToGit,gitFinalUrl)
                preScriptProcessed = True
            if os.path.exists(preScriptFileWorkspace) and preScriptFileWorkspace != deployStageUrl:
                shutil.copy(preScriptFileWorkspace, deployDataUrl)
                self.ProcessScript(deployDataUrl, preScriptFileWorkspace, deployStageUrl,moduleList,organizationGitURL,activationModuleScriptUrl,pushToGit,gitFinalUrl)
                preScriptProcessed = True
            if not preScriptProcessed and preScriptFile != deployStageUrl and len(preScriptFile) > 0:
                wx.CallAfter(self.OnText, "Script file not found on: " + preScriptFile)
                wx.CallAfter(self.OnText, os.linesep)
            if not preScriptProcessed and preScriptFileWorkspace != deployStageUrl and len(preScriptFileWorkspace) > 0:
                wx.CallAfter(self.OnText, "Script file not found on: " + preScriptFileWorkspace)
                wx.CallAfter(self.OnText, os.linesep)
            wx.CallAfter(self.SetButtonState, True)
        cmd = [
            "sfdx",
            "force:mdapi:deploy",
            "--apiversion",
            dtkglobal.defaultApiVersion,
            "-u",
            targetName,
            "-l",
            testLevel,
            "-w",
            waitParam
        ]
        if (platform.system() != "Windows"):
            cmd = ["/usr/local/bin/sfdx" + " " + "force:mdapi:deploy" + " " + "--apiversion" + " " + dtkglobal.defaultApiVersion + " " + "-u" + " " + targetName + " " + "-l" + " " + testLevel + " " + "-w" + " " + waitParam]
        if checkOnly:
            cmd.append("-c")
        if ignoreWarnings:
            cmd.append("-g")
        if ignoreErrors:
            cmd.append("-o")
        if testLevel == "RunSpecifiedTests":
            cmd.append("-r")
            cmd.append(specifiedTests)
        if deployType == "Zip":
            cmd.append("-f")
            cmd.append(zipFileUrlWorkspace)
        if deployType == "Folder" or deployType == "Git":
            cmd.append("-d")
            cmd.append(deployMetadataUrl)
        os.environ["SFDX_USE_PROGRESS_BAR"] = "false"
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE
        )

        #Accelerate Integration
        deployError = False
        #End Accelerate Integration

        for line in proc.stdout:
            lineStr = line.decode()
            if "jobid:  " in lineStr:
                lineSplit = lineStr.split("jobid: ")
                if len(lineSplit) > 1:
                    logEntry = {}
                    logEntry["type"] = "Deploy"
                    logEntry["file"] = zipFileUrlWorkspace
                    logEntry["scriptLine"] = ""
                    jobIdStrip = lineSplit[1].strip("\r\n")
                    jobIdStrip = jobIdStrip.strip()
                    logEntry["jobid"] = jobIdStrip
                    logEntry["batchid"] = ""
                    logEntry["targetname"] = targetName
                    logEntry["pathname"] = deployMetadataUrl
                    self.logList[jobIdStrip] = logEntry
            wx.CallAfter(self.OnText, lineStr)

            #Accelerate Integration
            if "Component errors:  " in lineStr:
                lineSplit = lineStr.split("Component errors: ")
                if len(lineSplit) > 1:
                    numErrors = int(lineSplit[1].strip("\r\n"))
                    if numErrors > 0:
                        deployError = True
            #End Accelerate Integration

        if not fromScript:
            #Accelerate Integration
            if not deployError:
            #End Accelerate Integration
                scriptProcessed = False
                if os.path.exists(scriptFile) and scriptFile != deployStageUrl:
                    shutil.copy(scriptFile, deployDataUrl)
                    self.ProcessScript(deployDataUrl, scriptFile, deployStageUrl,moduleList,organizationGitURL,activationModuleScriptUrl,pushToGit,gitFinalUrl)
                    scriptProcessed = True
                if os.path.exists(scriptFileWorkspace) and scriptFileWorkspace != deployStageUrl:
                    shutil.copy(scriptFileWorkspace, deployDataUrl)
                    self.ProcessScript(deployDataUrl, scriptFileWorkspace, deployStageUrl,moduleList,organizationGitURL,activationModuleScriptUrl,pushToGit,gitFinalUrl)
                    scriptProcessed = True
                if not scriptProcessed and scriptFile != deployStageUrl and len(scriptFile) > 0:
                    wx.CallAfter(self.OnText, "Script file not found on: " + scriptFile)
                    wx.CallAfter(self.OnText, os.linesep)
                if not scriptProcessed and scriptFileWorkspace != deployStageUrl and len(scriptFileWorkspace) > 0:
                    wx.CallAfter(self.OnText, "Script file not found on: " + scriptFileWorkspace)
                    wx.CallAfter(self.OnText, os.linesep)
                wx.CallAfter(self.SetButtonState, True)
            #Accelerate Integration: Push to ORG Git
                if (pushToGit):
                    self.PushToOrgGit(deployMetadataUrl,gitFinalUrl,deployUrl)
            else:
                wx.CallAfter(self.OnText, os.linesep)
                wx.CallAfter(self.OnText, os.linesep)
                wx.CallAfter(self.OnText, "---------------------------------------------------------------------------------")
                wx.CallAfter(self.OnText, os.linesep)
                wx.CallAfter(self.OnText, "Errors during deploy phase, Post Script and Push to Org Git won't be executed")
                wx.CallAfter(self.OnText, os.linesep)
                wx.CallAfter(self.OnText, "---------------------------------------------------------------------------------")
                wx.CallAfter(self.OnText, os.linesep)
            #End Accelerate Integration
    
    #Accelerate Integration
    def PushToOrgGit(self,deployMetadataUrl,gitFinalUrl,deployUrl):

        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        #Prepare local git folder, if exists -> recreate
        pushToOrgGitURL = os.path.join(self.Parent.Parent.Parent.Parent.currentWorkspace, "deploy","pushRemoteOrg")
        if os.path.exists(pushToOrgGitURL):
           shutil.rmtree(pushToOrgGitURL, onerror=dtkglobal.RemoveReadonly) 
        os.makedirs(pushToOrgGitURL)

        #Starting the process
        wx.CallAfter(self.OnText, "Pushing Accelerate Configuration to Git Organization...")
        wx.CallAfter(self.OnText, os.linesep)

        #Clone master
        cmd = ["git", "clone", "--single-branch", "--branch", "master", gitFinalUrl, pushToOrgGitURL]
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
        )
        for line in proc.stdout:
            wx.CallAfter(self.OnText, line)

        #Create and checkout Accelerate Branch
        orgRemoteBranch = dtkglobal.accelerateVersion.replace(" ", "_")+"_"+datetime.datetime.now().strftime("%d/%m/%Y_%H_%M_%S")
        cmd = ["git", "-C", pushToOrgGitURL, "checkout", "-b", orgRemoteBranch]
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
        )
        for line in proc.stdout:
            wx.CallAfter(self.OnText, line)

        #Preparing all files to push to remote org git
        metadataFiles = os.path.join(self.Parent.Parent.Parent.Parent.currentWorkspace, "deploy","metadata")
        if os.path.exists(metadataFiles):
            shutil.copytree(metadataFiles, pushToOrgGitURL+"\\sfdc\\src")
        else:
            wx.CallAfter(self.OnText, metadataFiles + " does not exist, it won't be copied.")
            wx.CallAfter(self.OnText, os.linesep)

        customSettings = os.path.join(self.Parent.Parent.Parent.Parent.currentWorkspace, "deploy","stage","CustomSettings")
        if os.path.exists(customSettings):
            shutil.copytree(customSettings, pushToOrgGitURL+"\\CustomSettings")
        else:
            wx.CallAfter(self.OnText, customSettings + " does not exist, it won't be copied.")
            wx.CallAfter(self.OnText, os.linesep)

        data = os.path.join(self.Parent.Parent.Parent.Parent.currentWorkspace, "deploy","stage","data")
        if os.path.exists(data):
            shutil.copytree(data, pushToOrgGitURL+"\\data")
        else:
            wx.CallAfter(self.OnText, data + " does not exist, it won't be copied.")
            wx.CallAfter(self.OnText, os.linesep)

        okMapping = os.path.join(self.Parent.Parent.Parent.Parent.currentWorkspace, "deploy","stage","Mapping")
        if os.path.exists(okMapping):
            shutil.copytree(okMapping, pushToOrgGitURL+"\\Mapping")
        else:
            wx.CallAfter(self.OnText, okMapping + " does not exist, it won't be copied.")
            wx.CallAfter(self.OnText, os.linesep)

        masterData = os.path.join(self.Parent.Parent.Parent.Parent.currentWorkspace, "deploy","stage","Master Data")
        if os.path.exists(masterData):
            shutil.copytree(masterData, pushToOrgGitURL+"\\Master Data")
        else:
            wx.CallAfter(self.OnText, masterData + " does not exist, it won't be copied.")
            wx.CallAfter(self.OnText, os.linesep)

        #Stash all files
        cmd = ["git", "-C", pushToOrgGitURL, "add", "--all"]
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
        )
        for line in proc.stdout:
            wx.CallAfter(self.OnText, line)

        #Commit all changes
        cmd = ["git", "-C", pushToOrgGitURL, "commit", "-am", "Initial configuration: "+dtkglobal.accelerateVersion]
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
        )
        for line in proc.stdout:
            wx.CallAfter(self.OnText, line)

        #Push the branch
        cmd = ["git", "-C", pushToOrgGitURL, "push", "--set-upstream", "origin", orgRemoteBranch]
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
        )
        for line in proc.stdout:
            wx.CallAfter(self.OnText, line)

        wx.CallAfter(self.OnText, "Finished!!! O> bvio!!!")
        wx.CallAfter(self.OnText, os.linesep)

        #End Accelerate Integration

    def OnText(self, text):
        self.consoleOutputTextCtrl.AppendText(text)

    def RunDataCmd(self, lineSplit, lineStr, target, pathString, cmd):
        if self.stop:
            return
        wx.CallAfter(self.OnText, os.linesep)
        wx.CallAfter(self.OnText, "Processing: " + lineStr)
        wx.CallAfter(self.OnText, os.linesep)
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
        )
        WINDOWS_LINE_ENDING = b'\r\n'
        UNIX_LINE_ENDING = b'\n'
        if "SOQLQUERY" in lineSplit:
            fileOutput = open(pathString, "w", encoding="utf8")
            for line in proc.stdout:
                lnStr = line.decode()
                if "Querying Data" not in lnStr:
                    if "sfdx-cli update available from" not in lnStr:
                        fileOutput.write(lnStr)
            fileOutput.close()
            fileRead = open(pathString, "rb")
            content = fileRead.read()
            content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)
            fileRead.close()
            fileOutput = open(pathString, "wb")
            fileOutput.write(content)
            fileOutput.close()
            wx.CallAfter(self.OnText, "Exported data to " + pathString + "\n")
        else:
            for line in proc.stdout:
                lnStr = line.decode()
                if "force:data:bulk:status" in lnStr:
                    lnSplit = lnStr.split("-i ")
                    if len(lnSplit) > 1:
                        lineSplitAgain = lnSplit[1].split(" -b ")
                        if len(lineSplitAgain) > 1:
                            logEntry = {}
                            logEntry["type"] = "Bulk"
                            logEntry["file"] = ""
                            logEntry["scriptLine"] = lineStr
                            jobIdStrip = lineSplitAgain[0].strip("\r\n")
                            jobIdStrip = jobIdStrip.strip()
                            logEntry["jobid"] = jobIdStrip
                            batchIdStrip = lineSplitAgain[1].strip("\r\n")
                            batchIdStrip = batchIdStrip.strip()
                            logEntry["batchid"] = batchIdStrip
                            logEntry["targetname"] = target
                            logEntry["pathname"] = pathString
                            self.logList[jobIdStrip] = logEntry
                wx.CallAfter(self.OnText, line)
        wx.CallAfter(self.SetButtonState, True)

    def Unzip(self, pathToZipFile):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        deployUrl = os.path.join(self.Parent.Parent.Parent.Parent.currentWorkspace, "deploy")
        deployMetadataUrl = os.path.join(deployUrl, "metadata")
        zipRef = zipfile.ZipFile(pathToZipFile, "r")
        zipName = dtkglobal.PathLeaf(pathToZipFile)
        zipNameForFolder = zipName.rstrip(".zip")
        unzippedFolder = os.path.join(deployMetadataUrl, zipNameForFolder)
        self.consoleOutputTextCtrl.AppendText("Unzipping files from: " + pathToZipFile + " - To: " + unzippedFolder)
        self.consoleOutputTextCtrl.AppendText(os.linesep)
        zipRef.extractall(unzippedFolder)

    def RefreshLog(self, event):
        self.stop = False
        if len(self.logList) == 0:
            return
        self.consoleOutputTextCtrl.AppendText(os.linesep)
        self.consoleOutputTextCtrl.AppendText(
            "----------------------------------------------------------------------------------"
        )
        self.consoleOutputTextCtrl.AppendText(os.linesep)
        self.consoleOutputTextCtrl.AppendText(
            "Refresh log started at: " + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        )
        self.consoleOutputTextCtrl.AppendText(os.linesep)
        waitMinutes = "0"
        self.SetButtonState(False)
        thread = threading.Thread(target=self.RunRefreshLog, args=(waitMinutes))
        thread.setDaemon(True)
        thread.start()

    def RunRefreshLog(self, waitMinutes):
        for jobId in self.logList:
            if self.stop:
                self.consoleOutputTextCtrl.AppendText("Process stopped.")
                self.consoleOutputTextCtrl.AppendText(os.linesep)
                return
            log = self.logList[jobId]
            type, file, scriptLine, jobId, batchId, targetName, pathName = (
                log["type"],
                log["file"],
                log["scriptLine"],
                log["jobid"],
                log["batchid"],
                log["targetname"],
                log["pathname"],
            )
            if type == "Retrieve":
                cmd = [
                    "sfdx",
                    "force:mdapi:retrieve:report",
                    "--apiversion",
                    dtkglobal.defaultApiVersion,
                    "-u",
                    targetName,
                    "-i",
                    jobId,
                    "-r",
                    pathName,
                    "-w",
                    waitMinutes,
                ]
                if (platform.system() != "Windows"):
                    cmd = ["/usr/local/bin/sfdx" + " " + "force:mdapi:retrieve:report" + " " + "--apiversion" + " " + dtkglobal.defaultApiVersion + " " + "-u" + " " + targetName + " " + "-i" + " " + jobId + " " + "-r" + " " + pathName + " " + "-w" + " " + waitMinutes]
                proc = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
                )
                # zipToExtract = self.unZipRetrievedCheckBox.GetValue()
                zipToExtract = False
                zipReady = False
                zipUrl = ""
                for line in proc.stdout:
                    lineStr = line.decode()
                    wx.CallAfter(self.OnText, line)
                    if zipToExtract:
                        if "Wrote retrieve zip to " in lineStr:
                            lineSplit = lineStr.split("Wrote retrieve zip to ")
                            if len(lineSplit) > 1:
                                zipUrl = lineSplit[1]
                                zipUrl = zipUrl.strip("\r\n")
                                zipUrl = zipUrl.rstrip(".")
                                zipReady = True
                if zipToExtract and zipReady:
                    wx.CallAfter(self.Unzip, zipUrl)
            if type == "Deploy":
                cmd = [
                    "sfdx",
                    "force:mdapi:deploy:report",
                    "--apiversion",
                    dtkglobal.defaultApiVersion,
                    "-u",
                    targetName,
                    "-i",
                    jobId,
                ]
                if (platform.system() != "Windows"):
                    cmd = ["/usr/local/bin/sfdx" + " " + "force:mdapi:deploy:report" + " " + "--apiversion" + " " + dtkglobal.defaultApiVersion + " " + "-u" + " " + targetName + " " + "-i" + " " + jobId]
                proc = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
                )
                self.consoleOutputTextCtrl.AppendText(os.linesep)
                self.consoleOutputTextCtrl.AppendText("Metadata Deployment:")
                for line in proc.stdout:
                    wx.CallAfter(self.OnText, line)
            if type == "Bulk":
                cmd = [
                    "sfdx",
                    "force:data:bulk:status",
                    "--apiversion",
                    dtkglobal.defaultApiVersion,
                    "-u",
                    targetName,
                    "-i",
                    jobId,
                    "-b",
                    batchId,
                ]
                if (platform.system() != "Windows"):
                    cmd = ["/usr/local/bin/sfdx" + " " + "force:data:bulk:status" + " " + "--apiversion" + " " + dtkglobal.defaultApiVersion + " " + "-u" + " " + targetName + " " + "-i" + " " + jobId + " " + "-b" + " " + batchId]
                self.consoleOutputTextCtrl.AppendText(os.linesep)
                self.consoleOutputTextCtrl.AppendText("Script Line: " + scriptLine)
                proc = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
                )
                for line in proc.stdout:
                    wx.CallAfter(self.OnText, line)
        wx.CallAfter(self.SetButtonState, True)

    def ProcessScript(self, deployDataUrl, scriptUrl, deployStageUrl,moduleList,organizationGitURL,activationModuleScriptUrl,pushToGit,gitFinalUrl):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        # shutil.rmtree(deployDataUrl, onerror=dtkglobal.RemoveReadonly)
        if not os.path.exists(deployDataUrl):
            os.makedirs(deployDataUrl)
        orgName = self.Parent.Parent.Parent.Parent.organizationComboBox.GetValue()
        sdbxNameSource = "Config"
        #Accelerate Integration
        """if dtkglobal.advSetting:
            sdbxNameSource = self.Parent.Parent.Parent.Parent.sandboxTypeSourceTextCtrl.GetValue()"""
        #Accelerate Integration
        sdbxName = self.Parent.Parent.Parent.Parent.sandboxTypeTargetComboBox.GetValue()
        sourceName = orgName + "_" + sdbxNameSource
        if "_" in sdbxNameSource:
            sourceName = sdbxNameSource
        targetName = self.Parent.Parent.Parent.Parent.currentTarget
        scriptFile = open(scriptUrl, "r", encoding="utf8")
        scriptFull = scriptFile.read()
        if "SOURCE" in scriptFull and len(sdbxNameSource) == 0:
            dlg = wx.MessageDialog(self, "Please select a Source.", "DTK - Deploy", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if "TARGET" in scriptFull and len(sdbxName) == 0:
            dlg = wx.MessageDialog(self, "Please select a Target.", "DTK - Deploy", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        scriptFile.close()
        i = 1
        scriptFile = open(scriptUrl, "r", encoding="utf8")
        for line in scriptFile:
            if self.stop:
                self.consoleOutputTextCtrl.AppendText("Process stopped.")
                self.consoleOutputTextCtrl.AppendText(os.linesep)
                return
            lineStr = line.strip("\r\n")
            lineSplit = lineStr.split("|")
            if len(lineSplit) > 0:
                if lineSplit[0] == "CMDEXECUTE":
                    self.ProcessCommandScriptLine(
                        lineSplit, lineStr, targetName, sourceName, deployDataUrl, i, deployStageUrl
                    )
                if lineSplit[0] == "FILE":
                    self.ProcessFileScriptLine(
                        lineSplit, lineStr, targetName, sourceName, deployDataUrl, i, deployStageUrl
                    )
                if (lineSplit[0] == "SOURCE" or lineSplit[0] == "TARGET") and (lineSplit[1] != "DEPLOYZIP" and lineSplit[1] != "DEPLOYFOLDER"):
                    self.ProcessDataScriptLine(
                        lineSplit, lineStr, targetName, sourceName, deployDataUrl, i, deployStageUrl
                    )
                if (lineSplit[0] == "SOURCE" or lineSplit[0] == "TARGET") and (lineSplit[1] == "DEPLOYZIP" or lineSplit[1] == "DEPLOYFOLDER"):
                    self.ProcessMetadataScriptLine(
                        lineSplit, lineStr, targetName, sourceName, deployDataUrl, i, deployStageUrl,moduleList,organizationGitURL,activationModuleScriptUrl,pushToGit,gitFinalUrl
                    )
        i += 1
        scriptFile.close()

    def ProcessCommandScriptLine(
        self, lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl
    ):
        error, errorMsg, cmd = dtkglobal.ProcessCommandScriptLine(
            lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl
        )
        if self.stop:
            return
        if error:
            self.consoleOutputTextCtrl.AppendText(errorMsg)
            self.consoleOutputTextCtrl.AppendText(os.linesep)
        else:
            proc = subprocess.Popen(cmd, shell=True, text=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            try:
                for line in proc.stdout:
                    self.consoleOutputTextCtrl.AppendText(line)
                self.consoleOutputTextCtrl.AppendText(os.linesep)
            except:
                self.consoleOutputTextCtrl.AppendText("Error processing stdout...")
                self.consoleOutputTextCtrl.AppendText(os.linesep)

    def ProcessFileScriptLine(
        self, lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl
    ):
        error, errorMsg, returnMsg = dtkglobal.ProcessFileScriptLine(
            lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl
        )
        if self.stop:
            return
        if error:
            self.consoleOutputTextCtrl.AppendText(errorMsg)
            self.consoleOutputTextCtrl.AppendText(os.linesep)
        else:
            self.consoleOutputTextCtrl.AppendText(returnMsg)
            self.consoleOutputTextCtrl.AppendText(os.linesep)

    def ProcessDataScriptLine(
        self, lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl
    ):
        error, errorMsg, target, pathString, cmd = dtkglobal.ProcessDataScriptLine(
            lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl
        )
        if self.stop:
            return
        if error:
            self.consoleOutputTextCtrl.AppendText(errorMsg)
            self.consoleOutputTextCtrl.AppendText(os.linesep)
        else:
            self.RunDataCmd(lineSplit, lineStr, target, pathString, cmd)
    
    def ProcessMetadataScriptLine(
            self, lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl,moduleList,organizationGitURL,activationModuleScriptUrl,pushToGit,gitFinalUrl
        ):  
            deployType = None,
            orgName = None,
            sdbxName = None,
            deployUrl = None,
            deployMetadataUrl = None,
            confirmDeploy = None,
            generateManifest = None,
            ignoreErrors = None,
            ignoreWarnings = None,
            specifiedTests = None,
            gitUrl = None,
            gitBranch = None,
            metadataGitFolder = None,
            metadataFolderSource = None,
            preScriptFile = None,
            scriptFile = None,
            zipFileUrlSource = None,
            zipFileUrlWorkspace = None
            preScriptFileWorkspace = None,
            scriptFileWorkspace = None,
            metadataTypes = None,

            error, errorMsg, target, pathString, cmd = dtkglobal.ProcessMetadataScriptLine(
                lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl
            )
        
            if self.stop:
                return
            if error:
                self.consoleOutputTextCtrl.AppendText(errorMsg)
                self.consoleOutputTextCtrl.AppendText(os.linesep)
            else:
                if lineSplit[1] == "DEPLOYZIP":
                    fileTarget = lineSplit[2]
                    testLevel = lineSplit[3]
                    checkOnly = False
                    if lineSplit[4] == "YES":
                        checkOnly = True
                    ignoreWarnings = False
                    if lineSplit[5] == "YES":
                        ignoreWarnings = True
                    ignoreErrors = False
                    if lineSplit[6] == "YES":
                        ignoreErrors = True
                    waitParam = lineSplit[7]
                    deployType = "Zip"
                    zipFileUrlWorkspace = pathString
                    fromScript = True
                    self.RunDeploy(
                            deployType,
                            orgName,
                            sdbxName,
                            targetName,
                            deployUrl,
                            deployMetadataUrl,
                            deployDataUrl,
                            deployStageUrl,
                            checkOnly,
                            ignoreWarnings,
                            ignoreErrors,
                            confirmDeploy,
                            generateManifest,
                            testLevel,
                            specifiedTests,
                            gitUrl,
                            gitBranch,
                            metadataGitFolder,
                            metadataFolderSource,
                            preScriptFile,
                            scriptFile,
                            zipFileUrlSource,
                            zipFileUrlWorkspace,
                            preScriptFileWorkspace,
                            scriptFileWorkspace,
                            metadataTypes,
                            fromScript,
                            waitParam,
                            moduleList,
                            organizationGitURL,
                            activationModuleScriptUrl,
                            pushToGit,
                            gitFinalUrl
                    )

    def SelectZipFile(self, event):
        dlg = wx.FileDialog(
            self, "Select zip file", wildcard="Zip files (*.zip)|*.zip", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        )

        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        pathname = dlg.GetPath()
        self.zipFileTextCtrl.Clear()
        self.zipFileTextCtrl.AppendText(pathname)

    def SelectMetadataFolder(self, event):
        dlg = wx.DirDialog(None, "Choose metadata folder", "", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        pathname = dlg.GetPath()
        self.metadataFolderTextCtrl.Clear()
        self.metadataFolderTextCtrl.AppendText(pathname)

    def selectPreScriptFolder(self, event):
        dlg = wx.FileDialog(
            self, "Select Pre Script file", wildcard="All files (*.*)|*.*", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        )

        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        pathname = dlg.GetPath()
        self.preScriptFolderTextCtrl.Clear()
        self.preScriptFolderTextCtrl.AppendText(pathname)    
    
    def SelectScriptFolder(self, event):
        dlg = wx.FileDialog(
            self, "Select script file", wildcard="All files (*.*)|*.*", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        )

        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        pathname = dlg.GetPath()
        self.scriptFolderTextCtrl.Clear()
        self.scriptFolderTextCtrl.AppendText(pathname)

    def ChangeTestLevels(self, event):
        if self.testLevelsComboBox.GetValue() == "RunSpecifiedTests":
            self.specifiedTestsLbl.Show()
            self.specifiedTestTextCtrl.Show()
        else:
            self.specifiedTestsLbl.Hide()
            self.specifiedTestTextCtrl.Hide()
        self.Layout()

    def ShowSelectedMetadataList(self, event):
        self.selectedMetadataTypesTextCtrl.SetValue("")
        for line in self.metadataTypesListBox.Selections:
            if self.selectedMetadataTypesTextCtrl.GetValue() != "":
                self.selectedMetadataTypesTextCtrl.AppendText(", " + self.metadataTypesListBox.Items[line])
            else:
                self.selectedMetadataTypesTextCtrl.AppendText(self.metadataTypesListBox.Items[line])

    def ChangeMetadataTemplate(self, event):
        self.metadataTypesListBox.SetSelection(-1)
        self.selectedMetadataTypesTextCtrl.SetValue("")
        if self.metadataTemplateComboBox.GetValue() == "All":
            for i in self.metadataTypesListBox.GetStrings():
                self.metadataTypesListBox.SetStringSelection(i)
                if self.selectedMetadataTypesTextCtrl.GetValue() != "":
                    self.selectedMetadataTypesTextCtrl.AppendText(", " + i)
                else:
                    self.selectedMetadataTypesTextCtrl.AppendText(i)
        if self.metadataTemplateComboBox.GetValue() in dtkglobal.metadataTemplatesSelection:
            for line in dtkglobal.metadataTemplatesSelection[self.metadataTemplateComboBox.GetValue()]:
                self.metadataTypesListBox.SetStringSelection(line)
                if self.selectedMetadataTypesTextCtrl.GetValue() != "":
                    self.selectedMetadataTypesTextCtrl.AppendText(", " + line)
                else:
                    self.selectedMetadataTypesTextCtrl.AppendText(line)

    def ChangeGitUrl(self, event):
        self.stop = False
        gitUrl = self.gitUrlComboBox.GetValue()
        orgName = self.Parent.Parent.Parent.Parent.organizationComboBox.GetValue()
        branchFilter = self.gitBranchFilterTextCtrl.GetLineText(0)

        if len(gitUrl) > 0:
            if orgName in dtkglobal.orgDict:
                self.consoleOutputTextCtrl.AppendText("Fetching branches...")
                self.consoleOutputTextCtrl.AppendText(os.linesep)
                thread = threading.Thread(target=self.RetrieveBranches, args=(orgName, gitUrl, branchFilter))
                thread.setDaemon(True)
                thread.start()
        else:
            self.gitBranchComboBox.Enable(False)

    def RetrieveBranches(self, orgName, gitUrl, branchFilter):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        gitUrlSplit = gitUrl.split("//")
        if len(gitUrlSplit) > 1:
            self.gitBranchComboBox.Enable(False)
            gitPreffix = gitUrlSplit[0] + "//"
            gitSuffix = gitUrlSplit[1]
            gitUser = dtkglobal.orgDict[orgName]["gituser"]
            gitPass = dtkglobal.Decode(gitUser, dtkglobal.orgDict[orgName]["gitpass"])
            outputFileUrl = os.path.join(self.Parent.Parent.Parent.Parent.currentWorkspace, "tmp")
            if not os.path.exists(outputFileUrl):
                os.makedirs(outputFileUrl)
            outputFileUrl = os.path.join(self.Parent.Parent.Parent.Parent.currentWorkspace, "tmp", "branches.tmp")
            gitFinalUrl = gitPreffix + gitUser + ":" + gitPass + "@" + gitSuffix
            branches = []
            proc = subprocess.Popen(
                "git ls-remote --heads --refs " + gitFinalUrl + " " + branchFilter,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
            )
            # os.system('git ls-remote --heads --refs ' + gitFinalUrl + ' ' + branchFilter + ' > ' + outputFileUrl)
            # fileOutput = open(outputFileUrl, 'r', encoding='utf8')
            # for line in fileOutput:
            for line in proc.stdout:
                lineStr = line.decode()
                if self.stop:
                    self.consoleOutputTextCtrl.AppendText("Process stopped.")
                    self.consoleOutputTextCtrl.AppendText(os.linesep)
                    return
                branchesInFile = lineStr.split("refs/heads/")
                if len(branchesInFile) > 1:
                    branchName = branchesInFile[1].strip("\r\n")
                    branchName = branchName.strip()
                    branches.append(branchName)
            branches = sorted(branches, key=lambda s: s.casefold())
            wx.CallAfter(self.FillBranches, branches)

    def FillBranches(self, branches):
        self.gitBranchComboBox.Enable(True)
        self.gitBranchComboBox.Items = branches
        self.consoleOutputTextCtrl.AppendText("Fetching branches finished.")
        self.consoleOutputTextCtrl.AppendText(os.linesep)

class DeployFrame(wx.Frame):
    def __init__(self, parent=None):
        super(DeployFrame, self).__init__(parent, title="Deploy Accelerate")
        myStream = dtkglobal.getImageStream()
        myImage = wx.Image(myStream)
        myBitmap = wx.Bitmap(myImage)
        icon = wx.Icon()
        icon.CopyFromBitmap(myBitmap)
        self.SetIcon(icon)
        self.currentTarget = ""
        self.currentWorkspace = ""
        self.InitUI()

    def InitUI(self):
        self.mainSizer = wx.GridBagSizer(1, 1)

        self.panelParent = wx.Panel(self)
        self.panel = scrolled.ScrolledPanel(self.panelParent, -1, name="panel1")
        self.panel.SetAutoLayout(1)
        self.panel.SetupScrolling()
        row = 0
        col = 0
        spanV = 0
        spanH = 2

        self.organizationLbl = wx.StaticText(self.panel, label="Organization")
        self.organizationLbl.ToolTip = "List of Organizations available."
        self.organizationComboBox = wx.ComboBox(self.panel, style=wx.CB_READONLY)
        self.organizationComboBox.ToolTip = "List of Organizations available."
        self.organizationComboBox.Items = dtkglobal.orgList
        self.organizationComboBox.Bind(wx.EVT_COMBOBOX, self.OrganizationSelected)

        self.accelerateURL = hl.HyperLinkCtrl(self.panel, -1, dtkglobal.accelerateVersion, pos=(100, 100), URL=dtkglobal.confluenceURL)
        self.accelerateURL.SetBold(True)
        self.accelerateURL.SetUnderlines(False, False, True)
        self.accelerateURL.EnableRollover(True)
        self.accelerateURL.UpdateLink()
        #Accelerate Integration:         if dtkglobal.unlockSetting:
        #Accelerate Integration:         self.sandboxTypeSourceLbl = wx.StaticText(self.panel, label="Source")
        #Accelerate Integration:         self.sandboxTypeSourceLbl.ToolTip = """Sandbox Source: Add the sandbox name to be used as Source when executing data scripts.
        #Accelerate Integration:         The Organization set will be set as preffix. Ex: Organization=MyOrg | Source=MySand >> MyOrg_MySand
        #Accelerate Integration:         If the Sandbox includes any '_' the Organization set will not be preffixed. Ex: Organization=MyOrg | Source=MyOtherOrg_My_Sand >> MyOtherOrg_My_Sand"""
        #Accelerate Integration:         self.sandboxTypeSourceTextCtrl = wx.TextCtrl(self.panel)
        #Accelerate Integration:         self.sandboxTypeSourceTextCtrl.ToolTip = """Sandbox Source: Add the sandbox name to be used as Source when executing data scripts.
        #Accelerate Integration:         The Organization set will be set as preffix. Ex: Organization=MyOrg | Source=MySand >> MyOrg_MySand
        #Accelerate Integration:         If the Sandbox includes any '_' the Organization set will not be preffixed. Ex: Organization=MyOrg | Source=MyOtherOrg_My_Sand >> MyOtherOrg_My_Sand"""
        #Accelerate Integration:         self.sandboxTypeSourceTextCtrl.AppendText("Config")

        self.sandboxTypeTargetLbl = wx.StaticText(self.panel, label="Target")
        self.sandboxTypeTargetLbl.ToolTip = "Sandbox Type: Config, QA, UAT or Prod."
        self.sandboxTypeTargetComboBox = wx.ComboBox(self.panel, style=wx.CB_READONLY)
        self.sandboxTypeTargetComboBox.ToolTip = "Sandbox Type: Config, QA, UAT or Prod."
        self.sandboxTypeTargetComboBox.Bind(wx.EVT_COMBOBOX, self.TargetSelected)
        self.sandboxTypeTargetComboBox.Enable(False)

        self.nb = wx.Notebook(self.panel)
        self.nb.AddPage(DeployMetadataPanel(self.nb, deployType="Git"), "Metadata")
        self.nb.AddPage(ScriptDataPanel(self.nb), "Post Master Data Script")

        self.mainSizer.Add(self.organizationLbl, pos=(row, col), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.organizationComboBox,
            pos=(row, col + 1),
            span=(0, 3),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )

        self.mainSizer.Add(
            self.accelerateURL,
            pos = (row, col + 5),
            flag = wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_TOP | wx.ALIGN_RIGHT,
            border = 5,
        )
        row += 1
        #Accelerate Integration: 
        """if dtkglobal.unlockSetting:
            self.mainSizer.Add(self.sandboxTypeSourceLbl, pos=(row, col), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5)
            self.mainSizer.Add(
                self.sandboxTypeSourceTextCtrl,
                pos=(row, col + 1),
                span=(0, 3),
                flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
                border=5,
            )
            row += 1"""
        #End Accelerate Integration

        self.mainSizer.Add(self.sandboxTypeTargetLbl, pos=(row, col), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.sandboxTypeTargetComboBox,
            pos=(row, col + 1),
            span=(0, 3),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        self.mainSizer.Add(self.nb, pos=(row, col), span=(0, 6), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)

        self.mainSizer.AddGrowableRow(row)
        self.mainSizer.AddGrowableCol(2)
        self.panel.SetSizerAndFit(self.mainSizer)
        self.mainSizer.SetEmptyCellSize((0, 0))
        self.mainSizer.Fit(self)

        self.panelSizer = wx.BoxSizer(wx.VERTICAL)
        self.panelSizer.Add(self.panel, 1, wx.EXPAND)
        self.panelParent.SetSizer(self.panelSizer)
        
        self.Layout()
        self.Fit()

        self.Centre()
        self.MinSize = self.Size
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Show()

    def OrganizationSelected(self, event):
        orgName = self.organizationComboBox.GetValue()
        """self.nb.GetPage(0).gitUrlComboBox.Clear()
        self.nb.GetPage(0).metadataGitFolderTextCtrl.Clear()        
        self.nb.GetPage(0).preScriptFolderTextCtrl.Clear()
        self.nb.GetPage(0).scriptFolderTextCtrl.Clear()"""
        self.sandboxTypeTargetComboBox.Enable(False)
        if len(orgName) == 0:
            self.sandboxTypeTargetComboBox.Clear()
        if orgName in dtkglobal.orgDict:
            sandboxList = dtkglobal.orgDict[orgName]["sandboxes"]
            sandboxList.sort()
            self.sandboxTypeTargetComboBox.Items = sandboxList
            #Accelerate Integration
            """if dtkglobal.unlockSetting:
                self.sandboxTypeSourceTextCtrl.Clear()
                self.sandboxTypeSourceTextCtrl.AppendText("Config")"""
            #Accelerate Integration
            
            #Accelerate Integration
            self.nb.GetPage(0).organizationGitUrlTextCtrl.SetValue([dtkglobal.orgDict[orgName]["giturl"]][0])
            #self.nb.GetPage(0).organizationGitUrlLbl.SetLabel(orgName + " Git URL")self.nb.GetPage(0).organizationGitUrlLbl.SetLabel(orgName + " Git URL")

            """self.nb.GetPage(0).gitUrlComboBox.Items = gitList
            self.nb.GetPage(0).metadataGitFolderTextCtrl.AppendText(dtkglobal.orgDict[orgName]["metadatafolder"])
            if "preScript" in dtkglobal.orgDict[orgName]:
                self.nb.GetPage(0).preScriptFolderTextCtrl.AppendText(dtkglobal.orgDict[orgName]["preScript"])
            self.nb.GetPage(0).scriptFolderTextCtrl.AppendText(dtkglobal.orgDict[orgName]["script"])"""
            #Accelerate Integration
            self.Title = "Deploy Accelerate: " + orgName
            self.sandboxTypeTargetComboBox.Enable(True)

    def TargetSelected(self, event):
        orgName = self.organizationComboBox.GetValue()
        sdbxName = self.sandboxTypeTargetComboBox.GetValue()
        ## Accelerate deploy always in Prod, Local test must be executed
        self.nb.GetPage(0).testLevelsComboBox.SetStringSelection("RunLocalTests")
        if len(orgName) == 0:
            dlg = wx.MessageDialog(self, "Please select an organization.", "DTK - Deploy", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if self.currentTarget == orgName + "_" + sdbxName:
            return
        else:
            if self.currentTarget in dtkglobal.targets:
                dtkglobal.targets.remove(self.currentTarget)
            if self.currentWorkspace in dtkglobal.workspaces:
                dtkglobal.workspaces.remove(self.currentWorkspace)
        self.currentTarget = orgName + "_" + sdbxName
        if self.currentTarget in dtkglobal.targets:
            i = 1
            exit = False
            if os.path.join(os.path.expanduser("~"), ".dtk", self.currentTarget) not in dtkglobal.workspaces:
                self.currentWorkspace = os.path.join(os.path.expanduser("~"), ".dtk", self.currentTarget)
                exit = True
            while not exit:
                if (
                    os.path.join(os.path.expanduser("~"), ".dtk", self.currentTarget + "_" + str(i))
                    not in dtkglobal.workspaces
                ):
                    self.currentWorkspace = os.path.join(
                        os.path.expanduser("~"), ".dtk", self.currentTarget + "_" + str(i)
                    )
                    exit = True
                else:
                    i += 1
        else:
            self.currentWorkspace = os.path.join(os.path.expanduser("~"), ".dtk", self.currentTarget)
        dtkglobal.targets.append(self.currentTarget)
        dtkglobal.workspaces.append(self.currentWorkspace)
        if not os.path.exists(self.currentWorkspace):
            os.makedirs(self.currentWorkspace)
        self.nb.GetPage(0).consoleOutputTextCtrl.AppendText("Workspace changed to: " + self.currentWorkspace)
        self.nb.GetPage(0).consoleOutputTextCtrl.AppendText(os.linesep)
        self.nb.GetPage(1).consoleOutputTextCtrl.Clear()
        self.nb.GetPage(1).consoleOutputTextCtrl.AppendText("Workspace changed to: " + self.currentWorkspace)
        self.nb.GetPage(1).consoleOutputTextCtrl.AppendText(os.linesep) 
        self.nb.GetPage(1).UploadFile()
        self.nb.GetPage(1).UploadScript()
        self.Title = "Deploy Accelerate: " + orgName + " - " + sdbxName

    def OnCloseWindow(self, event):
        if self.currentTarget in dtkglobal.targets:
            dtkglobal.targets.remove(self.currentTarget)
        if self.currentWorkspace in dtkglobal.workspaces:
            dtkglobal.workspaces.remove(self.currentWorkspace)
        self.Destroy()
