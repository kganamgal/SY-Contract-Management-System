#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gui import *
from background import *

class DateDialog(wx.Dialog):
    def __init__(self):
        self.init()
    def init(self):
        wx.Dialog.__init__(self, None, -1, '日期查看器', size=(260, 200))
        self.Centre(wx.BOTH)
        self.cc = wx.adv.CalendarCtrl(self, -1, style=wx.adv.CAL_SHOW_HOLIDAYS|wx.adv.CAL_SHOW_WEEK_NUMBERS)
        self.cc.Bind(wx.adv.EVT_CALENDAR, self.SetValue)
    def SetValue(self, event):
        self.EndModal(wx.ID_OK)
    def GetValue(self):
        year = self.cc.GetDate().GetYear()
        month = self.cc.GetDate().GetMonth()+1
        day = self.cc.GetDate().GetDay()
        return datetime.date(year, month, day)
        
class GridDialog(wx.Dialog):
    def init(self, title, data, size):
        wx.Dialog.__init__(self, None, -1, title, size=size, style=wx.CAPTION|wx.CLOSE_BOX|wx.MAXIMIZE_BOX)
        self.Centre(wx.BOTH)
        self.filter_satus = []
        # Create controls
        self.ctrl = {}
        self.ctrl[('Button', uc.新建)]     = wx.Button(self, -1, uc.新建,     size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.修改)]     = wx.Button(self, -1, uc.修改,     size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.删除)]     = wx.Button(self, -1, uc.删除,     size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.筛选)]     = wx.Button(self, -1, uc.筛选,     size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.查询结构)] = wx.Button(self, -1, uc.查询结构, size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.刷新)]     = wx.Button(self, -1, uc.刷新,     size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.导出)]     = wx.Button(self, -1, uc.导出,     size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.OK)]       = wx.Button(self, wx.ID_OK,        size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.CANCEL)]   = wx.Button(self, wx.ID_CANCEL,    size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.OK)].SetDefault()
        self.ctrl[('Textbox', uc.显示窗)]  = wx.TextCtrl(self, -1, '', size=(size[0]-100, 20), style=wx.TE_READONLY|wx.NO_BORDER)
        self.ctrl[('Grid', None)] = wx.grid.Grid(self, size=(size[0]-20, size[1]-100))
        # sizers
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(5)
        # 第一行控件
        hsz1 = wx.BoxSizer(wx.HORIZONTAL)
        hsz1.AddSpacer(10)
        hsz1.Add(self.ctrl[('Button', uc.新建)],     0, wx.EXPAND|wx.ALL, 2)
        hsz1.Add(self.ctrl[('Button', uc.修改)],     0, wx.EXPAND|wx.ALL, 2)
        hsz1.Add(self.ctrl[('Button', uc.删除)],     0, wx.EXPAND|wx.ALL, 2)
        hsz1.Add(self.ctrl[('Button', uc.筛选)],     0, wx.EXPAND|wx.ALL, 2)
        hsz1.Add(self.ctrl[('Button', uc.查询结构)], 0, wx.EXPAND|wx.ALL, 2)
        hsz1.Add(self.ctrl[('Button', uc.刷新)],     0, wx.EXPAND|wx.ALL, 2)
        hsz1.Add(self.ctrl[('Button', uc.导出)],     0, wx.EXPAND|wx.ALL, 2)
        btns = wx.StdDialogButtonSizer()
        btns.AddButton(self.ctrl[('Button', uc.OK)])
        btns.AddButton(self.ctrl[('Button', uc.CANCEL)])
        btns.Realize()
        hsz1.Add(btns, 0, wx.EXPAND|wx.ALL, 5)
        sizer.Add(hsz1, 0, 0, 5)
        sizer.AddSpacer(5)
        # 第二行控件
        hsz2 = wx.BoxSizer(wx.HORIZONTAL)
        hsz2.AddSpacer(50)
        hsz2.Add(self.ctrl[('Textbox', uc.显示窗)])
        sizer.AddSpacer(5)
        # 第三行控件
        sizer.Add(hsz2, 0, 0, 5)
        sizer.Add(self.ctrl[('Grid', None)], 1, wx.EXPAND|wx.ALL, 5)
        table = TestTable(data={}, colLabels={})
        self.ctrl[('Grid', None)].SetDefaultCellAlignment(1, 1)
        self.ctrl[('Grid', None)].SetTable(table, True, 1)         #一次只能选一整行
        self.ctrl[('Grid', None)].EnableEditing(False)             #表格不可编辑
        self.ctrl[('Grid', None)].SetColLabelSize(30)
        self.ctrl[('Grid', None)].SetRowLabelSize(40)
        # 重绘控件
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.ctrl[('Button', uc.CANCEL)].Bind(wx.EVT_BUTTON, self.closeDialog)
    # events
    def closeDialog(self, event):
        dlg = wx.MessageDialog(self, message='您确定要退出吗？点击OK退出对话框', caption='警告', style= wx.YES_NO | wx.NO_DEFAULT)
        if dlg.ShowModal() == wx.ID_NO:
            dlg.Destroy()
            return
        else:
            dlg.Destroy()
        self.EndModal(wx.ID_CANCEL)
    # methods
    def reFreshGrid(self, grid, data={}, gridColLabels=[], percentCols=[]):
        grid.GetTable().chageData(data)
        grid.GetTable().colLabels = gridColLabels
        grid.GetTable().percentCols = percentCols
        try:
            rownum = max(data.keys())[0] + 1
        except:
            rownum = 1
        colnum = len(gridColLabels)
        if rownum > grid.NumberRows:
            grid.AppendRows(rownum - grid.NumberRows)
        if rownum < grid.NumberRows:
            grid.DeleteRows(0, grid.NumberRows - rownum)
        if colnum > grid.NumberCols:
            grid.AppendCols(colnum - grid.NumberCols)
        if colnum < grid.NumberCols:
            grid.DeleteCols(0, grid.NumberCols - colnum)
        grid.AutoSizeColumns(True)
        grid.AutoSizeRows(True)
        grid.Refresh()
    def format_DBdata2Griddata(self, data):
        result = {}
        rownum = len(data)
        try:
            colnum = len(data[0])
        except:
            colnum = 0
        for row, each_row in zip(range(rownum), data):
            for col, each_cell in zip(range(colnum), each_row):
                result[(row, col)] = each_cell
        return result
    def get_data_by_sortGrid(self, grid, thecol=0, ifDESC=True, datatype=[]):
        def thousands(n): return '{:>,.2f}'.format(n)
        def percents(n): return '{:>.2f}'.format((n or 0) * 100) + '%'
        data = grid.GetTable().data
        data_lenth = max(data.keys())
        cols = {}
        newdata = {}
        for row in range(data_lenth[0] + 1):
            try:
                cols[row] = float(data[row, thecol])
            except:
                if datatype[thecol] == '字符串型':
                    cols[row] = data[row, thecol] or ''
                else:
                    cols[row] = data[row, thecol] or 0.0
        sortedcols = sorted(cols.items(), key=lambda asd:asd[1], reverse=ifDESC) #按值排列
        sortedindex = list(x[0] for x in sortedcols) #返回按值正序排列后的键序号
        for newrow, row in zip(range(data_lenth[0] + 1), sortedindex):
            for col in range(data_lenth[1] + 1):
                newdata[newrow, col] = data[row, col]
        return newdata

