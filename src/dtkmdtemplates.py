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
import subprocess
import threading
import dtkglobal
import wx
import json


class ManageMetadataTemplate(wx.Panel):
    def __init__(self, parent):
        super(ManageMetadataTemplate, self).__init__(parent)

        self.InitUI()

    def InitUI(self):
        self.mainSizer = wx.GridBagSizer(4, 4)
        self.metadataTemplatesLbl = wx.StaticText(self, label="Metadata Templates")
        self.metadataTemplatesLbl.ToolTip = "List of Metadata Templates available."

        self.metadataTemplatesComboBox = wx.ComboBox(self, style=wx.CB_READONLY)
        self.metadataTemplatesComboBox.ToolTip = "List of Metadata Templates available."
        self.metadataTemplatesComboBox.Items = dtkglobal.metadataTemplates
        self.metadataTemplatesComboBox.Bind(wx.EVT_COMBOBOX, self.ChangeMetadataTemplate)

        self.metadataTypesLbl = wx.StaticText(self, label="Metadata Types")
        self.metadataTypesLbl.ToolTip = "List of Metadata Types."
        self.metadataTypesListBox = wx.ListBox(self, style=wx.LB_MULTIPLE)
        self.metadataTypesListBox.ToolTip = "List of Metadata Types."
        self.metadataTypesListBox.Items = dtkglobal.metadataTypes
        self.btnSaveMetadataTemplate = wx.Button(self, label="Save")
        self.btnSaveMetadataTemplate.Bind(wx.EVT_BUTTON, self.SaveMetadataTemplate)
        self.btnDeleteMetadataTemplate = wx.Button(self, label="Delete")
        self.btnDeleteMetadataTemplate.Bind(wx.EVT_BUTTON, self.DeleteMetadataTemplate)

        row = 0
        col = 0
        self.mainSizer.Add(self.metadataTemplatesLbl, pos=(row, col), flag=wx.EXPAND | wx.ALL | wx.ALIGN_LEFT, border=5)
        row = 0
        col = 2
        self.mainSizer.Add(
            self.metadataTemplatesComboBox,
            pos=(row, col),
            span=(0, 10),
            flag=wx.EXPAND | wx.ALL | wx.ALIGN_RIGHT,
            border=5,
        )
        row = 1
        col = 0
        self.mainSizer.Add(self.metadataTypesLbl, pos=(row, col), flag=wx.EXPAND | wx.ALL | wx.ALIGN_LEFT, border=5)
        row = 1
        col = 2

        self.mainSizer.AddGrowableRow(row)
        self.mainSizer.Add(
            self.metadataTypesListBox, pos=(row, col), span=(0, 10), flag=wx.EXPAND | wx.ALL | wx.ALIGN_RIGHT, border=5
        )
        row = 2
        col = 0
        self.mainSizer.Add(
            self.btnSaveMetadataTemplate, pos=(row, col), flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_LEFT, border=5
        )
        row = 2
        col = 10
        self.mainSizer.Add(
            self.btnDeleteMetadataTemplate, pos=(row, col), flag=wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_RIGHT, border=5
        )

        self.mainSizer.AddGrowableCol(col)
        self.mainSizer.SetEmptyCellSize((0, 0))
        self.Layout()
        self.Fit()
        self.SetSizer(self.mainSizer)

    def ChangeMetadataTemplate(self, event):
        self.metadataTypesListBox.SetSelection(-1)
        if self.metadataTemplatesComboBox.GetValue() == "All":
            for i in range(self.metadataTypesListBox.GetCount()):
                self.metadataTypesListBox.SetSelection(i)
        if self.metadataTemplatesComboBox.GetValue() in dtkglobal.metadataTemplatesSelection:
            for line in dtkglobal.metadataTemplatesSelection[self.metadataTemplatesComboBox.GetValue()]:
                self.metadataTypesListBox.SetStringSelection(line)

    def DeleteMetadataTemplate(self, event):
        metadataTemplateStr = self.metadataTemplatesComboBox.GetValue()
        if metadataTemplateStr != "All" and metadataTemplateStr != "None":
            if metadataTemplateStr in dtkglobal.metadataTemplates:
                dlg = wx.MessageDialog(
                    self,
                    "Metadata template '" + metadataTemplateStr + "' will be removed from DTK. Please confirm.",
                    "DTK - Delete Metadata Template",
                    wx.YES_NO | wx.ICON_WARNING,
                )
                result = dlg.ShowModal()
                if result == wx.ID_NO:
                    dlg.Destroy()
                    return
            dtkglobal.metadataTemplatesSelection.pop(self.metadataTemplatesComboBox.GetValue())
            dtkglobal.StoreMetadataTemplates()
            dtkglobal.ReadMetadataTemplates()
            self.Parent.GetPage(0).metadataTemplatesComboBox.Items = dtkglobal.metadataTemplates
            self.Layout()
            self.metadataTemplatesComboBox.SetSelection(0)
            self.ChangeMetadataTemplate(event)
        else:
            dlg = wx.MessageDialog(
                self,
                "Metadata template '" + metadataTemplateStr + "' cannot be removed from DTK.",
                "DTK - Delete Metadata Template",
                wx.OK | wx.ICON_ERROR,
            )
            dlg.ShowModal()
            dlg.Destroy()
            return

    def SaveMetadataTemplate(self, event):
        metadataTemplateStr = self.metadataTemplatesComboBox.GetValue()
        if metadataTemplateStr != "All" and metadataTemplateStr != "None":
            if metadataTemplateStr in dtkglobal.metadataTemplates:
                dlg = wx.MessageDialog(
                    self,
                    "Metadata template '" + metadataTemplateStr + "' will be updated. Please confirm.",
                    "DTK - Update Metadata Template",
                    wx.YES_NO | wx.ICON_WARNING,
                )
                result = dlg.ShowModal()
                if result == wx.ID_NO:
                    dlg.Destroy()
                    return
                metadataTypes = self.metadataTypesListBox.GetSelections()
                strMetadataTypesList = []
                for numberMType in metadataTypes:
                    strMType = self.metadataTypesListBox.GetString(numberMType)
                    strMetadataTypesList.append(strMType)

                dtkglobal.metadataTemplatesSelection[metadataTemplateStr] = strMetadataTypesList
                dtkglobal.StoreMetadataTemplates()
                dtkglobal.ReadMetadataTemplates()
                self.Parent.GetPage(0).metadataTemplatesComboBox.Items = dtkglobal.metadataTemplates
                self.Layout()
        else:
            dlg = wx.MessageDialog(
                self,
                "Metadata template '" + metadataTemplateStr + "' cannot be modified.",
                "DTK - Update Metadata Template",
                wx.OK | wx.ICON_ERROR,
            )
            dlg.ShowModal()
            dlg.Destroy()
            return


