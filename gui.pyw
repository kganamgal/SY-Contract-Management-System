#!/usr/bin/env python
# -*- coding: utf-8 -*-

import userConst as uc
import wx, wx.grid, wx.dataview, wx.adv
from background import *

class TestTable(wx.grid.GridTableBase):#定义网格表
    def __init__(self, data={}, colLabels=[], rowLabels=None, percentCols=[]):
        wx.grid.GridTableBase.__init__(self)
        self.data = data
        self.colLabels = colLabels
        self.percentCols = percentCols
        self.attr = wx.grid.GridCellAttr()
        self.attr.SetAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.attr_float = wx.grid.GridCellAttr()
        self.attr_float.SetAlignment(wx.ALIGN_RIGHT, wx.ALIGN_CENTRE)
    def chageData(self, data):
        self.data = data
    # these five are the required methods
    def GetNumberRows(self):
        try:
            rownum, colnum = max(self.data.keys())    #取的是最大值而非长度，所以要+1
            return rownum + 1
        except:
            return 1
    def GetNumberCols(self):
        return len(self.colLabels)
    def IsEmptyCell(self, row, col):
        try:
            return self.data[(row, col)] is not None
        except:
            return True
    def GetValue(self, row, col):#为网格提供数据
        try:
            value = self.data.get((row, col))
        except:
            value = None
        if value is None:
            return ''
        def thousands(n): return '{:>,.2f}'.format(n)
        def percents(n): return '{:>.2f}'.format((n or 0) * 100) + '%'
        if str(type(value)) == "<class 'float'>" or str(type(value)) == "<class 'decimal.Decimal'>":
            if col in self.percentCols:
                return percents(value)
            else:
                return thousands(value)
        return str(value)
    def SetValue(self, row, col, value):#给表赋值
        self.data[(row,col)] = value
    def GetColLabelValue(self, col):#列标签
        try:
            return self.colLabels[col]
        except:
            return str(col + 1)
    def GetRowLabelValue(self, row):#行标签
        try:
            return self.rowLabels[row]
        except:
            return str(row + 1)
    def GetAttr(self, row, col, kind):
        try:
            value = self.data.get((row, col))
        except:
            value = None
        if str(type(value)) in ["<class 'float'>", "<class 'decimal.Decimal'>"]:
            attr = self.attr_float
        else:
            attr = self.attr
        attr.IncRef()
        return attr
    def AppendRows(self, numRows=1):
        gridView = self.GetView()
        gridView.BeginBatch()
        appendMsg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_APPENDED, numRows)
        gridView.ProcessTableMessage(appendMsg)
        gridView.EndBatch()
        getValueMsg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        gridView.ProcessTableMessage(getValueMsg)
        return True
    def DeleteRows(self, pos=0, numRows=1):
        gridView = self.GetView()
        gridView.BeginBatch()
        deleteMsg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_ROWS_DELETED, pos, numRows)
        gridView.ProcessTableMessage(deleteMsg)
        gridView.EndBatch()
        getValueMsg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        gridView.ProcessTableMessage(getValueMsg)
        return True
    def AppendCols(self, numCols=1):
        gridView = self.GetView()
        gridView.BeginBatch()
        appendMsg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_COLS_APPENDED, numCols)
        gridView.ProcessTableMessage(appendMsg)
        gridView.EndBatch()
        getValueMsg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        gridView.ProcessTableMessage(getValueMsg)
        return True
    def DeleteCols(self, pos=0, numCols=1):
        self.isModified = True
        gridView = self.GetView()
        gridView.BeginBatch()
        deleteMsg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_NOTIFY_COLS_DELETED,pos, numCols)
        gridView.ProcessTableMessage(deleteMsg)
        gridView.EndBatch()
        getValueMsg = wx.grid.GridTableMessage(self, wx.grid.GRIDTABLE_REQUEST_VIEW_GET_VALUES)
        gridView.ProcessTableMessage(getValueMsg)
        return True

if __name__ == '__main__':
    app = wx.App()
    dlg = FilterDialog()
    dlg.ShowModal()
    print(dlg.GetValue())
    dlg.Destroy()
    app.Destroy()
    # app.MainLoop()
    pass