class MaintainDialog(wx.Dialog):
    def init(self, title='', data=[], size=uc.Size_BaseDialog):
        wx.Dialog.__init__(self, None, -1, title, size=size)
        self.Centre(wx.BOTH)
        # Create controls
        self.ctrl = {}
        self.ctrl[('Button', uc.跳转)] = wx.Button(self, -1, uc.跳转, size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.附件)] = wx.Button(self, -1, uc.附件, size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.新建)] = wx.Button(self, -1, uc.新建, size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.修改)] = wx.Button(self, -1, uc.修改, size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.保存)] = wx.Button(self, -1, uc.保存, size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.会签表格)] = wx.Button(self, -1, uc.会签表格, size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.取消)] = wx.Button(self, -1, uc.取消, size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.退出)] = wx.Button(self, wx.ID_CANCEL, uc.退出, size=uc.Size_Button_BaseDialog)
        # sizers
        self.all_sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.all_sizer.Add(self.sizer)
        self.all_sizer.AddSpacer(5)
        # 最后一行控件
        self.hsz_button = wx.BoxSizer(wx.HORIZONTAL)
        self.hsz_button.Add(self.ctrl[('Button', uc.跳转)], 0, wx.EXPAND|wx.ALL, 5)
        self.hsz_button.Add(self.ctrl[('Button', uc.附件)], 0, wx.EXPAND|wx.ALL, 5)
        self.hsz_button.Add(self.ctrl[('Button', uc.新建)], 0, wx.EXPAND|wx.ALL, 5)
        self.hsz_button.Add(self.ctrl[('Button', uc.修改)], 0, wx.EXPAND|wx.ALL, 5)
        self.hsz_button.Add(self.ctrl[('Button', uc.保存)], 0, wx.EXPAND|wx.ALL, 5)
        self.hsz_button.Add(self.ctrl[('Button', uc.会签表格)], 0, wx.EXPAND|wx.ALL, 5)
        self.hsz_button.Add(self.ctrl[('Button', uc.取消)], 0, wx.EXPAND|wx.ALL, 5)
        self.hsz_button.Add(self.ctrl[('Button', uc.退出)], 0, wx.EXPAND|wx.ALL, 5)
        self.all_sizer.Add(self.hsz_button, 0, wx.ALIGN_RIGHT|wx.ALL, 10)
        # 重绘控件
        self.SetSizer(self.all_sizer)
        self.all_sizer.Fit(self)
        self.ctrl[('Button', uc.退出)].Bind(wx.EVT_BUTTON, self.closeDialog)
    # events
    def closeDialog(self, event):
        dlg = wx.MessageDialog(self, message='您确定要退出吗？点击OK退出对话框', caption='警告', style= wx.YES_NO | wx.NO_DEFAULT)
        if dlg.ShowModal() == wx.ID_NO:
            dlg.Destroy()
            return
        else:
            dlg.Destroy()
        self.EndModal(wx.ID_CANCEL)
    def Jump(self, event, UDID, Choices, class_Init, class_Bidding, class_Contract, class_Budget, class_Payment):
        dlg = JumpDialog(Label='跳转选项列表', Choices=Choices)
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        result = dlg.GetValue()
        dlg.Destroy()
        if UDID:
            if result.find('立项') > 0:
                where_sql = 'WHERE 立项识别码 IN %s'
                if operateDB().get_All_Children_Info_InitUDID(UDID):
                    UDIDs = operateDB().get_All_Grandchildren(UDID)
                    dlg = class_Init(where_sql='WHERE 立项识别码 IN %s', where_list=[UDIDs])
                else:
                    UDID = UDID
                    dlg = class_Init(where_sql='WHERE 立项识别码 IN %s', where_list=[[UDID]])
                dlg.ShowModal()
                dlg.Destroy()
            elif result.find('招标') > 0:
                where_sql = 'WHERE 立项识别码 IN %s'
                if operateDB().get_All_Children_Info_InitUDID(UDID):
                    UDIDs = operateDB().get_All_Grandchildren(UDID)
                    dlg = class_Bidding(where_sql='WHERE 立项识别码 IN %s', where_list=[UDIDs])
                else:
                    UDID = UDID
                    dlg = class_Bidding(where_sql='WHERE 立项识别码 IN %s', where_list=[[UDID]])
                dlg.ShowModal()
                dlg.Destroy()
            elif result.find('合同') > 0:
                where_sql = 'WHERE 立项识别码 IN %s'
                if operateDB().get_All_Children_Info_InitUDID(UDID):
                    UDIDs = operateDB().get_All_Grandchildren(UDID)
                    dlg = class_Contract(where_sql='WHERE 立项识别码 IN %s', where_list=[UDIDs])
                else:
                    UDID = UDID
                    dlg = class_Contract(where_sql='WHERE 立项识别码 IN %s', where_list=[[UDID]])
                dlg.ShowModal()
                dlg.Destroy()
            elif result.find('预算') > 0:
                where_sql = 'WHERE 立项识别码 IN %s'
                if operateDB().get_All_Children_Info_InitUDID(UDID):
                    UDIDs = operateDB().get_All_Grandchildren(UDID)
                    dlg = class_Budget(where_sql='WHERE 立项识别码 IN %s', where_list=[UDIDs])
                else:
                    UDID = UDID
                    dlg = class_Budget(where_sql='WHERE 立项识别码 IN %s', where_list=[[UDID]])
                dlg.ShowModal()
                dlg.Destroy()
            elif result.find('付款') > 0:
                where_sql = 'WHERE 立项识别码 IN %s'
                if operateDB().get_All_Children_Info_InitUDID(UDID):
                    UDIDs = operateDB().get_All_Grandchildren(UDID)
                    dlg = class_Payment(where_sql='WHERE 立项识别码 IN %s', where_list=[UDIDs])
                else:
                    UDID = UDID
                    dlg = class_Payment(where_sql='WHERE 立项识别码 IN %s', where_list=[[UDID]])
                dlg.ShowModal()
                dlg.Destroy()