class AddMetadataTemplate(wx.Panel):
    def __init__(self, parent):
        super(AddMetadataTemplate, self).__init__(parent)

        self.InitUI()

    def InitUI(self):
        self.mainSizer = wx.GridBagSizer(5, 5)

        self.metadataTemplatesLbl = wx.StaticText(self, label="Metadata Template name")
        self.metadataTemplatesLbl.ToolTip = "List of Metadata Templates available."
        self.metadataTemplateName = wx.TextCtrl(self)
        self.metadataTemplateName.ToolTip = "Name of new Metadata Template."

        self.metadataTypesLbl = wx.StaticText(self, label="Metadata Types")
        self.metadataTypesLbl.ToolTip = "List of Metadata Types."
        self.metadataTypesListBox = wx.ListBox(self, style=wx.LB_MULTIPLE)
        self.metadataTypesListBox.ToolTip = "List of Metadata Types."
        self.metadataTypesListBox.Items = dtkglobal.metadataTypes

        self.btnAddMetadataTemplate = wx.Button(self, label="Add Metadata Template")
        self.btnAddMetadataTemplate.Bind(wx.EVT_BUTTON, self.AddMetadataTemplate)

        row = 0
        col = 0
        self.mainSizer.Add(
            self.metadataTemplatesLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        row = 0
        col = 1
        self.mainSizer.Add(
            self.metadataTemplateName,
            pos=(row, col),
            span=(0, 10),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT | wx.ALIGN_RIGHT,
            border=5,
        )

        row = 1
        col = 0
        self.mainSizer.Add(
            self.metadataTypesLbl, pos=(row, col), flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5
        )
        row = 1
        col = 1
        self.mainSizer.AddGrowableRow(row)
        self.mainSizer.Add(
            self.metadataTypesListBox,
            pos=(row, col),
            span=(0, 10),
            flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT,
            border=5,
        )
        row = 2
        col = 1
        self.mainSizer.Add(
            self.btnAddMetadataTemplate,
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

    def ChangeMetadataTemplate(self, event):
        self.metadataTypesListBox.SetSelection(-1)
        if self.metadataTemplatesComboBox.GetValue() == "All":
            for i in range(self.metadataTypesListBox.GetCount()):
                self.metadataTypesListBox.SetSelection(i)
        if self.metadataTemplatesComboBox.GetValue() in dtkglobal.metadataTemplatesSelection:
            for line in dtkglobal.metadataTemplatesSelection[self.metadataTemplatesComboBox.GetValue()]:
                self.metadataTypesListBox.SetStringSelection(line)

    def AddMetadataTemplate(self, event):
        metadataTemplateStr = self.metadataTemplateName.GetValue()
        if len(metadataTemplateStr) == 0:
            dlg = wx.MessageDialog(
                self, "Please introduce a metadata template name.", "DTK - Add Metadata Template", wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return
        if (metadataTemplateStr == "All") or (metadataTemplateStr == "None"):
            dlg = wx.MessageDialog(
                self,
                "Metadata template '"
                + metadataTemplateStr
                + "' already exist and cannot be changed, please introduce other metadata template name",
                "DTK - Update Metadata Template",
                wx.OK | wx.ICON_ERROR,
            )
            dlg.ShowModal()
            dlg.Destroy()
            return
        if metadataTemplateStr in dtkglobal.metadataTemplates:
            dlg = wx.MessageDialog(
                self,
                "Metadata template '"
                + metadataTemplateStr
                + "' already exist, please confirm if you want to update it",
                "DTK - Update Metadata Template",
                wx.YES_NO | wx.ICON_WARNING,
            )
            result = dlg.ShowModal()
            if result == wx.ID_NO:
                dlg.Destroy()
                return

        metadataTypes = self.metadataTypesListBox.GetSelections()
        strMetadataTypesList = []
        for numberMType in metadataTypes:
            strMType = self.metadataTypesListBox.GetString(numberMType)
            strMetadataTypesList.append(strMType)

        dlg = wx.MessageDialog(
            self,
            "Metadata template '" + metadataTemplateStr + "' created.",
            "DTK - Add Metadata Template",
            wx.OK | wx.ICON_INFORMATION,
        )
        dlg.ShowModal()
        dlg.Destroy()
        dtkglobal.metadataTemplatesSelection[self.metadataTemplateName.GetValue()] = strMetadataTypesList
        dtkglobal.StoreMetadataTemplates()
        dtkglobal.ReadMetadataTemplates()
        self.Parent.GetPage(0).metadataTemplatesComboBox.Items = dtkglobal.metadataTemplates
        self.Layout()


class MetadataTemplatesFrame(wx.Frame):
    def __init__(self, parent=None):
        super(MetadataTemplatesFrame, self).__init__(parent, title="Metadata Templates")
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
        self.nb.AddPage(ManageMetadataTemplate(self.nb), "Manage Metadata Templates")
        self.nb.AddPage(AddMetadataTemplate(self.nb), "Add Metadata Template")
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
