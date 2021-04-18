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
import zipfile


class RetrieveMetadataPanel(wx.Panel):
    def __init__(self, parent, retrieveType):
        super(RetrieveMetadataPanel, self).__init__(parent)
        self.logList = dict()
        self.stop = False
        self.InitUI(retrieveType)

    def InitUI(self, retrieveType):
        self.mainSizer = wx.GridBagSizer(1, 1)
        self.retrieveTypeSelected = retrieveType

        self.retrieveTypeLbl = wx.StaticText(self, label="Retrieve Type")
        self.retrieveTypeLbl.ToolTip = "Retrieve Type: Manifest File, Metadata Retrieve."
        self.retrieveTypeComboBox = wx.ComboBox(self, style=wx.CB_READONLY)
        self.retrieveTypeComboBox.ToolTip = "Retrieve Type: Manifest File, Metadata Retrieve."
        self.retrieveTypeComboBox.Items = dtkglobal.retrieveTypes
        self.retrieveTypeComboBox.Bind(wx.EVT_COMBOBOX, self.ChangeRetrieveType)
        self.retrieveTypeComboBox.SetValue(self.retrieveTypeSelected)

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

        self.excludePackagesLbl = wx.StaticText(self, label="Exclude Packages")
        self.excludePackagesLbl.ToolTip = "Exclude the following list of packages. Separated by comma."
        self.excludePackagesTextCtrl = wx.TextCtrl(self)
        self.excludePackagesTextCtrl.ToolTip = "Exclude the following list of packages. Separated by comma."
        self.excludePackagesTextCtrl.WriteText(dtkglobal.defaultPackagesToExclude)

        self.includeManagePackagesLbl = wx.StaticText(self, label="Include Managed Packages")
        self.includeManagePackagesLbl.ToolTip = "Include mananaged packages."
        self.includeManagePackagesCheckBox = wx.CheckBox(self)
        self.includeManagePackagesCheckBox.ToolTip = "Include mananaged packages."
        self.includeManagePackagesCheckBox.SetValue(True)

        self.unZipRetrievedLbl = wx.StaticText(self, label="Unzip Retrieved")
        self.unZipRetrievedLbl.ToolTip = "Unzip the retrieved file."
        self.unZipRetrievedCheckBox = wx.CheckBox(self)
        self.unZipRetrievedCheckBox.ToolTip = "Unzip the retrieved file."
        self.unZipRetrievedCheckBox.SetValue(dtkglobal.unzipSetting)

        self.clearLogsLbl = wx.StaticText(self, label="Clear Logs")
        self.clearLogsLbl.ToolTip = "Clear log output and asynchronous jobs."
        self.clearLogsCheckBox = wx.CheckBox(self)
        self.clearLogsCheckBox.ToolTip = "Clear log output and asynchronous jobs."
        self.clearLogsCheckBox.SetValue(True)

        self.selectedMetadataTypesLbl = wx.StaticText(self, label="Selected Metadata Types")
        self.selectedMetadataTypesLbl.ToolTip = "Selected Metadata Types."
        self.selectedMetadataTypesTextCtrl = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_AUTO_URL | wx.VSCROLL | wx.TE_WORDWRAP
        )
        self.selectedMetadataTypesTextCtrl.ToolTip = "Selected Metadata Types."

        self.manifestFileLbl = wx.StaticText(self, label="Manifest File")
        self.manifestFileLbl.ToolTip = "Provide a manifest file to retrieve the metadata from the source selected."
        self.manifestFileTextCtrl = wx.TextCtrl(self)
        self.manifestFileTextCtrl.ToolTip = "Provide a manifest file to retrieve the metadata from the source selected."

        self.btnUploadManifestFile = wx.Button(self, label="Browse")
        self.btnUploadManifestFile.Bind(wx.EVT_BUTTON, self.UploadManifestFile)

        self.btnRetrieve = wx.Button(self, label="Retrieve")
        self.btnRetrieve.Bind(wx.EVT_BUTTON, self.RetrieveButton)

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

        self.waitParamLbl = wx.StaticText(self, label="Wait time")
        self.waitParamLbl.ToolTip = "Wait time for SFDX Deploy (minutes)."
        self.waitParamNumCtrl = wx.TextCtrl(self, size = (-1,-1),style = wx.TE_RIGHT)
        self.waitParamNumCtrl.ToolTip = "Wait time for SFDX Deploy. DTK will wait for the input minutes. If the deploy finishes before, then DTK wil stop waiting. For Unlimited waiting use '-1'"
        self.waitParamNumCtrl.SetValue('-1')

        row = 0
        col = 0

        self.waitTimeSizer = wx.GridBagSizer(1, 1)
        self.waitTimeSizer.Add(self.waitParamLbl, pos=(0, 0))
        self.waitTimeSizer.Add(
        self.waitParamNumCtrl, pos=(0, 2))

        self.retrieveTypeSizer = wx.GridBagSizer(1, 1)

        self.retrieveTypeSizer.Add(
            self.retrieveTypeLbl, pos=(0, 0), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5
        )
        self.retrieveTypeSizer.Add(
            self.retrieveTypeComboBox,
            pos=(0, 1),
            span=(0, 5),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )

        self.retrieveTypeSizer.AddGrowableCol(1)
        self.retrieveTypeSizer.SetEmptyCellSize((0, 0))

        self.firstSizer = wx.GridBagSizer(1, 1)

        self.leftSizer = wx.GridBagSizer(1, 1)
        self.leftSizer.Add(self.metadataTemplateLbl, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)
        self.leftSizer.Add(
            self.metadataTemplateComboBox,
            pos=(0, 1),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )
        self.leftSizer.Add(self.metadataTypesLbl, pos=(1, 0), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.leftSizer.Add(
            self.metadataTypesListBox, pos=(1, 1), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )

        self.leftSizer.AddGrowableCol(1)
        self.leftSizer.AddGrowableRow(1)

        self.leftSizer.SetEmptyCellSize((0, 0))

        self.firstSizer.Add(
            self.leftSizer, pos=(0, 0), span=(0, 5), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=0
        )

        self.rightSizer = wx.GridBagSizer(1, 1)
        self.rightSizer.Add(self.excludePackagesLbl, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.rightSizer.Add(
            self.excludePackagesTextCtrl, pos=(0, 1), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5
        )

        self.rightSizer.Add(self.includeManagePackagesLbl, pos=(1, 0), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.rightSizer.Add(
            self.includeManagePackagesCheckBox, pos=(1, 1), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.rightSizer.Add(self.unZipRetrievedLbl, pos=(2, 0), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.rightSizer.Add(
            self.unZipRetrievedCheckBox, pos=(2, 1), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.rightSizer.Add(self.clearLogsLbl, pos=(3, 0), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.rightSizer.Add(self.clearLogsCheckBox, pos=(3, 1), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)

        self.rightSizer.Add(self.selectedMetadataTypesLbl, pos=(4, 0), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.rightSizer.Add(
            self.selectedMetadataTypesTextCtrl,
            pos=(5, 0),
            span=(1, 2),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )
        self.rightSizer.AddGrowableCol(1)
        self.rightSizer.AddGrowableRow(5)
        self.rightSizer.SetEmptyCellSize((0, 0))

        self.firstSizer.Add(self.rightSizer, pos=(0, 5), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=0)

        self.includeManagePackagesLbl.Hide()
        self.includeManagePackagesCheckBox.Hide()

        self.firstSizer.AddGrowableCol(0)
        self.firstSizer.AddGrowableCol(1)
        self.firstSizer.AddGrowableRow(0)
        self.firstSizer.SetEmptyCellSize((0, 0))

        self.manifestSizer = wx.GridBagSizer(1, 1)
        self.manifestSizer.Add(self.manifestFileLbl, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.manifestFileSizer = wx.GridBagSizer(1, 1)
        self.manifestFileSizer.Add(
            self.manifestFileTextCtrl,
            pos=(0, 0),
            span=(0, 4),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )
        self.manifestFileSizer.Add(self.btnUploadManifestFile, pos=(0, 5), flag=wx.TOP | wx.BOTTOM | wx.RIGHT, border=5)
        self.manifestFileSizer.AddGrowableCol(0)
        self.manifestFileSizer.SetEmptyCellSize((0, 0))
        self.manifestSizer.Add(
            self.manifestFileSizer, pos=(0, 1), span=(0, 5), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=0
        )
        self.manifestSizer.AddGrowableCol(1)
        self.manifestSizer.SetEmptyCellSize((0, 0))

        self.secondSizer = wx.GridBagSizer(1, 1)
        self.secondSizer.Add(self.consoleOutputLbl, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.secondSizer.Add(
            self.consoleOutputTextCtrl,
            pos=(1, 0),
            span=(5, 5),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )

        self.secondSizer.AddGrowableCol(0)
        self.secondSizer.AddGrowableRow(1)
        self.secondSizer.SetEmptyCellSize((0, 0))

        row = 0
        self.btnRetrieveSizer= wx.GridBagSizer(1,1)
        self.btnRetrieveSizer.Add(
                self.waitTimeSizer,
                pos=(row,0),
                flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT | wx.ALIGN_RIGHT,
                border=10,
        )
        self.btnRetrieveSizer.Add(self.btnRetrieve, pos=(row, 1), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT | wx.ALIGN_RIGHT, border=10)


        self.mainSizer.Add(
            self.retrieveTypeSizer,
            pos=(0, 0),
            span=(0, 5),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )
        self.mainSizer.Add(
            self.manifestSizer,
            pos=(1, 0),
            span=(0, 5),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )
        self.mainSizer.Add(
            self.firstSizer, pos=(2, 0), span=(0, 5), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5
        )
        self.mainSizer.Add(
            self.btnRetrieveSizer, pos=(3, 4), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT | wx.ALIGN_RIGHT
        )
        self.mainSizer.Add(
            self.secondSizer,
            pos=(4, 0),
            span=(10, 5),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )
        self.mainSizer.Add(self.btnStop, pos=(14, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.btnRefreshLog, pos=(14, 4), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT | wx.ALIGN_RIGHT, border=10
        )

        if self.retrieveTypeSelected == "Metadata Retrieve":
            self.manifestFileLbl.Hide()
            self.manifestFileTextCtrl.Hide()
            self.btnUploadManifestFile.Hide()

        if self.retrieveTypeSelected == "Manifest File":
            self.metadataTypesLbl.Hide()
            self.metadataTypesListBox.Hide()
            self.metadataTemplateLbl.Hide()
            self.metadataTemplateComboBox.Hide()
            self.excludePackagesLbl.Hide()
            self.excludePackagesTextCtrl.Hide()
            self.includeManagePackagesLbl.Hide()
            self.includeManagePackagesCheckBox.Hide()
            self.selectedMetadataTypesLbl.Hide()
            self.selectedMetadataTypesTextCtrl.Hide()

        self.mainSizer.AddGrowableCol(0)
        self.mainSizer.AddGrowableRow(2)
        self.mainSizer.AddGrowableRow(4)
        self.mainSizer.SetEmptyCellSize((0, 0))
        self.Layout()

        self.SetSizer(self.mainSizer)

    def ShowSelectedMetadataList(self, event):
        self.selectedMetadataTypesTextCtrl.SetValue("")
        for line in self.metadataTypesListBox.Selections:
            if self.selectedMetadataTypesTextCtrl.GetValue() != "":
                self.selectedMetadataTypesTextCtrl.AppendText(", " + self.metadataTypesListBox.Items[line])
            else:
                self.selectedMetadataTypesTextCtrl.AppendText(self.metadataTypesListBox.Items[line])

    def StopButton(self, event):
        self.stop = True
        self.SetButtonState(True)

    def SetButtonState(self, state):
        if state:
            self.btnRetrieve.Enable()
            self.btnRefreshLog.Enable()
        else:
            self.btnRetrieve.Disable()
            self.btnRefreshLog.Disable()

    def ChangeRetrieveType(self, event):
        self.retrieveTypeSelected = self.retrieveTypeComboBox.GetValue()
        if self.retrieveTypeSelected == "Metadata Retrieve":
            self.metadataTypesLbl.Show()
            self.metadataTypesListBox.Show()
            self.metadataTemplateLbl.Show()
            self.metadataTemplateComboBox.Show()
            self.excludePackagesLbl.Show()
            self.excludePackagesTextCtrl.Show()
            # self.includeManagePackagesLbl.Show()
            # self.includeManagePackagesCheckBox.Show()
            self.selectedMetadataTypesLbl.Show()
            self.selectedMetadataTypesTextCtrl.Show()

            self.manifestFileLbl.Hide()
            self.manifestFileTextCtrl.Hide()
            self.btnUploadManifestFile.Hide()

        if self.retrieveTypeSelected == "Manifest File":
            self.manifestFileLbl.Show()
            self.manifestFileTextCtrl.Show()
            self.btnUploadManifestFile.Show()

            self.metadataTypesLbl.Hide()
            self.metadataTypesListBox.Hide()
            self.metadataTemplateLbl.Hide()
            self.metadataTemplateComboBox.Hide()
            self.excludePackagesLbl.Hide()
            self.excludePackagesTextCtrl.Hide()
            self.includeManagePackagesLbl.Hide()
            self.includeManagePackagesCheckBox.Hide()
            self.selectedMetadataTypesLbl.Hide()
            self.selectedMetadataTypesTextCtrl.Hide()
        self.Layout()

    def UploadManifestFile(self, event):
        if len(self.Parent.Parent.Parent.currentWorkspace) == 0:
            dlg = wx.MessageDialog(self, "Workspace not set yet.", "DTK - Retrieve", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        retrieveUrl = os.path.join(self.Parent.Parent.Parent.currentWorkspace, "retrieve")
        retrieveMetadataUrl = os.path.join(retrieveUrl, "metadata")

        if not os.path.exists(retrieveUrl):
            os.makedirs(retrieveUrl)
        if not os.path.exists(retrieveMetadataUrl):
            os.makedirs(retrieveMetadataUrl)
        else:
            shutil.rmtree(retrieveMetadataUrl, onerror=dtkglobal.RemoveReadonly)
            os.makedirs(retrieveMetadataUrl)

        dlg = wx.FileDialog(
            self, "Select manifest file", wildcard="XML files (*.xml)|*.xml", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        )

        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        pathname = dlg.GetPath()
        self.manifestFileTextCtrl.Clear()
        self.manifestFileTextCtrl.AppendText(pathname)
        shutil.copy(pathname, retrieveMetadataUrl)
        self.consoleOutputTextCtrl.AppendText(
            "File copied into workspace metadata folder: " + dtkglobal.PathLeaf(pathname)
        )
        self.consoleOutputTextCtrl.AppendText(os.linesep)

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

    def RetrieveButton(self, event):
        self.stop = False
        if len(self.Parent.Parent.Parent.currentWorkspace) == 0:
            dlg = wx.MessageDialog(self, "Workspace not set yet.", "DTK - Retrieve", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        orgName = self.Parent.Parent.Parent.organizationComboBox.GetValue()
        sdbxName = "Config"
        if dtkglobal.unlockSetting:
            sdbxName = self.Parent.Parent.Parent.sandboxTypeSourceComboBox.GetValue()
        orgName = self.Parent.Parent.Parent.organizationComboBox.GetValue()
        if len(orgName) == 0:
            dlg = wx.MessageDialog(self, "Please select an organization.", "DTK - Retrieve", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(sdbxName) == 0:
            dlg = wx.MessageDialog(self, "Please select a source.", "DTK - Retrieve", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if self.clearLogsCheckBox.GetValue():
            self.consoleOutputTextCtrl.Clear()
            self.consoleOutputTextCtrl.AppendText("Workspace: " + self.Parent.Parent.Parent.currentWorkspace)
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            self.logList.clear()

        targetName = orgName + "_" + sdbxName
        metadataTypes = self.metadataTypesListBox.GetSelections()
        excludePackages = self.excludePackagesTextCtrl.GetValue()

        retrieveUrl = os.path.join(self.Parent.Parent.Parent.currentWorkspace, "retrieve")
        retrieveMetadataUrl = os.path.join(retrieveUrl, "metadata")
        retrieveDataUrl = os.path.join(retrieveUrl, "data")
        manifestFileUrl = self.manifestFileTextCtrl.GetValue()
        waitMinutes = self.waitParamNumCtrl.GetValue()
        self.SetButtonState(False)
        if not os.path.exists(retrieveUrl):
            os.makedirs(retrieveUrl)
        if not os.path.exists(retrieveMetadataUrl):
            os.makedirs(retrieveMetadataUrl)
        if self.retrieveTypeComboBox.GetValue() == "Metadata Retrieve":
            thread = threading.Thread(
                target=self.GenerateManifestFirst,
                args=(
                    orgName,
                    sdbxName,
                    targetName,
                    retrieveUrl,
                    retrieveMetadataUrl,
                    metadataTypes,
                    excludePackages,
                    waitMinutes,
                ),
            )
            thread.setDaemon(True)
            thread.start()
        if self.retrieveTypeComboBox.GetValue() == "Manifest File":
            thread = threading.Thread(
                target=self.RetrieveMetadataManifest,
                args=(orgName, sdbxName, targetName, retrieveUrl, retrieveMetadataUrl, manifestFileUrl, waitMinutes),
            )
            thread.setDaemon(True)
            thread.start()

    def RetrieveMetadataManifest(
        self, orgName, sdbxName, targetName, retrieveUrl, retrieveMetadataUrl, manifestFileUrl, waitMinutes
    ):
        thread = threading.Thread(
            target=self.RetrieveMetadata,
            args=(orgName, sdbxName, targetName, retrieveUrl, retrieveMetadataUrl, manifestFileUrl, waitMinutes),
        )
        thread.setDaemon(True)
        thread.start()

    def RetrieveMetadata(
        self, orgName, sdbxName, targetName, retrieveUrl, retrieveMetadataUrl, manifestFileUrl, waitMinutes
    ):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        cmd = [
            "sfdx",
            "force:mdapi:retrieve",
            "--apiversion",
            dtkglobal.defaultApiVersion,
            "-u",
            targetName,
            "-r",
            retrieveMetadataUrl,
            "-k",
            manifestFileUrl,
            "-s",
            "-w",
            waitMinutes,
        ]
        if (platform.system() != "Windows"):
            cmd = ["/usr/local/bin/sfdx" + " " + "force:mdapi:retrieve" + " " + "--apiversion" + " " + dtkglobal.defaultApiVersion + " " + "-u" + " " + targetName + " " + "-r" + " " + retrieveMetadataUrl + " " + "-k" + " " + manifestFileUrl + " " + "-s" + " " + "-w" + " " + waitMinutes]
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
        )
        jobIdStrip = ""
        zipToExtract = self.unZipRetrievedCheckBox.GetValue()
        # zipToExtract = False
        zipReady = False
        zipUrl = ""
        for line in proc.stdout:
            lineStr = line.decode()
            if "jobid:  " in lineStr:
                lineSplit = lineStr.split("jobid: ")
                if len(lineSplit) > 1:
                    logEntry = {}
                    logEntry["type"] = "Retrieve"
                    logEntry["file"] = manifestFileUrl
                    jobIdStrip = lineSplit[1].strip("\r\n")
                    jobIdStrip = jobIdStrip.strip()
                    logEntry["jobid"] = jobIdStrip
                    logEntry["batchid"] = ""
                    logEntry["targetname"] = targetName
                    logEntry["pathname"] = retrieveMetadataUrl
                    self.logList[jobIdStrip] = logEntry
            wx.CallAfter(self.OnText, lineStr)
            if waitMinutes != 0:
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
        wx.CallAfter(self.SetButtonState, True)

    def GenerateManifestFirst(
        self,
        orgName,
        sdbxName,
        targetName,
        retrieveUrl,
        retrieveMetadataUrl,
        metadataTypes,
        excludePackages,
        waitMinutes,
    ):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        if os.path.exists(retrieveMetadataUrl):
            shutil.rmtree(retrieveMetadataUrl, onerror=dtkglobal.RemoveReadonly)
        if not os.path.exists(retrieveMetadataUrl):
            os.makedirs(retrieveMetadataUrl)
        outputFileUrl = os.path.join(self.Parent.Parent.Parent.currentWorkspace, "tmp")
        if not os.path.exists(outputFileUrl):
            os.makedirs(outputFileUrl)
        outputFileUrl = os.path.join(self.Parent.Parent.Parent.currentWorkspace, "tmp", "describeMetadata.log")
        thread = threading.Thread(
            target=self.GenerateManifestSecond,
            args=(
                orgName,
                sdbxName,
                targetName,
                retrieveUrl,
                retrieveMetadataUrl,
                metadataTypes,
                excludePackages,
                waitMinutes,
                outputFileUrl,
            ),
        )
        thread.setDaemon(True)
        thread.start()

    def DescribeMetadata(
        self,
        orgName,
        sdbxName,
        targetName,
        retrieveUrl,
        retrieveMetadataUrl,
        metadataTypes,
        excludePackages,
        waitMinutes,
        outputFileUrl,
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
                orgName,
                sdbxName,
                targetName,
                retrieveUrl,
                retrieveMetadataUrl,
                metadataTypes,
                excludePackages,
                waitMinutes,
                outputFileUrl,
            ),
        )
        thread.setDaemon(True)
        thread.start()

    def GenerateManifestSecond(
        self,
        orgName,
        sdbxName,
        targetName,
        retrieveUrl,
        retrieveMetadataUrl,
        metadataTypes,
        excludePackages,
        waitMinutes,
        outputFileUrl,
    ):
        # fileOutput = open(outputFileUrl, 'r', encoding='utf8')
        # describeMetadataDict = json.loads(fileOutput.read())
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        manifestFileUrl = os.path.join(retrieveMetadataUrl, "package.xml")
        manifestFile = open(manifestFileUrl, "wb")
        strContent = '<?xml version="1.0" encoding="UTF-8"?>\n'
        strContent += '<Package xmlns="http://soap.sforce.com/2006/04/metadata">\n'
        metadataTypesSelected = []
        oneIncluded = False
        for i in metadataTypes:
            metadataTypesSelected.append(self.metadataTypesListBox.GetString(i))
        for item in metadataTypesSelected:
            if self.stop:
                self.consoleOutputTextCtrl.AppendText("Process stopped.")
                self.consoleOutputTextCtrl.AppendText(os.linesep)
                return
            typeIncluded = False
            addWildcard = False
            charMetaSeparator = ""
            needPrefixAddition = False
            specialReplace = False
            folder = ""
            simpleListMetadata = True
            if item in ["CustomMetadata", "QuickAction"]:
                charMetaSeparator = "."
                needPrefixAddition = True
            if item == "Layout":
                charMetaSeparator = "-"
                needPrefixAddition = True
                specialReplace = True
            if item == "Flow":
                addWildcard = True
            if item == "Dashboard":
                simpleListMetadata = False
                folder = "DashboardFolder"
            if item == "Document":
                simpleListMetadata = False
                folder = "DocumentFolder"
            if item == "EmailTemplate":
                simpleListMetadata = False
                folder = "EmailFolder"
            if item == "Report":
                simpleListMetadata = False
                folder = "ReportFolder"
            typeContent = "\t<types>\n"
            if simpleListMetadata:
                members = self.GetListMetadataMembers(
                    targetName,
                    retrieveUrl,
                    excludePackages,
                    item,
                    charMetaSeparator,
                    needPrefixAddition,
                    specialReplace,
                )
            else:
                members = self.GetFolderMetadataMembers(
                    targetName,
                    retrieveUrl,
                    excludePackages,
                    item,
                    charMetaSeparator,
                    needPrefixAddition,
                    specialReplace,
                    folder,
                )
            if len(members) == 0:
                continue
            members.sort()
            for member in members:
                typeIncluded = True
                typeContent += "\t\t<members>" + member + "</members>\n"
            if addWildcard:
                typeContent += "\t\t<members>*</members>\n"
            typeContent += "\t\t<name>" + item + "</name>\n"
            typeContent += "\t</types>\n"
            if typeIncluded:
                oneIncluded = True
                strContent += typeContent
        if not oneIncluded:
            self.OnText("No metadata selected to retrieve.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        strContent += "\t<version>" + dtkglobal.defaultApiVersion + "</version>\n"
        strContent += "</Package>\n"
        bynaryContent = strContent.encode()
        manifestFile.write(bynaryContent)
        manifestFile.close()
        wx.CallAfter(self.OnText, "Manifest file generated.")
        wx.CallAfter(self.OnText, os.linesep)
        thread = threading.Thread(
            target=self.RetrieveMetadata,
            args=(orgName, sdbxName, targetName, retrieveUrl, retrieveMetadataUrl, manifestFileUrl, waitMinutes),
        )
        thread.setDaemon(True)
        thread.start()

    def GetListMetadataMembers(
        self,
        targetName,
        retrieveUrl,
        excludePackages,
        metadataItem,
        charMetaSeparator,
        needPrefixAddition,
        specialReplace,
    ):
        if self.stop:
            return []
        pathUrl = os.path.join(retrieveUrl, "tmp")
        resultMetadata = []
        if not os.path.exists(pathUrl):
            os.makedirs(pathUrl)
        outputFileUrl = os.path.join(pathUrl, metadataItem + ".tmp")
        cmd = [
            "sfdx",
            "force:mdapi:listmetadata",
            "--apiversion",
            dtkglobal.defaultApiVersion,
            "-u",
            targetName,
            "-m",
            metadataItem,
            "-f",
            outputFileUrl,
        ]
        if (platform.system() != "Windows"):
            cmd = ["/usr/local/bin/sfdx" + " " + "force:mdapi:listmetadata" + " " + "--apiversion" + " " + dtkglobal.defaultApiVersion + " " + "-u" + " " + targetName + " " + "-m" + " " + metadataItem + " " + "-f" + " " + outputFileUrl]
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
        )
        for line in proc.stdout:
            wx.CallAfter(self.OnText, line)
        if not os.path.exists(outputFileUrl):
            return []
        fileOutput = open(outputFileUrl, "r", encoding="utf8")
        metadataStr = fileOutput.read()
        if len(metadataStr) == 0 or metadataStr == "undefined":
            return []
        if not "[" in metadataStr and not "]" in metadataStr and "{" in metadataStr:
            metadataStr = "[" + metadataStr + "]"
        if metadataStr == "[]":
            return []
        metadataDict = json.loads(metadataStr)
        for metadata in metadataDict:
            if self.stop:
                return []
            nameToAdd = metadata["fullName"]
            add = False
            if len(excludePackages) == 0:
                add = True
            if len(excludePackages) > 0:
                if "namespacePrefix" in metadata:
                    if len(metadata["namespacePrefix"]) > 0:
                        if not metadata["namespacePrefix"] in excludePackages:
                            add = True
                            if needPrefixAddition:
                                if specialReplace:
                                    nameToAdd = nameToAdd.replace(
                                        charMetaSeparator, charMetaSeparator + metadata["namespacePrefix"] + "__", 1
                                    )
                                else:
                                    nameToAdd = nameToAdd.replace(
                                        charMetaSeparator, charMetaSeparator + metadata["namespacePrefix"] + "__"
                                    )
                    else:
                        add = True
                else:
                    add = True
            if add:
                resultMetadata.append(nameToAdd)
        return resultMetadata

    def GetFolderMetadataMembers(
        self,
        targetName,
        retrieveUrl,
        excludePackages,
        metadataItem,
        charMetaSeparator,
        needPrefixAddition,
        specialReplace,
        folder,
    ):
        if self.stop:
            return []
        pathUrl = os.path.join(retrieveUrl, "tmp")
        resultMetadata = []
        if not os.path.exists(pathUrl):
            os.makedirs(pathUrl)
        outputFileUrl = os.path.join(pathUrl, folder + ".tmp")
        cmd = [
            "sfdx",
            "force:mdapi:listmetadata",
            "--apiversion",
            dtkglobal.defaultApiVersion,
            "-u",
            targetName,
            "-m",
            folder,
            "-f",
            outputFileUrl,
        ]
        if (platform.system() != "Windows"):
            cmd = ["/usr/local/bin/sfdx" + " " + "force:mdapi:listmetadata" + " " + "--apiversion" + " " + dtkglobal.defaultApiVersion + " " + "-u" + " " + targetName + " " + "-m" + " " + folder + " " + "-f" + " " + outputFileUrl]
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
        )
        for line in proc.stdout:
            wx.CallAfter(self.OnText, line)
        if not os.path.exists(outputFileUrl):
            return []
        fileOutput = open(outputFileUrl, "r", encoding="utf8")
        metadataStr = fileOutput.read()
        if len(metadataStr) == 0 or metadataStr == "undefined":
            return []
        if not "[" in metadataStr and not "]" in metadataStr and "{" in metadataStr:
            metadataStr = "[" + metadataStr + "]"
        if metadataStr == "[]":
            return []
        metadataDict = json.loads(metadataStr)
        for metadata in metadataDict:
            if self.stop:
                return []
            outputFileFolderUrl = os.path.join(pathUrl, metadata["fullName"] + ".tmp")
            cmd = [
                "sfdx",
                "force:mdapi:listmetadata",
                "--apiversion",
                dtkglobal.defaultApiVersion,
                "-u",
                targetName,
                "-m",
                metadataItem,
                "--folder",
                metadata["fullName"],
                "-f",
                outputFileFolderUrl,
            ]
            if (platform.system() != "Windows"):
                cmd = ["/usr/local/bin/sfdx" + " " + "force:mdapi:listmetadata" + " " + "--apiversion" + " " + dtkglobal.defaultApiVersion + " " + "-u" + " " + targetName + " " + "-m" + " " + metadataItem + " " + "--folder" + " " + metadata["fullName"] + " " + "-f" + " " + outputFileFolderUrl]
            proc = subprocess.Popen(
                cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
            )
            for line in proc.stdout:
                wx.CallAfter(self.OnText, line)
            if not os.path.exists(outputFileFolderUrl):
                continue
            fileOutputFolder = open(outputFileFolderUrl, "r", encoding="utf8")
            metadataStr = fileOutputFolder.read()
            if len(metadataStr) == 0 or metadataStr == "undefined":
                continue
            if not "[" in metadataStr and not "]" in metadataStr and "{" in metadataStr:
                metadataStr = "[" + metadataStr + "]"
            if metadataStr == "[]":
                return []
            metadataFolderDict = json.loads(metadataStr)
            resultMetadata.append(metadata["fullName"])
            for metadataFolder in metadataFolderDict:
                if self.stop:
                    return []
                nameToAdd = metadataFolder["fullName"]
                add = False
                if len(excludePackages) > 0:
                    if "namespacePrefix" in metadataFolder:
                        if len(metadataFolder["namespacePrefix"]) > 0:
                            if not metadataFolder["namespacePrefix"] in excludePackages:
                                add = True
                                if needPrefixAddition:
                                    if specialReplace:
                                        nameToAdd = nameToAdd.replace(charMetaSeparator, charMetaSeparator + "__", 1)
                                    else:
                                        nameToAdd = nameToAdd.replace(charMetaSeparator, charMetaSeparator + "__")
                        else:
                            add = True
                    else:
                        add = True
                if add:
                    resultMetadata.append(nameToAdd)
        return resultMetadata

    def Unzip(self, pathToZipFile):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        thread = threading.Thread(target=self.UnzipFile, args=(pathToZipFile,))
        thread.setDaemon(True)
        thread.start()

    def UnzipFile(self, pathToZipFile):
        retrieveUrl = os.path.join(self.Parent.Parent.Parent.currentWorkspace, "retrieve")
        retrieveMetadataUrl = os.path.join(retrieveUrl, "metadata")
        zipRef = zipfile.ZipFile(pathToZipFile, "r")
        zipName = dtkglobal.PathLeaf(pathToZipFile)
        zipNameForFolder = zipName.rstrip(".zip")
        unzippedFolder = os.path.join(retrieveMetadataUrl, zipNameForFolder)
        self.consoleOutputTextCtrl.AppendText("Unzipping files from: " + pathToZipFile + " - To: " + unzippedFolder)
        self.consoleOutputTextCtrl.AppendText(os.linesep)
        zipRef.extractall(unzippedFolder)
        self.consoleOutputTextCtrl.AppendText("Files unzipped")
        self.consoleOutputTextCtrl.AppendText(os.linesep)

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
            type, file, jobId, batchId, targetName, pathName = (
                log["type"],
                log["file"],
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
                zipToExtract = self.unZipRetrievedCheckBox.GetValue()
                # zipToExtract = False
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
                    cmd = ["/usr/local/bin/sfdx" + " " + "force:data:bulk:status" + " " + "--apiversion" + " " + dtkglobal.defaultApiVersion + " " + "-u" + " " + targetName + " " + "-i" + " " + jobId + " " +  "-b" + " " + batchId]
                proc = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
                )
                for line in proc.stdout:
                    wx.CallAfter(self.OnText, line)
        wx.CallAfter(self.SetButtonState, True)

    def OnText(self, text):
        self.consoleOutputTextCtrl.AppendText(text)


class ExportDataPanel(wx.Panel):
    def __init__(self, parent):
        super(ExportDataPanel, self).__init__(parent)
        self.logList = dict()
        self.stop = False
        self.InitUI()

    def InitUI(self):
        self.mainSizer = wx.GridBagSizer(1, 1)

        # self.queryTemplateLbl = wx.StaticText(self, label="Query Template")
        # self.queryTemplateLbl.ToolTip = "Template to autoselect Query."
        # self.queryTemplateComboBox = wx.ComboBox(self, style=wx.CB_READONLY)
        # self.queryTemplateComboBox.ToolTip = "Template to autoselect Query."

        self.fileNameLbl = wx.StaticText(self, label="File Name")
        self.fileNameLbl.ToolTip = "File name to store the data retrieved."
        self.fileNameTextCtrl = wx.TextCtrl(self)
        self.fileNameTextCtrl.ToolTip = "File name to store the data retrieved."
        self.fileNameTextCtrl.AppendText("extract_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".csv")

        self.soqlTemplatesLbl = wx.StaticText(self, label="SOQL Templates")
        self.soqlTemplatesLbl.ToolTip = "List of SOQL Templates available."
        self.soqlTemplatesComboBox = wx.ComboBox(self, style=wx.CB_READONLY)
        self.soqlTemplatesComboBox.ToolTip = "List of SOQL Templates available."
        self.soqlTemplatesComboBox.Items = dtkglobal.soqlList
        self.soqlTemplatesComboBox.Bind(wx.EVT_COMBOBOX, self.ChangeSOQLTemplate)

        self.queryLbl = wx.StaticText(self, label="SOQL Query")
        self.queryLbl.ToolTip = "SOQL Query to retrieve data."
        self.queryTextCtrl = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_AUTO_URL | wx.TE_BESTWRAP)
        self.queryTextCtrl.ToolTip = "SOQL Query to retrieve data."

        self.btnRetrieve = wx.Button(self, label="Retrieve")
        self.btnRetrieve.Bind(wx.EVT_BUTTON, self.RetrieveButton)

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

        self.fileNameSizer = wx.GridBagSizer(1, 1)
        self.fileNameSizer.Add(self.fileNameLbl, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)
        self.fileNameSizer.Add(
            self.fileNameTextCtrl, pos=(0, 1), flag=wx.EXPAND | wx.TOP | wx.BOTTOM | wx.RIGHT, border=5
        )
        self.fileNameSizer.Add(self.soqlTemplatesLbl, pos=(1, 0), flag=wx.EXPAND | wx.ALL | wx.ALIGN_LEFT, border=5)
        self.fileNameSizer.Add(
            self.soqlTemplatesComboBox, pos=(1, 1), flag=wx.EXPAND | wx.ALL | wx.ALIGN_RIGHT, border=5
        )

        self.fileNameSizer.AddGrowableCol(1)
        self.fileNameSizer.SetEmptyCellSize((0, 0))

        self.querySizer = wx.GridBagSizer(1, 1)

        self.querySizer.Add(self.queryLbl, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.querySizer.Add(
            self.queryTextCtrl, pos=(1, 0), span=(5, 5), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )

        self.querySizer.AddGrowableCol(0)
        self.querySizer.AddGrowableRow(1)
        self.querySizer.SetEmptyCellSize((0, 0))

        self.secondSizer = wx.GridBagSizer(1, 1)
        self.secondSizer.Add(self.consoleOutputLbl, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.secondSizer.Add(
            self.consoleOutputTextCtrl,
            pos=(1, 0),
            span=(5, 5),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )

        self.secondSizer.AddGrowableCol(0)
        self.secondSizer.AddGrowableRow(1)
        self.secondSizer.SetEmptyCellSize((0, 0))

        self.mainSizer.Add(
            self.fileNameSizer,
            pos=(0, 0),
            span=(0, 5),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )

        self.mainSizer.Add(
            self.querySizer, pos=(1, 0), span=(5, 5), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5
        )
        self.mainSizer.Add(self.btnRetrieve, pos=(6, 4), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.secondSizer,
            pos=(7, 0),
            span=(5, 5),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
            border=5,
        )
        self.mainSizer.Add(self.btnStop, pos=(12, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)
        self.mainSizer.Add(self.btnRefreshLog, pos=(12, 4), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)

        self.mainSizer.AddGrowableCol(0)
        self.mainSizer.AddGrowableRow(1)
        self.mainSizer.AddGrowableRow(7)
        self.mainSizer.SetEmptyCellSize((0, 0))
        self.Layout()
        self.SetSizer(self.mainSizer)

    def ChangeSOQLTemplate(self, event):
        if self.soqlTemplatesComboBox.GetValue() in dtkglobal.soqlList:
            self.queryTextCtrl.SetValue(dtkglobal.soqlDict[self.soqlTemplatesComboBox.GetValue()])

    def StopButton(self, event):
        self.stop = True
        self.SetButtonState(True)

    def SetButtonState(self, state):
        if state:
            self.btnRetrieve.Enable()
            self.btnRefreshLog.Enable()
        else:
            self.btnRetrieve.Disable()
            self.btnRefreshLog.Disable()

    def RetrieveButton(self, event):
        self.stop = False
        if len(self.Parent.Parent.Parent.currentWorkspace) == 0:
            dlg = wx.MessageDialog(self, "Workspace not set yet.", "DTK - Retrieve", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        orgName = self.Parent.Parent.Parent.organizationComboBox.GetValue()
        sourceName = self.Parent.Parent.Parent.sandboxTypeSourceComboBox.GetValue()
        if len(orgName) == 0:
            dlg = wx.MessageDialog(self, "Please select an organization.", "DTK - Retrieve", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(sourceName) == 0:
            dlg = wx.MessageDialog(self, "Please select a source.", "DTK - Retrieve", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        retrieveUrl = os.path.join(self.Parent.Parent.Parent.currentWorkspace, "retrieve")
        retrieveMetadataUrl = os.path.join(retrieveUrl, "metadata")
        retrieveDataUrl = os.path.join(retrieveUrl, "data")
        if not os.path.exists(retrieveUrl):
            os.makedirs(retrieveUrl)
        if not os.path.exists(retrieveDataUrl):
            os.makedirs(retrieveDataUrl)

        soqlquery = self.queryTextCtrl.GetValue()
        soqlquery = soqlquery.replace("\n", " ")
        fileName = self.fileNameTextCtrl.GetLineText(0)
        self.SetButtonState(False)
        thread = threading.Thread(target=self.ProcessScript, args=(retrieveDataUrl, soqlquery, fileName))
        thread.setDaemon(True)
        thread.start()

    def ProcessScript(self, retrieveDataUrl, soqlquery, fileName):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        #shutil.rmtree(retrieveDataUrl, onerror=dtkglobal.RemoveReadonly)
        if not os.path.exists(retrieveDataUrl):
            os.makedirs(retrieveDataUrl)
        orgName = self.Parent.Parent.Parent.organizationComboBox.GetValue()
        sdbxNameSource = "Config"
        if dtkglobal.advSetting:
            sdbxNameSource = self.Parent.Parent.Parent.sandboxTypeSourceComboBox.GetValue()
        targetName = self.Parent.Parent.Parent.currentTarget

        scriptLine = 'SOURCE|SOQLQUERY|"' + soqlquery + '"|' + fileName
        lineSplit = scriptLine.split("|")
        self.ProcessDataScriptLine(lineSplit, scriptLine, targetName, targetName, retrieveDataUrl, 1, "")

    def ProcessDataScriptLine(
        self, lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl
    ):
        error, errorMsg, target, pathString, cmd = dtkglobal.ProcessDataScriptLine(
            lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl
        )
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        if error:
            self.consoleOutputTextCtrl.AppendText(errorMsg)
            self.consoleOutputTextCtrl.AppendText(os.linesep)
        else:
            self.RunDataCmd(lineSplit, target, pathString, cmd)

    def OnText(self, text):
        self.consoleOutputTextCtrl.AppendText(text)

    def RunDataCmd(self, lineSplit, target, pathString, cmd):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
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
                lineStr = line.decode()
                if "force:data:bulk:status" in lineStr:
                    lineSplit = lineStr.split("-i ")
                    if len(lineSplit) > 1:
                        lineSplitAgain = lineSplit[1].split(" -b ")
                        if len(lineSplitAgain) > 1:
                            logEntry = {}
                            logEntry["type"] = "Bulk"
                            logEntry["file"] = ""
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
            type, file, jobId, batchId, targetName, pathName = (
                log["type"],
                log["file"],
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
                for line in proc.stdout:
                    wx.CallAfter(self.OnText, line)
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
                proc = subprocess.Popen(
                    cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
                )
                for line in proc.stdout:
                    wx.CallAfter(self.OnText, line)
        wx.CallAfter(self.SetButtonState, True)


class RetrieveFrame(wx.Frame):
    def __init__(self, parent=None):
        super(RetrieveFrame, self).__init__(parent, title="Retrieve")
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
        self.panel = wx.Panel(self)
        row = 0
        col = 0

        self.organizationLbl = wx.StaticText(self.panel, label="Organization")
        self.organizationLbl.ToolTip = "List of Organizations available."
        self.organizationComboBox = wx.ComboBox(self.panel, style=wx.CB_READONLY)
        self.organizationComboBox.ToolTip = "List of Organizations available."
        self.organizationComboBox.Items = dtkglobal.orgList
        self.organizationComboBox.Bind(wx.EVT_COMBOBOX, self.OrganizationSelected)

        if dtkglobal.unlockSetting:
            self.sandboxTypeSourceLbl = wx.StaticText(self.panel, label="Source")
            self.sandboxTypeSourceLbl.ToolTip = "Sandbox Type: Config, QA, UAT or Prod."
            self.sandboxTypeSourceComboBox = wx.ComboBox(self.panel, style=wx.CB_READONLY)
            self.sandboxTypeSourceComboBox.ToolTip = "Sandbox Type: Config, QA, UAT or Prod."
            self.sandboxTypeSourceComboBox.Bind(wx.EVT_COMBOBOX, self.SourceSelected)
            self.sandboxTypeSourceComboBox.Enable(False)

        self.nb = wx.Notebook(self.panel)
        self.nb.AddPage(RetrieveMetadataPanel(self.nb, retrieveType="Metadata Retrieve"), "Metadata")
        self.nb.AddPage(ExportDataPanel(self.nb), "Export Data")

        self.mainSizer.Add(self.organizationLbl, pos=(row, col), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.organizationComboBox,
            pos=(row, col + 1),
            span=(0, 3),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        if dtkglobal.unlockSetting:
            self.mainSizer.Add(self.sandboxTypeSourceLbl, pos=(row, col), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5)
            self.mainSizer.Add(
                self.sandboxTypeSourceComboBox,
                pos=(row, col + 1),
                span=(0, 3),
                flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
                border=5,
            )
            row += 1

        self.mainSizer.Add(self.nb, pos=(row, col), span=(0, 6), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)

        self.mainSizer.AddGrowableRow(row)
        self.mainSizer.AddGrowableCol(2)
        self.mainSizer.SetEmptyCellSize((0, 0))
        self.panel.SetSizerAndFit(self.mainSizer)
        self.mainSizer.Fit(self)
        self.mainSizer.SetEmptyCellSize((0, 0))
        self.Layout()
        self.Fit()

        self.Centre()
        self.MinSize = self.Size
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Show()

    def OrganizationSelected(self, event):
        orgName = self.organizationComboBox.GetValue()
        if dtkglobal.unlockSetting:
            self.sandboxTypeSourceComboBox.Enable(False)
        if len(orgName) == 0:
            self.sandboxTypeSourceComboBox.Clear()
        if orgName in dtkglobal.orgDict:
            sandboxList = dtkglobal.orgDict[orgName]["sandboxes"]
            sandboxList.sort()
            self.Title = "Retrieve: " + orgName
            if dtkglobal.unlockSetting:
                self.sandboxTypeSourceComboBox.Items = sandboxList
                self.sandboxTypeSourceComboBox.Enable(True)
            else:
                self.SetSource(orgName, "Config")

    def SourceSelected(self, event):
        orgName = self.organizationComboBox.GetValue()
        sdbxName = self.sandboxTypeSourceComboBox.GetValue()
        self.SetSource(orgName, sdbxName)

    def SetSource(self, orgName, sdbxName):
        if len(orgName) == 0:
            dlg = wx.MessageDialog(self, "Please select an organization.", "DTK - Retrieve", wx.OK | wx.ICON_ERROR)
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
        self.nb.GetPage(1).consoleOutputTextCtrl.AppendText("Workspace changed to: " + self.currentWorkspace)
        self.nb.GetPage(1).consoleOutputTextCtrl.AppendText(os.linesep)
        self.Title = "Retrieve: " + orgName + " - " + sdbxName

    def OnCloseWindow(self, event):
        if self.currentTarget in dtkglobal.targets:
            dtkglobal.targets.remove(self.currentTarget)
        if self.currentWorkspace in dtkglobal.workspaces:
            dtkglobal.workspaces.remove(self.currentWorkspace)
        self.Destroy()