class FilterDialog(wx.Dialog):
    def __init__(self, fields=[], fields_type=[], filter_case=[]):
        self.init(fields, fields_type, filter_case)
    def init(self, fields=[], fields_type=[], filter_case=[], title='筛选信息', size=uc.Size_BaseDialog):
        self.fields = fields
        self.fields_type = fields_type
        self.filter_case = filter_case
        wx.Dialog.__init__(self, None, -1, title, size=size)
        self.Centre(wx.BOTH)
        # Create controls
        little_sizer = {}
        def create_Label_Textbox_Pairs(key, size_Textbox):
            little_sizer[key] = wx.BoxSizer(wx.HORIZONTAL)
            self.ctrl[('Label', key)] = wx.StaticText(self, -1, '数据类型：', size=uc.Size_Label_FilterDialog, style=wx.ALIGN_RIGHT)
            self.ctrl[('Textbox', key)] = wx.TextCtrl(self, -1, '', size=size_Textbox, style=wx.TE_READONLY|wx.TE_CENTRE|wx.BORDER_STATIC)
            little_sizer[key].Add(self.ctrl[('Label', key)])
            little_sizer[key].Add(self.ctrl[('Textbox', key)])
        self.ctrl = {}
        self.ctrl[('Listbox', uc.筛选器)] = wx.ListBox(self, -1, size=uc.Size_Listbox_FilterDialog, choices=[], style=wx.LB_SINGLE)
        self.ctrl[('Button', uc.删除)] = wx.Button(self, -1, uc.删除, size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.清空)] = wx.Button(self, -1, uc.清空, size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.新增筛选条件)] = wx.Button(self, -1, uc.新增筛选条件, size=uc.Size_Button_Case_FilterDialog)
        self.ctrl[('Button', uc.修改筛选条件)] = wx.Button(self, -1, uc.修改筛选条件, size=uc.Size_Button_Case_FilterDialog)
        self.ctrl[('Button', uc.OK)] = wx.Button(self, wx.ID_OK, uc.OK, size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.OK)].SetDefault()
        self.ctrl[('Button', uc.取消)] = wx.Button(self, wx.ID_CANCEL, uc.取消, size=uc.Size_Button_BaseDialog)
        self.ctrl[('Combobox', uc.筛选字段[0])] = wx.ComboBox(self, -1, value='', size=uc.Size_Combobox_Normal_FilterDialog, choices=[], style=wx.CB_DROPDOWN|wx.CB_READONLY)
        self.ctrl[('Combobox', uc.筛选字段[1])] = wx.ComboBox(self, -1, value='', size=uc.Size_Combobox_Normal_FilterDialog, choices=[], style=wx.CB_DROPDOWN|wx.CB_READONLY)
        self.ctrl[('Combobox', uc.比较符[0])] = wx.ComboBox(self, -1, value='', size=uc.Size_Combobox_Short_FilterDialog, choices=[], style=wx.CB_DROPDOWN|wx.CB_READONLY)
        self.ctrl[('Combobox', uc.比较符[1])] = wx.ComboBox(self, -1, value='', size=uc.Size_Combobox_Short_FilterDialog, choices=[], style=wx.CB_DROPDOWN|wx.CB_READONLY)
        self.ctrl[('Combobox', uc.逻辑符)] = wx.ComboBox(self, -1, value='', size=uc.Size_Combobox_Short_FilterDialog, choices=[], style=wx.CB_DROPDOWN|wx.CB_READONLY)
        create_Label_Textbox_Pairs(uc.数据类型[0], uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs(uc.数据类型[1], uc.Size_Textbox_Normal_BaseDialog)
        self.ctrl[('Textbox', uc.筛选值[0])] = wx.TextCtrl(self, -1, '', size=uc.Size_Textbox_Long_BaseDialog, style=wx.TE_CENTRE|wx.BORDER_STATIC)
        self.ctrl[('Textbox', uc.筛选值[1])] = wx.TextCtrl(self, -1, '', size=uc.Size_Textbox_Long_BaseDialog, style=wx.TE_CENTRE|wx.BORDER_STATIC)
        self.ctrl[('Combobox', uc.比较符[0])].AppendItems('大于 小于 大于等于 小于等于 等于 不等于 包含 不包含 开头是 开头不是 结尾是 结尾不是 属于'.split())
        self.ctrl[('Combobox', uc.比较符[1])].AppendItems('大于 小于 大于等于 小于等于 等于 不等于 包含 不包含 开头是 开头不是 结尾是 结尾不是 属于'.split())
        self.ctrl[('Combobox', uc.逻辑符)].AppendItems(',并且,或者'.split(','))
        self.ctrl[('Combobox', uc.筛选字段[0])].AppendItems(fields)
        self.ctrl[('Combobox', uc.筛选字段[1])].AppendItems(fields)
        self.ClearCtrls()
        # sizers       
        self.all_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # 筛选器
        self.list_sizer = wx.BoxSizer(wx.VERTICAL)
        self.list_sizer.Add(self.ctrl[('Listbox', uc.筛选器)], 0, wx.ALL, 5)
        self.list_bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.list_bottom_sizer.Add(self.ctrl[('Button', uc.删除)], 0, wx.ALL, 20)
        self.list_bottom_sizer.Add(self.ctrl[('Button', uc.清空)], 0, wx.ALL, 20)
        self.list_sizer.Add(self.list_bottom_sizer, 0, wx.ALIGN_CENTRE)
        self.all_sizer.Add(self.list_sizer, 0, wx.ALL, 10)
        # 添加、修改按钮
        self.middle_sizer = wx.BoxSizer(wx.VERTICAL)
        self.middle_sizer.AddSpacer(100)
        self.middle_sizer.Add(self.ctrl[('Button', uc.新增筛选条件)], 0, wx.ALL, 10)
        self.middle_sizer.Add(self.ctrl[('Button', uc.修改筛选条件)], 0, wx.ALL, 10)
        self.all_sizer.Add(self.middle_sizer)
        # 编辑控件群
        self.right_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right_hsz1 = wx.BoxSizer(wx.HORIZONTAL)
        self.right_hsz1.Add(self.ctrl[('Combobox', uc.筛选字段[0])])
        self.right_hsz1.Add(little_sizer[uc.数据类型[0]])
        self.right_sizer.Add(self.right_hsz1, 0, wx.ALL, 10)
        self.right_hsz2 = wx.BoxSizer(wx.HORIZONTAL)
        self.right_hsz2.Add(self.ctrl[('Combobox', uc.比较符[0])], 0, wx.RIGHT, 10)
        self.right_hsz2.Add(self.ctrl[('Textbox', uc.筛选值[0])])
        self.right_sizer.Add(self.right_hsz2, 0, wx.ALL, 10)
        self.right_sizer.Add(self.ctrl[('Combobox', uc.逻辑符)], 0, wx.ALL, 10)
        self.right_hsz3 = wx.BoxSizer(wx.HORIZONTAL)
        self.right_hsz3.Add(self.ctrl[('Combobox', uc.筛选字段[1])])
        self.right_hsz3.Add(little_sizer[uc.数据类型[1]])
        self.right_sizer.Add(self.right_hsz3, 0, wx.ALL, 10)
        self.right_hsz4 = wx.BoxSizer(wx.HORIZONTAL)
        self.right_hsz4.Add(self.ctrl[('Combobox', uc.比较符[1])], 0, wx.RIGHT, 10)
        self.right_hsz4.Add(self.ctrl[('Textbox', uc.筛选值[1])])
        self.right_sizer.Add(self.right_hsz4, 0, wx.ALL, 10)
        self.right_bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.right_bottom_sizer.Add(self.ctrl[('Button', uc.OK)], 0, wx.ALL, 30)
        self.right_bottom_sizer.Add(self.ctrl[('Button', uc.取消)], 0, wx.ALL, 30)
        self.right_sizer.Add(self.right_bottom_sizer, 0, wx.ALIGN_CENTRE)
        self.all_sizer.Add(self.right_sizer, 0, wx.ALL, 10)
        # 重绘控件
        self.SetSizer(self.all_sizer)
        self.all_sizer.Fit(self)
        self.FillListbox()
        for key, eachEvent, eachHandler in self.ctrlBindData():
            self.ctrl[key].Bind(eachEvent, eachHandler)
        self.ctrl[('Button', uc.取消)].Bind(wx.EVT_BUTTON, self.closeDialog)
    # binder
    def ctrlBindData(self):
        return ((('Listbox',  uc.筛选器), wx.EVT_LISTBOX, self.listboxOnSelect),
                (('Combobox',  uc.逻辑符), wx.EVT_COMBOBOX, self.changeLogicCombobox),
                (('Combobox',  uc.筛选字段[0]), wx.EVT_COMBOBOX, self.changeFieldsType0),
                (('Combobox',  uc.筛选字段[1]), wx.EVT_COMBOBOX, self.changeFieldsType1),
                (('Button',  uc.新增筛选条件), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.修改筛选条件), wx.EVT_BUTTON, self.clickOnButton),
                (('Textbox',  uc.筛选值[0]), wx.EVT_LEFT_DCLICK, self.inputDate0),
                (('Textbox',  uc.筛选值[1]), wx.EVT_LEFT_DCLICK, self.inputDate1),
                (('Button',  uc.清空), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.删除), wx.EVT_BUTTON, self.clickOnButton),
               )
    # events
    def closeDialog(self, event):
        dlg = wx.MessageDialog(self, message='您确定要退出吗？点击"是"退出对话框', caption='警告', style= wx.YES_NO | wx.NO_DEFAULT)
        if dlg.ShowModal() == wx.ID_NO:
            dlg.Destroy()
            return
        else:
            dlg.Destroy()
        self.EndModal(wx.ID_CANCEL)
    def listboxOnSelect(self, event):
        n = self.ctrl[('Listbox', uc.筛选器)].GetSelection()
        self.FillCtrls(n)
    def changeLogicCombobox(self, event):
        self.hide_or_show_condition2()
    def changeFieldsType0(self, event):
        n = self.ctrl[('Combobox', uc.筛选字段[0])].GetSelection()
        value_type = self.fields_type[n]
        self.ctrl[('Textbox', uc.数据类型[0])].SetValue(value_type)
        self.ctrl[('Textbox', uc.筛选值[0])].SetEditable(value_type != '日期型')
        if value_type in '整数型 浮点型 日期型'.split():
            self.ctrl[('Combobox', uc.比较符[0])].Clear()
            self.ctrl[('Combobox', uc.比较符[0])].AppendItems('大于 小于 大于等于 小于等于 等于 不等于 属于'.split())
        elif value_type == '字符串型':
            self.ctrl[('Combobox', uc.比较符[0])].Clear()
            self.ctrl[('Combobox', uc.比较符[0])].AppendItems('等于 不等于 包含 不包含 开头是 开头不是 结尾是 结尾不是 属于'.split())
    def changeFieldsType1(self, event):
        n = self.ctrl[('Combobox', uc.筛选字段[1])].GetSelection()
        value_type = self.fields_type[n]
        self.ctrl[('Textbox', uc.数据类型[1])].SetValue(value_type)
        self.ctrl[('Textbox', uc.筛选值[1])].SetEditable(value_type != '日期型')
        if value_type in '整数型 浮点型 日期型'.split():
            self.ctrl[('Combobox', uc.比较符[1])].Clear()
            self.ctrl[('Combobox', uc.比较符[1])].AppendItems('大于 小于 大于等于 小于等于 等于 不等于 属于'.split())
        elif value_type == '字符串型':
            self.ctrl[('Combobox', uc.比较符[1])].Clear()
            self.ctrl[('Combobox', uc.比较符[1])].AppendItems('等于 不等于 包含 不包含 开头是 开头不是 结尾是 结尾不是 属于'.split())
    def clickOnButton(self, event):
        label = wx.FindWindowById(event.Id, self).GetLabel()
        if label == uc.新增筛选条件:
            self.AppendFilterCase()
        elif label == uc.修改筛选条件:
            n = self.ctrl[('Listbox', uc.筛选器)].GetSelection()
            if n < 0:
                dlg = wx.MessageDialog(self, message='请先选择一个筛选条件', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            self.EditFilterCase(n)
        elif label == uc.清空:
            dlg = wx.MessageDialog(self, message='您确定要清除全部筛选条件吗？点击"是"完成清空', caption='警告', style= wx.YES_NO | wx.NO_DEFAULT)
            if dlg.ShowModal() == wx.ID_YES:
                self.ctrl[('Listbox', uc.筛选器)].Clear()
                self.filter_case = []
            dlg.Destroy()
            return
        elif label == uc.删除:
            n = self.ctrl[('Listbox', uc.筛选器)].GetSelection()
            if n < 0:
                dlg = wx.MessageDialog(self, message='请先选择一个筛选条件', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            dlg = wx.MessageDialog(self, message='您确定要删除选中的筛选条件吗？点击"是"完成删除', caption='警告', style= wx.YES_NO | wx.NO_DEFAULT)
            if dlg.ShowModal() == wx.ID_YES:
                self.ctrl[('Listbox', uc.筛选器)].Delete(n)
                self.filter_case.pop(n)
            dlg.Destroy()
            return
    def inputDate0(self, event):
        if self.ctrl[('Textbox', uc.数据类型[0])].GetValue() != '日期型':
            return
        dlg = DateDialog()
        if dlg.ShowModal() == wx.ID_OK:
            self.ctrl[('Textbox', uc.筛选值[0])].SetValue(str(dlg.GetValue()))
        dlg.Destroy()
    def inputDate1(self, event):
        if self.ctrl[('Textbox', uc.数据类型[1])].GetValue() != '日期型':
            return
        dlg = DateDialog()
        if dlg.ShowModal() == wx.ID_OK:
            self.ctrl[('Textbox', uc.筛选值[1])].SetValue(str(dlg.GetValue()))
        dlg.Destroy()
    # methods
    def GetValue(self):
        return self.filter_case
    def hide_or_show_condition2(self):
        value = self.ctrl[('Combobox',  uc.逻辑符)].GetValue()
        if value:
            self.ctrl[('Combobox', uc.筛选字段[1])].Show()
            self.ctrl[('Combobox', uc.比较符[1])].Show()
            self.ctrl[('Textbox', uc.数据类型[1])].Show()
            self.ctrl[('Label', uc.数据类型[1])].Show()
            self.ctrl[('Textbox', uc.筛选值[1])].Show()
        else:
            self.ctrl[('Combobox', uc.筛选字段[1])].Hide()
            self.ctrl[('Combobox', uc.比较符[1])].Hide()
            self.ctrl[('Textbox', uc.数据类型[1])].Hide()
            self.ctrl[('Label', uc.数据类型[1])].Hide()
            self.ctrl[('Textbox', uc.筛选值[1])].Hide()
    def AppendFilterCase(self):
        str_case, var_case = self.formatFilterCase()
        self.ctrl[('Listbox', uc.筛选器)].Append(str_case)
        self.filter_case.append([str_case, var_case])
        n = self.ctrl[('Listbox', uc.筛选器)].GetSelection()
        self.FillCtrls(n)
    def EditFilterCase(self, n):
        str_case, var_case = self.formatFilterCase()
        self.ctrl[('Listbox', uc.筛选器)].SetString(n, str_case)
        self.filter_case[n] = [str_case, var_case]
        n = self.ctrl[('Listbox', uc.筛选器)].GetSelection()
        self.FillCtrls(n)
    def formatFilterCase(self):
        field_0        = self.ctrl[('Combobox', uc.筛选字段[0])].GetValue()
        fieldtype_0    = self.ctrl[('Textbox', uc.数据类型[0])].GetValue()
        comparer_0     = self.ctrl[('Combobox', uc.比较符[0])].GetValue()
        value_0        = self.ctrl[('Textbox', uc.筛选值[0])].GetValue()
        if value_0.find('|') < 0:
            if fieldtype_0 == '整数型':
                try:
                    value_0 = int(value_0.replace(',', ''))
                except:
                    value_0 = 0
            elif fieldtype_0 == '浮点型':
                try:
                    value_0 = float(value_0.replace(',', ''))
                except:
                    value_0 = 0.0
            elif fieldtype_0 == '日期型':
                try:
                    value_0 = datetime.date(*time.strptime(value_0, "%Y-%m-%d")[:3])
                except:
                    value_0 = datetime.date.today()
            str_case = '【%s %s %s】' % (field_0, comparer_0, str(value_0))
        else:
            str_case = '【%s %s %s】' % (field_0, comparer_0, str(value_0))
            value_0 = value_0.split('|')
        logic          = self.ctrl[('Combobox', uc.逻辑符)].GetValue()
        field_1        = self.ctrl[('Combobox', uc.筛选字段[1])].GetValue()
        fieldtype_1    = self.ctrl[('Textbox', uc.数据类型[1])].GetValue()
        comparer_1     = self.ctrl[('Combobox', uc.比较符[1])].GetValue()
        value_1        = self.ctrl[('Textbox', uc.筛选值[1])].GetValue()
        if value_1.find('|') < 0:
            if fieldtype_1 == '整数型':
                try:
                    value_1 = int(value_1.replace(',', ''))
                except:
                    value_1 = 0
            elif fieldtype_1 == '浮点型':
                try:
                    value_1 = float(value_1.replace(',', ''))
                except:
                    value_1 = 0.0
            elif fieldtype_1 == '日期型':
                try:
                    value_1 = datetime.date(*time.strptime(value_1, "%Y-%m-%d")[:3])
                except:
                    value_1 = datetime.date.today()
            if logic:
                str_case += ' %s 【%s %s %s】' % (logic, field_1, comparer_1, str(value_1))
        else:
            if logic:
                str_case += ' %s 【%s %s %s】' % (logic, field_1, comparer_1, str(value_1))
            value_1 = value_1.split('|')
        logic = 'AND' if logic == '并且' else logic
        logic = 'OR' if logic == '或者' else logic
        if comparer_0 == '大于':
            sql0      = '{}>%s'.format(field_0)
            value     = value_0
        elif comparer_0 == '小于':
            sql0      = '{}<%s'.format(field_0)
            value     = value_0
        elif comparer_0 == '大于等于':
            sql0      = '{}>=%s'.format(field_0)
            value     = value_0
        elif comparer_0 == '小于等于':
            sql0      = '{}<=%s'.format(field_0)
            value     = value_0
        elif comparer_0 == '等于':
            sql0      = '{}=%s'.format(field_0)
            value     = value_0
        elif comparer_0 == '不等于':
            sql0      = '{}<>%s'.format(field_0)
            value     = value_0
        elif comparer_0 == '包含':
            sql0      = "{} LIKE %s".format(field_0)
            value     = '%' + value_0 + '%'
        elif comparer_0 == '不包含':
            sql0      = "{} NOT LIKE %s".format(field_0)
            value     = '%' + value_0 + '%'
        elif comparer_0 == '开头是':
            sql0      = "{} LIKE %s".format(field_0)
            value     = value_0 + '%'
        elif comparer_0 == '开头不是':
            sql0      = "{} NOT LIKE %s".format(field_0)
            value     = value_0 + '%'
        elif comparer_0 == '结尾是':
            sql0      = "{} LIKE %s".format(field_0)
            value     = '%' + value_0
        elif comparer_0 == '结尾不是':
            sql0      = "{} NOT LIKE %s".format(field_0)
            value     = '%' + value_0
        elif comparer_0 == '属于':
            sql0      = "{} IN %s".format(field_0)
            value     = value_0
        sql = sql0
        sql_list = [value]
        if logic:
            if comparer_1 == '大于':
                sql1      = '{}>%s'.format(field_1)
                value     = value_1
            elif comparer_1 == '小于':
                sql1      = '{}<%s'.format(field_1)
                value     = value_1
            elif comparer_1 == '大于等于':
                sql1      = '{}>=%s'.format(field_1)
                value     = value_1
            elif comparer_1 == '小于等于':
                sql1      = '{}<=%s'.format(field_1)
                value     = value_1
            elif comparer_1 == '等于':
                sql1      = '{}=%s'.format(field_1)
                value     = value_1
            elif comparer_1 == '不等于':
                sql1      = '{}<>%s'.format(field_1)
                value     = value_1
            elif comparer_1 == '包含':
                sql1      = "{} LIKE %s".format(field_1)
                value     = '%' + value_1 + '%'
            elif comparer_1 == '不包含':
                sql1      = "{} NOT LIKE %s".format(field_1)
                value     = '%' + value_1 + '%'
            elif comparer_1 == '开头是':
                sql1      = "{} LIKE %s".format(field_1)
                value     = value_1 + '%'
            elif comparer_1 == '开头不是':
                sql1      = "{} NOT LIKE %s".format(field_1)
                value     = value_1 + '%'
            elif comparer_1 == '结尾是':
                sql1      = "{} LIKE %s".format(field_1)
                value     = '%' + value_1
            elif comparer_1 == '结尾不是':
                sql1      = "{} NOT LIKE %s".format(field_1)
                value     = '%' + value_1
            elif comparer_0 == '属于':
                sql1      = "{} IN %s".format(field_1)
                value     = value_1
            sql = '({} {} {})'.format(sql0, logic, sql1)
            sql_list.append(value)
        logic = '并且' if logic == 'AND' else logic
        logic = '并且' if logic == 'OR' else logic
        ctrl_value = [field_0, fieldtype_0, comparer_0, value_0, logic, field_1, fieldtype_1, comparer_1, value_1]
        return [str_case, [sql, sql_list, ctrl_value]]
    def FillCtrls(self, n):
        try:
            field_0, fieldtype_0, comparer_0, value_0, logic, field_1, fieldtype_1, comparer_1, value_1 = self.filter_case[n][1][2]
        except:
            self.ClearCtrls()
            return
        self.ctrl[('Combobox', uc.筛选字段[0])].SetValue(str(field_0))
        self.ctrl[('Textbox', uc.数据类型[0])].SetValue(str(fieldtype_0))
        if fieldtype_0 in '整数型 浮点型 日期型'.split():
            self.ctrl[('Combobox', uc.比较符[0])].Clear()
            self.ctrl[('Combobox', uc.比较符[0])].AppendItems('大于 小于 大于等于 小于等于 等于 不等于 属于'.split())
        elif fieldtype_0 == '字符串型':
            self.ctrl[('Combobox', uc.比较符[0])].Clear()
            self.ctrl[('Combobox', uc.比较符[0])].AppendItems('等于 不等于 包含 不包含 开头是 开头不是 结尾是 结尾不是 属于'.split())
        self.ctrl[('Combobox', uc.比较符[0])].SetValue(str(comparer_0))
        if str(type(value_0)) == "<class 'list'>":
            self.ctrl[('Textbox', uc.筛选值[0])].SetValue('|'.join(map(str, value_0)))
        else:
            self.ctrl[('Textbox', uc.筛选值[0])].SetValue(str(value_0))
        self.ctrl[('Combobox', uc.逻辑符)].SetValue(str(logic))
        self.ctrl[('Combobox', uc.筛选字段[1])].SetValue(str(field_1))
        self.ctrl[('Textbox', uc.数据类型[1])].SetValue(str(fieldtype_1))
        if fieldtype_1 in '整数型 浮点型 日期型'.split():
            self.ctrl[('Combobox', uc.比较符[1])].Clear()
            self.ctrl[('Combobox', uc.比较符[1])].AppendItems('大于 小于 大于等于 小于等于 等于 不等于 属于'.split())
        elif fieldtype_1 == '字符串型':
            self.ctrl[('Combobox', uc.比较符[1])].Clear()
            self.ctrl[('Combobox', uc.比较符[1])].AppendItems('等于 不等于 包含 不包含 开头是 开头不是 结尾是 结尾不是 属于'.split())
        self.ctrl[('Combobox', uc.比较符[1])].SetValue(str(comparer_1))
        if str(type(value_1)) == "<class 'list'>":
            self.ctrl[('Textbox', uc.筛选值[1])].SetValue('|'.join(map(str, value_1)))
        else:
            self.ctrl[('Textbox', uc.筛选值[1])].SetValue(str(value_1))
        self.hide_or_show_condition2()
    def ClearCtrls(self):
        self.ctrl[('Combobox', uc.筛选字段[0])].SetSelection(0)
        self.ctrl[('Combobox', uc.筛选字段[1])].SetSelection(0)
        self.ctrl[('Textbox', uc.数据类型[0])].SetValue(self.fields_type[0])
        self.ctrl[('Textbox', uc.数据类型[1])].SetValue(self.fields_type[0])
        if self.fields_type[0] in '整数型 浮点型 日期型'.split():
            self.ctrl[('Combobox', uc.比较符[0])].Clear()
            self.ctrl[('Combobox', uc.比较符[0])].AppendItems('大于 小于 大于等于 小于等于 等于 不等于 属于'.split())
        elif self.fields_type[0] == '字符串型':
            self.ctrl[('Combobox', uc.比较符[0])].Clear()
            self.ctrl[('Combobox', uc.比较符[0])].AppendItems('等于 不等于 包含 不包含 开头是 开头不是 结尾是 结尾不是 属于'.split())
        if self.fields_type[0] in '整数型 浮点型 日期型'.split():
            self.ctrl[('Combobox', uc.比较符[1])].Clear()
            self.ctrl[('Combobox', uc.比较符[1])].AppendItems('大于 小于 大于等于 小于等于 等于 不等于 属于'.split())
        elif self.fields_type[0] == '字符串型':
            self.ctrl[('Combobox', uc.比较符[1])].Clear()
            self.ctrl[('Combobox', uc.比较符[1])].AppendItems('等于 不等于 包含 不包含 开头是 开头不是 结尾是 结尾不是 属于'.split())
        self.ctrl[('Combobox', uc.比较符[0])].SetSelection(0)
        self.ctrl[('Combobox', uc.比较符[1])].SetSelection(0)
        self.ctrl[('Combobox', uc.逻辑符)].SetSelection(1)
        self.ctrl[('Textbox', uc.筛选值[0])].SetValue('')
        self.ctrl[('Textbox', uc.筛选值[1])].SetValue('')
        self.ctrl[('Textbox', uc.筛选值[0])].SetEditable(True)
        self.ctrl[('Textbox', uc.筛选值[1])].SetEditable(True)
        self.hide_or_show_condition2()
    def FillListbox(self):
        if not self.filter_case:
            return
        data = list(x[0] for x in self.filter_case)
        self.ctrl[('Listbox', uc.筛选器)].AppendItems(data)

class TreeDialog(wx.Dialog):
    __result = None
    def __init__(self):
        self.init()
    def init(self):
        wx.Dialog.__init__(self, None, -1, '树形结构查看器', size=uc.Size_BigDialog, style=wx.CAPTION|wx.CLOSE_BOX|wx.MAXIMIZE_BOX)
        self.Centre(wx.BOTH)
        # Create the tree
        self.tree = wx.dataview.TreeListCtrl(self, style = wx.dataview.TL_SINGLE|wx.TR_FULL_ROW_HIGHLIGHT, size=uc.Size_BigDialog)
        self.tree.AppendColumn("项目名称-分项名称", align=wx.ALIGN_CENTER)
        self.tree.AppendColumn("合同名称", align=wx.ALIGN_RIGHT)
        self.tree.AppendColumn("项目概算", align=wx.ALIGN_RIGHT)
        self.tree.AppendColumn("概算已分配率", align=wx.ALIGN_RIGHT)
        self.tree.AppendColumn("概算付款比", align=wx.ALIGN_RIGHT)
        self.tree.AppendColumn("招标方式", align=wx.ALIGN_CENTER)
        self.tree.AppendColumn("中标价", align=wx.ALIGN_RIGHT)
        self.tree.AppendColumn("合同值", align=wx.ALIGN_RIGHT)        
        self.tree.AppendColumn("合同付款比", align=wx.ALIGN_RIGHT)
        self.tree.AppendColumn("已付款", align=wx.ALIGN_RIGHT)
        self.tree.AppendColumn("层级", align=wx.ALIGN_CENTER)
        self.treeData = operateDB().format_Contract_Details_By_Tree()
        root = self.tree.GetRootItem()
        self.makeTree(root, self.treeData)
        # buttons
        self.button_Collapse = []
        for i in range(1, 8):
            self.button_Collapse.append(wx.Button(self, -1, label=str(i), size=uc.Size_Button_MiniDialog))
        self.button_OK = wx.Button(self, wx.ID_OK, size=uc.Size_Button_BaseDialog)
        self.button_CANCEL = wx.Button(self, wx.ID_CANCEL, size=uc.Size_Button_BaseDialog)
        # sizers
        sizer = wx.BoxSizer(wx.VERTICAL)
        hsz = wx.BoxSizer(wx.HORIZONTAL)
        for i in range(7):
            hsz.Add(self.button_Collapse[i], 0, wx.ALL, 5)
        hsz.AddSpacer(30)
        hsz.Add(self.button_OK, 0, wx.ALL, 5)
        hsz.Add(self.button_CANCEL, 0, wx.ALL, 5)
        sizer.Add(hsz, 0, wx.ALIGN_RIGHT|wx.ALL, 5)
        sizer.Add(self.tree, 1, wx.EXPAND|wx.ALL, 0)
        self.SetSizer(sizer)
        sizer.Fit(self)
        # events
        self.button_OK.Bind(wx.EVT_BUTTON, self.clickOnOK)
        for i in range(7):
            self.button_Collapse[i].Bind(wx.EVT_BUTTON, self.clickOnCollapse)
        self.tree.Bind(wx.dataview.EVT_TREELIST_ITEM_ACTIVATED, self.clickOnOK)
    def makeTree(self, root, treeData):
        def thousands(n): return '{:>,.2f}'.format(n)
        def percents(n): return '{:>.2f}'.format((n or 0) * 100) + '%'
        child = root
        for item in treeData:
            if str(type(item[0])) == "<class 'int'>":
                child = self.tree.AppendItem(root, str(item[0]) + '-' + item[1] + ('-' + item[2] if item[2] else '')) # 项目名称-分项名称
                self.tree.SetItemText(child, 1, str(item[3]) if item[3] else '')                                      # 合同名称
                self.tree.SetItemText(child, 2, thousands(item[4]) if item[4] is not None else '')                    # 项目概算
                self.tree.SetItemText(child, 3, percents(item[5]) if item[5] is not None else '')                     # 概算已分配率
                self.tree.SetItemText(child, 4, percents(item[6]) if item[6] is not None else '')                     # 概算付款比
                self.tree.SetItemText(child, 5, str(item[7]) if item[7] else '')                                      # 招标方式
                self.tree.SetItemText(child, 6, thousands(item[8]) if item[8] is not None else '')                    # 中标价
                self.tree.SetItemText(child, 7, thousands(item[9]) if item[9] is not None else '')                    # 合同值
                self.tree.SetItemText(child, 8, percents(item[10]) if item[10] is not None else '')                   # 合同付款比
                self.tree.SetItemText(child, 9, thousands(item[11]) if item[11] is not None else '')                  # 已付款
                self.tree.SetItemText(child, 10, str(item[-1]))                                                       # 层级
            else:
                self.makeTree(child, item)
    def SetValue(self, value): self.__result = value
    def GetValue(self): return self.__result
    def clickOnOK(self, event):
        try:
            UDID = int(self.tree.GetItemText(self.tree.GetSelection()).split('-')[0])
        except:
            UDID = None
        self.GetDataFromTreeData(self.treeData, UDID)
        self.EndModal(wx.ID_OK)
    def clickOnCollapse(self, event):
        Id = event.GetId()
        name = wx.FindWindowById(Id).GetLabel()
        def ExpandItemsByFloor(n):
            item = self.tree.GetRootItem()
            colnum = self.tree.GetColumnCount()
            while item:
                floor = int(self.tree.GetItemText(item, colnum-1) or 0)
                if floor < n:
                    self.tree.Expand(item)
                else:
                    self.tree.Collapse(item)
                item = self.tree.GetNextItem(item)
        ExpandItemsByFloor(int(name) - 1)
    def GetDataFromTreeData(self, parentItem, UDID):
        if not UDID:
            return
        for item in parentItem:
            if item[0] == UDID:
                self.SetValue(item)
            elif str(type(item[0])) != "<class 'list'>":
                pass
            else:
                self.GetDataFromTreeData(item, UDID)

class AttachFileDialog(wx.Dialog):
    __path = os.getcwd() + '\\attach\\立项\\' + '%s\\' % '000001'
    def __init__(self, classify='立项', UDID=1):
        self.init()
    def init(self):
        wx.Dialog.__init__(self, None, -1, '附件查看器', size=uc.Size_BaseDialog, style=wx.CAPTION|wx.CLOSE_BOX|wx.MAXIMIZE_BOX)
        self.Centre(wx.BOTH)
        self.list = wx.ListCtrl(self, -1, size=uc.Size_BaseDialog, style=wx.LC_REPORT|wx.LC_SINGLE_SEL)    # 创建列表
        self.LoadList()
        self.ctrl = {}
        self.ctrl[('Button', uc.打开)] = wx.Button(self, -1, uc.打开, size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.另存为)] = wx.Button(self, -1, uc.另存为, size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.删除)] = wx.Button(self, -1, uc.删除, size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.上传)] = wx.Button(self, -1, uc.上传, size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.下载)] = wx.Button(self, -1, uc.下载, size=uc.Size_Button_BaseDialog)
        self.ctrl[('Label', '')] = wx.StaticText(self, -1, '以下为<北王安置房-立项>的相关附件：')
        # 组合控件
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        titleSizer = wx.BoxSizer(wx.HORIZONTAL)
        titleSizer.AddSpacer(20)
        titleSizer.Add(self.ctrl[('Label', '')], 1, wx.ALL|wx.EXPAND, 5)
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.ctrl[('Button', uc.打开)], 0, wx.ALL, 5)
        buttonSizer.Add(self.ctrl[('Button', uc.另存为)], 0, wx.ALL, 5)
        buttonSizer.Add(self.ctrl[('Button', uc.删除)], 0, wx.ALL, 5)
        buttonSizer.Add(self.ctrl[('Button', uc.上传)], 0, wx.ALL, 5)
        buttonSizer.Add(self.ctrl[('Button', uc.下载)], 0, wx.ALL, 5)
        titleSizer.Add(buttonSizer, 0, wx.ALL, 0)
        mainSizer.Add(titleSizer, 0, wx.ALL|wx.EXPAND, 0)
        mainSizer.Add(self.list, 1, wx.ALL|wx.EXPAND, 0)
        self.SetSizer(mainSizer)
        self.Fit()
        for key, eachEvent, eachHandler in self.ctrlBindData():
            self.ctrl[key].Bind(eachEvent, eachHandler)

    # binder
    def ctrlBindData(self):
        return ((('Button',  uc.打开), wx.EVT_BUTTON, self.clickOnButton),
               )
    # events
    def clickOnButton(self, event):
        label = wx.FindWindowById(event.Id, self).GetLabel()
        if label == uc.打开:
            if not self.OpenFile():
                return
    # methods
    def traverseDir(self, path):
        if not os.path.exists(path):
            return []
        fileList = []
        for fileInfo in os.walk(path):
            dir = (fileInfo[0] + '\\').replace(path, '')
            for filename in fileInfo[2]:
                fileList.append((dir, filename))
        return fileList
    def LoadList(self):
        self.SetColumns('文件名 文件类型 修改时间 文件大小 缓存状况'.split())
        # 确定一下文件夹是否存在，不存在的话就新建一个
        try:
            os.makedirs(self.__path)
        except:
            pass
        for eachDir, eachFile in self.traverseDir(self.__path):
            self.list.Append([eachFile, eachFile.split('.')[-1], '', '', ''])
    def SetColumns(self, column_names):
        for i, column_name in enumerate(column_names):
            if i == 0:
                self.list.InsertColumn(i, column_name, format=wx.LIST_FORMAT_LEFT, width=400)
            else:
                self.list.InsertColumn(i, column_name, format=wx.LIST_FORMAT_CENTER)
    def AppendItems(self, items):
        for item in items:
            self.list.Append(item)
    def OpenFile(self):
        i = self.list.GetFocusedItem()
        if i < 0:
            dlg = wx.MessageDialog(self, message='请先选择一个文件', caption='提示', style=wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        # 若未缓存，提示“请先下载该文件”
        filename = self.list.GetItemText(i)
        filepath = self.__path + filename
        os.startfile(filepath)
        return True

class JumpDialog(wx.Dialog):
    __value = None
    def __init__(self, Label='', Choices=[]):
        super(JumpDialog, self).__init__()
        self.Label = Label
        self.sampleList = Choices
        self.init()
    def init(self):
        wx.Dialog.__init__(self, None, -1, self.Label, size=uc.Size_BaseDialog, style=wx.CAPTION|wx.CLOSE_BOX|wx.MAXIMIZE_BOX)
        self.Centre(wx.BOTH)
        self.list = wx.ListBox(self, -1, size=(300, 200), choices=self.sampleList, style=wx.LB_SINGLE)
        self.list.SetSelection(0)
        self.__value = self.list.GetString(self.list.GetSelection())
        self.ctrl = {}
        self.ctrl[('Button', uc.OK)] = wx.Button(self, -1, uc.OK, size=uc.Size_Button_BaseDialog)
        self.ctrl[('Button', uc.CANCEL)] = wx.Button(self, -1, uc.CANCEL, size=uc.Size_Button_BaseDialog)
        self.ctrl[('Label', '')] = wx.StaticText(self, -1, '')
        # 组合控件
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        titleSizer = wx.BoxSizer(wx.HORIZONTAL)
        titleSizer.AddSpacer(20)
        titleSizer.Add(self.ctrl[('Label', '')], 1, wx.ALL|wx.EXPAND, 5)
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.ctrl[('Button', uc.OK)], 0, wx.ALL, 5)
        buttonSizer.Add(self.ctrl[('Button', uc.CANCEL)], 0, wx.ALL, 5)
        titleSizer.Add(buttonSizer, 0, wx.ALL, 0)
        mainSizer.Add(titleSizer, 0, wx.ALL|wx.EXPAND, 0)
        mainSizer.Add(self.list, 1, wx.ALL|wx.EXPAND, 0)
        self.SetSizer(mainSizer)
        self.Fit()
        self.list.Bind(wx.EVT_LISTBOX, self.clickOnList)
        for key, eachEvent, eachHandler in self.ctrlBindData():
            self.ctrl[key].Bind(eachEvent, eachHandler)

    # binder
    def ctrlBindData(self):
        return ((('Button',  uc.OK), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.CANCEL), wx.EVT_BUTTON, self.clickOnButton)
               )
    # events
    def clickOnList(self, event):
        self.__value = self.list.GetString(self.list.GetSelection())
    def clickOnButton(self, event):
        label = wx.FindWindowById(event.Id, self).GetLabel()
        if label == uc.OK:
            self.EndModal(wx.ID_OK)
        elif label == uc.CANCEL:
            self.EndModal(wx.ID_CANCEL)
    # methods
    def GetValue(self):
        return self.__value

if __name__ == '__main__':
    app = wx.App()
    # dlg = Initiation_TreeDialog()
    dlg = JumpDialog()
    if dlg.ShowModal() == wx.ID_OK:
        print(dlg.GetValue())
    dlg.Destroy()
    app.Destroy()
    pass