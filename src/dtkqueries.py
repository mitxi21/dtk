import os
import subprocess
import threading
import dtkglobal
import wx
import json


class ManageSOQLTemplate(wx.Panel):
    def __init__(self, parent):
        super(ManageSOQLTemplate, self).__init__(parent)

        self.InitUI()

    def InitUI(self):
        self.mainSizer = wx.GridBagSizer(4, 4)
        self.soqlTemplatesLbl = wx.StaticText(self, label="SOQL Templates")
        self.soqlTemplatesLbl.ToolTip = "List of SOQL Templates available."

        self.soqlTemplatesComboBox = wx.ComboBox(self, style=wx.CB_READONLY)
        self.soqlTemplatesComboBox.ToolTip = "List of SOQL Templates available."
        self.soqlTemplatesComboBox.Items = dtkglobal.soqlList
        self.soqlTemplatesComboBox.Bind(wx.EVT_COMBOBOX, self.ChangeSOQLTemplate)

        self.soqlTextCtrlLbl = wx.StaticText(self, label="SOQL Query")
        self.soqlTextCtrlLbl.ToolTip = "List of SOQL Templates available."
        self.soqlTextCtrl = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_AUTO_URL)
        self.soqlTextCtrl.WriteText("")
        self.btnSaveSOQLTemplate = wx.Button(self, label="Save")
        self.btnSaveSOQLTemplate.Bind(wx.EVT_BUTTON, self.SaveSOQLTemplate)
        self.btnDeleteSOQLTemplate = wx.Button(self, label="Delete")
        self.btnDeleteSOQLTemplate.Bind(wx.EVT_BUTTON, self.DeleteSOQLTemplate)

        row = 0
        col = 0
        self.mainSizer.Add(self.soqlTemplatesLbl, pos=(row, col), flag=wx.EXPAND | wx.ALL | wx.ALIGN_LEFT, border=5)
        row = 0
        col = 2

        self.mainSizer.Add(
            self.soqlTemplatesComboBox, pos=(row, col), span=(0, 40), flag=wx.EXPAND | wx.ALL | wx.ALIGN_RIGHT, border=5
        )
        row = 1
        col = 0
        self.mainSizer.Add(
            self.soqlTextCtrlLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.BOTTOM | wx.RIGHT, border=5
        )

        row = 1
        col = 2
        spanV = 30
        spanH = 40
        self.mainSizer.AddGrowableRow(row)
        self.mainSizer.AddGrowableCol(col)
        self.mainSizer.Add(
            self.soqlTextCtrl, pos=(row, col), span=(spanV, spanH), flag=wx.EXPAND | wx.ALL | wx.ALIGN_RIGHT, border=5
        )

        row = 2
        col = 0
        self.mainSizer.Add(
            self.btnSaveSOQLTemplate, pos=(row + spanV, col), flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT, border=5
        )
        row = 2
        self.mainSizer.Add(
            self.btnDeleteSOQLTemplate,
            pos=(row + spanV, spanH + 1),
            flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_RIGHT,
            border=5,
        )

        self.mainSizer.SetEmptyCellSize((0, 0))
        self.Layout()
        self.Fit()
        self.SetSizer(self.mainSizer)

    def ChangeSOQLTemplate(self, event):
        if self.soqlTemplatesComboBox.GetValue() in dtkglobal.soqlList:
            self.soqlTextCtrl.SetValue(dtkglobal.soqlDict[self.soqlTemplatesComboBox.GetValue()])

    def DeleteSOQLTemplate(self, event):
        soqlTemplateStr = self.soqlTemplatesComboBox.GetValue()
        if soqlTemplateStr in dtkglobal.soqlList:
            dlg = wx.MessageDialog(
                self,
                "SOQL template '" + soqlTemplateStr + "' will be removed from DTK. Please confirm.",
                "DTK - Delete SOQL Template",
                wx.YES_NO | wx.ICON_WARNING,
            )
            result = dlg.ShowModal()
            if result == wx.ID_NO:
                dlg.Destroy()
                return
            dtkglobal.soqlDict.pop(self.soqlTemplatesComboBox.GetValue())
            dtkglobal.StoreSOQLTemplates()
            dtkglobal.ReadSOQLTemplates()
            self.Parent.GetPage(0).soqlTemplatesComboBox.Items = dtkglobal.soqlList
            self.Layout()
            self.soqlTextCtrl.SetValue("")
            self.ChangeSOQLTemplate(event)
        else:
            dlg = wx.MessageDialog(
                self, "Please select a SOQL Template to delete", "DTK - Delete SOQL Template", wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return

    def SaveSOQLTemplate(self, event):
        soqlTemplateStr = self.soqlTemplatesComboBox.GetValue()
        if soqlTemplateStr in dtkglobal.soqlList:
            dlg = wx.MessageDialog(
                self,
                "SOQL template '" + soqlTemplateStr + "' will be updated. Please confirm.",
                "DTK - Update SOQL Template",
                wx.YES_NO | wx.ICON_WARNING,
            )
            result = dlg.ShowModal()
            if result == wx.ID_NO:
                dlg.Destroy()
                return
            soqlQuery = self.soqlTextCtrl.GetValue()
            dtkglobal.soqlDict[soqlTemplateStr] = soqlQuery
            dtkglobal.StoreSOQLTemplates()
            dtkglobal.ReadSOQLTemplates()
            self.Parent.GetPage(0).soqlTemplatesComboBox.Items = dtkglobal.soqlList
            self.soqlTemplatesComboBox.SetValue(soqlTemplateStr)
            self.soqlTextCtrl.SetValue(soqlQuery)
            self.Layout()
        else:
            dlg = wx.MessageDialog(
                self, "Please select a SOQL Template to save", "DTK - Save SOQL Template", wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return


class AddSOQLTemplate(wx.Panel):
    def __init__(self, parent):
        super(AddSOQLTemplate, self).__init__(parent)

        self.InitUI()

    def InitUI(self):
        self.mainSizer = wx.GridBagSizer(5, 5)

        self.soqlTemplatesLbl = wx.StaticText(self, label="SOQL Template name")
        self.soqlTemplatesLbl.ToolTip = "List of SOQL Templates available."
        self.soqlTemplateName = wx.TextCtrl(self)
        self.soqlTemplateName.ToolTip = "Name of new SOQL Template."

        self.soqlTextCtrlLbl = wx.StaticText(self, label="SOQL Query")
        self.soqlTextCtrlLbl.ToolTip = "List of SOQL Templates available."
        self.soqlTextCtrl = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_AUTO_URL)
        self.soqlTextCtrl.WriteText("")

        self.btnAddSOQLTemplate = wx.Button(self, label="Add SOQL Template")
        self.btnAddSOQLTemplate.Bind(wx.EVT_BUTTON, self.AddSOQLTemplate)

        row = 0
        col = 0
        self.mainSizer.Add(
            self.soqlTemplatesLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        row = 0
        col = 1
        self.mainSizer.Add(
            self.soqlTemplateName,
            pos=(row, col),
            span=(0, 10),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_RIGHT,
            border=5,
        )

        row = 1
        col = 0
        self.mainSizer.Add(self.soqlTextCtrlLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        row = 1
        col = 1
        self.mainSizer.AddGrowableRow(row)
        self.mainSizer.Add(
            self.soqlTextCtrl, pos=(row, col), span=(0, 10), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        row = 2
        col = 1
        self.mainSizer.Add(
            self.btnAddSOQLTemplate,
            pos=(row, col),
            span=(0, 10),
            flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_RIGHT,
            border=5,
        )

        self.mainSizer.AddGrowableCol(col)

        self.mainSizer.SetEmptyCellSize((0, 0))
        self.Layout()
        self.Fit()
        self.SetSizer(self.mainSizer)

    def AddSOQLTemplate(self, event):
        soqlTemplateStr = self.soqlTemplateName.GetValue()
        if len(soqlTemplateStr) == 0:
            dlg = wx.MessageDialog(
                self, "Please introduce a SOQL template name.", "DTK - Add SOQL Template", wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return
        if soqlTemplateStr in dtkglobal.soqlList:
            dlg = wx.MessageDialog(
                self,
                "SOQL template '" + soqlTemplateStr + "' already exist, please confirm if you want to update it",
                "DTK - Update SOQL Template",
                wx.YES_NO | wx.ICON_WARNING,
            )
            result = dlg.ShowModal()
            if result == wx.ID_NO:
                dlg.Destroy()
                return
            else:
                dlg = wx.MessageDialog(
                    self,
                    "SOQL template '" + soqlTemplateStr + "' updated.",
                    "DTK - Update SOQL Template",
                    wx.OK | wx.ICON_INFORMATION,
                )
                dlg.ShowModal()
                dlg.Destroy()

        else:
            dlg = wx.MessageDialog(
                self,
                "SOQL template '" + soqlTemplateStr + "' created.",
                "DTK - Add SOQL Template",
                wx.OK | wx.ICON_INFORMATION,
            )
            dlg.ShowModal()
            dlg.Destroy()

        soqlQuery = self.soqlTextCtrl.GetValue()
        dtkglobal.soqlDict[self.soqlTemplateName.GetValue()] = soqlQuery
        dtkglobal.StoreSOQLTemplates()
        dtkglobal.ReadSOQLTemplates()
        self.Parent.GetPage(0).soqlTemplatesComboBox.Items = dtkglobal.soqlList
        self.Layout()


class SOQLTemplatesFrame(wx.Frame):
    def __init__(self, parent=None):
        super(SOQLTemplatesFrame, self).__init__(parent, title="SOQL Templates")
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
        self.nb.AddPage(ManageSOQLTemplate(self.nb), "Manage SOQL Templates")
        self.nb.AddPage(AddSOQLTemplate(self.nb), "Add SOQL Template")
        self.mainSizer = wx.GridBagSizer(5, 5)

        row = 0
        col = 0

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
