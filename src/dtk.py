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

import dtkdeploy
import dtkdeployAccelerate
import dtkglobal
import dtkorg
import dtkretrieve
import dtkmdtemplates
import dtkqueries
import tempfile
import ctypes
import os
import wx

pid_file = tempfile.gettempdir() + "tmp_armor_pid.txt"


class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MainFrame, self).__init__(parent, title=title)

        myStream = dtkglobal.getImageStream()
        myImage = wx.Image(myStream)
        myBitmap = wx.Bitmap(myImage)
        icon = wx.Icon()
        icon.CopyFromBitmap(myBitmap)
        self.SetIcon(icon)
        dtkglobal.LoadSettings()
        dtkglobal.LoadOrganizations()
        dtkglobal.LoadMetadataTemplates()
        dtkglobal.LoadSOQLTemplates()
        self.InitUI()
        self.Centre()

    def InitUI(self):

        panel = wx.Panel(self)

        mainSizer = wx.GridBagSizer(5, 5)
        environmentsLbl = wx.StaticBox(panel, -1, "Org Management:")
        environmentSizer = wx.StaticBoxSizer(environmentsLbl, wx.VERTICAL)

        btnManageSandbox = wx.Button(panel, label="Organizations")
        btnManageSandbox.Bind(wx.EVT_BUTTON, self.ManageSandboxButton)

        environmentSizer.Add(btnManageSandbox, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=5)

        releaseLbl = wx.StaticBox(panel, -1, "Release Management:")
        releaseSizer = wx.StaticBoxSizer(releaseLbl, wx.VERTICAL)

        btnRetrieve = wx.Button(panel, label="Retrieve")
        btnRetrieve.Bind(wx.EVT_BUTTON, self.RetrieveButton)

        btnDeploy = wx.Button(panel, label="Deploy")
        btnDeploy.Bind(wx.EVT_BUTTON, self.DeployButton)

        releaseSizer.Add(btnRetrieve, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=5)
        releaseSizer.Add(btnDeploy, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=5)

        #Show Accelerete deployment option if setting it's enabled
        if dtkglobal.accelerateEnableSetting and dtkglobal.advSetting:
            btnAccDeploy = wx.Button(panel, label="Accelerate Deploy")
            btnAccDeploy.Bind(wx.EVT_BUTTON, self.DeployAccelerateButton)
            releaseSizer.Add(btnAccDeploy, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=5)

        line = wx.StaticLine(panel)

        btnExit = wx.Button(panel, label="Exit")
        btnExit.Bind(wx.EVT_BUTTON, self.OnExit)

        row = 0
        col = 0

        mainSizer.Add(
            environmentSizer, pos=(row, col), span=(1, 5), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        row += 1
        mainSizer.Add(releaseSizer, pos=(row, col), span=(1, 5), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        row += 1
        mainSizer.Add(btnExit, pos=(row, col + 3), span=(4, 1), flag=wx.TOP | wx.BOTTOM | wx.RIGHT, border=5)

        mainSizer.AddGrowableCol(2)
        mainSizer.AddGrowableRow(2)
        self.CreateStatusBar()
        panel.SetSizer(mainSizer)
        mainSizer.Fit(self)

        # Setting up the menu.
        filemenu = wx.Menu()

        # wx.ID_ABOUT and wx.ID_EXIT are standard ids provided by wxWidgets.
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About", " Information about DTK")
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", " Exit DTK")

        editmenu = wx.Menu()
        menuSettings = editmenu.Append(wx.ID_EDIT, "&Settings", "DTK Settings")
        menuMetadataTemplates = editmenu.Append(wx.ID_ANY, "&Metadata Templates", "Manage Metadata Templates")
        menuSOQLTemplates = editmenu.Append(wx.ID_ANY, "&SOQL Templates", "Manage SOQL Templates")
        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")  # Adding the "filemenu" to the MenuBar
        menuBar.Append(editmenu, "&Edit")
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        # Set events.
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

        self.Bind(wx.EVT_MENU, self.OnSettings, menuSettings)
        self.Bind(wx.EVT_MENU, self.OnMetadataTemplates, menuMetadataTemplates)
        self.Bind(wx.EVT_MENU, self.OnSOQLTemplates, menuSOQLTemplates)

        self.Fit()
        self.MinSize = self.Size
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Show()

    def DeployButton(self, event):
        frame = dtkdeploy.DeployFrame()

    def DeployAccelerateButton(self, event):
        event.EventObject.Disable()
        event.EventObject.SetLabel("Loading configuration...")
        readyToDeploy = dtkglobal.LoadAccelerateConfiguration()
        if readyToDeploy:
            frame = dtkdeployAccelerate.DeployFrame()
        else:
            wx.MessageBox("Error loading configuration", 'Error', wx.OK | wx.ICON_ERROR)
        event.EventObject.SetLabel("Accelerate Deploy")
        event.EventObject.Enable()

    def RetrieveButton(self, event):
        frame = dtkretrieve.RetrieveFrame()

    def ManageSandboxButton(self, event):
        frame = dtkorg.ManageOrgsFrame()

    def OnAbout(self, e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog(self, "Version 3.2\n\nPraise The Sun!\n\nMIT License\n\nCopyright (c) 2019\n\nMiguel Perales - miguelperalesbermejo@gmail.com \nJose Manuel Caballero - jcaballeromunoz4@gmail.com\nJose Antonio Martin - ja.martin.esteban@gmail.com\nMiguel Diaz - migueldiazgil92@gmail.com\nJesus Blanco Garrido - jesusblancogarrido@gmail.com\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the 'Software'), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.", "About DTK", wx.OK)
        dlg.ShowModal()  # Show it
        dlg.Destroy()  # finally destroy it when finished.

    def OnSettings(self, e):
        frame = EditSettingsFrame()

    def OnMetadataTemplates(self, e):
        frame = dtkmdtemplates.MetadataTemplatesFrame()

    def OnSOQLTemplates(self, e):
        frame = dtkqueries.SOQLTemplatesFrame()

    def OnExit(self, e):
        self.Destroy()

    def OnCloseWindow(self, event):
        self.Destroy()


class EditSettingsFrame(wx.Dialog):
    def __init__(self, parent=None):
        wx.Dialog.__init__(self, parent=parent, title="Edit Settings")
        # dtkglobal.MakeModal(self, True)
        self.Centre()
        self.InitUI()

    def InitUI(self):

        self.panel = wx.Panel(self, wx.ID_PREFERENCES)
        self.mainSizer = wx.GridBagSizer(5, 5)

        self.advSettingLbl = wx.StaticText(self.panel, label="Use Advanced DTK")
        self.advSettingLbl.ToolTip = "Check this to display all advanced controls."
        self.advCheckBox = wx.CheckBox(self.panel)
        self.advCheckBox.ToolTip = "Check this to display all advanced controls."

        self.unlockLbl = wx.StaticText(self.panel, label="Unlock Source")
        self.unlockLbl.ToolTip = "Check this to display Source textbox."
        self.unlockCheckBox = wx.CheckBox(self.panel)
        self.unlockCheckBox.ToolTip = "Check this to display Source textbox in Deploy."

        self.unzipLbl = wx.StaticText(self.panel, label="Unzip Retrieved")
        self.unzipLbl.ToolTip = "Check this to unzip the file rerieved."
        self.unzipCheckBox = wx.CheckBox(self.panel)
        self.unzipCheckBox.ToolTip = "Check this to unzip the file rerieved."

        self.metadataTypesLbl = wx.StaticText(self.panel, label="Metadata Types")
        self.metadataTypesLbl.ToolTip = "Metadata types to be used in retrievals and deployments. Separate new additions by comma. Check Metadata type names on https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_types_list.htm"
        self.metadataTypesTextCtrl = wx.TextCtrl(self.panel)
        self.metadataTypesTextCtrl.ToolTip = "Metadata types to be used in retrievals and deployments. Separate new additions by comma. Check Metadata type names on https://developer.salesforce.com/docs/atlas.en-us.api_meta.meta/api_meta/meta_types_list.htm"

        self.defaultPackagesToExcludeLbl = wx.StaticText(self.panel, label="Prefix(es) to Exclude Package(s)")
        self.defaultPackagesToExcludeLbl.ToolTip = "Prefix of the package to exclude when retrieving metadata. Separate it by comma if more than one needs to be set."
        self.defaultPackagesToExcludeTextCtrl = wx.TextCtrl(self.panel)
        self.defaultPackagesToExcludeTextCtrl.ToolTip = "Prefix of the package to exclude when retrieving metadata. Separate it by comma if more than one needs to be set."

        self.defaultMetadataFolderLbl = wx.StaticText(self.panel, label="Default Metadata Folder")
        self.defaultMetadataFolderLbl.ToolTip = "Default metadata folder to be included when deploying from git."
        self.defaultMetadataFolderTextCtrl = wx.TextCtrl(self.panel)
        self.defaultMetadataFolderTextCtrl.ToolTip = "Default metadata folder to be included when deploying from git."

        self.defaultPreScriptFolderLbl = wx.StaticText(self.panel, label="Default Pre-deploy Data Script")
        self.defaultPreScriptFolderLbl.ToolTip = "Default pre-deploy data script to be included when deploying from git."
        self.defaultPreScriptFolderTextCtrl = wx.TextCtrl(self.panel)
        self.defaultPreScriptFolderTextCtrl.ToolTip = "Default pre-deploy data script to be included when deploying from git."

        self.defaultScriptFolderLbl = wx.StaticText(self.panel, label="Default Post-deploy Data Script")
        self.defaultScriptFolderLbl.ToolTip = "Default post-deploy data script to be included when deploying from git."
        self.defaultScriptFolderTextCtrl = wx.TextCtrl(self.panel)
        self.defaultScriptFolderTextCtrl.ToolTip = "Default post-deploy data script to be included when deploying from git."

        self.defaultApiVersionLbl = wx.StaticText(self.panel, label="Default API Version")
        self.defaultApiVersionLbl.ToolTip = "Default API version to be used in the retrieve and deploy. Execute 'sfdx force' in a terminal to see your latest version installed."
        self.defaultApiVersionCtrl = wx.TextCtrl(self.panel)
        self.defaultApiVersionCtrl.ToolTip = "Default API version to be used in the retrieve and deploy. Execute 'sfdx force' in a terminal to see your latest version installed."

        #Accelerate start
        #if dtkglobal.advSetting:
        #    self.accelerateEnableLbl = wx.StaticText(self.panel, label="Enable Accelerate Deployment")
        #    self.accelerateEnableLbl.ToolTip = "Check this to enable Accelerate deployment."
        #    self.accelerateEnableCheckBox = wx.CheckBox(self.panel)
        #    self.accelerateEnableCheckBox.ToolTip = "Check this to enable Accelerate deployment."
        #    self.accelerateGitURLLbl = wx.StaticText(self.panel, label="Accelerate Git URL")
        #    self.accelerateGitURLLbl.ToolTip = "Accelerate Git URL"
        #    self.accelerateGitURL = wx.TextCtrl(self.panel)
        #    self.accelerateGitURL.ToolTip = "Accelerate Git URL - Do not change the default value if you don't know what are you doing..."
        #    self.accelerateGitUserLbl = wx.StaticText(self.panel, label="Git User")
        #    self.accelerateGitUserLbl.ToolTip = "IQVIA GitLab user to download Accelerate configuration"
        #    self.accelerateGitUser = wx.TextCtrl(self.panel)
        #    self.accelerateGitUser.ToolTip = "IQVIA GitLab user to download Accelerate configuration"
        #    self.gitPasswordLbl = wx.StaticText(self.panel, label="Git Password")
        #    self.gitPasswordLbl.ToolTip = "IQVIA GitLab Password. If you have a 2 factor authentication git server then you need to set here the granted token generated."
        #    self.accelerateGitPassword = wx.TextCtrl(self.panel, style=wx.TE_PASSWORD)
        #    self.accelerateGitPassword.ToolTip = "IQVIA GitLab Password. If you have a 2 factor authentication git server then you need to set here the granted token generated."
        #    self.accelerateDevEnableLbl = wx.StaticText(self.panel, label="Download Accelerate Settings for developers")
        #    self.accelerateDevEnableLbl.ToolTip = "Check this to download Accelerate Settings for developers. Do not change if you dont know what you are doing."
        #    self.accelerateDevEnableCheckBox = wx.CheckBox(self.panel)
        #    self.accelerateDevEnableCheckBox.ToolTip = "Check this to download Accelerate Settings for developers. Do not enable it if you don't know what you are doing!!!"
#
        #else:
        #    self.accelerateEnableCheckBox = wx.CheckBox()
        #    self.accelerateGitURL = wx.TextCtrl(self.panel)
        #    self.accelerateGitUser = wx.TextCtrl(self.panel)
        #    self.accelerateGitPassword = wx.TextCtrl(self.panel, style=wx.TE_PASSWORD)
        #    self.accelerateDevEnableCheckBox = wx.CheckBox()
        #    self.accelerateEnableCheckBox.Hide()
        #    self.accelerateGitURL.Hide()
        #    self.accelerateGitUser.Hide()
        #    self.accelerateGitPassword.Hide()
        #Accelerate end

        self.btnSaveSettings = wx.Button(self.panel, label="Save")
        self.btnSaveSettings.Bind(wx.EVT_BUTTON, self.SaveSettings)

        self.btnCancel = wx.Button(self.panel, label="Cancel")
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnCancel)

        row = 0
        col = 0

        self.advSettingLbl.Hide()
        self.advCheckBox.Hide()
        self.unlockLbl.Hide()
        self.unlockCheckBox.Hide()

        # self.mainSizer.Add(self.advSettingLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        # self.mainSizer.Add(self.advCheckBox, pos=(row, col + 1), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        # row += 1

        # self.mainSizer.Add(self.unlockLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        # self.mainSizer.Add(self.unlockCheckBox, pos=(row, col + 1), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        # row += 1

        self.mainSizer.Add(self.unzipLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.mainSizer.Add(
            self.unzipCheckBox, pos=(row, col + 1), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        row += 1

        self.mainSizer.Add(
            self.metadataTypesLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.mainSizer.Add(
            self.metadataTypesTextCtrl,
            pos=(row, col + 1),
            span=(1, 4),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        self.mainSizer.Add(
            self.defaultPackagesToExcludeLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.mainSizer.Add(
            self.defaultPackagesToExcludeTextCtrl,
            pos=(row, col + 1),
            span=(1, 4),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        self.mainSizer.Add(
            self.defaultMetadataFolderLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.mainSizer.Add(
            self.defaultMetadataFolderTextCtrl,
            pos=(row, col + 1),
            span=(1, 4),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        self.mainSizer.Add(
            self.defaultPreScriptFolderLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.mainSizer.Add(
            self.defaultPreScriptFolderTextCtrl,
            pos=(row, col + 1),
            span=(1, 4),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        self.mainSizer.Add(
            self.defaultScriptFolderLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.mainSizer.Add(
            self.defaultScriptFolderTextCtrl,
            pos=(row, col + 1),
            span=(1, 4),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        self.mainSizer.Add(
            self.defaultApiVersionLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        self.mainSizer.Add(
            self.defaultApiVersionCtrl,
            pos=(row, col + 1),
            span=(1, 4),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row += 1

        #Accelerate start
        #if dtkglobal.advSetting:
        #    self.mainSizer.Add(self.accelerateEnableLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        #    self.mainSizer.Add(
        #        self.accelerateEnableCheckBox, pos=(row, col + 1), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        #    )
        #    row += 1
#
#
        #    self.mainSizer.Add(self.accelerateGitURLLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        #    self.mainSizer.Add(
        #        self.accelerateGitURL, pos=(row, col + 1), span=(1, 4), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        #    )
        #    row += 1
#
        #    self.mainSizer.Add(self.accelerateGitUserLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        #    self.mainSizer.Add(
        #        self.accelerateGitUser, pos=(row, col + 1), span=(1, 4), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        #    )
        #    row += 1
#
        #    self.mainSizer.Add(self.gitPasswordLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        #    self.mainSizer.Add(
        #        self.accelerateGitPassword, pos=(row, col + 1),span=(1, 4), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        #    )
        #    row += 1
#
        #    self.mainSizer.Add(self.accelerateDevEnableLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        #    self.mainSizer.Add(
        #        self.accelerateDevEnableCheckBox, pos=(row, col + 1), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        #    )
        #    row += 1
        #Accelerate end

        self.mainSizer.Add(self.btnSaveSettings, pos=(row, col + 2), span=(1, 1), flag=wx.BOTTOM | wx.RIGHT, border=5)
        self.mainSizer.Add(self.btnCancel, pos=(row, col + 3), span=(1, 1), flag=wx.BOTTOM | wx.RIGHT, border=5)

        self.mainSizer.AddGrowableCol(2)
        self.mainSizer.AddGrowableRow(2)
        self.panel.SetSizer(self.mainSizer)
        self.mainSizer.Fit(self)

        self.advCheckBox.SetValue(dtkglobal.advSetting)
        self.unlockCheckBox.SetValue(dtkglobal.unlockSetting)
        self.unzipCheckBox.SetValue(dtkglobal.unzipSetting)
        self.metadataTypesTextCtrl.write(','.join(dtkglobal.metadataTypes))
        self.defaultPackagesToExcludeTextCtrl.write(dtkglobal.defaultPackagesToExclude)
        self.defaultMetadataFolderTextCtrl.write(dtkglobal.defaultMetadataFolder)
        self.defaultPreScriptFolderTextCtrl.write(dtkglobal.defaultPreScriptFolder)
        self.defaultScriptFolderTextCtrl.write(dtkglobal.defaultScriptFolder)
        self.defaultApiVersionCtrl.write(dtkglobal.defaultApiVersion)
        
        #Accelerate start
        #self.accelerateEnableCheckBox.SetValue(dtkglobal.accelerateEnableSetting)
        #self.accelerateGitURL.write(dtkglobal.accelerateGitURL)
        #self.accelerateGitUser.write(dtkglobal.accelerateGitUser)
        #self.accelerateGitPassword.write(dtkglobal.accelerateGitPassword)
        #self.accelerateDevEnableCheckBox.SetValue(dtkglobal.accelerateDevEnableSetting)
        #Accelerate end

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.mainSizer.SetEmptyCellSize((0, 0))
        self.Layout()
        self.Fit()
        self.MinSize = self.Size
        self.ShowModal()

    def SaveSettings(self, event):
        dtkglobal.SaveSettings(
            advSettingIn=self.advCheckBox.GetValue(),
            unlockSettingIn=self.unlockCheckBox.GetValue(),
            unzipSettingIn=self.unzipCheckBox.GetValue(),
            metadataTypesSettingIn=self.metadataTypesTextCtrl.GetLineText(0),
            defaultPackagesToExcludeIn=self.defaultPackagesToExcludeTextCtrl.GetLineText(0),
            defaultMetadataFolderIn=self.defaultMetadataFolderTextCtrl.GetLineText(0),
            defaultScriptFolderIn=self.defaultScriptFolderTextCtrl.GetLineText(0),
            defaultApiVersionIn=self.defaultApiVersionCtrl.GetLineText(0),
            defaultPreScriptFolderIn=self.defaultPreScriptFolderTextCtrl.GetLineText(0),
        )
        self.Destroy()

    def OnCancel(self, e):
        self.Destroy()
    
    def OnCloseWindow(self, event):
        self.Destroy()


class SingleApp(wx.App):
    """
    class that extends wx.App and only permits a single running instance.
    """

    def OnInit(self):
        """
        wx.App init function that returns False if the app is already running.
        """
        self.name = "SingleApp-%s".format(wx.GetUserId())
        self.instance = wx.SingleInstanceChecker(self.name)
        if self.instance.IsAnotherRunning():
            wx.MessageBox("An instance of the application is already running", "Error", wx.OK | wx.ICON_WARNING)
            return False
        return True


if __name__ == "__main__":
    app = SingleApp(redirect=False)
    frame = MainFrame(None, title="DTK")
    app.MainLoop()

