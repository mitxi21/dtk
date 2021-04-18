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

import os
import platform
import subprocess
import threading

import dtkglobal
import wx


class AddSandboxPanel(wx.Panel):
    def __init__(self, parent):
        super(AddSandboxPanel, self).__init__(parent)

        self.InitUI()

    def InitUI(self):
        self.mainSizer = wx.GridBagSizer(5, 5)

        self.organizationLbl = wx.StaticText(self, label="Organization")
        self.organizationLbl.ToolTip = "List of Organizations available."
        self.organizationComboBox = wx.ComboBox(self, style=wx.CB_READONLY)
        self.organizationComboBox.ToolTip = "List of Organizations available."
        self.organizationComboBox.Items = dtkglobal.orgList

        self.sandboxTypeLbl = wx.StaticText(self, label="Sandbox Type")
        self.sandboxTypeLbl.ToolTip = "Sandbox Type: Config, QA, UAT or Prod."
        self.sandboxTypeComboBox = wx.ComboBox(self, style=wx.CB_READONLY)
        self.sandboxTypeComboBox.ToolTip = "Sandbox Type: Config, QA, UAT or Prod."
        self.sandboxTypeComboBox.Items = dtkglobal.defaultSandboxTypes

        if dtkglobal.advSetting:
            self.sandboxOverrideLbl = wx.StaticText(self, label="Sandbox Override Name")
            self.sandboxOverrideLbl.ToolTip = "The sandbox name set here will be added instead of the Sandbox Type."
            self.sandboxOverrideTextCtrl = wx.TextCtrl(self)
            self.sandboxOverrideTextCtrl.ToolTip = (
                "The sandbox name set here will be added instead of the Sandbox Type."
            )

        self.btnShowSfdxAliasList = wx.Button(self, label="Show SFDX Alias List")
        self.btnShowSfdxAliasList.Bind(wx.EVT_BUTTON, self.ShowSfdxAliasList)

        self.btnAddSandbox = wx.Button(self, label="Add Sandbox")
        self.btnAddSandbox.Bind(wx.EVT_BUTTON, self.AddSandboxButton)

        self.consoleOutputLbl = wx.StaticText(self, label="Log")
        self.consoleOutputLbl.ToolTip = "Console output log."
        self.consoleOutputTextCtrl = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_AUTO_URL | wx.HSCROLL
        )
        self.consoleOutputTextCtrl.ToolTip = "Console output log."

        row = 0
        col = 0
        spanV = 0
        spanH = 15

        self.mainSizer.Add(self.organizationLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.organizationComboBox,
            pos=(row, col + 1),
            span=(spanV, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        self.mainSizer.Add(self.sandboxTypeLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.sandboxTypeComboBox,
            pos=(row, col + 1),
            span=(spanV, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        if dtkglobal.advSetting:
            self.mainSizer.Add(
                self.sandboxOverrideLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
            )
            self.mainSizer.Add(
                self.sandboxOverrideTextCtrl,
                pos=(row, col + 1),
                span=(spanV, spanH),
                flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
                border=5,
            )
            row += 1

        self.mainSizer.Add(self.btnShowSfdxAliasList, pos=(row, 0), flag=wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.btnAddSandbox, pos=(row, col + 15), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        row += 1
        self.mainSizer.Add(
            self.consoleOutputLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        row += 1
        self.mainSizer.Add(
            self.consoleOutputTextCtrl,
            pos=(row, col),
            span=(spanV + 10, spanH + 1),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        self.mainSizer.AddGrowableCol(2)
        self.mainSizer.AddGrowableRow(row)
        self.mainSizer.SetEmptyCellSize((0, 0))
        self.Layout()
        self.Fit()
        self.SetSizer(self.mainSizer)

    def ShowSfdxAliasList(self, event):
        cmd = ["sfdx", "force:alias:list"]
        if (platform.system() != "Windows"):
            cmd = ["/usr/local/bin/sfdx" + " " + "force:alias:list"]
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
        )
        self.consoleOutputTextCtrl.AppendText(proc.stdout.read())
        self.consoleOutputTextCtrl.AppendText(os.linesep)

    def AddSandboxButton(self, event):
        self.consoleOutputTextCtrl.Clear()
        orgName = self.organizationComboBox.GetValue()
        sdbxName = self.sandboxTypeComboBox.GetValue()
        if dtkglobal.advSetting:
            sandboxOverride = self.sandboxOverrideTextCtrl.GetValue()
            if len(sandboxOverride) > 0:
                sdbxName = sandboxOverride
        if len(orgName) == 0:
            dlg = wx.MessageDialog(self, "Please select an organization.", "DTK - Organizations", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(sdbxName) == 0:
            dlg = wx.MessageDialog(self, "Please select a sandbox.", "DTK - Organizations", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        sdbxName = sdbxName.rstrip()
        sdbxName = sdbxName.replace(" ", "_")
        sandboxName = orgName + "_" + sdbxName
        if sdbxName in dtkglobal.orgDict[orgName]["sandboxes"]:
            dlg = wx.MessageDialog(
                self,
                "The sandbox '"
                + sdbxName
                + "' already exist for organization '"
                + orgName
                + "', please choose another sandbox.",
                "DTK - Add Sandbox",
                wx.OK | wx.ICON_ERROR,
            )
            dlg.ShowModal()
            dlg.Destroy()
        else:
            if sdbxName == "Prod":
                serverUrl = "https://login.salesforce.com"
            else:
                serverUrl = "https://test.salesforce.com"
            self.consoleOutputTextCtrl.AppendText(
                "Adding sandbox '" + sdbxName + "' for organization '" + orgName + "'."
            )
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            self.consoleOutputTextCtrl.AppendText("This needs an online login on the browser to complete the addition.")
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            self.consoleOutputTextCtrl.AppendText(
                "If the browser is closed without doing the login the sandbox won't be added."
            )
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            thread = threading.Thread(target=self.RunAddSandbox, args=(orgName, sdbxName, sandboxName, serverUrl))
            thread.setDaemon(True)
            thread.start()

    def OnText(self, text):
        self.consoleOutputTextCtrl.AppendText(text)

    def RunAddSandbox(self, orgName, sdbxName, sandboxName, serverUrl):
        cmd = ["sfdx", "force:auth:web:login", "-a", sandboxName, "-r", serverUrl]
        if (platform.system() != "Windows"):
            cmd = ["/usr/local/bin/sfdx" + " " + "force:auth:web:login" + " " + "-a" + " " + sandboxName + " " + "-r" + " " + serverUrl]
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
        )
        for line in proc.stdout:
            wx.CallAfter(self.OnText, line)
        dtkglobal.orgDict[orgName]["sandboxes"].append(sdbxName)
        dtkglobal.StoreOrgs()
        dtkglobal.ReadOrgs()
        sandboxList = dtkglobal.orgDict[orgName]["sandboxes"]
        sandboxList.sort()
        self.Parent.GetPage(0).sandboxesListBox.Items = sandboxList


class ManageSandboxPanel(wx.Panel):
    def __init__(self, parent):
        super(ManageSandboxPanel, self).__init__(parent)

        self.InitUI()

    def InitUI(self):
        self.mainSizer = wx.GridBagSizer(1, 1)

        self.organizationLbl = wx.StaticText(self, label="Organization")
        self.organizationLbl.ToolTip = "List of Organizations available."
        self.organizationComboBox = wx.ComboBox(self, style=wx.CB_READONLY)
        self.organizationComboBox.ToolTip = "List of Organizations available."
        self.organizationComboBox.Items = dtkglobal.orgList
        self.organizationComboBox.Bind(wx.EVT_COMBOBOX, self.OrganizationSelected)

        self.sandboxesLbl = wx.StaticText(self, label="Sandboxes")
        self.sandboxesLbl.ToolTip = "List of Sandboxes available."
        self.sandboxesListBox = wx.ListBox(self)
        self.sandboxesListBox.ToolTip = "List of Sandboxes available."

        self.btnOpenSandbox = wx.Button(self, label="Open")
        self.btnOpenSandbox.Bind(wx.EVT_BUTTON, self.OpenSandboxButton)

        self.btnDeleteSandbox = wx.Button(self, label="Delete Sandbox")
        self.btnDeleteSandbox.Bind(wx.EVT_BUTTON, self.DeleteSandboxButton)

        row = 0
        col = 0
        spanV = 0
        spanH = 18

        self.mainSizer.Add(self.organizationLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.organizationComboBox,
            pos=(row, col + 1),
            span=(spanV, spanH - 1),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        self.mainSizer.Add(self.sandboxesLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        row += 1
        self.mainSizer.Add(
            self.sandboxesListBox,
            pos=(row, col),
            span=(spanV + 10, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 10

        self.mainSizer.Add(self.btnOpenSandbox, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.btnDeleteSandbox, pos=(row, col + spanH - 1), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.mainSizer.AddGrowableCol(2)
        self.mainSizer.AddGrowableRow(row - 1)
        self.mainSizer.SetEmptyCellSize((0, 0))
        self.Layout()
        self.Fit()
        self.SetSizer(self.mainSizer)

    def OrganizationSelected(self, event):
        orgName = self.organizationComboBox.GetValue()
        if orgName in dtkglobal.orgDict:
            sandboxList = dtkglobal.orgDict[orgName]["sandboxes"]
            sandboxList.sort()
            self.sandboxesListBox.Items = sandboxList

    def OpenSandboxButton(self, event):
        orgName = self.organizationComboBox.GetValue()
        if len(orgName) == 0:
            dlg = wx.MessageDialog(self, "Please select an organization.", "DTK - Organizations", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if self.sandboxesListBox.GetSelection() == -1:
            dlg = wx.MessageDialog(self, "Please select a sandbox.", "DTK - Organizations", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        sdbxName = self.sandboxesListBox.GetString(self.sandboxesListBox.GetSelection())
        sandboxName = orgName + "_" + sdbxName
        thread = threading.Thread(target=self.RunOpenSandbox, args=(sandboxName,))
        thread.setDaemon(True)
        thread.start()

    def RunOpenSandbox(self, sandboxName):
        cmd = ["sfdx", "force:org:open", "-u", sandboxName]
        if (platform.system() != "Windows"):
            cmd = ["/usr/local/bin/sfdx" + " " + "force:org:open" + " " + "-u" + " " + sandboxName]
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
        )
        directory = os.path.join(os.path.expanduser("~"), ".dtk", "log")
        if not os.path.exists(directory):
            os.makedirs(directory)
        outputFileUrl = os.path.join(directory, "output.log")
        outputFile = open(outputFileUrl, "wb")
        outputFile.write(proc.stdout.read())
        outputFile.close()
        fileOutput = open(outputFileUrl, "r", encoding="utf8")
        for line in fileOutput:
            if "ERROR" in line:
                dlg = wx.MessageDialog(self, line + "\nPlease remove the sandbox and register it again.", "DTK - Organizations", wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                break

    def DeleteSandboxButton(self, event):
        orgName = self.organizationComboBox.GetValue()
        if len(orgName) == 0:
            dlg = wx.MessageDialog(self, "Please select an organization.", "DTK - Organizations", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if self.sandboxesListBox.GetSelection() == -1:
            dlg = wx.MessageDialog(self, "Please select a sandbox.", "DTK - Organizations", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        sdbxName = self.sandboxesListBox.GetString(self.sandboxesListBox.GetSelection())
        sandboxName = orgName + "_" + sdbxName
        dlg = wx.MessageDialog(
            self,
            "The sandbox '"
            + sdbxName
            + "' from organization '"
            + orgName
            + "' will be removed from DTK. Please confirm.",
            "DTK - Delete Sandbox",
            wx.YES_NO | wx.ICON_WARNING,
        )
        result = dlg.ShowModal()
        if result == wx.ID_YES:
            thread = threading.Thread(target=self.RunDeleteSandbox, args=(orgName, sdbxName, sandboxName))
            thread.setDaemon(True)
            thread.start()
        dlg.Destroy()

    def RunDeleteSandbox(self, orgName, sdbxName, sandboxName):
        cmd = ["sfdx", "force:alias:set", sandboxName + "="]
        if (platform.system() != "Windows"):
            cmd = ["/usr/local/bin/sfdx" + " " + "force:alias:set" + " " + sandboxName + "="]
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE
        )
        directory = os.path.join(os.path.expanduser("~"), ".dtk", "log")
        if not os.path.exists(directory):
            os.makedirs(directory)
        outputFileUrl = os.path.join(directory, "output.log")
        outputFile = open(outputFileUrl, "wb")
        outputFile.write(proc.stdout.read())
        outputFile.close()
        dtkglobal.orgDict[orgName]["sandboxes"].remove(sdbxName)
        dtkglobal.StoreOrgs()
        dtkglobal.ReadOrgs()
        sandboxList = dtkglobal.orgDict[orgName]["sandboxes"]
        sandboxList.sort()
        self.sandboxesListBox.Items = sandboxList
        self.Layout()


class ManageOrganizationPanel(wx.Panel):
    def __init__(self, parent):
        super(ManageOrganizationPanel, self).__init__(parent)

        self.InitUI()

    def InitUI(self):
        self.mainSizer = wx.GridBagSizer(5, 5)

        self.organizationLbl = wx.StaticText(self, label="Organizations")
        self.organizationLbl.ToolTip = "List of Organizations available."
        self.organizationListBox = wx.ListBox(self)
        self.organizationListBox.ToolTip = "List of Organizations available."
        self.organizationListBox.Items = dtkglobal.orgList
        self.organizationListBox.Bind(wx.EVT_LISTBOX, self.SelectOrganization)

        self.gitUrlLbl = wx.StaticText(self, label="Git URL")
        self.gitUrlLbl.ToolTip = "Git URL linked with the Organization."
        self.gitUrlTextCtrl = wx.TextCtrl(self)
        self.gitUrlTextCtrl.ToolTip = "Git URL linked with the Organization."

        self.gitUserLbl = wx.StaticText(self, label="Git Username")
        self.gitUserLbl.ToolTip = "Git Username."
        self.gitUserTextCtrl = wx.TextCtrl(self)
        self.gitUserTextCtrl.ToolTip = "Git Username."

        self.gitPassLbl = wx.StaticText(self, label="Git Password")
        self.gitPassLbl.ToolTip = "Git Password. If you have a 2 factor authentication git server then you need to set here the granted token generated."
        self.gitPassTextCtrl = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        self.gitPassTextCtrl.ToolTip = "Git Password. If you have a 2 factor authentication git server then you need to set here the granted token generated."

        self.metadataFolderLbl = wx.StaticText(self, label="Metadata Folder")
        self.metadataFolderLbl.ToolTip = "Metadata Folder."
        self.metadataFolderTextCtrl = wx.TextCtrl(self)
        self.metadataFolderTextCtrl.ToolTip = "Metadata Folder."

        self.preScriptFolderLbl = wx.StaticText(self, label="Pre-deploy Script")
        self.preScriptFolderLbl.ToolTip = "Pre-deploy Script Folder."
        self.preScriptFolderTextCtrl = wx.TextCtrl(self)
        self.preScriptFolderTextCtrl.ToolTip = "Pre-deploy Script Folder."

        self.scriptFolderLbl = wx.StaticText(self, label="Post-deploy Script")
        self.scriptFolderLbl.ToolTip = "Post-deploy Script Folder."
        self.scriptFolderTextCtrl = wx.TextCtrl(self)
        self.scriptFolderTextCtrl.ToolTip = "Post-deploy Script Folder."

        self.btnUpdate = wx.Button(self, label="Update")
        self.btnUpdate.Bind(wx.EVT_BUTTON, self.UpdateButton)

        self.btnDelete = wx.Button(self, label="Delete")
        self.btnDelete.Bind(wx.EVT_BUTTON, self.DeleteButton)

        row = 0
        col = 0
        spanV = 0
        spanH = 18

        self.mainSizer.Add(self.organizationLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.organizationListBox,
            pos=(row, col + 1),
            span=(spanV + 10, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 10

        self.mainSizer.Add(self.gitUrlLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.gitUrlTextCtrl,
            pos=(row, col + 1),
            span=(spanV, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        self.mainSizer.Add(self.gitUserLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.gitUserTextCtrl,
            pos=(row, col + 1),
            span=(spanV, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        self.mainSizer.Add(self.gitPassLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.gitPassTextCtrl,
            pos=(row, col + 1),
            span=(spanV, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        self.mainSizer.Add(
            self.metadataFolderLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.mainSizer.Add(
            self.metadataFolderTextCtrl,
            pos=(row, col + 1),
            span=(spanV, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        self.mainSizer.Add(self.preScriptFolderLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.preScriptFolderTextCtrl,
            pos=(row, col + 1),
            span=(spanV, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        self.mainSizer.Add(self.scriptFolderLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.scriptFolderTextCtrl,
            pos=(row, col + 1),
            span=(spanV, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        self.mainSizer.Add(self.btnUpdate, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.btnDelete, pos=(row, col + spanH), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.mainSizer.AddGrowableCol(2)
        self.mainSizer.SetEmptyCellSize((0, 0))
        self.Layout()
        self.Fit()
        self.SetSizer(self.mainSizer)

    def SelectOrganization(self, event):
        sdbxName = self.organizationListBox.GetString(self.organizationListBox.GetSelection())
        self.gitUrlTextCtrl.Clear()
        self.gitUserTextCtrl.Clear()
        self.gitPassTextCtrl.Clear()
        self.metadataFolderTextCtrl.Clear()
        self.preScriptFolderTextCtrl.Clear()
        self.scriptFolderTextCtrl.Clear()
        if sdbxName in dtkglobal.orgDict:
            if len(dtkglobal.orgDict[sdbxName]["giturl"]) > 0:
                self.gitUrlTextCtrl.WriteText(dtkglobal.orgDict[sdbxName]["giturl"])
            if len(dtkglobal.orgDict[sdbxName]["gituser"]) > 0:
                self.gitUserTextCtrl.WriteText(dtkglobal.orgDict[sdbxName]["gituser"])
                if len(dtkglobal.orgDict[sdbxName]["gitpass"]) > 0:
                    gitpassDecoded = dtkglobal.Decode(
                        dtkglobal.orgDict[sdbxName]["gituser"], dtkglobal.orgDict[sdbxName]["gitpass"]
                    )
                    self.gitPassTextCtrl.WriteText(gitpassDecoded)
            if len(dtkglobal.orgDict[sdbxName]["metadatafolder"]) > 0:
                self.metadataFolderTextCtrl.WriteText(dtkglobal.orgDict[sdbxName]["metadatafolder"])
            if "preScript" in dtkglobal.orgDict[sdbxName]:
                if len(dtkglobal.orgDict[sdbxName]["preScript"]) > 0:
                    self.preScriptFolderTextCtrl.WriteText(dtkglobal.orgDict[sdbxName]["preScript"])
            if len(dtkglobal.orgDict[sdbxName]["script"]) > 0:
                self.scriptFolderTextCtrl.WriteText(dtkglobal.orgDict[sdbxName]["script"])

    def UpdateButton(self, event):
        if self.organizationListBox.GetSelection() == -1:
            dlg = wx.MessageDialog(self, "Please select an organization.", "DTK - Organizations", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        sdbxName = self.organizationListBox.GetString(self.organizationListBox.GetSelection())
        if sdbxName in dtkglobal.orgDict:
            dtkglobal.orgDict[sdbxName]["giturl"] = self.gitUrlTextCtrl.GetValue()
            dtkglobal.orgDict[sdbxName]["gituser"] = self.gitUserTextCtrl.GetValue()
            gitpassEncoded = dtkglobal.Encode(self.gitUserTextCtrl.GetValue(), self.gitPassTextCtrl.GetValue())
            dtkglobal.orgDict[sdbxName]["gitpass"] = gitpassEncoded
            dtkglobal.orgDict[sdbxName]["metadatafolder"] = self.metadataFolderTextCtrl.GetValue()
            dtkglobal.orgDict[sdbxName]["preScript"] = self.preScriptFolderTextCtrl.GetValue()
            dtkglobal.orgDict[sdbxName]["script"] = self.scriptFolderTextCtrl.GetValue()
            dtkglobal.StoreOrgs()
            dlg = wx.MessageDialog(
                self,
                "The organization '" + sdbxName + "' has been updated.",
                "DTK - Update Organization",
                wx.OK | wx.ICON_INFORMATION,
            )
            dlg.ShowModal()
            dlg.Destroy()

    def DeleteButton(self, event):
        if self.organizationListBox.GetSelection() == -1:
            dlg = wx.MessageDialog(self, "Please select an organization.", "DTK - Organizations", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        sdbxName = self.organizationListBox.GetString(self.organizationListBox.GetSelection())
        if sdbxName in dtkglobal.orgDict:
            if len(dtkglobal.orgDict[sdbxName]["sandboxes"]) > 0:
                dlg = wx.MessageDialog(
                    self,
                    "The organization '"
                    + sdbxName
                    + "' can't be deleted, please remove first the sandboxes linked to this organization.",
                    "DTK - Delete Organization",
                    wx.OK | wx.ICON_ERROR,
                )
                dlg.ShowModal()
                dlg.Destroy()
            else:
                dlg = wx.MessageDialog(
                    self,
                    "The organization '" + sdbxName + "' will be deleted from DTK. Please confirm.",
                    "DTK - Delete Organization",
                    wx.YES_NO | wx.ICON_WARNING,
                )
                result = dlg.ShowModal()
                if result == wx.ID_YES:
                    dtkglobal.orgDict.pop(sdbxName)
                    dtkglobal.StoreOrgs()
                    dtkglobal.ReadOrgs()
                    self.Parent.GetPage(0).organizationComboBox.Items = dtkglobal.orgList
                    self.Parent.GetPage(1).organizationComboBox.Items = dtkglobal.orgList
                    self.Parent.GetPage(2).organizationListBox.Items = dtkglobal.orgList
                    self.Layout()
                dlg.Destroy()


class AddOrganizationPanel(wx.Panel):
    def __init__(self, parent):
        super(AddOrganizationPanel, self).__init__(parent)
        self.InitUI()

    def InitUI(self):
        self.mainSizer = wx.GridBagSizer(5, 5)

        self.organizationLbl = wx.StaticText(self, label="Organization")
        self.organizationLbl.ToolTip = "List of Organizations available."
        self.organizationTextCtrl = wx.TextCtrl(self)
        self.organizationTextCtrl.ToolTip = "List of Organizations available."

        self.gitUrlLbl = wx.StaticText(self, label="Git URL")
        self.gitUrlLbl.ToolTip = "Git URL linked with the Organization."
        self.gitUrlTextCtrl = wx.TextCtrl(self)
        self.gitUrlTextCtrl.ToolTip = "Git URL linked with the Organization."

        self.gitUserLbl = wx.StaticText(self, label="Git Username")
        self.gitUserLbl.ToolTip = "Git Username."
        self.gitUserTextCtrl = wx.TextCtrl(self)
        self.gitUserTextCtrl.ToolTip = "Git Username."

        self.gitPassLbl = wx.StaticText(self, label="Git Password")
        self.gitPassLbl.ToolTip = "Git Password. If you have a 2 factor authentication git server then you need to set here the granted token generated."
        self.gitPassTextCtrl = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        self.gitPassTextCtrl.ToolTip = "Git Password. If you have a 2 factor authentication git server then you need to set here the granted token generated."

        self.metadataFolderLbl = wx.StaticText(self, label="Metadata Folder")
        self.metadataFolderLbl.ToolTip = "Metadata Folder."
        self.metadataFolderTextCtrl = wx.TextCtrl(self)
        self.metadataFolderTextCtrl.ToolTip = "Metadata Folder."
        self.metadataFolderTextCtrl.AppendText(dtkglobal.defaultMetadataFolder)

        self.preScriptFolderLbl = wx.StaticText(self, label="Pre-deploy Script")
        self.preScriptFolderLbl.ToolTip = "Pre-deploy Script Folder."
        self.preScriptFolderTextCtrl = wx.TextCtrl(self)
        self.preScriptFolderTextCtrl.ToolTip = "Pre-deploy Script Folder."
        self.preScriptFolderTextCtrl.AppendText(dtkglobal.defaultPreScriptFolder)

        self.scriptFolderLbl = wx.StaticText(self, label="Post-deploy Script")
        self.scriptFolderLbl.ToolTip = "Post-deploy Script Folder."
        self.scriptFolderTextCtrl = wx.TextCtrl(self)
        self.scriptFolderTextCtrl.ToolTip = "Post-deploy Script Folder."
        self.scriptFolderTextCtrl.AppendText(dtkglobal.defaultScriptFolder)

        self.btnAddOrganization = wx.Button(self, label="Add Organization")
        self.btnAddOrganization.Bind(wx.EVT_BUTTON, self.AddOrganizationButton)

        self.consoleOutputLbl = wx.StaticText(self, label="Log")
        self.consoleOutputLbl.ToolTip = "Console output log."
        self.consoleOutputTextCtrl = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_AUTO_URL | wx.HSCROLL
        )
        self.consoleOutputTextCtrl.ToolTip = "Console output log."

        row = 0
        col = 0
        spanV = 0
        spanH = 19

        self.mainSizer.Add(self.organizationLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.organizationTextCtrl,
            pos=(row, col + 1),
            span=(spanV, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        self.mainSizer.Add(self.gitUrlLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.gitUrlTextCtrl,
            pos=(row, col + 1),
            span=(spanV, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        self.mainSizer.Add(self.gitUserLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.gitUserTextCtrl,
            pos=(row, col + 1),
            span=(spanV, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        self.mainSizer.Add(self.gitPassLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.gitPassTextCtrl,
            pos=(row, col + 1),
            span=(spanV, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        self.mainSizer.Add(
            self.metadataFolderLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.mainSizer.Add(
            self.metadataFolderTextCtrl,
            pos=(row, col + 1),
            span=(spanV, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        self.mainSizer.Add(self.preScriptFolderLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.preScriptFolderTextCtrl,
            pos=(row, col + 1),
            span=(spanV, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        self.mainSizer.Add(self.scriptFolderLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.scriptFolderTextCtrl,
            pos=(row, col + 1),
            span=(spanV, spanH),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        self.mainSizer.Add(
            self.btnAddOrganization, pos=(row, col + spanH), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        row += 1
        self.mainSizer.Add(
            self.consoleOutputLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        row += 1
        self.mainSizer.Add(
            self.consoleOutputTextCtrl,
            pos=(row, col),
            span=(spanV + 9, spanH + 2),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        self.mainSizer.AddGrowableCol(2)
        self.mainSizer.AddGrowableRow(row)
        self.mainSizer.SetEmptyCellSize((0, 0))
        self.Layout()
        self.Fit()
        self.SetSizer(self.mainSizer)

    def AddOrganizationButton(self, event):
        sdbxName = self.organizationTextCtrl.GetLineText(0)
        sdbxName = sdbxName.rstrip()
        sdbxName = sdbxName.replace(" ", "_")
        if len(sdbxName) == 0:
            dlg = wx.MessageDialog(
                self, "Please select an organization name.", "DTK - Organizations", wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return
        giturl = self.gitUrlTextCtrl.GetLineText(0)
        gituser = self.gitUserTextCtrl.GetLineText(0)
        gitpass = self.gitPassTextCtrl.GetLineText(0)
        metadatafolder = self.metadataFolderTextCtrl.GetLineText(0)
        preScript = self.preScriptFolderTextCtrl.GetLineText(0)
        script = self.scriptFolderTextCtrl.GetLineText(0)
        gitpassEncoded = dtkglobal.Encode(gituser, gitpass)
        if sdbxName in dtkglobal.orgDict:
            dlg = wx.MessageDialog(
                self,
                "The organization '" + sdbxName + "' already exist, please choose another name",
                "DTK - Add Organization.",
                wx.OK | wx.ICON_ERROR,
            )
            dlg.ShowModal()
            dlg.Destroy()
        else:
            sdbxConf = {}
            sdbxConf["sandboxes"] = []
            sdbxConf["giturl"] = giturl
            sdbxConf["gituser"] = gituser
            sdbxConf["gitpass"] = gitpassEncoded
            sdbxConf["metadatafolder"] = metadatafolder
            sdbxConf["preScript"] = preScript
            sdbxConf["script"] = script
            dtkglobal.orgDict[sdbxName] = sdbxConf
            dtkglobal.StoreOrgs()
            self.consoleOutputTextCtrl.AppendText("Organization added with name: " + sdbxName)
            self.consoleOutputTextCtrl.AppendText(os.linesep)
            dtkglobal.ReadOrgs()
            self.Parent.GetPage(0).organizationComboBox.Items = dtkglobal.orgList
            self.Parent.GetPage(1).organizationComboBox.Items = dtkglobal.orgList
            self.Parent.GetPage(2).organizationListBox.Items = dtkglobal.orgList


class ManageOrgsFrame(wx.Frame):
    def __init__(self, parent=None):
        super(ManageOrgsFrame, self).__init__(parent, title="Organizations")
        myStream = dtkglobal.getImageStream()
        myImage = wx.Image(myStream)
        myBitmap = wx.Bitmap(myImage)
        icon = wx.Icon()
        icon.CopyFromBitmap(myBitmap)
        self.SetIcon(icon)
        # dtkglobal.MakeModal(self, True)
        self.InitUI()

    def InitUI(self):
        self.panel = wx.Panel(self)
        self.nb = wx.Notebook(self.panel)
        self.nb.AddPage(ManageSandboxPanel(self.nb), "Manage Sandboxes")
        self.nb.AddPage(AddSandboxPanel(self.nb), "Add Sandbox")
        self.nb.AddPage(ManageOrganizationPanel(self.nb), "Manage Organizations")
        self.nb.AddPage(AddOrganizationPanel(self.nb), "Add Organization")

        self.mainSizer = wx.GridBagSizer(5, 5)

        row = 0
        col = 0
        spanV = 0
        spanH = 2

        self.mainSizer.Add(self.nb, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)

        self.mainSizer.AddGrowableCol(0)
        self.mainSizer.AddGrowableRow(0)
        self.panel.SetSizerAndFit(self.mainSizer)
        self.mainSizer.Fit(self)
        self.Layout()

        self.Centre()
        self.MinSize = self.Size
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Show()

    def OnCloseWindow(self, event):
        self.Destroy()
