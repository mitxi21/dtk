import datetime
import json
import os
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

        self.manifestFileLbl = wx.StaticText(self, label="Manifest File")
        self.manifestFileLbl.ToolTip = "Provide a manifest file to retrieve the metadata from the source selected."
        self.manifestFileTextCtrl = wx.TextCtrl(self)
        self.manifestFileTextCtrl.ToolTip = "Provide a manifest file to retrieve the metadata from the source selected."

        self.btnUploadManifestFile = wx.Button(self, label='Browse')
        self.btnUploadManifestFile.Bind(wx.EVT_BUTTON, self.UploadManifestFile)

        self.btnRetrieve = wx.Button(self, label='Retrieve')
        self.btnRetrieve.Bind(wx.EVT_BUTTON, self.RetrieveButton)

        self.consoleOutputLbl = wx.StaticText(self, label="Log")
        self.consoleOutputLbl.ToolTip = "Console output log."
        self.consoleOutputTextCtrl = wx.TextCtrl(self, style = wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_AUTO_URL|wx.HSCROLL)
        self.consoleOutputTextCtrl.ToolTip = "Console output log."

        self.btnStop = wx.Button(self, label='Stop')
        self.btnStop.Bind(wx.EVT_BUTTON, self.StopButton)

        self.btnRefreshLog = wx.Button(self, label='Refresh Log')
        self.btnRefreshLog.Bind(wx.EVT_BUTTON, self.RefreshLog)

        row = 0
        col = 0

        self.retrieveTypeSizer = wx.GridBagSizer(1, 1)

        self.retrieveTypeSizer.Add(self.retrieveTypeLbl, pos=(0, 0),
                       flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)
        self.retrieveTypeSizer.Add(self.retrieveTypeComboBox, pos=(0, 1), span=(0, 5),
                       flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)

        self.retrieveTypeSizer.AddGrowableCol(1)
        self.retrieveTypeSizer.SetEmptyCellSize((0, 0))

        self.firstSizer = wx.GridBagSizer(1, 1)

        self.leftSizer = wx.GridBagSizer(1, 1)
        self.leftSizer.Add(self.metadataTemplateLbl, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
                            border=5)
        self.leftSizer.Add(self.metadataTemplateComboBox, pos=(0, 1),
                            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)
        self.leftSizer.Add(self.metadataTypesLbl, pos=(1, 0), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.leftSizer.Add(self.metadataTypesListBox, pos=(1, 1),
                            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.leftSizer.AddGrowableCol(1)
        self.leftSizer.SetEmptyCellSize((0, 0))

        self.firstSizer.Add(self.leftSizer, pos=(0, 0), span=(0, 5), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
                            border=0)

        self.rightSizer = wx.GridBagSizer(1, 1)
        self.rightSizer.Add(self.excludePackagesLbl, pos=(0, 0), flag= wx.TOP | wx.LEFT | wx.RIGHT,
                            border=5)
        self.rightSizer.Add(self.excludePackagesTextCtrl, pos=(0, 1),
                            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)

        self.rightSizer.Add(self.includeManagePackagesLbl, pos=(1, 0), flag= wx.TOP | wx.LEFT | wx.RIGHT,
                            border=5)
        self.rightSizer.Add(self.includeManagePackagesCheckBox, pos=(1, 1), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
                            border=5)
        self.rightSizer.Add(self.unZipRetrievedLbl, pos=(2, 0), flag=wx.TOP | wx.LEFT | wx.RIGHT,
                            border=5)
        self.rightSizer.Add(self.unZipRetrievedCheckBox, pos=(2, 1),
                            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
                            border=5)
        self.rightSizer.Add(self.clearLogsLbl, pos=(3, 0), flag=wx.TOP | wx.LEFT | wx.RIGHT,
                            border=5)
        self.rightSizer.Add(self.clearLogsCheckBox, pos=(3, 1),
                            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
                            border=5)
        self.rightSizer.AddGrowableCol(1)
        self.rightSizer.SetEmptyCellSize((0, 0))

        self.firstSizer.Add(self.rightSizer, pos=(0, 5), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
                            border=0)

        self.includeManagePackagesLbl.Hide()
        self.includeManagePackagesCheckBox.Hide()

        self.firstSizer.AddGrowableCol(0)
        self.firstSizer.AddGrowableCol(1)
        self.firstSizer.AddGrowableRow(0)
        self.firstSizer.SetEmptyCellSize((0, 0))

        self.manifestSizer = wx.GridBagSizer(1, 1)
        self.manifestSizer.Add(self.manifestFileLbl, pos=(0, 0), flag= wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.manifestFileSizer = wx.GridBagSizer(1, 1)
        self.manifestFileSizer.Add(self.manifestFileTextCtrl, pos=(0, 0), span=(0, 4),
                                   flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)
        self.manifestFileSizer.Add(self.btnUploadManifestFile, pos=(0, 5),
                                   flag=wx.TOP | wx.BOTTOM | wx.RIGHT, border=5)
        self.manifestFileSizer.AddGrowableCol(0)
        self.manifestFileSizer.SetEmptyCellSize((0, 0))
        self.manifestSizer.Add(self.manifestFileSizer, pos=(0, 1), span=(0, 5), flag= wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=0)
        self.manifestSizer.AddGrowableCol(1)
        self.manifestSizer.SetEmptyCellSize((0, 0))


        self.secondSizer = wx.GridBagSizer(1, 1)
        self.secondSizer.Add(self.consoleOutputLbl, pos=(0, 0), flag= wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.secondSizer.Add(self.consoleOutputTextCtrl, pos=(1, 0), span=(5,5),
                      flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)

        self.secondSizer.AddGrowableCol(0)
        self.secondSizer.AddGrowableRow(1)
        self.secondSizer.SetEmptyCellSize((0, 0))

        self.mainSizer.Add(self.retrieveTypeSizer, pos=(0, 0), span=(0, 5), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
                      border=5)
        self.mainSizer.Add(self.manifestSizer, pos=(1, 0), span=(0, 5), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
                      border=5)
        self.mainSizer.Add(self.firstSizer, pos=(2, 0), span=(0, 5), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
                      border=5)
        self.mainSizer.Add(self.btnRetrieve, pos=(3, 4), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
                       border=5)
        self.mainSizer.Add(self.secondSizer, pos=(4, 0), span=(10, 5), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
                      border=5)
        self.mainSizer.Add(self.btnStop, pos=(14, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
                           border=5)
        self.mainSizer.Add(self.btnRefreshLog, pos=(14, 4), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
                        border=5)

        if self.retrieveTypeSelected == 'Metadata Retrieve':
            self.manifestFileLbl.Hide()
            self.manifestFileTextCtrl.Hide()
            self.btnUploadManifestFile.Hide()

        if self.retrieveTypeSelected == 'Manifest File':
            self.metadataTypesLbl.Hide()
            self.metadataTypesListBox.Hide()
            self.metadataTemplateLbl.Hide()
            self.metadataTemplateComboBox.Hide()
            self.excludePackagesLbl.Hide()
            self.excludePackagesTextCtrl.Hide()
            self.includeManagePackagesLbl.Hide()
            self.includeManagePackagesCheckBox.Hide()

        self.mainSizer.AddGrowableCol(0)
        self.mainSizer.AddGrowableRow(4)
        self.mainSizer.SetEmptyCellSize((0, 0))
        self.Layout()

        self.SetSizer(self.mainSizer)

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
        if self.retrieveTypeSelected == 'Metadata Retrieve':
            self.metadataTypesLbl.Show()
            self.metadataTypesListBox.Show()
            self.metadataTemplateLbl.Show()
            self.metadataTemplateComboBox.Show()
            self.excludePackagesLbl.Show()
            self.excludePackagesTextCtrl.Show()
            self.includeManagePackagesLbl.Show()
            self.includeManagePackagesCheckBox.Show()

            self.manifestFileLbl.Hide()
            self.manifestFileTextCtrl.Hide()
            self.btnUploadManifestFile.Hide()

        if self.retrieveTypeSelected == 'Manifest File':
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
        self.Layout()


    def UploadManifestFile(self, event):
        if len(self.Parent.Parent.Parent.currentWorkspace) == 0:
            dlg = wx.MessageDialog(self,
                                   "Workspace not set yet.",
                                   "DTK - Retrieve", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        retrieveUrl = os.path.join(self.Parent.Parent.Parent.currentWorkspace, 'retrieve')
        retrieveMetadataUrl = os.path.join(retrieveUrl, 'metadata')

        if not os.path.exists(retrieveUrl):
            os.makedirs(retrieveUrl)
        if not os.path.exists(retrieveMetadataUrl):
            os.makedirs(retrieveMetadataUrl)
        else:
            shutil.rmtree(retrieveMetadataUrl, onerror=dtkglobal.RemoveReadonly)
            os.makedirs(retrieveMetadataUrl)

        dlg = wx.FileDialog(self, "Select manifest file", wildcard="XML files (*.xml)|*.xml",
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)

        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        pathname = dlg.GetPath()
        self.manifestFileTextCtrl.Clear()
        self.manifestFileTextCtrl.AppendText(pathname)
        shutil.copy(pathname, retrieveMetadataUrl)
        self.consoleOutputTextCtrl.AppendText('File copied into workspace metadata folder: ' + dtkglobal.PathLeaf(pathname))
        self.consoleOutputTextCtrl.AppendText(os.linesep)

    def ChangeMetadataTemplate(self, event):
        self.metadataTypesListBox.SetSelection(-1)
        if self.metadataTemplateComboBox.GetValue() == 'All':
            for i in range(self.metadataTypesListBox.GetCount()):
                self.metadataTypesListBox.SetSelection(i)
        if self.metadataTemplateComboBox.GetValue() in dtkglobal.metadataTemplatesSelection:
            for line in dtkglobal.metadataTemplatesSelection[self.metadataTemplateComboBox.GetValue()]:
                self.metadataTypesListBox.SetStringSelection(line)

    def RetrieveButton(self, event):
        self.stop = False
        if len(self.Parent.Parent.Parent.currentWorkspace) == 0:
            dlg = wx.MessageDialog(self,
                                   "Workspace not set yet.",
                                   "DTK - Retrieve", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        orgName = self.Parent.Parent.Parent.organizationComboBox.GetValue()
        sdbxName = self.Parent.Parent.Parent.sandboxTypeSourceComboBox.GetValue()
        orgName = self.Parent.Parent.Parent.organizationComboBox.GetValue()
        if len(orgName) == 0:
            dlg = wx.MessageDialog(self,
                                   "Please select an organization.",
                                   "DTK - Retrieve", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(sdbxName) == 0:
            dlg = wx.MessageDialog(self,
                                   "Please select a source.",
                                   "DTK - Retrieve", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        if self.clearLogsCheckBox.GetValue():
            self.consoleOutputTextCtrl.Clear()
            self.consoleOutputTextCtrl.AppendText('Workspace: ' + self.Parent.Parent.Parent.currentWorkspace)
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            self.logList.clear()

        targetName = orgName + '_' + sdbxName
        metadataTypes = self.metadataTypesListBox.GetSelections()
        excludePackages = self.excludePackagesTextCtrl.GetValue()

        retrieveUrl = os.path.join(self.Parent.Parent.Parent.currentWorkspace, 'retrieve')
        retrieveMetadataUrl = os.path.join(retrieveUrl, 'metadata')
        retrieveDataUrl = os.path.join(retrieveUrl, 'data')
        manifestFileUrl = self.manifestFileTextCtrl.GetValue()
        waitMinutes = '0'
        self.SetButtonState(False)
        if not os.path.exists(retrieveUrl):
            os.makedirs(retrieveUrl)
        if not os.path.exists(retrieveMetadataUrl):
            os.makedirs(retrieveMetadataUrl)
        if (self.retrieveTypeComboBox.GetValue() == 'Metadata Retrieve'):
            thread = threading.Thread(target=self.GenerateManifestFirst,
                                      args=(orgName, sdbxName, targetName, retrieveUrl, retrieveMetadataUrl, metadataTypes, excludePackages, waitMinutes))
            thread.setDaemon(True)
            thread.start()
        if (self.retrieveTypeComboBox.GetValue() == 'Manifest File'):
            thread = threading.Thread(target=self.RetrieveMetadataManifest,
                                      args=(
                                          orgName, sdbxName, targetName, retrieveUrl, retrieveMetadataUrl,
                                          manifestFileUrl,
                                          waitMinutes))
            thread.setDaemon(True)
            thread.start()

    def RetrieveMetadataManifest(self, orgName, sdbxName, targetName, retrieveUrl, retrieveMetadataUrl, manifestFileUrl,
                         waitMinutes):
        thread = threading.Thread(target=self.RetrieveMetadata,
                                  args=(
                                  orgName, sdbxName, targetName, retrieveUrl, retrieveMetadataUrl, manifestFileUrl,
                                  waitMinutes))
        thread.setDaemon(True)
        thread.start()

    def RetrieveMetadata(self, orgName, sdbxName, targetName, retrieveUrl, retrieveMetadataUrl, manifestFileUrl, waitMinutes):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        cmd = ['sfdx', 'force:mdapi:retrieve', '--apiversion', dtkglobal.defaultApiVersion, '-u', targetName,
               '-r', retrieveMetadataUrl, '-k', manifestFileUrl, '-s', '-w', waitMinutes]
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
        jobIdStrip = ''
        for line in proc.stdout:
            lineStr = line.decode()
            if 'jobid:  ' in lineStr:
                lineSplit = lineStr.split('jobid: ')
                if len(lineSplit) > 1:
                    logEntry = {}
                    logEntry["type"] = 'Retrieve'
                    logEntry["file"] = manifestFileUrl
                    jobIdStrip = lineSplit[1].strip('\r\n')
                    jobIdStrip = jobIdStrip.strip()
                    logEntry["jobid"] = jobIdStrip
                    logEntry["batchid"] = ""
                    logEntry["targetname"] = targetName
                    logEntry["pathname"] = retrieveMetadataUrl
                    self.logList[jobIdStrip] = logEntry
            wx.CallAfter(self.OnText, lineStr)
        wx.CallAfter(self.SetButtonState, True)

    def GenerateManifestFirst(self, orgName, sdbxName, targetName, retrieveUrl, retrieveMetadataUrl, metadataTypes, excludePackages, waitMinutes):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        if os.path.exists(retrieveMetadataUrl):
            shutil.rmtree(retrieveMetadataUrl, onerror=dtkglobal.RemoveReadonly)
        if not os.path.exists(retrieveMetadataUrl):
            os.makedirs(retrieveMetadataUrl)
        outputFileUrl = os.path.join(self.Parent.Parent.Parent.currentWorkspace, 'tmp')
        if not os.path.exists(outputFileUrl):
            os.makedirs(outputFileUrl)
        outputFileUrl = os.path.join(self.Parent.Parent.Parent.currentWorkspace, 'tmp', 'describeMetadata.log')
        thread = threading.Thread(target=self.GenerateManifestSecond, args=(
        orgName, sdbxName, targetName, retrieveUrl, retrieveMetadataUrl, metadataTypes, excludePackages, waitMinutes,
        outputFileUrl))
        thread.setDaemon(True)
        thread.start()

    def DescribeMetadata(self, orgName, sdbxName, targetName, retrieveUrl, retrieveMetadataUrl, metadataTypes, excludePackages, waitMinutes, outputFileUrl):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        cmd = ['sfdx', 'force:mdapi:describemetadata', '--apiversion', dtkglobal.defaultApiVersion, '-u', targetName, '-f', outputFileUrl]
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
        for line in proc.stdout:
            wx.CallAfter(self.OnText, line)
        thread = threading.Thread(target=self.GenerateManifestSecond, args=(orgName, sdbxName, targetName, retrieveUrl, retrieveMetadataUrl, metadataTypes, excludePackages, waitMinutes, outputFileUrl))
        thread.setDaemon(True)
        thread.start()

    def GenerateManifestSecond(self, orgName, sdbxName, targetName, retrieveUrl, retrieveMetadataUrl, metadataTypes, excludePackages, waitMinutes, outputFileUrl):
        #fileOutput = open(outputFileUrl, 'r', encoding='utf8')
        #describeMetadataDict = json.loads(fileOutput.read())
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        manifestFileUrl = os.path.join(retrieveMetadataUrl, 'package.xml')
        manifestFile = open(manifestFileUrl, 'wb')
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
            charMetaSeparator = ''
            needPrefixAddition = False
            specialReplace = False
            folder = ''
            simpleListMetadata = True
            if item in ['CustomMetadata','QuickAction']:
                charMetaSeparator = '.'
                needPrefixAddition = True
            if item == 'Layout':
                charMetaSeparator = '-'
                needPrefixAddition = True
                specialReplace = True
            if item == 'Flow':
                addWildcard = True
            if item == 'Dashboard':
                simpleListMetadata = False
                folder = 'DashboardFolder'
            if item == 'Document':
                simpleListMetadata = False
                folder = 'DocumentFolder'
            if item == 'EmailTemplate':
                simpleListMetadata = False
                folder = 'EmailFolder'
            if item == 'Report':
                simpleListMetadata = False
                folder = 'ReportFolder'
            typeContent = '\t<types>\n'
            if simpleListMetadata:
                members = self.GetListMetadataMembers(targetName, retrieveUrl, excludePackages, item, charMetaSeparator, needPrefixAddition, specialReplace)
            else:
                members = self.GetFolderMetadataMembers(targetName, retrieveUrl, excludePackages, item, charMetaSeparator, needPrefixAddition, specialReplace, folder)
            if len(members) == 0:
                continue
            members.sort()
            for member in members:
                typeIncluded = True
                typeContent += '\t\t<members>' + member + '</members>\n'
            if addWildcard:
                typeContent += '\t\t<members>*</members>\n'
            typeContent += '\t\t<name>' + item + '</name>\n'
            typeContent += '\t</types>\n'
            if typeIncluded:
                oneIncluded = True
                strContent += typeContent
        if not oneIncluded:
            self.OnText("No metadata selected to retrieve.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        strContent += '\t<version>' + dtkglobal.defaultApiVersion + '</version>\n'
        strContent += '</Package>\n'
        bynaryContent = strContent.encode()
        manifestFile.write(bynaryContent)
        manifestFile.close()
        wx.CallAfter(self.OnText, 'Manifest file generated.')
        wx.CallAfter(self.OnText, os.linesep)
        thread = threading.Thread(target=self.RetrieveMetadata, args=(orgName, sdbxName, targetName, retrieveUrl, retrieveMetadataUrl, manifestFileUrl,
                         waitMinutes))
        thread.setDaemon(True)
        thread.start()

    def GetListMetadataMembers(self, targetName, retrieveUrl, excludePackages, metadataItem, charMetaSeparator, needPrefixAddition, specialReplace):
        if self.stop:
            return []
        pathUrl = os.path.join(retrieveUrl, 'tmp')
        resultMetadata = []
        if not os.path.exists(pathUrl):
            os.makedirs(pathUrl)
        outputFileUrl = os.path.join(pathUrl, metadataItem + '.tmp')
        cmd = ['sfdx', 'force:mdapi:listmetadata', '--apiversion', dtkglobal.defaultApiVersion, '-u', targetName, '-m', metadataItem,
               '-f', outputFileUrl]
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
        for line in proc.stdout:
            wx.CallAfter(self.OnText, line)
        if not os.path.exists(outputFileUrl):
            return []
        fileOutput = open(outputFileUrl, 'r', encoding='utf8')
        metadataStr = fileOutput.read()
        if len(metadataStr) == 0 or metadataStr == 'undefined':
            return []
        if not '[' in metadataStr and not ']' in metadataStr and '{' in metadataStr:
            metadataStr = '[' + metadataStr + ']'
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
                if 'namespacePrefix' in metadata:
                    if len(metadata["namespacePrefix"]) > 0:
                        if (not metadata["namespacePrefix"] in excludePackages):
                            add = True
                            if needPrefixAddition:
                                if specialReplace:
                                    nameToAdd = nameToAdd.replace(charMetaSeparator, charMetaSeparator + metadata["namespacePrefix"] + '__', 1)
                                else:
                                    nameToAdd = nameToAdd.replace(charMetaSeparator, charMetaSeparator + metadata["namespacePrefix"] + '__')
                    else:
                        add = True
                else:
                    add = True
            if add:
                resultMetadata.append(nameToAdd)
        return resultMetadata

    def GetFolderMetadataMembers(self, targetName, retrieveUrl, excludePackages, metadataItem, charMetaSeparator, needPrefixAddition, specialReplace, folder):
        if self.stop:
            return []
        pathUrl = os.path.join(retrieveUrl, 'tmp')
        resultMetadata = []
        if not os.path.exists(pathUrl):
            os.makedirs(pathUrl)
        outputFileUrl = os.path.join(pathUrl, folder + '.tmp')
        cmd = ['sfdx', 'force:mdapi:listmetadata', '--apiversion', dtkglobal.defaultApiVersion, '-u', targetName, '-m', folder,
               '-f', outputFileUrl]
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
        for line in proc.stdout:
            wx.CallAfter(self.OnText, line)
        if not os.path.exists(outputFileUrl):
            return []
        fileOutput = open(outputFileUrl, 'r', encoding='utf8')
        metadataStr = fileOutput.read()
        if len(metadataStr) == 0 or metadataStr == 'undefined':
            return []
        if not '[' in metadataStr and not ']' in metadataStr and '{' in metadataStr:
            metadataStr = '[' + metadataStr + ']'
        if metadataStr == "[]":
            return []
        metadataDict = json.loads(metadataStr)
        for metadata in metadataDict:
            if self.stop:
                return []
            outputFileFolderUrl = os.path.join(pathUrl, metadata["fullName"] + '.tmp')
            cmd = ['sfdx', 'force:mdapi:listmetadata', '--apiversion', dtkglobal.defaultApiVersion, '-u', targetName,
                   '-m', metadataItem, '--folder', metadata["fullName"],
                   '-f', outputFileFolderUrl]
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
            for line in proc.stdout:
                wx.CallAfter(self.OnText, line)
            if not os.path.exists(outputFileFolderUrl):
                continue
            fileOutputFolder = open(outputFileFolderUrl, 'r', encoding='utf8')
            metadataStr = fileOutputFolder.read()
            if len(metadataStr) == 0 or metadataStr == 'undefined':
                continue
            if not '[' in metadataStr and not ']' in metadataStr and '{' in metadataStr:
                metadataStr = '[' + metadataStr + ']'
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
                    if 'namespacePrefix' in metadataFolder:
                        if len(metadataFolder["namespacePrefix"]) > 0:
                            if (not metadataFolder["namespacePrefix"] in excludePackages):
                                add = True
                                if needPrefixAddition:
                                    if specialReplace:
                                        nameToAdd = nameToAdd.replace(charMetaSeparator, charMetaSeparator + '__', 1)
                                    else:
                                        nameToAdd = nameToAdd.replace(charMetaSeparator, charMetaSeparator + '__')
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
        retrieveUrl = os.path.join(self.Parent.Parent.Parent.currentWorkspace, 'retrieve')
        retrieveMetadataUrl = os.path.join(retrieveUrl, 'metadata')
        zipRef = zipfile.ZipFile(pathToZipFile, 'r')
        zipName = dtkglobal.PathLeaf(pathToZipFile)
        zipNameForFolder = zipName.rstrip('.zip')
        unzippedFolder = os.path.join(retrieveMetadataUrl, zipNameForFolder)
        self.consoleOutputTextCtrl.AppendText("Unzipping files from: " + pathToZipFile + " - To: " + unzippedFolder)
        self.consoleOutputTextCtrl.AppendText(os.linesep)
        zipRef.extractall(unzippedFolder)
        self.consoleOutputTextCtrl.AppendText("Files unzipped")
        self.consoleOutputTextCtrl.AppendText(os.linesep)

    def RefreshLog(self, event):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        if len(self.logList) == 0:
            return
        self.consoleOutputTextCtrl.AppendText(
            '----------------------------------------------------------------------------------')
        self.consoleOutputTextCtrl.AppendText(os.linesep)
        self.consoleOutputTextCtrl.AppendText(
            'Refresh log started at: ' + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        self.consoleOutputTextCtrl.AppendText(os.linesep)
        waitMinutes = '0'
        self.SetButtonState(False)
        thread = threading.Thread(target=self.RunRefreshLog, args=(waitMinutes))
        thread.setDaemon(True)
        thread.start()

    def RunRefreshLog(self, waitMinutes):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        for jobId in self.logList:
            log = self.logList[jobId]
            type, file, jobId, batchId, targetName, pathName = log["type"], log["file"], log["jobid"], log["batchid"], log["targetname"], log["pathname"]
            if type == 'Retrieve':
                cmd = ['sfdx', 'force:mdapi:retrieve:report', '--apiversion', dtkglobal.defaultApiVersion, '-u', targetName,
                       '-i', jobId, '-r', pathName, '-w', waitMinutes]
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
                zipToExtract = self.unZipRetrievedCheckBox.GetValue()
                # zipToExtract = False
                zipReady = False
                zipUrl = ''
                for line in proc.stdout:
                    lineStr = line.decode()
                    wx.CallAfter(self.OnText, line)
                    if zipToExtract:
                        if 'Wrote retrieve zip to ' in lineStr:
                            lineSplit = lineStr.split('Wrote retrieve zip to ')
                            if len(lineSplit) > 1:
                                zipUrl = lineSplit[1]
                                zipUrl = zipUrl.strip('\r\n')
                                zipUrl = zipUrl.rstrip('.')
                                zipReady = True
                if zipToExtract and zipReady:
                    wx.CallAfter(self.Unzip, zipUrl)
            if type == 'Deploy':
                cmd = ['sfdx', 'force:mdapi:deploy:report', '--apiversion', dtkglobal.defaultApiVersion, '-u', targetName,
                       '-i', jobId]
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
                for line in proc.stdout:
                    wx.CallAfter(self.OnText, line)
            if type == 'Bulk':
                cmd = ['sfdx', 'force:data:bulk:status', '--apiversion', dtkglobal.defaultApiVersion, '-u', targetName,
                       '-i', jobId, '-b', batchId]
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
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
        self.fileNameTextCtrl.AppendText('extract_' + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.csv')

        self.queryLbl = wx.StaticText(self, label="SOQL Query")
        self.queryLbl.ToolTip = "SOQL Query to retrieve data."
        self.queryTextCtrl = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_AUTO_URL|wx.TE_BESTWRAP)
        self.queryTextCtrl.ToolTip = "SOQL Query to retrieve data."

        self.btnRetrieve = wx.Button(self, label='Retrieve')
        self.btnRetrieve.Bind(wx.EVT_BUTTON, self.RetrieveButton)

        self.consoleOutputLbl = wx.StaticText(self, label="Log")
        self.consoleOutputLbl.ToolTip = "Console output log."
        self.consoleOutputTextCtrl = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_AUTO_URL|wx.HSCROLL)
        self.consoleOutputTextCtrl.ToolTip = "Console output log."

        self.btnStop = wx.Button(self, label='Stop')
        self.btnStop.Bind(wx.EVT_BUTTON, self.StopButton)

        self.btnRefreshLog = wx.Button(self, label='Refresh Log')
        self.btnRefreshLog.Bind(wx.EVT_BUTTON, self.RefreshLog)

        row = 0
        col = 0

        self.fileNameSizer = wx.GridBagSizer(1, 1)
        self.fileNameSizer.Add(self.fileNameLbl, pos=(0, 0),
                               flag= wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)
        self.fileNameSizer.Add(self.fileNameTextCtrl, pos=(0, 1),
                               flag=wx.EXPAND | wx.TOP | wx.BOTTOM | wx.RIGHT, border=5)
        self.fileNameSizer.AddGrowableCol(1)
        self.fileNameSizer.SetEmptyCellSize((0, 0))


        self.querySizer = wx.GridBagSizer(1, 1)

        self.querySizer.Add(self.queryLbl, pos=(0, 0), flag= wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.querySizer.Add(self.queryTextCtrl, pos=(1, 0), span=(5, 5),
                      flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)

        self.querySizer.AddGrowableCol(0)
        self.querySizer.AddGrowableRow(1)
        self.querySizer.SetEmptyCellSize((0, 0))

        self.secondSizer = wx.GridBagSizer(1, 1)
        self.secondSizer.Add(self.consoleOutputLbl, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.secondSizer.Add(self.consoleOutputTextCtrl, pos=(1, 0), span=(5, 5),
                        flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5)

        self.secondSizer.AddGrowableCol(0)
        self.secondSizer.AddGrowableRow(1)
        self.secondSizer.SetEmptyCellSize((0, 0))

        self.mainSizer.Add(self.fileNameSizer, pos=(0, 0), span=(0, 5), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
                      border=5)
        self.mainSizer.Add(self.querySizer, pos=(1, 0), span=(5, 5),
                           flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
                           border=5)
        self.mainSizer.Add(self.btnRetrieve, pos=(6, 4), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
                      border=5)
        self.mainSizer.Add(self.secondSizer, pos=(7, 0), span=(5, 5), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
                      border=5)
        self.mainSizer.Add(self.btnStop, pos=(12, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
                           border=5)
        self.mainSizer.Add(self.btnRefreshLog, pos=(12, 4), flag=wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT,
                      border=5)

        self.mainSizer.AddGrowableCol(0)
        self.mainSizer.AddGrowableRow(1)
        self.mainSizer.AddGrowableRow(7)
        self.mainSizer.SetEmptyCellSize((0, 0))
        self.Layout()
        self.SetSizer(self.mainSizer)

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
            dlg = wx.MessageDialog(self,
                                   "Workspace not set yet.",
                                   "DTK - Retrieve", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        orgName = self.Parent.Parent.Parent.organizationComboBox.GetValue()
        sourceName = self.Parent.Parent.Parent.sandboxTypeSourceComboBox.GetValue()
        if len(orgName) == 0:
            dlg = wx.MessageDialog(self,
                                   "Please select an organization.",
                                   "DTK - Retrieve", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(sourceName) == 0:
            dlg = wx.MessageDialog(self,
                                   "Please select a source.",
                                   "DTK - Retrieve", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        retrieveUrl = os.path.join(self.Parent.Parent.Parent.currentWorkspace, 'retrieve')
        retrieveMetadataUrl = os.path.join(retrieveUrl, 'metadata')
        retrieveDataUrl = os.path.join(retrieveUrl, 'data')
        if not os.path.exists(retrieveUrl):
            os.makedirs(retrieveUrl)
        if not os.path.exists(retrieveDataUrl):
            os.makedirs(retrieveDataUrl)

        soqlquery = self.queryTextCtrl.GetValue()
        soqlquery = soqlquery.replace('\n',' ')
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
        shutil.rmtree(retrieveDataUrl, onerror=dtkglobal.RemoveReadonly)
        if not os.path.exists(retrieveDataUrl):
            os.makedirs(retrieveDataUrl)
        orgName = self.Parent.Parent.Parent.organizationComboBox.GetValue()
        sdbxNameSource = 'Config'
        if dtkglobal.advSetting:
            sdbxNameSource = self.Parent.Parent.Parent.sandboxTypeSourceComboBox.GetValue()
        targetName = self.Parent.Parent.Parent.currentTarget

        scriptLine = 'SOURCE|SOQLQUERY|"' + soqlquery + '"|' + fileName
        lineSplit = scriptLine.split('|')
        self.ProcessDataScriptLine(lineSplit, scriptLine, targetName, targetName, retrieveDataUrl, 1, '')

    def ProcessDataScriptLine(self, lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl):
        error, errorMsg, target, pathString, cmd = dtkglobal.ProcessDataScriptLine(lineSplit, lineStr, targetName, sourceName, deployDataUrl, lineNumber, deployStageUrl)
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
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
        if 'SOQLQUERY' in lineSplit:
            fileOutput = open(pathString, 'wb')
            fileOutput.write(proc.stdout.read())
            for line in proc.stdout:
                wx.CallAfter(self.OnText, line)
            wx.CallAfter(self.OnText, "Exported data to " + pathString + '\n')
        else:
            for line in proc.stdout:
                lineStr = line.decode()
                if 'force:data:bulk:status' in lineStr:
                    lineSplit = lineStr.split('-i ')
                    if len(lineSplit) > 1:
                        lineSplitAgain = lineSplit[1].split(' -b ')
                        if len(lineSplitAgain) > 1:
                            logEntry = {}
                            logEntry["type"] = 'Bulk'
                            logEntry["file"] = ''
                            jobIdStrip = lineSplitAgain[0].strip('\r\n')
                            jobIdStrip = jobIdStrip.strip()
                            logEntry["jobid"] = jobIdStrip
                            batchIdStrip = lineSplitAgain[1].strip('\r\n')
                            batchIdStrip = batchIdStrip.strip()
                            logEntry["batchid"] = batchIdStrip
                            logEntry["targetname"] = target
                            logEntry["pathname"] = pathString
                            self.logList[jobIdStrip] = logEntry
                wx.CallAfter(self.OnText, line)
        wx.CallAfter(self.SetButtonState, True)

    def RefreshLog(self, event):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        if len(self.logList) == 0:
            return
        self.consoleOutputTextCtrl.AppendText(
            '----------------------------------------------------------------------------------')
        self.consoleOutputTextCtrl.AppendText(os.linesep)
        self.consoleOutputTextCtrl.AppendText(
            'Refresh log started at: ' + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        self.consoleOutputTextCtrl.AppendText(os.linesep)
        waitMinutes = '0'
        self.SetButtonState(False)
        thread = threading.Thread(target=self.RunRefreshLog, args=(waitMinutes))
        thread.setDaemon(True)
        thread.start()

    def RunRefreshLog(self, waitMinutes):
        if self.stop:
            self.consoleOutputTextCtrl.AppendText("Process stopped.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            return
        for jobId in self.logList:
            log = self.logList[jobId]
            type, file, jobId, batchId, targetName, pathName = log["type"], log["file"], log["jobid"], log["batchid"], \
                                                               log["targetname"], log["pathname"]
            if type == 'Retrieve':
                cmd = ['sfdx', 'force:mdapi:retrieve:report', '--apiversion', dtkglobal.defaultApiVersion, '-u',
                       targetName,
                       '-i', jobId, '-r', pathName, '-w', waitMinutes]
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
                for line in proc.stdout:
                    wx.CallAfter(self.OnText, line)
            if type == 'Deploy':
                cmd = ['sfdx', 'force:mdapi:deploy:report', '--apiversion', dtkglobal.defaultApiVersion, '-u',
                       targetName,
                       '-i', jobId]
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
                for line in proc.stdout:
                    wx.CallAfter(self.OnText, line)
            if type == 'Bulk':
                cmd = ['sfdx', 'force:data:bulk:status', '--apiversion', dtkglobal.defaultApiVersion, '-u', targetName,
                       '-i', jobId, '-b', batchId]
                proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
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
        self.organizationComboBox.Bind(wx.EVT_TEXT, self.OrganizationSelected)

        if dtkglobal.unlockSetting:
            self.sandboxTypeSourceLbl = wx.StaticText(self.panel, label="Source")
            self.sandboxTypeSourceLbl.ToolTip = "Sandbox Type: Config, QA, UAT or Prod."
            self.sandboxTypeSourceComboBox = wx.ComboBox(self.panel, style=wx.CB_READONLY)
            self.sandboxTypeSourceComboBox.ToolTip = "Sandbox Type: Config, QA, UAT or Prod."
            self.sandboxTypeSourceComboBox.Bind(wx.EVT_TEXT, self.SourceSelected)
            self.sandboxTypeSourceComboBox.Enable(False)

        self.nb = wx.Notebook(self.panel)
        self.nb.AddPage(RetrieveMetadataPanel(self.nb, retrieveType='Metadata Retrieve'), "Metadata")
        self.nb.AddPage(ExportDataPanel(self.nb), "Export Data")

        self.mainSizer.Add(self.organizationLbl, pos=(row, col), flag= wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(self.organizationComboBox, pos=(row, col + 1), span=(0, 3),
                      flag= wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        row += 1

        if dtkglobal.unlockSetting:
            self.mainSizer.Add(self.sandboxTypeSourceLbl, pos=(row, col), flag= wx.TOP | wx.LEFT | wx.RIGHT, border=5)
            self.mainSizer.Add(self.sandboxTypeSourceComboBox, pos=(row, col + 1), span=(0, 3),
                          flag= wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
            row += 1

        self.mainSizer.Add(self.nb, pos=(row, col), span=(0, 6),
                      flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)

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
        self.Show()

    def OrganizationSelected(self, event):
        orgName = self.organizationComboBox.GetValue()
        self.sandboxTypeSourceComboBox.Enable(False)
        if len(orgName) == 0:
            self.sandboxTypeSourceComboBox.Clear()
        if orgName in dtkglobal.orgDict:
            sandboxList = dtkglobal.orgDict[orgName]["sandboxes"]
            sandboxList.sort()
            if dtkglobal.unlockSetting:
                self.sandboxTypeSourceComboBox.Items = sandboxList
            self.Title = 'Retrieve: ' + orgName
            self.sandboxTypeSourceComboBox.Enable(True)

    def SourceSelected(self, event):
        orgName = self.organizationComboBox.GetValue()
        sdbxName = self.sandboxTypeSourceComboBox.GetValue()
        if len(orgName) == 0:
            dlg = wx.MessageDialog(self,
                                   "Please select an organization.",
                                   "DTK - Retrieve", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if self.currentTarget == orgName + '_' + sdbxName:
            return
        else:
            if self.currentTarget in dtkglobal.targets:
                dtkglobal.targets.remove(self.currentTarget)
            if self.currentWorkspace in dtkglobal.workspaces:
                dtkglobal.workspaces.remove(self.currentWorkspace)
        self.currentTarget = orgName + '_' + sdbxName
        if self.currentTarget in dtkglobal.targets:
            i = 1
            exit = False
            if (os.path.join(os.path.expanduser('~'), '.dtk', self.currentTarget) not in dtkglobal.workspaces):
                self.currentWorkspace = os.path.join(os.path.expanduser('~'), '.dtk', self.currentTarget)
                exit = True
            while not exit:
                if (os.path.join(os.path.expanduser('~'), '.dtk', self.currentTarget + '_' + str(i)) not in dtkglobal.workspaces):
                    self.currentWorkspace = os.path.join(os.path.expanduser('~'), '.dtk', self.currentTarget + '_' + str(i))
                    exit = True
                else:
                    i += 1
        else:
            self.currentWorkspace = os.path.join(os.path.expanduser('~'), '.dtk', self.currentTarget)
        dtkglobal.targets.append(self.currentTarget)
        dtkglobal.workspaces.append(self.currentWorkspace)
        if not os.path.exists(self.currentWorkspace):
            os.makedirs(self.currentWorkspace)
        self.nb.GetPage(0).consoleOutputTextCtrl.AppendText('Workspace changed to: ' + self.currentWorkspace)
        self.nb.GetPage(0).consoleOutputTextCtrl.AppendText(os.linesep)
        self.nb.GetPage(1).consoleOutputTextCtrl.AppendText('Workspace changed to: ' + self.currentWorkspace)
        self.nb.GetPage(1).consoleOutputTextCtrl.AppendText(os.linesep)
        self.Title = 'Retrieve: ' + orgName + ' - ' + sdbxName

    def OnCloseWindow(self, event):
        if self.currentTarget in dtkglobal.targets:
            dtkglobal.targets.remove(self.currentTarget)
        if self.currentWorkspace in dtkglobal.workspaces:
            dtkglobal.workspaces.remove(self.currentWorkspace)
        self.Destroy()