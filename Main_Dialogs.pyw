#!/usr/bin/env python
# -*- coding: utf-8 -*-

from gui import *
from Base_Dialogs import *
from background import *

class Company_GridDialog(GridDialog):
    __value = None
    __colLabels = uc.CompanyFields
    __colLabels_type = uc.CompanyFields_Type
    filter_case = []
    def __init__(self, title='单位信息', data=None, size=uc.Size_BaseDialog, limit=False, where_sql='' ,where_list=[]):
        self.init(title, data, size)
        self.ctrl[('Button', uc.查询结构)].Enable(False)
        if limit:
            self.ctrl[('Button', uc.筛选)].Enable(False)
            self.ctrl[('Button', uc.刷新)].Enable(False)
        for eachEvent, eachHandler in self.gridBindData():
            self.ctrl[('Grid', None)].Bind(eachEvent, eachHandler)
        for key, eachEvent, eachHandler in self.ctrlBindData():
            self.ctrl[key].Bind(eachEvent, eachHandler)
        self.readDB_and_reFreshGrid(where_sql=where_sql, where_list=where_list)
        self.ctrl[('Grid', None)].SelectRow(0)
    # binder
    def gridBindData(self):
        return ((wx.grid.EVT_GRID_LABEL_LEFT_CLICK,  self.labelOnClick),
                (wx.grid.EVT_GRID_SELECT_CELL,       self.gridOnSelectACell),
                (wx.grid.EVT_GRID_LABEL_LEFT_DCLICK, self.labelOnDCLICK),
                (wx.grid.EVT_GRID_CELL_RIGHT_CLICK,  self.gridOnRClick),
                (wx.grid.EVT_GRID_CELL_LEFT_DCLICK,  self.gridOnDClick))
    def ctrlBindData(self):
        return ((('Button',  uc.新建), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.修改), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.筛选), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.刷新), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.导出), wx.EVT_BUTTON, self.clickOnButton),
               )
    # events
    def clickOnButton(self, event):
        label = wx.FindWindowById(event.Id, self).GetLabel()
        if label == uc.刷新:
            self.readDB_and_reFreshGrid()
            self.filter_case = []
        elif label == uc.新建:
            dlg = Company_MaintainDialog(uc.Dialog_New)
            dlg.ShowModal()
            dlg.Destroy()
            self.readDB_and_reFreshGrid()
        elif label == uc.修改:
            data = self.GetValue()
            dlg = Company_MaintainDialog(uc.Dialog_Edit, data[0])
            dlg.ShowModal()
            dlg.Destroy()
            self.readDB_and_reFreshGrid()
        elif label == uc.筛选:
            dlg = FilterDialog(self.__colLabels, self.__colLabels_type, self.filter_case)
            if dlg.ShowModal() == wx.ID_OK:
                self.filter_case = dlg.GetValue()
            dlg.Destroy()
            # 整理出where_sql和where_list
            if not self.filter_case:
                return
            where_sql = []
            where_list = []
            for each_filter in self.filter_case:
                where_sql.append(each_filter[1][0])
                where_list.extend(each_filter[1][1])
            where_sql = 'WHERE ' + ' AND '.join(where_sql)
            self.readDB_and_reFreshGrid(where_sql, where_list)
        elif label == uc.导出:
            wildcard = 'Excel files (*.xlsx)|*.xlsx'
            dlg = wx.FileDialog(None, "Choose a file", '', '', wildcard, 0)    #选择文件对话框
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            dlg.Destroy()
            filename = dlg.GetPath()
            if os.path.exists(filename):
                dlg = wx.MessageDialog(self, message='该文件已存在，点击<是>覆盖文件', caption='警告', style= wx.YES_NO | wx.NO_DEFAULT)
                if dlg.ShowModal() == wx.ID_NO:
                    dlg.Destroy()
                    return
                else:
                    dlg.Destroy()
            data = self.ctrl[('Grid', None)].GetTable().data
            try:
                Exporter().commonExport(filename, self.ctrl[('Grid', None)], self.__colLabels, data)
                dlg = wx.MessageDialog(self, message='文件导出成功', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except Exception as e:
                dlg = wx.MessageDialog(self, message='文件导出失败！\n%s' % str(e), caption='警告', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
    def labelOnClick(self, event):
        col = event.GetCol()
        isCtrl = event.ControlDown()
        isShift = event.ShiftDown()
        if col >= 0 and isCtrl:
            data = self.get_data_by_sortGrid(self.ctrl[('Grid', None)], col, False, self.__colLabels_type)
            self.reFreshGrid(self.ctrl[('Grid', None)], data, self.__colLabels)
        elif col >= 0 and isShift:
            data = self.get_data_by_sortGrid(self.ctrl[('Grid', None)], col, True, self.__colLabels_type)
            self.reFreshGrid(self.ctrl[('Grid', None)], data, self.__colLabels)
        else:
            return
    def gridOnSelectACell(self, event):
        row = event.GetRow()
        result = self.SetValue(row)
        if result:
            self.ctrl[('Textbox', uc.显示窗)].SetValue('%d-%s' % (result[self.__colLabels.index('单位识别码')], result[self.__colLabels.index('单位名称')]))
    def labelOnDCLICK(self, event):
        col = event.GetCol()
        data = self.ctrl[('Grid', None)].GetTable().data
        colLabels = self.ctrl[('Grid', None)].GetTable().colLabels
        values = []
        def thousands(n):
            return '{:>,.2f}'.format(n)
        if self.__colLabels_type[col] in '整数型 浮点型'.split():
            for key, value in data.items():
                if key[1] == col and value is not None:
                    values.append(value)
            try:
                dlg = wx.MessageDialog(self, message='<%s>列下：\n共有<%d>个值，\n和为<%s>，\n最大值为<%s>，\n最小值为<%s>' \
                                       % (colLabels[col], len(values), thousands(sum(values)), thousands(max(values)), thousands(min(values))),
                                       caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except:
                pass
        elif self.__colLabels_type[col] in ['日期型']:
            for key, value in data.items():
                if key[1] == col and value is not None:
                    values.append(value)
            try:
                dlg = wx.MessageDialog(self, message='<%s>列下：\n共有<%d>个值，\n最大值为<%s>，\n最小值为<%s>' % (colLabels[col], len(values), max(values), min(values)),
                                       caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except:
                pass
    def gridOnDClick(self, event):
        self.EndModal(wx.ID_OK)
    def gridOnRClick(self, event):
        row = event.GetRow()
        if row >= 0:
            self.SetValue(row)
            self.ctrl[('Grid', None)].SelectRow(row)
            self.checkCompany()
    # methods
    def checkCompany(self):
        data = self.GetValue()
        dlg = Company_MaintainDialog(uc.Dialog_Check, data[0])
        dlg.ShowModal()
        dlg.Destroy()
        self.readDB_and_reFreshGrid()
    def GetValue(self):
        return self.__value
    def SetValue(self, row):
        data = self.ctrl[('Grid', None)].GetTable().data
        colLabels = self.ctrl[('Grid', None)].GetTable().colLabels
        try:
            rownum = max(data.keys())[0] + 1
        except:
            rownum = 0
        colnum = len(colLabels)
        result = []
        if rownum == 0:
            return
        for col in range(colnum):
            result.append(data.get((row, col)))
        self.__value = result
        return result
    def readDB(self, where_sql='', where_list=[], order_sql='', order_list=[]):
        return operateDB().read_For_Company_GridDialog(where_sql, where_list, order_sql, order_list)
    def readDB_and_reFreshGrid(self, where_sql='', where_list=[], order_sql='', order_list=[]):
        data = self.format_DBdata2Griddata(self.readDB(where_sql, where_list, order_sql, order_list))
        self.reFreshGrid(self.ctrl[('Grid', None)], data, self.__colLabels)

class Company_MaintainDialog(MaintainDialog):
    __mode = uc.Dialog_Check
    __value = None
    __save_point = None
    __ctrl_key = list(zip('Textbox Textbox Combobox Combobox'.split() + ['Textbox'] * 7, uc.CompanyColLabels))
    __ctrl_value_type = uc.CompanyColLabels_Type
    def __init__(self, mode=uc.Dialog_Check, UDID=-1):
        self.init()
        little_sizer = {}
        def create_Label_Textbox_Pairs(key, size_Textbox):
            little_sizer[key] = wx.BoxSizer(wx.HORIZONTAL)
            self.ctrl[('Label', key)] = wx.StaticText(self, -1, key+'：', size=uc.Size_Label_Company_MaintainDialog, style=wx.ALIGN_RIGHT)
            self.ctrl[('Textbox', key)] = wx.TextCtrl(self, -1, '', size=size_Textbox, style=wx.TE_READONLY|wx.TE_CENTRE|wx.BORDER_STATIC)
            little_sizer[key].Add(self.ctrl[('Label', key)])
            little_sizer[key].Add(self.ctrl[('Textbox', key)])
        def create_Label_MultiTextbox_Pairs(key, size_Textbox, size_Label=uc.Size_Label_BaseDialog):
            little_sizer[key] = wx.BoxSizer(wx.HORIZONTAL)
            self.ctrl[('Label', key)] = wx.StaticText(self, -1, key+'：', size=size_Label, style=wx.ALIGN_RIGHT)
            self.ctrl[('Textbox', key)] = wx.TextCtrl(self, -1, '', size=size_Textbox, style=wx.TE_READONLY|wx.BORDER_STATIC|wx.TE_MULTILINE, name=key)
            little_sizer[key].Add(self.ctrl[('Label', key)])
            little_sizer[key].Add(self.ctrl[('Textbox', key)])
        def create_Label_Combobox_Pairs(key, size_Combobox):
            little_sizer[key] = wx.BoxSizer(wx.HORIZONTAL)
            self.ctrl[('Label', key)] = wx.StaticText(self, -1, key+'：', size=uc.Size_Label_Company_MaintainDialog, style=wx.ALIGN_RIGHT)
            style = wx.TE_PROCESS_ENTER|wx.CB_DROPDOWN|wx.TE_CENTER
            self.ctrl[('Combobox', key)] = wx.ComboBox(self, -1, value='', size=size_Combobox, choices=[], style=style)
            little_sizer[key].Add(self.ctrl[('Label', key)])
            little_sizer[key].Add(self.ctrl[('Combobox', key)])
        # 重绘控件
        create_Label_Textbox_Pairs( '单位识别码', uc.Size_Textbox_Short_BaseDialog   )
        create_Label_Textbox_Pairs( '单位名称'  , uc.Size_Textbox_Long_BaseDialog    )
        create_Label_Combobox_Pairs('单位类别'  , uc.Size_Combobox_Short_BaseDialog  )
        create_Label_Combobox_Pairs('单位性质'  , uc.Size_Combobox_Short_BaseDialog  )
        create_Label_Textbox_Pairs( '法定代表人', uc.Size_Textbox_Short_BaseDialog   )
        create_Label_Textbox_Pairs( '注册资金'  , uc.Size_Textbox_Normal_BaseDialog  )
        create_Label_Textbox_Pairs( '单位资质'  , uc.Size_Textbox_Long_BaseDialog    )
        create_Label_Textbox_Pairs( '银行账号'  , uc.Size_Textbox_Long_BaseDialog    )
        create_Label_Textbox_Pairs( '联系人'    , uc.Size_Textbox_Normal_BaseDialog  )
        create_Label_Textbox_Pairs( '联系方式'  , uc.Size_Textbox_Normal_BaseDialog  )
        create_Label_MultiTextbox_Pairs( '单位备注'    , uc.Size_Textbox_Note)
        self.ctrl[('Combobox', '单位类别')].AppendItems('房地产开发 前期咨询 勘察 设计 造价 施工 材料设备 监理'.split())
        self.ctrl[('Combobox', '单位性质')].AppendItems('国有企业 行政单位 非国有企业'.split())
        core_sizer = wx.BoxSizer(wx.VERTICAL)
        row_sizer = []
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['单位识别码'   ])
        row_sizer[-1].Add(little_sizer['单位名称'     ])
        row_sizer[-1].Add(little_sizer['法定代表人'   ])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['单位类别'     ])
        row_sizer[-1].Add(little_sizer['单位性质'     ])
        row_sizer[-1].Add(little_sizer['注册资金'     ])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['单位资质'     ])
        row_sizer[-1].Add(little_sizer['联系人'       ])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['银行账号'     ])
        row_sizer[-1].Add(little_sizer['联系方式'     ])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['单位备注'     ])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        self.sizer.Add(core_sizer, 0, wx.ALL, 10)
        self.SetSizer(self.all_sizer)
        self.all_sizer.Fit(self)
        for key, eachEvent, eachHandler in self.ctrlBindData():
            self.ctrl[key].Bind(eachEvent, eachHandler)
        # 检查模式
        self.ChangeMode(mode, UDID)    # 通过识别码读取信息
        self.SaveTap(self.FormatInfoFromUI())
    # binder
    def ctrlBindData(self):
        return ((('Button',  uc.新建), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.修改), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.保存), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.取消), wx.EVT_BUTTON, self.clickOnButton)
               )
    # events
    def clickOnButton(self, event):
        label = wx.FindWindowById(event.Id, self).GetLabel()
        if label == uc.新建:
            self.SaveTap(self.FormatInfoFromUI())
            self.ChangeMode(uc.Dialog_New)
        elif label == uc.修改:
            self.SaveTap(self.FormatInfoFromUI())
            try:
                UDID = int(self.ctrl[('Textbox', '单位识别码')].GetValue())
            except:
                UDID = 0
            self.ChangeMode(uc.Dialog_Edit, UDID)
        elif label == uc.取消:
            hasChanged = self.FormatInfoFromUI() != self.LoadTap()
            if hasChanged:
                dlg = wx.MessageDialog(self, message='更改的数据尚未保存，你确定要退出吗？', caption='警告', style= wx.YES_NO | wx.NO_DEFAULT)
                if dlg.ShowModal() == wx.ID_NO:
                    dlg.Destroy()
                    return
                else:
                    dlg.Destroy()
            self.ChangeMode(uc.Dialog_Check)
            self.FillBlanks(self.LoadTap())
        elif label == uc.保存:
            hasChanged = self.FormatInfoFromUI() != self.LoadTap()
            if not hasChanged:
                dlg = wx.MessageDialog(self, message='数据并未做任何更改，不需要保存。', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            dlg = wx.MessageDialog(self, message='点击确定保存数据。', caption='提示', style= wx.YES_NO | wx.NO_DEFAULT)
            if dlg.ShowModal() == wx.ID_NO:
                dlg.Destroy()
                return
            else:
                dlg.Destroy()
            data = self.FormatInfoForDB()
            UDID = data[0]
            save_result = operateDB().save_For_Company_MaintainDialog(data)
            try:
                assert save_result
                dlg = wx.MessageDialog(self, message='数据保存成功。', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except Exception as e:
                dlg = wx.MessageDialog(self, message='数据保存失败\n%s' % str(e), caption='警告', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            self.ChangeMode(uc.Dialog_Check, UDID)
            self.SaveTap(data)
    # methods
    def GetValue(self):
        return self.__value
    def SetValue(self):
        self.__value = []
        for each_ctrl_key, each_value_type in zip(self.__ctrl_key, self.__ctrl_value_type):
            value = self.ctrl[each_ctrl_key].GetValue()
            try:
                if value == '':
                    value = None
                elif each_value_type == '整数型':
                    value = int(value)
                elif each_value_type == '浮点型':
                    value = decimal.Decimal(value.strip().replace(',', ''))
            except:
                value = None
            self.__value.append(value)
        return self.__value
    def LoadTap(self):
        return self.__save_point
    def SaveTap(self, data=[]):
        self.__save_point = data
    def FormatInfoFromUI(self, ifReport=False):
        data = []
        for i, each_ctrl_key in zip(range(len(self.__ctrl_key)), self.__ctrl_key):
            value = self.ctrl[each_ctrl_key].GetValue()
            if len(value) == 0:
                value = None
            elif self.__ctrl_value_type[i] == '整数型':
                try:
                    value = int(value)
                except:
                    value = None
                    if ifReport:
                        dlg = wx.MessageDialog(self, message='<%s>中数据未能识别，将记录为NULL值' % each_ctrl_key[1], caption='警告', style=wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
            elif self.__ctrl_value_type[i] == '浮点型':
                try:
                    value = decimal.Decimal(value.strip().replace(',', ''))
                except:
                    value = None
                    if ifReport:
                        dlg = wx.MessageDialog(self, message='<%s>中数据未能识别，将记录为NULL值' % each_ctrl_key[1], caption='警告', style=wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
            elif self.__ctrl_value_type[i] == '日期型':
                try:
                    value = datetime.date(*time.strptime(value, "%Y-%m-%d")[:3])
                except:
                    value = None
                    if ifReport:
                        dlg = wx.MessageDialog(self, message='<%s>中数据未能识别，将记录为NULL值' % each_ctrl_key[1], caption='警告', style=wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
            data.append(value)
        return data
    def FormatInfoForDB(self):
        data = self.FormatInfoFromUI(True)
        result = []
        for key, value in zip(uc.CompanyColLabels, data):
            if key in uc.CompanyFields:
                result.append(value)
        return result
    def GetDataFromUDID(self, UDID):
        try:
            result = operateDB().read_For_Company_GridDialog(where_sql='WHERE 单位识别码=%s', where_list=[UDID])[0]
        except:
            result = None
        return result
    def ChangeMode(self, mode, UDID=None):
        if mode == uc.Dialog_Check:
            self.__mode = mode
            data = self.GetDataFromUDID(UDID) if UDID else []
            self.SetTitle('查看单位信息')
            for each_ctrl_key in self.__ctrl_key:
                if each_ctrl_key[0] == 'Textbox':
                    self.ctrl[each_ctrl_key].SetEditable(False)                    
                elif each_ctrl_key[0] == 'Combobox':
                    self.ctrl[each_ctrl_key].Enable(False)
            self.ctrl[('Button', uc.新建)].Enable(True)
            self.ctrl[('Button', uc.修改)].Enable(True)
            self.ctrl[('Button', uc.保存)].Enable(False)
            self.ctrl[('Button', uc.取消)].Enable(False)
            self.FillBlanks(data)
        elif mode == uc.Dialog_New:
            self.__mode = mode
            self.SetTitle('新建单位信息')
            for each_ctrl_key in self.__ctrl_key:
                if each_ctrl_key[0] == 'Textbox':
                    self.ctrl[each_ctrl_key].SetEditable(True)
                elif each_ctrl_key[0] == 'Combobox':
                    self.ctrl[each_ctrl_key].Enable(True)
            self.ctrl[('Textbox', '单位识别码')].SetEditable(False)
            self.ctrl[('Button', uc.新建)].Enable(False)
            self.ctrl[('Button', uc.修改)].Enable(False)
            self.ctrl[('Button', uc.保存)].Enable(True)
            self.ctrl[('Button', uc.取消)].Enable(True)
            self.FillBlanks()
        elif mode == uc.Dialog_Edit:
            try:
                data = self.GetDataFromUDID(UDID) if UDID else []
                assert data
            except:
                dlg = wx.MessageDialog(self, message='该单位识别码数据库中未记录，请检查', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            self.__mode = mode
            self.SetTitle('修改单位信息')
            for each_ctrl_key in self.__ctrl_key:
                if each_ctrl_key[0] == 'Textbox':
                    self.ctrl[each_ctrl_key].SetEditable(True)
                elif each_ctrl_key[0] == 'Combobox':
                    self.ctrl[each_ctrl_key].Enable(True)
            self.ctrl[('Textbox', '单位识别码')].SetEditable(False)
            self.ctrl[('Button', uc.新建)].Enable(False)
            self.ctrl[('Button', uc.修改)].Enable(False)
            self.ctrl[('Button', uc.保存)].Enable(True)
            self.ctrl[('Button', uc.取消)].Enable(True)
            self.FillBlanks(data)
    def FillBlanks(self, data=[]):
        def thousands(n): return '{:>,.2f}'.format(n)
        def percents(n): return '{:>.2f}'.format((n or 0) * 100) + '%'
        for each_ctrl_key in self.__ctrl_key:
            try:
                value = data[self.__ctrl_key.index(each_ctrl_key)]
                value_type = self.__ctrl_value_type[self.__ctrl_key.index(each_ctrl_key)]
                if value is None:
                    value = ''
                elif value_type == '浮点型':
                    value = thousands(value)
                elif value_type == '百分比':
                    value = percents(value)
                else:
                    value = str(value)
                self.ctrl[each_ctrl_key].SetValue(value)
            except:
                self.ctrl[each_ctrl_key].SetValue('')

class Initiation_GridDialog(GridDialog):
    __value = None
    __colLabels = uc.InitiationColLabels
    __colLabels_type = uc.InitiationColLabels_Type
    filter_case = []
    def __init__(self, title='立项信息', data=None, size=uc.Size_BaseDialog, limit=False, where_sql='' ,where_list=[]):
        self.init(title, data, size)
        if limit:
            self.ctrl[('Button', uc.筛选)].Enable(False)
            self.ctrl[('Button', uc.查询结构)].Enable(False)
            self.ctrl[('Button', uc.刷新)].Enable(False)
        for eachEvent, eachHandler in self.gridBindData():
            self.ctrl[('Grid', None)].Bind(eachEvent, eachHandler)
        for key, eachEvent, eachHandler in self.ctrlBindData():
            self.ctrl[key].Bind(eachEvent, eachHandler)
        self.readDB_and_reFreshGrid(where_sql=where_sql, where_list=where_list)
        self.ctrl[('Grid', None)].SelectRow(0)
    # binder
    def gridBindData(self):
        return ((wx.grid.EVT_GRID_LABEL_LEFT_CLICK,  self.labelOnClick),
                (wx.grid.EVT_GRID_SELECT_CELL,       self.gridOnSelectACell),
                (wx.grid.EVT_GRID_LABEL_LEFT_DCLICK, self.labelOnDCLICK),
                (wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.gridOnRClick),
                (wx.grid.EVT_GRID_CELL_LEFT_DCLICK,  self.gridOnDClick))
    def ctrlBindData(self):
        return ((('Button',  uc.新建),     wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.修改),     wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.筛选),     wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.查询结构), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.刷新),     wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.导出),     wx.EVT_BUTTON, self.clickOnButton),
               )
    # events
    def clickOnButton(self, event):
        label = wx.FindWindowById(event.Id, self).GetLabel()
        if label == uc.刷新:
            self.readDB_and_reFreshGrid()
            self.filter_case = []
        elif label == uc.新建:
            dlg = Initiation_MaintainDialog(uc.Dialog_New)
            dlg.ShowModal()
            dlg.Destroy()
            self.readDB_and_reFreshGrid()
        elif label == uc.修改:
            data = self.GetValue()
            dlg = Initiation_MaintainDialog(uc.Dialog_Edit, data[0])
            dlg.ShowModal()
            dlg.Destroy()
            self.readDB_and_reFreshGrid()
        elif label == uc.筛选:
            dlg = FilterDialog(self.__colLabels, self.__colLabels_type, self.filter_case)
            if dlg.ShowModal() == wx.ID_OK:
                self.filter_case = dlg.GetValue()
            dlg.Destroy()
            # 整理出where_sql和where_list
            if not self.filter_case:
                return
            where_sql = []
            where_list = []
            for each_filter in self.filter_case:
                where_sql.append(each_filter[1][0])
                where_list.extend(each_filter[1][1])
            where_sql = 'WHERE ' + ' AND '.join(where_sql)
            self.readDB_and_reFreshGrid(where_sql, where_list)
        elif label == uc.查询结构:
            dlg = TreeDialog()
            if dlg.ShowModal() == wx.ID_OK:
                data = dlg.GetValue()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return
            # 筛选树型框里传递来的记录
            UDID = data[0]
            where_sql = 'WHERE 立项识别码=%s'
            self.filter_case = [['【立项识别码 等于 %d】' % UDID, ['立项识别码=%s', [UDID], ['立项识别码', '整数型', '等于', UDID, '', '招标识别码', '整数型', '大于', 0]]]]
            self.readDB_and_reFreshGrid(where_sql, [UDID])
            # 点选树型框里选来的记录
            # row = 0
            # UDID = data[0]
            # gridData = self.ctrl[('Grid', None)].GetTable().data
            # for key, value in gridData.items():
            #   if value == UDID:
            #       row = key[0]
            #       break
            # if row:
            #     self.SetValue(row)
            #     self.ctrl[('Grid', None)].SelectRow(row)
        elif label == uc.导出:
            wildcard = 'Excel files (*.xlsx)|*.xlsx'
            dlg = wx.FileDialog(None, "Choose a file", '', '', wildcard, 0)    #选择文件对话框
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            dlg.Destroy()
            filename = dlg.GetPath()
            if os.path.exists(filename):
                dlg = wx.MessageDialog(self, message='该文件已存在，点击<是>覆盖文件', caption='警告', style= wx.YES_NO | wx.NO_DEFAULT)
                if dlg.ShowModal() == wx.ID_NO:
                    dlg.Destroy()
                    return
                else:
                    dlg.Destroy()
            data = self.ctrl[('Grid', None)].GetTable().data
            try:
                Exporter().commonExport(filename, self.ctrl[('Grid', None)], self.__colLabels, data)
                dlg = wx.MessageDialog(self, message='文件导出成功', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except Exception as e:
                dlg = wx.MessageDialog(self, message='文件导出失败！\n%s' % str(e), caption='警告', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
    def labelOnClick(self, event):
        col = event.GetCol()
        isCtrl = event.ControlDown()
        isShift = event.ShiftDown()
        if col >= 0 and isCtrl:
            data = self.get_data_by_sortGrid(self.ctrl[('Grid', None)], col, False, self.__colLabels_type)
            self.reFreshGrid(self.ctrl[('Grid', None)], data, self.__colLabels, [uc.InitiationColLabels.index('概算付款比')])
        elif col >= 0 and isShift:
            data = self.get_data_by_sortGrid(self.ctrl[('Grid', None)], col, True, self.__colLabels_type)
            self.reFreshGrid(self.ctrl[('Grid', None)], data, self.__colLabels, [uc.InitiationColLabels.index('概算付款比')])
        else:
            return
    def gridOnSelectACell(self, event):
        row = event.GetRow()
        result = self.SetValue(row)
        if result:
            self.ctrl[('Textbox', uc.显示窗)].SetValue('%d-%s%s' % (result[self.__colLabels.index('立项识别码')], result[self.__colLabels.index('项目名称')], result[self.__colLabels.index('分项名称')]))
    def labelOnDCLICK(self, event):
        col = event.GetCol()
        data = self.ctrl[('Grid', None)].GetTable().data
        colLabels = self.ctrl[('Grid', None)].GetTable().colLabels
        values = []
        def thousands(n):
            return '{:>,.2f}'.format(n)
        if self.__colLabels_type[col] in '整数型 浮点型'.split():
            for key, value in data.items():
                if key[1] == col and value is not None:
                    values.append(value)
            try:
                dlg = wx.MessageDialog(self, message='<%s>列下：\n共有<%d>个值，\n和为<%s>，\n最大值为<%s>，\n最小值为<%s>' \
                                       % (colLabels[col], len(values), thousands(sum(values)), thousands(max(values)), thousands(min(values))),
                                       caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except:
                pass
        elif self.__colLabels_type[col] in ['日期型']:
            for key, value in data.items():
                if key[1] == col and value is not None:
                    values.append(value)
            try:
                dlg = wx.MessageDialog(self, message='<%s>列下：\n共有<%d>个值，\n最大值为<%s>，\n最小值为<%s>' % (colLabels[col], len(values), max(values), min(values)),
                                       caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except:
                pass
    def gridOnDClick(self, event):
        self.EndModal(wx.ID_OK)
    def gridOnRClick(self, event):
        row = event.GetRow()
        if row >= 0:
            self.SetValue(row)
            self.ctrl[('Grid', None)].SelectRow(row)
            self.checkInit()
    # methods
    def checkInit(self):
        data = self.GetValue()
        dlg = Initiation_MaintainDialog(uc.Dialog_Check, data[0])
        dlg.ShowModal()
        dlg.Destroy()
        self.readDB_and_reFreshGrid()
    def GetValue(self):
        return self.__value
    def SetValue(self, row):
        data = self.ctrl[('Grid', None)].GetTable().data
        colLabels = self.ctrl[('Grid', None)].GetTable().colLabels
        try:
            rownum = max(data.keys())[0] + 1
        except:
            rownum = 0
        colnum = len(colLabels)
        result = []
        if rownum == 0:
            return
        for col in range(colnum):
            result.append(data.get((row, col)))
        self.__value = result
        return result
    def readDB(self, where_sql='', where_list=[], order_sql='', order_list=[]):
        return operateDB().read_For_Initiation_GridDialog(where_sql, where_list, order_sql, order_list)
    def readDB_and_reFreshGrid(self, where_sql='', where_list=[], order_sql='', order_list=[]):
        data = self.format_DBdata2Griddata(self.readDB(where_sql, where_list, order_sql, order_list))
        self.reFreshGrid(self.ctrl[('Grid', None)], data, self.__colLabels, [uc.InitiationColLabels.index('概算付款比')])

class Initiation_MaintainDialog(MaintainDialog):
    __mode = uc.Dialog_Check
    __choice_dialog_could_open = False
    __value = None
    __save_point = None
    __ctrl_key = list(zip(['Textbox'] * 15, uc.InitiationColLabels))
    __ctrl_value_type = uc.InitiationColLabels_Type
    def __init__(self, mode=uc.Dialog_Check, UDID=-1):
        self.init()
        self.ctrl[('Button', uc.会签表格)].Enable(False)
        little_sizer = {}
        def create_Label_Textbox_Pairs(key, size_Textbox, size_Label=uc.Size_Label_BaseDialog):
            little_sizer[key] = wx.BoxSizer(wx.HORIZONTAL)
            self.ctrl[('Label', key)] = wx.StaticText(self, -1, key+'：', size=size_Label, style=wx.ALIGN_RIGHT)
            self.ctrl[('Textbox', key)] = wx.TextCtrl(self, -1, '', size=size_Textbox, style=wx.TE_READONLY|wx.TE_CENTRE|wx.BORDER_STATIC, name=key)
            little_sizer[key].Add(self.ctrl[('Label', key)])
            little_sizer[key].Add(self.ctrl[('Textbox', key)])
        def create_Label_MultiTextbox_Pairs(key, size_Textbox, size_Label=uc.Size_Label_BaseDialog):
            little_sizer[key] = wx.BoxSizer(wx.HORIZONTAL)
            self.ctrl[('Label', key)] = wx.StaticText(self, -1, key+'：', size=size_Label, style=wx.ALIGN_RIGHT)
            self.ctrl[('Textbox', key)] = wx.TextCtrl(self, -1, '', size=size_Textbox, style=wx.TE_READONLY|wx.BORDER_STATIC|wx.TE_MULTILINE, name=key)
            little_sizer[key].Add(self.ctrl[('Label', key)])
            little_sizer[key].Add(self.ctrl[('Textbox', key)])
        def create_Label_Combobox_Pairs(key, size_Combobox):
            little_sizer[key] = wx.BoxSizer(wx.HORIZONTAL)
            self.ctrl[('Label', key)] = wx.StaticText(self, -1, key+'：', size=size_Label, style=wx.ALIGN_RIGHT)
            style = wx.TE_PROCESS_ENTER|wx.CB_DROPDOWN|wx.TE_CENTER
            self.ctrl[('Combobox', key)] = wx.ComboBox(self, -1, value='', size=size_Combobox, choices=[], style=style)
            little_sizer[key].Add(self.ctrl[('Label', key)])
            little_sizer[key].Add(self.ctrl[('Combobox', key)])
        # 重绘控件
        create_Label_Textbox_Pairs( '立项识别码'       , uc.Size_Textbox_Short_BaseDialog)
        create_Label_Textbox_Pairs( '项目名称'         , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '分项名称'         , uc.Size_Textbox_Long_BaseDialog)
        create_Label_Textbox_Pairs( '父项立项识别码'   , uc.Size_Textbox_Short_BaseDialog)
        create_Label_Textbox_Pairs( '父项项目名称'     , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '父项分项名称'     , uc.Size_Textbox_Long_BaseDialog)
        create_Label_Textbox_Pairs( '建设单位识别码'   , uc.Size_Textbox_Short_BaseDialog)
        create_Label_Textbox_Pairs( '建设单位名称'     , uc.Size_Textbox_Long_BaseDialog)
        create_Label_Textbox_Pairs( '代建单位识别码'   , uc.Size_Textbox_Short_BaseDialog)
        create_Label_Textbox_Pairs( '代建单位名称'     , uc.Size_Textbox_Long_BaseDialog)
        create_Label_Textbox_Pairs( '立项文件名称'     , uc.Size_Textbox_Long_BaseDialog)
        create_Label_Textbox_Pairs( '立项时间'         , uc.Size_Textbox_Normal_BaseDialog, uc.Size_Label_Company_MaintainDialog)
        create_Label_Textbox_Pairs( '项目概算'         , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '概算付款比'       , uc.Size_Textbox_Normal_BaseDialog, uc.Size_Label_Company_MaintainDialog)
        create_Label_MultiTextbox_Pairs( '立项备注'    , uc.Size_Textbox_Note)
        core_sizer = wx.BoxSizer(wx.VERTICAL)
        row_sizer = []
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['立项识别码'])
        row_sizer[-1].Add(little_sizer['项目名称'])
        row_sizer[-1].Add(little_sizer['分项名称'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['父项立项识别码'])
        row_sizer[-1].Add(little_sizer['父项项目名称'])
        row_sizer[-1].Add(little_sizer['父项分项名称'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['建设单位识别码'])
        row_sizer[-1].Add(little_sizer['建设单位名称'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['代建单位识别码'])
        row_sizer[-1].Add(little_sizer['代建单位名称'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['立项文件名称'])
        row_sizer[-1].Add(little_sizer['立项时间'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['项目概算'])
        row_sizer[-1].Add(little_sizer['概算付款比'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['立项备注'     ])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        self.sizer.Add(core_sizer, 0, wx.ALL, 10)
        self.SetSizer(self.all_sizer)
        self.all_sizer.Fit(self)
        for key, eachEvent, eachHandler in self.ctrlBindData():
            self.ctrl[key].Bind(eachEvent, eachHandler)
        # 检查模式
        self.ChangeMode(mode, UDID)    # 通过识别码读取信息
        self.SaveTap(self.FormatInfoFromUI())
    # binder
    def ctrlBindData(self):
        return ((('Button',  uc.跳转), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.附件), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.新建), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.修改), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.保存), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.取消), wx.EVT_BUTTON, self.clickOnButton),
                (('Textbox', '父项立项识别码'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '父项项目名称'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '父项分项名称'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '建设单位识别码'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '建设单位名称'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '代建单位识别码'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '代建单位名称'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '立项时间'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox)
               )
    # events
    def clickOnButton(self, event):
        label = wx.FindWindowById(event.Id, self).GetLabel()
        if label == uc.跳转:
            try:
                UDID = self.FormatInfoForDB()[0]
            except:
                UDID = None
            self.Jump(event, UDID, '跳转至相应<招标>信息 跳转至相应<合同>信息 跳转至相应<付款>信息'.split(), 
                      Initiation_GridDialog, Bidding_GridDialog, Contract_GridDialog, Budget_GridDialog, Payment_GridDialog)
        elif label == uc.附件:            
            dlg = AttachFileDialog(uc.Dialog_New)
            dlg.ShowModal()
            dlg.Destroy()
        elif label == uc.新建:
            self.SaveTap(self.FormatInfoFromUI())
            self.ChangeMode(uc.Dialog_New)
        elif label == uc.修改:
            self.SaveTap(self.FormatInfoFromUI())
            try:
                UDID = int(self.ctrl[('Textbox', '立项识别码')].GetValue())
            except:
                UDID = 0
            self.ChangeMode(uc.Dialog_Edit, UDID)
        elif label == uc.取消:
            hasChanged = self.FormatInfoFromUI() != self.LoadTap()
            if hasChanged:
                dlg = wx.MessageDialog(self, message='更改的数据尚未保存，你确定要退出吗？', caption='警告', style= wx.YES_NO | wx.NO_DEFAULT)
                if dlg.ShowModal() == wx.ID_NO:
                    dlg.Destroy()
                    return
                else:
                    dlg.Destroy()
            self.ChangeMode(uc.Dialog_Check)
            self.FillBlanks(self.LoadTap())
        elif label == uc.保存:
            hasChanged = self.FormatInfoFromUI() != self.LoadTap()
            if not hasChanged:
                dlg = wx.MessageDialog(self, message='数据并未做任何更改，不需要保存。', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            dlg = wx.MessageDialog(self, message='点击确定保存数据。', caption='提示', style= wx.YES_NO | wx.NO_DEFAULT)
            if dlg.ShowModal() == wx.ID_NO:
                dlg.Destroy()
                return
            else:
                dlg.Destroy()
            data = self.FormatInfoForDB()
            UDID = data[0]
            save_result = operateDB().save_For_Initiation_MaintainDialog(data)
            try:
                assert save_result
                dlg = wx.MessageDialog(self, message='数据保存成功。', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except Exception as e:
                dlg = wx.MessageDialog(self, message='数据保存失败\n%s' % str(e), caption='警告', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            self.ChangeMode(uc.Dialog_Check, UDID)
            self.SaveTap(data)
    def DclickOnTextbox(self, event):
        if not self.__choice_dialog_could_open:
            return
        isCtrl = event.ControlDown()
        name = wx.FindWindowById(event.GetId()).GetName()
        data = self.FormatInfoFromUI()
        if name in '父项立项识别码 父项项目名称 父项分项名称'.split():
            if isCtrl:
                self.ctrl[('Textbox', '父项立项识别码')].SetValue('')
                self.ctrl[('Textbox', '父项项目名称')].SetValue('')
                self.ctrl[('Textbox', '父项分项名称')].SetValue('')
                return
            dlg = Initiation_GridDialog()
            if dlg.ShowModal() == wx.ID_OK:
                UDID, project, subproject = dlg.GetValue()[:3]
                self.ctrl[('Textbox', '父项立项识别码')].SetValue(str(UDID))
                self.ctrl[('Textbox', '父项项目名称')].SetValue(project or '')
                self.ctrl[('Textbox', '父项分项名称')].SetValue(subproject or '')
            dlg.Destroy()
        elif name in '建设单位识别码 建设单位名称'.split():
            if isCtrl:
                self.ctrl[('Textbox', '建设单位识别码')].SetValue('')
                self.ctrl[('Textbox', '建设单位名称')].SetValue('')
                return
            dlg = Company_GridDialog()
            if dlg.ShowModal() == wx.ID_OK:
                UDID, company_name = dlg.GetValue()[:2]
                self.ctrl[('Textbox', '建设单位识别码')].SetValue(str(UDID) or '')
                self.ctrl[('Textbox', '建设单位名称')].SetValue(company_name or '')
            dlg.Destroy()
        elif name in '代建单位识别码 代建单位名称'.split():
            if isCtrl:
                self.ctrl[('Textbox', '代建单位识别码')].SetValue('')
                self.ctrl[('Textbox', '代建单位名称')].SetValue('')
                return
            dlg = Company_GridDialog()
            if dlg.ShowModal() == wx.ID_OK:
                UDID, company_name = dlg.GetValue()[:2]
                self.ctrl[('Textbox', '代建单位识别码')].SetValue(str(UDID) or '')
                self.ctrl[('Textbox', '代建单位名称')].SetValue(company_name or '')
            dlg.Destroy()
        elif name in ['立项时间']:
            if isCtrl:
                self.ctrl[('Textbox', '立项时间')].SetValue('')
                return
            dlg = DateDialog()
            if dlg.ShowModal() == wx.ID_OK:
                yearmonthday = dlg.GetValue()
                self.ctrl[('Textbox', '立项时间')].SetValue(str(yearmonthday) or '')
            dlg.Destroy()
    # methods
    def GetValue(self):
        return self.__value
    def SetValue(self):
        self.__value = []
        for each_ctrl_key, each_value_type in zip(self.__ctrl_key, self.__ctrl_value_type):
            value = self.ctrl[each_ctrl_key].GetValue()
            try:
                if value == '':
                    value = None
                elif each_value_type == '整数型':
                    value = int(value)
                elif each_value_type == '浮点型':
                    value = decimal.Decimal(value.strip().replace(',', ''))
            except:
                value = None
            self.__value.append(value)
        return self.__value
    def LoadTap(self):
        return self.__save_point
    def SaveTap(self, data=[]):
        self.__save_point = data
    def FormatInfoFromUI(self, ifReport=False):
        data = []
        for i, each_ctrl_key in zip(range(len(self.__ctrl_key)), self.__ctrl_key):
            value = self.ctrl[each_ctrl_key].GetValue()
            if len(value) == 0:
                value = None
            elif self.__ctrl_value_type[i] == '整数型':
                try:
                    value = int(value)
                except:
                    value = None
                    if ifReport:
                        dlg = wx.MessageDialog(self, message='<%s>中数据未能识别，将记录为NULL值' % each_ctrl_key[1], caption='警告', style=wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
            elif self.__ctrl_value_type[i] == '浮点型':
                try:
                    value = decimal.Decimal(value.strip().replace(',', ''))
                except:
                    value = None
                    if ifReport:
                        dlg = wx.MessageDialog(self, message='<%s>中数据未能识别，将记录为NULL值' % each_ctrl_key[1], caption='警告', style=wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
            elif self.__ctrl_value_type[i] == '日期型':
                try:
                    value = datetime.date(*time.strptime(value, "%Y-%m-%d")[:3])
                except:
                    value = None
                    if ifReport:
                        dlg = wx.MessageDialog(self, message='<%s>中数据未能识别，将记录为NULL值' % each_ctrl_key[1], caption='警告', style=wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
            data.append(value)
        return data
    def FormatInfoForDB(self):
        data = self.FormatInfoFromUI(True)
        result = []
        for key, value in zip(uc.InitiationColLabels, data):
            if key in uc.InitiationFields:
                result.append(value)
        return result
    def GetDataFromUDID(self, UDID):
        try:
            result = operateDB().read_For_Initiation_GridDialog(where_sql='WHERE 立项识别码=%s', where_list=[UDID])[0]
        except:
            result = None
        return result
    def ChangeMode(self, mode, UDID=None):
        if mode == uc.Dialog_Check:
            self.__mode = mode
            data = self.GetDataFromUDID(UDID) if UDID else []
            self.SetTitle('查看立项信息')
            for each_ctrl_key in self.__ctrl_key:
                if each_ctrl_key[0] == 'Textbox':
                    self.ctrl[each_ctrl_key].SetEditable(False)
            self.ctrl[('Button', uc.新建)].Enable(True)
            self.ctrl[('Button', uc.修改)].Enable(True)
            self.ctrl[('Button', uc.保存)].Enable(False)
            self.ctrl[('Button', uc.取消)].Enable(False)
            self.ChoiceDialog(False)
            self.FillBlanks(data)
        elif mode == uc.Dialog_New:
            self.__mode = mode
            self.SetTitle('新建立项信息')
            for each_ctrl_key in self.__ctrl_key:
                if each_ctrl_key[0] == 'Textbox' and each_ctrl_key[1] in '项目名称 分项名称 立项文件名称 项目概算 立项备注'.split():
                    self.ctrl[each_ctrl_key].SetEditable(True)
            self.ctrl[('Textbox', '立项识别码')].SetEditable(False)
            self.ctrl[('Button', uc.新建)].Enable(False)
            self.ctrl[('Button', uc.修改)].Enable(False)
            self.ctrl[('Button', uc.保存)].Enable(True)
            self.ctrl[('Button', uc.取消)].Enable(True)
            self.ChoiceDialog(True)
            self.FillBlanks()
        elif mode == uc.Dialog_Edit:
            try:
                data = self.GetDataFromUDID(UDID) if UDID else []
                assert data
            except:
                dlg = wx.MessageDialog(self, message='该立项识别码数据库中未记录，请检查', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            self.__mode = mode
            self.SetTitle('修改立项信息')
            for each_ctrl_key in self.__ctrl_key:
                if each_ctrl_key[0] == 'Textbox' and each_ctrl_key[1] in '项目名称 分项名称 立项文件名称 项目概算 立项备注'.split():
                    self.ctrl[each_ctrl_key].SetEditable(True)
            self.ctrl[('Textbox', '立项识别码')].SetEditable(False)
            self.ctrl[('Button', uc.新建)].Enable(False)
            self.ctrl[('Button', uc.修改)].Enable(False)
            self.ctrl[('Button', uc.保存)].Enable(True)
            self.ctrl[('Button', uc.取消)].Enable(True)
            self.ChoiceDialog(True)
            self.FillBlanks(data)
    def FillBlanks(self, data=[]):
        def thousands(n): return '{:>,.2f}'.format(n)
        def percents(n): return '{:>.2f}'.format((n or 0) * 100) + '%'
        for each_ctrl_key in self.__ctrl_key:
            try:
                value = data[self.__ctrl_key.index(each_ctrl_key)]
                value_type = self.__ctrl_value_type[self.__ctrl_key.index(each_ctrl_key)]
                if value is None:
                    value = ''
                elif value_type == '浮点型':
                    value = thousands(value)
                elif value_type == '百分比':
                    value = percents(value)
                else:
                    value = str(value)
                self.ctrl[each_ctrl_key].SetValue(value)
            except:
                self.ctrl[each_ctrl_key].SetValue('')
    def ChoiceDialog(self, could_open):
        self.__choice_dialog_could_open = could_open

class Bidding_GridDialog(GridDialog):
    __value = None
    __colLabels = uc.BiddingColLabels
    __colLabels_type = uc.BiddingColLabels_Type
    filter_case = []
    def __init__(self, title='招标信息', data=None, size=uc.Size_BaseDialog, limit=False, where_sql='' ,where_list=[]):
        self.init(title, data, size)
        if limit:
            self.ctrl[('Button', uc.筛选)].Enable(False)
            self.ctrl[('Button', uc.查询结构)].Enable(False)
            self.ctrl[('Button', uc.刷新)].Enable(False)
        for eachEvent, eachHandler in self.gridBindData():
            self.ctrl[('Grid', None)].Bind(eachEvent, eachHandler)
        for key, eachEvent, eachHandler in self.ctrlBindData():
            self.ctrl[key].Bind(eachEvent, eachHandler)
        self.readDB_and_reFreshGrid(where_sql=where_sql, where_list=where_list)
        self.ctrl[('Grid', None)].SelectRow(0)
    # binder
    def gridBindData(self):
        return ((wx.grid.EVT_GRID_LABEL_LEFT_CLICK,  self.labelOnClick),
                (wx.grid.EVT_GRID_SELECT_CELL,       self.gridOnSelectACell),
                (wx.grid.EVT_GRID_LABEL_LEFT_DCLICK, self.labelOnDCLICK),
                (wx.grid.EVT_GRID_CELL_RIGHT_CLICK,  self.gridOnRClick),
                (wx.grid.EVT_GRID_CELL_LEFT_DCLICK,  self.gridOnDClick))
    def ctrlBindData(self):
        return ((('Button',  uc.新建),     wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.修改),     wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.筛选),     wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.查询结构), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.刷新),     wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.导出),     wx.EVT_BUTTON, self.clickOnButton),
               )
    # events
    def clickOnButton(self, event):
        label = wx.FindWindowById(event.Id, self).GetLabel()
        if label == uc.刷新:
            self.readDB_and_reFreshGrid()
            self.filter_case = []
        elif label == uc.新建:
            dlg = Bidding_MaintainDialog(uc.Dialog_New)
            dlg.ShowModal()
            dlg.Destroy()
            self.readDB_and_reFreshGrid()
        elif label == uc.修改:
            data = self.GetValue()
            dlg = Bidding_MaintainDialog(uc.Dialog_Edit, data[0])
            dlg.ShowModal()
            dlg.Destroy()
            self.readDB_and_reFreshGrid()
        elif label == uc.筛选:
            dlg = FilterDialog(self.__colLabels, self.__colLabels_type, self.filter_case)
            if dlg.ShowModal() == wx.ID_OK:
                self.filter_case = dlg.GetValue()
            dlg.Destroy()
            # 整理出where_sql和where_list
            if not self.filter_case:
                return
            where_sql = []
            where_list = []
            for each_filter in self.filter_case:
                where_sql.append(each_filter[1][0])
                where_list.extend(each_filter[1][1])
            where_sql = 'WHERE ' + ' AND '.join(where_sql)
            self.readDB_and_reFreshGrid(where_sql, where_list)
        elif label == uc.查询结构:
            dlg = TreeDialog()
            if dlg.ShowModal() == wx.ID_OK:
                data = dlg.GetValue()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return
            # 筛选树型框里传递来的记录
            UDID = data[0]
            where_sql = 'WHERE 立项识别码=%s'
            self.filter_case = [['【立项识别码 等于 %d】' % UDID, ['立项识别码=%s', [UDID], ['立项识别码', '整数型', '等于', UDID, '', '立项识别码', '整数型', '大于', 0]]]]
            self.readDB_and_reFreshGrid(where_sql, [UDID])
        elif label == uc.导出:
            wildcard = 'Excel files (*.xlsx)|*.xlsx'
            dlg = wx.FileDialog(None, "Choose a file", '', '', wildcard, 0)    #选择文件对话框
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            dlg.Destroy()
            filename = dlg.GetPath()
            if os.path.exists(filename):
                dlg = wx.MessageDialog(self, message='该文件已存在，点击<是>覆盖文件', caption='警告', style= wx.YES_NO | wx.NO_DEFAULT)
                if dlg.ShowModal() == wx.ID_NO:
                    dlg.Destroy()
                    return
                else:
                    dlg.Destroy()
            data = self.ctrl[('Grid', None)].GetTable().data
            try:
                Exporter().commonExport(filename, self.ctrl[('Grid', None)], self.__colLabels, data)
                dlg = wx.MessageDialog(self, message='文件导出成功', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except Exception as e:
                dlg = wx.MessageDialog(self, message='文件导出失败！\n%s' % str(e), caption='警告', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
    def labelOnClick(self, event):
        col = event.GetCol()
        isCtrl = event.ControlDown()
        isShift = event.ShiftDown()
        if col >= 0 and isCtrl:
            data = self.get_data_by_sortGrid(self.ctrl[('Grid', None)], col, False, self.__colLabels_type)
            self.reFreshGrid(self.ctrl[('Grid', None)], data, self.__colLabels)
        elif col >= 0 and isShift:
            data = self.get_data_by_sortGrid(self.ctrl[('Grid', None)], col, True, self.__colLabels_type)
            self.reFreshGrid(self.ctrl[('Grid', None)], data, self.__colLabels)
        else:
            return
    def gridOnSelectACell(self, event):
        row = event.GetRow()
        result = self.SetValue(row)
        if result:
            self.ctrl[('Textbox', uc.显示窗)].SetValue('%d-%s%s' % (result[self.__colLabels.index('招标识别码')], result[self.__colLabels.index('项目名称')], result[self.__colLabels.index('分项名称')]))
    def labelOnDCLICK(self, event):
        col = event.GetCol()
        data = self.ctrl[('Grid', None)].GetTable().data
        colLabels = self.ctrl[('Grid', None)].GetTable().colLabels
        values = []
        def thousands(n):
            return '{:>,.2f}'.format(n)
        if self.__colLabels_type[col] in '整数型 浮点型'.split():
            for key, value in data.items():
                if key[1] == col and value is not None:
                    values.append(value)
            try:
                dlg = wx.MessageDialog(self, message='<%s>列下：\n共有<%d>个值，\n和为<%s>，\n最大值为<%s>，\n最小值为<%s>' \
                                       % (colLabels[col], len(values), thousands(sum(values)), thousands(max(values)), thousands(min(values))),
                                       caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except:
                pass
        elif self.__colLabels_type[col] in ['日期型']:
            for key, value in data.items():
                if key[1] == col and value is not None:
                    values.append(value)
            try:
                dlg = wx.MessageDialog(self, message='<%s>列下：\n共有<%d>个值，\n最大值为<%s>，\n最小值为<%s>' % (colLabels[col], len(values), max(values), min(values)),
                                       caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except:
                pass
    def gridOnDClick(self, event):
        self.EndModal(wx.ID_OK)
    def gridOnRClick(self, event):
        row = event.GetRow()
        if row >= 0:
            self.SetValue(row)
            self.ctrl[('Grid', None)].SelectRow(row)
            self.checkBidding()
    # methods
    def checkBidding(self):
        data = self.GetValue()
        dlg = Bidding_MaintainDialog(uc.Dialog_Check, data[0])
        dlg.ShowModal()
        dlg.Destroy()
        self.readDB_and_reFreshGrid()
    def GetValue(self):
        return self.__value
    def SetValue(self, row):
        data = self.ctrl[('Grid', None)].GetTable().data
        colLabels = self.ctrl[('Grid', None)].GetTable().colLabels
        try:
            rownum = max(data.keys())[0] + 1
        except:
            rownum = 0
        colnum = len(colLabels)
        result = []
        if rownum == 0:
            return
        for col in range(colnum):
            result.append(data.get((row, col)))
        self.__value = result
        return result
    def readDB(self, where_sql='', where_list=[], order_sql='', order_list=[]):
        return operateDB().read_For_Bidding_GridDialog(where_sql, where_list, order_sql, order_list)
    def readDB_and_reFreshGrid(self, where_sql='', where_list=[], order_sql='', order_list=[]):
        data = self.format_DBdata2Griddata(self.readDB(where_sql, where_list, order_sql, order_list))
        self.reFreshGrid(self.ctrl[('Grid', None)], data, self.__colLabels)

class Bidding_MaintainDialog(MaintainDialog):
    __mode = uc.Dialog_Check
    __choice_dialog_could_open = False
    __value = None
    __save_point = None
    __ctrl_key = list(zip(['Textbox'] * 4 + ['Combobox'] + ['Textbox'] * 14,
                      uc.BiddingColLabels))
    __ctrl_value_type = uc.BiddingColLabels_Type
    def __init__(self, mode=uc.Dialog_Check, UDID=-1):
        self.init()
        self.ctrl[('Button', uc.会签表格)].Enable(False)
        little_sizer = {}
        def create_Label_Textbox_Pairs(key, size_Textbox, size_Label=uc.Size_Label_Bidding_MaintainDialog):
            little_sizer[key] = wx.BoxSizer(wx.HORIZONTAL)
            self.ctrl[('Label', key)] = wx.StaticText(self, -1, key+'：', size=size_Label, style=wx.ALIGN_RIGHT)
            self.ctrl[('Textbox', key)] = wx.TextCtrl(self, -1, '', size=size_Textbox, style=wx.TE_READONLY|wx.TE_CENTRE|wx.BORDER_STATIC, name=key)
            little_sizer[key].Add(self.ctrl[('Label', key)])
            little_sizer[key].Add(self.ctrl[('Textbox', key)])
        def create_Label_MultiTextbox_Pairs(key, size_Textbox, size_Label=uc.Size_Label_BaseDialog):
            little_sizer[key] = wx.BoxSizer(wx.HORIZONTAL)
            self.ctrl[('Label', key)] = wx.StaticText(self, -1, key+'：', size=size_Label, style=wx.ALIGN_RIGHT)
            self.ctrl[('Textbox', key)] = wx.TextCtrl(self, -1, '', size=size_Textbox, style=wx.TE_READONLY|wx.BORDER_STATIC|wx.TE_MULTILINE, name=key)
            little_sizer[key].Add(self.ctrl[('Label', key)])
            little_sizer[key].Add(self.ctrl[('Textbox', key)])
        def create_Label_Combobox_Pairs(key, size_Combobox, size_Label=uc.Size_Label_Bidding_MaintainDialog):
            little_sizer[key] = wx.BoxSizer(wx.HORIZONTAL)
            self.ctrl[('Label', key)] = wx.StaticText(self, -1, key+'：', size=size_Label, style=wx.ALIGN_RIGHT)
            style = wx.TE_PROCESS_ENTER|wx.CB_DROPDOWN|wx.TE_CENTER|wx.TE_READONLY
            self.ctrl[('Combobox', key)] = wx.ComboBox(self, -1, value='', size=size_Combobox, choices=[], style=style, name=key)
            little_sizer[key].Add(self.ctrl[('Label', key)])
            little_sizer[key].Add(self.ctrl[('Combobox', key)])
        # 重绘控件
        create_Label_Textbox_Pairs( '招标识别码'         , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Combobox_Pairs('招标方式'           , uc.Size_Combobox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '项目概算'           , uc.Size_Textbox_Normal_BaseDialog, uc.Size_Label_BaseDialog)
        create_Label_Textbox_Pairs( '立项识别码'         , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '项目名称'           , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '分项名称'           , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '招标单位识别码'     , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '招标单位名称'       , uc.Size_Textbox_Long_BaseDialog)
        create_Label_Textbox_Pairs( '招标代理识别码'     , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '招标代理单位名称'   , uc.Size_Textbox_Long_BaseDialog)
        create_Label_Textbox_Pairs( '招标文件定稿时间'   , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '公告邀请函发出时间' , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '开标时间'           , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '预算控制价'         , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '中标价'             , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '中标通知书发出时间' , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '中标单位识别码'     , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '中标单位名称'       , uc.Size_Textbox_Long_BaseDialog)
        create_Label_MultiTextbox_Pairs( '招标备注'    , uc.Size_Textbox_Note)
        self.ctrl[('Combobox', '招标方式')].AppendItems('公开招标 邀请招标 竞争性谈判 政府定点采购 直接发包 询价'.split())
        core_sizer = wx.BoxSizer(wx.VERTICAL)
        row_sizer = []
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['招标识别码'])
        row_sizer[-1].Add(little_sizer['招标方式'])
        row_sizer[-1].Add(little_sizer['项目概算'])
        core_sizer.AddSpacer(10)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['立项识别码'])
        row_sizer[-1].Add(little_sizer['项目名称'])
        row_sizer[-1].Add(little_sizer['分项名称'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['招标单位识别码'])
        row_sizer[-1].Add(little_sizer['招标单位名称'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['招标代理识别码'])
        row_sizer[-1].Add(little_sizer['招标代理单位名称'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['招标文件定稿时间'])
        row_sizer[-1].Add(little_sizer['公告邀请函发出时间'])
        row_sizer[-1].Add(little_sizer['开标时间'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['预算控制价'])
        row_sizer[-1].Add(little_sizer['中标价'])
        row_sizer[-1].Add(little_sizer['中标通知书发出时间'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['中标单位识别码'])
        row_sizer[-1].Add(little_sizer['中标单位名称'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['招标备注'     ])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        self.sizer.Add(core_sizer, 0, wx.ALL, 10)
        self.SetSizer(self.all_sizer)
        self.all_sizer.Fit(self)
        for key, eachEvent, eachHandler in self.ctrlBindData():
            self.ctrl[key].Bind(eachEvent, eachHandler)
        # 检查模式
        self.ChangeMode(mode, UDID)    # 通过识别码读取信息
        self.SaveTap(self.FormatInfoFromUI())
    # binder
    def ctrlBindData(self):
        return ((('Button',  uc.跳转), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.新建), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.修改), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.保存), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.取消), wx.EVT_BUTTON, self.clickOnButton),
                (('Textbox', '立项识别码'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '项目名称'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '分项名称'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '招标单位识别码'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '招标单位名称'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '招标代理识别码'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '招标代理单位名称'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '招标文件定稿时间'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '公告邀请函发出时间'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '开标时间'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '中标通知书发出时间'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '中标单位识别码'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '中标单位名称'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox)
               )
    # events
    def clickOnButton(self, event):
        label = wx.FindWindowById(event.Id, self).GetLabel()        
        if label == uc.跳转:
            try:
                UDID = self.FormatInfoForDB()[uc.BiddingFields.index('立项识别码')]
            except:
                UDID = None
            self.Jump(event, UDID, '跳转至相应<立项>信息 跳转至相应<合同>信息 跳转至相应<付款>信息'.split(), 
                      Initiation_GridDialog, Bidding_GridDialog, Contract_GridDialog, Budget_GridDialog, Payment_GridDialog)
        elif label == uc.新建:
            self.SaveTap(self.FormatInfoFromUI())
            self.ChangeMode(uc.Dialog_New)
        elif label == uc.修改:
            self.SaveTap(self.FormatInfoFromUI())
            try:
                UDID = int(self.ctrl[('Textbox', '招标识别码')].GetValue())
            except:
                UDID = 0
            self.ChangeMode(uc.Dialog_Edit, UDID)
        elif label == uc.取消:
            hasChanged = self.FormatInfoFromUI() != self.LoadTap()
            if hasChanged:
                dlg = wx.MessageDialog(self, message='更改的数据尚未保存，你确定要退出吗？', caption='警告', style= wx.YES_NO | wx.NO_DEFAULT)
                if dlg.ShowModal() == wx.ID_NO:
                    dlg.Destroy()
                    return
                else:
                    dlg.Destroy()
            self.ChangeMode(uc.Dialog_Check)
            self.FillBlanks(self.LoadTap())
        elif label == uc.保存:
            hasChanged = self.FormatInfoFromUI() != self.LoadTap()
            if not hasChanged:
                dlg = wx.MessageDialog(self, message='数据并未做任何更改，不需要保存。', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            dlg = wx.MessageDialog(self, message='点击确定保存数据。', caption='提示', style= wx.YES_NO | wx.NO_DEFAULT)
            if dlg.ShowModal() == wx.ID_NO:
                dlg.Destroy()
                return
            else:
                dlg.Destroy()
            data = self.FormatInfoForDB()
            UDID = data[0]
            InitUDID = data[uc.BiddingFields.index('立项识别码')]
            if not InitUDID:
                dlg = wx.MessageDialog(self, message='立项信息未填写，请检查', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            save_result = operateDB().save_For_Bidding_MaintainDialog(data)
            try:
                assert save_result
                dlg = wx.MessageDialog(self, message='数据保存成功。', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except Exception as e:
                dlg = wx.MessageDialog(self, message='数据保存失败\n%s' % str(e), caption='警告', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            self.ChangeMode(uc.Dialog_Check, UDID)
            self.SaveTap(data)
    def DclickOnTextbox(self, event):
        if not self.__choice_dialog_could_open:
            return
        isCtrl = event.ControlDown()
        name = wx.FindWindowById(event.GetId()).GetName()
        data = self.FormatInfoFromUI()
        if name in '立项识别码 项目名称 分项名称'.split():
            if isCtrl:
                self.ctrl[('Textbox', '立项识别码')].SetValue('')
                self.ctrl[('Textbox', '项目名称')].SetValue('')
                self.ctrl[('Textbox', '分项名称')].SetValue('')
                self.ctrl[('Textbox', '项目概算')].SetValue('')
                return
            dlg = Initiation_GridDialog()
            if dlg.ShowModal() == wx.ID_OK:
                UDID, project, subproject = dlg.GetValue()[:3]
                estimate = dlg.GetValue()[uc.InitiationColLabels.index('项目概算')]
                def thousands(n): return '{:>,.2f}'.format(n)
                self.ctrl[('Textbox', '立项识别码')].SetValue(str(UDID))
                self.ctrl[('Textbox', '项目名称')].SetValue(project or '')
                self.ctrl[('Textbox', '分项名称')].SetValue(subproject or '')
                self.ctrl[('Textbox', '项目概算')].SetValue(thousands(estimate) if estimate is not None else '')
            dlg.Destroy()
        elif name in '招标单位识别码 招标单位名称'.split():
            if isCtrl:
                self.ctrl[('Textbox', '招标单位识别码')].SetValue('')
                self.ctrl[('Textbox', '招标单位名称')].SetValue('')
                return
            InitUDID = data[uc.BiddingColLabels.index('立项识别码')]
            if InitUDID:
                UnitUDID_list = operateDB().get_Init_Unit_List(InitUDID)
                dlg = Company_GridDialog(limit=True, where_sql='WHERE 单位识别码 IN %s', where_list=[UnitUDID_list])
            else:
                dlg = Company_GridDialog()
            if dlg.ShowModal() == wx.ID_OK:
                UDID, company_name = dlg.GetValue()[:2]
                self.ctrl[('Textbox', '招标单位识别码')].SetValue(str(UDID) or '')
                self.ctrl[('Textbox', '招标单位名称')].SetValue(company_name or '')
            dlg.Destroy()
        elif name in '招标代理识别码 招标代理单位名称'.split():
            if isCtrl:
                self.ctrl[('Textbox', '招标代理识别码')].SetValue('')
                self.ctrl[('Textbox', '招标代理单位名称')].SetValue('')
                return
            dlg = Company_GridDialog()
            if dlg.ShowModal() == wx.ID_OK:
                UDID, company_name = dlg.GetValue()[:2]
                self.ctrl[('Textbox', '招标代理识别码')].SetValue(str(UDID) or '')
                self.ctrl[('Textbox', '招标代理单位名称')].SetValue(company_name or '')
            dlg.Destroy()
        elif name in '中标单位识别码 中标单位名称'.split():
            if isCtrl:
                self.ctrl[('Textbox', '中标单位识别码')].SetValue('')
                self.ctrl[('Textbox', '中标单位名称')].SetValue('')
                return
            dlg = Company_GridDialog()
            if dlg.ShowModal() == wx.ID_OK:
                UDID, company_name = dlg.GetValue()[:2]
                self.ctrl[('Textbox', '中标单位识别码')].SetValue(str(UDID) or '')
                self.ctrl[('Textbox', '中标单位名称')].SetValue(company_name or '')
            dlg.Destroy()
        elif name == '招标文件定稿时间':
            if isCtrl:
                self.ctrl[('Textbox', '招标文件定稿时间')].SetValue('')
                return
            dlg = DateDialog()
            if dlg.ShowModal() == wx.ID_OK:
                yearmonthday = dlg.GetValue()
                self.ctrl[('Textbox', '招标文件定稿时间')].SetValue(str(yearmonthday) or '')
            dlg.Destroy()
        elif name == '公告邀请函发出时间':
            if isCtrl:
                self.ctrl[('Textbox', '公告邀请函发出时间')].SetValue('')
                return
            dlg = DateDialog()
            if dlg.ShowModal() == wx.ID_OK:
                yearmonthday = dlg.GetValue()
                self.ctrl[('Textbox', '公告邀请函发出时间')].SetValue(str(yearmonthday) or '')
            dlg.Destroy()
        elif name == '开标时间':
            if isCtrl:
                self.ctrl[('Textbox', '开标时间')].SetValue('')
                return
            dlg = DateDialog()
            if dlg.ShowModal() == wx.ID_OK:
                yearmonthday = dlg.GetValue()
                self.ctrl[('Textbox', '开标时间')].SetValue(str(yearmonthday) or '')
            dlg.Destroy()
        elif name == '中标通知书发出时间':
            if isCtrl:
                self.ctrl[('Textbox', '中标通知书发出时间')].SetValue('')
                return
            dlg = DateDialog()
            if dlg.ShowModal() == wx.ID_OK:
                yearmonthday = dlg.GetValue()
                self.ctrl[('Textbox', '中标通知书发出时间')].SetValue(str(yearmonthday) or '')
            dlg.Destroy()
    # methods
    def GetValue(self): return self.__value
    def SetValue(self):
        self.__value = []
        for each_ctrl_key, each_value_type in zip(self.__ctrl_key, self.__ctrl_value_type):
            value = self.ctrl[each_ctrl_key].GetValue()
            try:
                if value == '':
                    value = None
                elif each_value_type == '整数型':
                    value = int(value)
                elif each_value_type == '浮点型':
                    value = decimal.Decimal(value.strip().replace(',', ''))
            except:
                value = None
            self.__value.append(value)
        return self.__value
    def LoadTap(self): return self.__save_point
    def SaveTap(self, data=[]): self.__save_point = data
    def FormatInfoFromUI(self, ifReport=False):
        data = []
        for i, each_ctrl_key in zip(range(len(self.__ctrl_key)), self.__ctrl_key):
            value = self.ctrl[each_ctrl_key].GetValue()
            if len(value) == 0:
                value = None
            elif self.__ctrl_value_type[i] == '整数型':
                try:
                    value = int(value)
                except:
                    value = None
                    if ifReport:
                        dlg = wx.MessageDialog(self, message='<%s>中数据未能识别，将记录为NULL值' % each_ctrl_key[1], caption='警告', style=wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
            elif self.__ctrl_value_type[i] == '浮点型':
                try:
                    value = decimal.Decimal(value.strip().replace(',', ''))
                except:
                    value = None
                    if ifReport:
                        dlg = wx.MessageDialog(self, message='<%s>中数据未能识别，将记录为NULL值' % each_ctrl_key[1], caption='警告', style=wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
            elif self.__ctrl_value_type[i] == '日期型':
                try:
                    value = datetime.date(*time.strptime(value, "%Y-%m-%d")[:3])
                except:
                    value = None
                    if ifReport:
                        dlg = wx.MessageDialog(self, message='<%s>中数据未能识别，将记录为NULL值' % each_ctrl_key[1], caption='警告', style=wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
            data.append(value)
        return data
    def FormatInfoForDB(self):
        data = self.FormatInfoFromUI(True)
        result = []
        for key, value in zip(uc.BiddingColLabels, data):
            if key in uc.BiddingFields:
                result.append(value)
        return result
    def GetDataFromUDID(self, UDID):
        try:
            result = operateDB().read_For_Bidding_GridDialog(where_sql='WHERE 招标识别码=%s', where_list=[UDID])[0]
        except:
            result = None
        return result
    def ChangeMode(self, mode, UDID=None):
        if mode == uc.Dialog_Check:
            self.__mode = mode
            data = self.GetDataFromUDID(UDID) if UDID else []
            self.SetTitle('查看招标信息')
            for each_ctrl_key in self.__ctrl_key:
                if each_ctrl_key[0] == 'Textbox':
                    self.ctrl[each_ctrl_key].SetEditable(False)
                elif each_ctrl_key[0] == 'Combobox':
                    self.ctrl[each_ctrl_key].Enable(False)
            self.ctrl[('Button', uc.新建)].Enable(True)
            self.ctrl[('Button', uc.修改)].Enable(True)
            self.ctrl[('Button', uc.保存)].Enable(False)
            self.ctrl[('Button', uc.取消)].Enable(False)
            self.ChoiceDialog(False)
            self.FillBlanks(data)
        elif mode == uc.Dialog_New:
            self.__mode = mode
            self.SetTitle('新建招标信息')
            for each_ctrl_key in self.__ctrl_key:
                if each_ctrl_key[0] == 'Textbox' and each_ctrl_key[1] in '预算控制价 中标价 招标备注'.split():
                    self.ctrl[each_ctrl_key].SetEditable(True)
                elif each_ctrl_key[0] == 'Combobox':
                    self.ctrl[each_ctrl_key].Enable(True)
            self.ctrl[('Button', uc.新建)].Enable(False)
            self.ctrl[('Button', uc.修改)].Enable(False)
            self.ctrl[('Button', uc.保存)].Enable(True)
            self.ctrl[('Button', uc.取消)].Enable(True)
            self.ChoiceDialog(True)
            self.FillBlanks()
        elif mode == uc.Dialog_Edit:
            try:
                data = self.GetDataFromUDID(UDID) if UDID else []
                assert data
            except:
                dlg = wx.MessageDialog(self, message='该招标识别码数据库中未记录，请检查', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            self.__mode = mode
            self.SetTitle('修改招标信息')
            for each_ctrl_key in self.__ctrl_key:
                if each_ctrl_key[0] == 'Textbox' and each_ctrl_key[1] in '预算控制价 中标价 招标备注'.split():
                    self.ctrl[each_ctrl_key].SetEditable(True)
                elif each_ctrl_key[0] == 'Combobox':
                    self.ctrl[each_ctrl_key].Enable(True)
            self.ctrl[('Button', uc.新建)].Enable(False)
            self.ctrl[('Button', uc.修改)].Enable(False)
            self.ctrl[('Button', uc.保存)].Enable(True)
            self.ctrl[('Button', uc.取消)].Enable(True)
            self.ChoiceDialog(True)
            self.FillBlanks(data)
    def FillBlanks(self, data=[]):
        def thousands(n): return '{:>,.2f}'.format(n)
        def percents(n): return '{:>.2f}'.format((n or 0) * 100) + '%'
        for each_ctrl_key in self.__ctrl_key:
            try:
                value = data[self.__ctrl_key.index(each_ctrl_key)]
                value_type = self.__ctrl_value_type[self.__ctrl_key.index(each_ctrl_key)]
                if value is None:
                    value = ''
                elif value_type == '浮点型':
                    value = thousands(value)
                elif value_type == '百分比':
                    value = percents(value)
                else:
                    value = str(value)
                self.ctrl[each_ctrl_key].SetValue(value)
            except:
                self.ctrl[each_ctrl_key].SetValue('')
    def ChoiceDialog(self, could_open): self.__choice_dialog_could_open = could_open

class Contract_GridDialog(GridDialog):
    __value = None
    __colLabels = uc.ContractColLabels
    __colLabels_type = uc.ContractColLabels_Type
    filter_case = []
    def __init__(self, title='合同信息', data=None, size=uc.Size_BaseDialog, limit=False, where_sql='' ,where_list=[]):
        self.init(title, data, size)
        if limit:
            self.ctrl[('Button', uc.筛选)].Enable(False)
            self.ctrl[('Button', uc.查询结构)].Enable(False)
            self.ctrl[('Button', uc.刷新)].Enable(False)
        for eachEvent, eachHandler in self.gridBindData():
            self.ctrl[('Grid', None)].Bind(eachEvent, eachHandler)
        for key, eachEvent, eachHandler in self.ctrlBindData():
            self.ctrl[key].Bind(eachEvent, eachHandler)
        self.readDB_and_reFreshGrid(where_sql=where_sql, where_list=where_list)
        self.ctrl[('Grid', None)].SelectRow(0)
    # binder
    def gridBindData(self):
        return ((wx.grid.EVT_GRID_LABEL_LEFT_CLICK,  self.labelOnClick),
                (wx.grid.EVT_GRID_SELECT_CELL,       self.gridOnSelectACell),
                (wx.grid.EVT_GRID_LABEL_LEFT_DCLICK, self.labelOnDCLICK),
                (wx.grid.EVT_GRID_CELL_RIGHT_CLICK,  self.gridOnRClick),
                (wx.grid.EVT_GRID_CELL_LEFT_DCLICK,  self.gridOnDClick))
    def ctrlBindData(self):
        return ((('Button',  uc.新建),     wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.修改),     wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.筛选),     wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.查询结构), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.刷新),     wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.导出),     wx.EVT_BUTTON, self.clickOnButton),
               )
    # events
    def clickOnButton(self, event):
        label = wx.FindWindowById(event.Id, self).GetLabel()
        if label == uc.刷新:
            self.readDB_and_reFreshGrid()
            self.filter_case = []
        elif label == uc.新建:
            dlg = Contract_MaintainDialog(uc.Dialog_New)
            dlg.ShowModal()
            dlg.Destroy()
            self.readDB_and_reFreshGrid()
        elif label == uc.修改:
            data = self.GetValue()
            dlg = Contract_MaintainDialog(uc.Dialog_Edit, data[0])
            dlg.ShowModal()
            dlg.Destroy()
            self.readDB_and_reFreshGrid()
        elif label == uc.筛选:
            dlg = FilterDialog(self.__colLabels, self.__colLabels_type, self.filter_case)
            if dlg.ShowModal() == wx.ID_OK:
                self.filter_case = dlg.GetValue()
            dlg.Destroy()
            # 整理出where_sql和where_list
            if not self.filter_case:
                return
            where_sql = []
            where_list = []
            for each_filter in self.filter_case:
                where_sql.append(each_filter[1][0])
                where_list.extend(each_filter[1][1])
            where_sql = 'WHERE ' + ' AND '.join(where_sql)
            self.readDB_and_reFreshGrid(where_sql, where_list)
        elif label == uc.查询结构:
            dlg = TreeDialog()
            if dlg.ShowModal() == wx.ID_OK:
                data = dlg.GetValue()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return
            # 筛选树型框里传递来的记录
            UDID = data[0]
            where_sql = 'WHERE 立项识别码=%s'
            self.filter_case = [['【立项识别码 等于 %d】' % UDID, ['立项识别码=%s', [UDID], ['立项识别码', '整数型', '等于', UDID, '', '', '', '', 0]]]]
            self.readDB_and_reFreshGrid(where_sql, [UDID])
        elif label == uc.导出:
            wildcard = 'Excel files (*.xlsx)|*.xlsx'
            dlg = wx.FileDialog(None, "Choose a file", '', '', wildcard, 0)    #选择文件对话框
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            dlg.Destroy()
            filename = dlg.GetPath()
            if os.path.exists(filename):
                dlg = wx.MessageDialog(self, message='该文件已存在，点击<是>覆盖文件', caption='警告', style= wx.YES_NO | wx.NO_DEFAULT)
                if dlg.ShowModal() == wx.ID_NO:
                    dlg.Destroy()
                    return
                else:
                    dlg.Destroy()
            data = self.ctrl[('Grid', None)].GetTable().data
            try:
                Exporter().commonExport(filename, self.ctrl[('Grid', None)], self.__colLabels, data)
                dlg = wx.MessageDialog(self, message='文件导出成功', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except Exception as e:
                dlg = wx.MessageDialog(self, message='文件导出失败！\n%s' % str(e), caption='警告', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
    def labelOnClick(self, event):
        col = event.GetCol()
        isCtrl = event.ControlDown()
        isShift = event.ShiftDown()
        if col >= 0 and isCtrl:
            data = self.get_data_by_sortGrid(self.ctrl[('Grid', None)], col, False, self.__colLabels_type)
            self.reFreshGrid(self.ctrl[('Grid', None)], data, self.__colLabels, [uc.ContractColLabels.index('已付款占概算'), uc.ContractColLabels.index('已付款占合同')])
        elif col >= 0 and isShift:
            data = self.get_data_by_sortGrid(self.ctrl[('Grid', None)], col, True, self.__colLabels_type)
            self.reFreshGrid(self.ctrl[('Grid', None)], data, self.__colLabels, [uc.ContractColLabels.index('已付款占概算'), uc.ContractColLabels.index('已付款占合同')])
        else:
            return
    def gridOnSelectACell(self, event):
        row = event.GetRow()
        result = self.SetValue(row)
        if result:
            self.ctrl[('Textbox', uc.显示窗)].SetValue('%s-%s%s-%s' % (result[self.__colLabels.index('合同识别码')] or '', 
                      result[self.__colLabels.index('项目名称')] or '', result[self.__colLabels.index('分项名称')] or '', 
                      result[self.__colLabels.index('合同名称')] or ''))
    def labelOnDCLICK(self, event):
        col = event.GetCol()
        data = self.ctrl[('Grid', None)].GetTable().data
        colLabels = self.ctrl[('Grid', None)].GetTable().colLabels
        values = []
        def thousands(n):
            return '{:>,.2f}'.format(n)
        if self.__colLabels_type[col] in '整数型 浮点型'.split():
            for key, value in data.items():
                if key[1] == col and value is not None:
                    values.append(value)
            try:
                dlg = wx.MessageDialog(self, message='<%s>列下：\n共有<%d>个值，\n和为<%s>，\n最大值为<%s>，\n最小值为<%s>' \
                                       % (colLabels[col], len(values), thousands(sum(values)), thousands(max(values)), thousands(min(values))),
                                       caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except:
                pass
        elif self.__colLabels_type[col] in ['日期型']:
            for key, value in data.items():
                if key[1] == col and value is not None:
                    values.append(value)
            try:
                dlg = wx.MessageDialog(self, message='<%s>列下：\n共有<%d>个值，\n最大值为<%s>，\n最小值为<%s>' % (colLabels[col], len(values), max(values), min(values)),
                                       caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except:
                pass
    def gridOnDClick(self, event):
        self.EndModal(wx.ID_OK)
    def gridOnRClick(self, event):
        row = event.GetRow()
        if row >= 0:
            self.SetValue(row)
            self.ctrl[('Grid', None)].SelectRow(row)
            self.checkContract()
    # methods
    def checkContract(self):
        data = self.GetValue()
        dlg = Contract_MaintainDialog(uc.Dialog_Check, data[0])
        dlg.ShowModal()
        dlg.Destroy()
        self.readDB_and_reFreshGrid()
    def GetValue(self):
        return self.__value
    def SetValue(self, row):
        data = self.ctrl[('Grid', None)].GetTable().data
        colLabels = self.ctrl[('Grid', None)].GetTable().colLabels
        try:
            rownum = max(data.keys())[0] + 1
        except:
            rownum = 0
        colnum = len(colLabels)
        result = []
        if rownum == 0:
            return
        for col in range(colnum):
            result.append(data.get((row, col)))
        self.__value = result
        return result
    def readDB(self, where_sql='', where_list=[], order_sql='', order_list=[]):
        return operateDB().read_For_Contract_GridDialog(where_sql, where_list, order_sql, order_list)
    def readDB_and_reFreshGrid(self, where_sql='', where_list=[], order_sql='', order_list=[]):
        data = self.format_DBdata2Griddata(self.readDB(where_sql, where_list, order_sql, order_list))
        self.reFreshGrid(self.ctrl[('Grid', None)], data, self.__colLabels, [uc.ContractColLabels.index('已付款占概算'), uc.ContractColLabels.index('已付款占合同')])

class Contract_MaintainDialog(MaintainDialog):
    __mode = uc.Dialog_Check
    __choice_dialog_could_open = False
    __init_dialog_could_open = True
    __value = None
    __save_point = None
    __ctrl_key = list(zip(['Textbox'] * 11 + ['Combobox'] + ['Textbox'] * 22, 
                      uc.ContractColLabels))
    __ctrl_value_type = uc.ContractColLabels_Type
    def __init__(self, mode=uc.Dialog_Check, UDID=-1):
        self.init()
        little_sizer = {}
        def create_Label_Textbox_Pairs(key, size_Textbox, size_Label=uc.Size_Label_BaseDialog):
            little_sizer[key] = wx.BoxSizer(wx.HORIZONTAL)
            self.ctrl[('Label', key)] = wx.StaticText(self, -1, key+'：', size=size_Label, style=wx.ALIGN_RIGHT)
            self.ctrl[('Textbox', key)] = wx.TextCtrl(self, -1, '', size=size_Textbox, style=wx.TE_READONLY|wx.TE_CENTRE|wx.BORDER_STATIC, name=key)
            little_sizer[key].Add(self.ctrl[('Label', key)])
            little_sizer[key].Add(self.ctrl[('Textbox', key)])
        def create_Label_MultiTextbox_Pairs(key, size_Textbox, size_Label=uc.Size_Label_BaseDialog):
            little_sizer[key] = wx.BoxSizer(wx.HORIZONTAL)
            self.ctrl[('Label', key)] = wx.StaticText(self, -1, key+'：', size=size_Label, style=wx.ALIGN_RIGHT)
            self.ctrl[('Textbox', key)] = wx.TextCtrl(self, -1, '', size=size_Textbox, style=wx.TE_READONLY|wx.BORDER_STATIC|wx.TE_MULTILINE, name=key)
            little_sizer[key].Add(self.ctrl[('Label', key)])
            little_sizer[key].Add(self.ctrl[('Textbox', key)])
        def create_Label_Combobox_Pairs(key, size_Combobox, size_Label=uc.Size_Label_BaseDialog):
            little_sizer[key] = wx.BoxSizer(wx.HORIZONTAL)
            self.ctrl[('Label', key)] = wx.StaticText(self, -1, key+'：', size=size_Label, style=wx.ALIGN_RIGHT)
            style = wx.TE_PROCESS_ENTER|wx.CB_DROPDOWN|wx.TE_CENTER|wx.TE_READONLY
            self.ctrl[('Combobox', key)] = wx.ComboBox(self, -1, value='', size=size_Combobox, choices=[], style=style, name=key)
            little_sizer[key].Add(self.ctrl[('Label', key)])
            little_sizer[key].Add(self.ctrl[('Combobox', key)])
        # 重绘控件
        create_Label_Textbox_Pairs( '合同识别码'   , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '立项识别码'   , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '项目名称'     , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '分项名称'     , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '招标识别码'   , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '招标方式'     , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '项目概算'     , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '中标价'       , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '合同编号'     , uc.Size_Textbox_Long_BaseDialog)
        create_Label_Textbox_Pairs( '合同名称'     , uc.Size_Textbox_Long_BaseDialog)
        create_Label_Textbox_Pairs( '合同主要内容' , uc.Size_Textbox_Long_BaseDialog)
        create_Label_Combobox_Pairs('合同类别'     , uc.Size_Combobox_Short_BaseDialog)
        create_Label_Textbox_Pairs( '甲方识别码'   , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '甲方单位名称' , uc.Size_Textbox_Long_BaseDialog)
        create_Label_Textbox_Pairs( '乙方识别码'   , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '乙方单位名称' , uc.Size_Textbox_Long_BaseDialog)
        create_Label_Textbox_Pairs( '丙方识别码'   , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '丙方单位名称' , uc.Size_Textbox_Long_BaseDialog)
        create_Label_Textbox_Pairs( '丁方识别码'   , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '丁方单位名称' , uc.Size_Textbox_Long_BaseDialog)
        create_Label_Textbox_Pairs( '合同签订时间' , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '合同值_签订时', uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '合同值_最新值', uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '合同值_最终值', uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '已付款'       , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '已付款占概算' , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '已付款占合同' , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '形象进度'     , uc.Size_Textbox_VeryLong_BaseDialog)
        create_Label_Textbox_Pairs( '支付上限'     , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '开工时间'     , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '竣工合格时间' , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '保修结束时间' , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '审计完成时间' , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_MultiTextbox_Pairs( '合同备注'    , uc.Size_Textbox_Note)
        self.ctrl[('Combobox', '合同类别')].AppendItems('代建 前期 招标代理 勘察 设计 造价 监理 施工 材料、设备 其他'.split())
        core_sizer = wx.BoxSizer(wx.VERTICAL)
        row_sizer = []
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['合同识别码'])
        row_sizer[-1].Add(little_sizer['立项识别码'])
        row_sizer[-1].Add(little_sizer['项目名称'])
        row_sizer[-1].Add(little_sizer['分项名称'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['招标识别码'])
        row_sizer[-1].Add(little_sizer['招标方式'])
        row_sizer[-1].Add(little_sizer['项目概算'])
        row_sizer[-1].Add(little_sizer['中标价'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['合同编号'])
        row_sizer[-1].Add(little_sizer['合同名称'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['合同主要内容'])
        row_sizer[-1].Add(little_sizer['合同类别'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['甲方识别码'])
        row_sizer[-1].Add(little_sizer['甲方单位名称'])
        core_sizer.AddSpacer(10)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['乙方识别码'])
        row_sizer[-1].Add(little_sizer['乙方单位名称'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['丙方识别码'])
        row_sizer[-1].Add(little_sizer['丙方单位名称'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['丁方识别码'])
        row_sizer[-1].Add(little_sizer['丁方单位名称'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['合同签订时间'])
        row_sizer[-1].Add(little_sizer['合同值_签订时'])
        row_sizer[-1].Add(little_sizer['合同值_最新值'])
        row_sizer[-1].Add(little_sizer['合同值_最终值'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['已付款'])
        row_sizer[-1].Add(little_sizer['已付款占概算'])
        row_sizer[-1].Add(little_sizer['已付款占合同'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['形象进度'])
        row_sizer[-1].Add(little_sizer['支付上限'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['开工时间'])
        row_sizer[-1].Add(little_sizer['竣工合格时间'])
        row_sizer[-1].Add(little_sizer['保修结束时间'])
        row_sizer[-1].Add(little_sizer['审计完成时间'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['合同备注'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        self.sizer.Add(core_sizer, 0, wx.ALL, 10)
        self.SetSizer(self.all_sizer)
        self.all_sizer.Fit(self)
        for key, eachEvent, eachHandler in self.ctrlBindData():
            self.ctrl[key].Bind(eachEvent, eachHandler)
        # 检查模式
        self.ChangeMode(mode, UDID)    # 通过识别码读取信息
        self.SaveTap(self.FormatInfoFromUI())
    # binder
    def ctrlBindData(self):
        return ((('Button',  uc.跳转), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.新建), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.修改), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.保存), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.会签表格), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.取消), wx.EVT_BUTTON, self.clickOnButton),
                (('Textbox', '立项识别码'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '项目名称'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '分项名称'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '项目概算'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '招标识别码'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '招标方式'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '中标价'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '甲方识别码'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '甲方单位名称'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '乙方识别码'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '乙方单位名称'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '丙方识别码'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '丙方单位名称'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '丁方识别码'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '丁方单位名称'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '合同签订时间'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '开工时间'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '竣工合格时间'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '保修结束时间'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '审计完成时间'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox)
               )
    # events
    def clickOnButton(self, event):
        label = wx.FindWindowById(event.Id, self).GetLabel()
        if label == uc.跳转:
            try:
                UDID = self.FormatInfoForDB()[uc.ContractFields.index('立项识别码')]
            except:
                UDID = None
            self.Jump(event, UDID, '跳转至相应<立项>信息 跳转至相应<招标>信息 跳转至相应<付款>信息'.split(), 
                      Initiation_GridDialog, Bidding_GridDialog, Contract_GridDialog, Budget_GridDialog, Payment_GridDialog)
        elif label == uc.新建:
            self.SaveTap(self.FormatInfoFromUI())
            self.ChangeMode(uc.Dialog_New)
        elif label == uc.修改:
            self.SaveTap(self.FormatInfoFromUI())
            try:
                UDID = int(self.ctrl[('Textbox', '合同识别码')].GetValue())
            except:
                UDID = 0
            self.ChangeMode(uc.Dialog_Edit, UDID)
        elif label == uc.取消:
            hasChanged = self.FormatInfoFromUI() != self.LoadTap()
            if hasChanged:
                dlg = wx.MessageDialog(self, message='更改的数据尚未保存，你确定要退出吗？', caption='警告', style= wx.YES_NO | wx.NO_DEFAULT)
                if dlg.ShowModal() == wx.ID_NO:
                    dlg.Destroy()
                    return
                else:
                    dlg.Destroy()
            self.ChangeMode(uc.Dialog_Check)
            self.FillBlanks(self.LoadTap())
        elif label == uc.保存:
            hasChanged = self.FormatInfoFromUI() != self.LoadTap()
            if not hasChanged:
                dlg = wx.MessageDialog(self, message='数据并未做任何更改，不需要保存。', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            dlg = wx.MessageDialog(self, message='点击确定保存数据。', caption='提示', style= wx.YES_NO | wx.NO_DEFAULT)
            if dlg.ShowModal() == wx.ID_NO:
                dlg.Destroy()
                return
            else:
                dlg.Destroy()
            data = self.FormatInfoForDB()
            UDID = data[0]
            InitUDID = data[uc.ContractFields.index('立项识别码')]
            if not InitUDID:
                dlg = wx.MessageDialog(self, message='立项信息未填写，请检查', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            save_result = operateDB().save_For_Contract_MaintainDialog(data)
            try:
                assert save_result
                dlg = wx.MessageDialog(self, message='数据保存成功。', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except Exception as e:
                dlg = wx.MessageDialog(self, message='数据保存失败\n%s' % str(e), caption='警告', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            self.ChangeMode(uc.Dialog_Check, UDID)
            self.SaveTap(data)
        elif label == uc.会签表格:
            # 取得数据，存入字典
            data = self.FormatInfoFromUI()
            sign_Keys = '合同名称 合同编号 甲方单位名称 乙方单位名称 合同主要内容 合同值_签订时'.split()
            sign_Dict = {}
            for i, value in enumerate(data):
                if uc.ContractColLabels[i] in sign_Keys:
                    sign_Dict[uc.ContractColLabels[i]] = value
            today = datetime.date.today()
            sign_Dict['提交日期'] = str(today)
            if sign_Dict['合同值_签订时'] is not None:
                def thousands(n): return '{:>,.2f}'.format(n)
                sign_Dict['合同值_签订时'] = '￥' + thousands(sign_Dict['合同值_签订时'])
            # 选取导出路径
            wildcard = 'Word files (*.docx)|*.docx'
            dlg = wx.FileDialog(None, "Choose a file", '', '', wildcard, 0)    #选择文件对话框
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            dlg.Destroy()
            filename = dlg.GetPath()
            if os.path.exists(filename):
                dlg = wx.MessageDialog(self, message='该文件已存在，点击<是>覆盖文件', caption='警告', style= wx.YES_NO | wx.NO_DEFAULT)
                if dlg.ShowModal() == wx.ID_NO:
                    dlg.Destroy()
                    return
                else:
                    dlg.Destroy()
            # 生成文件
            try:
                Exporter().docx_Contract_Export(OutputFile=filename, ContractDict=sign_Dict)
                os.startfile(filename)
            except Exception as e:
                dlg = wx.MessageDialog(self, message='合同会签表未能成功导出！错误代码：\n%s' % e, caption='警告', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
    def DclickOnTextbox(self, event):
        if not self.__choice_dialog_could_open:
            return
        def thousands(n): return '{:>,.2f}'.format(n)
        isCtrl = event.ControlDown()
        name = wx.FindWindowById(event.GetId()).GetName()
        data = self.FormatInfoFromUI()
        if name in '立项识别码 项目名称 分项名称 项目概算'.split() and self.__init_dialog_could_open:
            if isCtrl:
                self.ctrl[('Textbox', '立项识别码')].SetValue('')
                self.ctrl[('Textbox', '项目名称')].SetValue('')
                self.ctrl[('Textbox', '分项名称')].SetValue('')
                self.ctrl[('Textbox', '项目概算')].SetValue('')
                return
            dlg = Initiation_GridDialog()
            if dlg.ShowModal() == wx.ID_OK:
                UDID, project, subproject = dlg.GetValue()[:3]
                estimate = dlg.GetValue()[uc.InitiationColLabels.index('项目概算')]
                self.ctrl[('Textbox', '立项识别码')].SetValue(str(UDID))
                self.ctrl[('Textbox', '项目名称')].SetValue(project or '')
                self.ctrl[('Textbox', '分项名称')].SetValue(subproject or '')
                self.ctrl[('Textbox', '项目概算')].SetValue(thousands(estimate) if estimate is not None else '')
            dlg.Destroy()
        elif name in '招标识别码 招标方式 中标价'.split():
            if isCtrl:
                self.ctrl[('Textbox', '招标识别码')].SetValue('')
                self.ctrl[('Textbox', '招标方式')].SetValue('')
                self.ctrl[('Textbox', '中标价')].SetValue('')
                self.__init_dialog_could_open = True
                return
            InitUDID = data[uc.ContractColLabels.index('立项识别码')]
            if InitUDID:
                dlg = Bidding_GridDialog(limit=True, where_sql='WHERE 立项识别码=%s', where_list=[InitUDID])
            else:
                dlg = Bidding_GridDialog()
            if dlg.ShowModal() == wx.ID_OK:
                UDID = dlg.GetValue()[0]
                bidding_mode = dlg.GetValue()[uc.BiddingColLabels.index('招标方式')]
                price_winner = dlg.GetValue()[uc.BiddingColLabels.index('中标价')]
                InitUDID = dlg.GetValue()[uc.BiddingColLabels.index('立项识别码')]
                project = dlg.GetValue()[uc.BiddingColLabels.index('项目名称')]
                subproject = dlg.GetValue()[uc.BiddingColLabels.index('分项名称')]
                estimate = dlg.GetValue()[uc.BiddingColLabels.index('项目概算')]
                self.ctrl[('Textbox', '招标识别码')].SetValue(str(UDID) or '')
                self.ctrl[('Textbox', '招标方式')].SetValue(bidding_mode or '')
                self.ctrl[('Textbox', '中标价')].SetValue(thousands(price_winner) if price_winner is not None else '')
                self.ctrl[('Textbox', '立项识别码')].SetValue(str(InitUDID))
                self.ctrl[('Textbox', '项目名称')].SetValue(project or '')
                self.ctrl[('Textbox', '分项名称')].SetValue(subproject or '')
                self.ctrl[('Textbox', '项目概算')].SetValue(thousands(estimate) if estimate is not None else '')
                self.__init_dialog_could_open = False
            dlg.Destroy()
        elif name in '甲方识别码 甲方单位名称'.split():
            if isCtrl:
                self.ctrl[('Textbox', '甲方识别码')].SetValue('')
                self.ctrl[('Textbox', '甲方单位名称')].SetValue('')
                return
            InitUDID = data[uc.ContractColLabels.index('立项识别码')]
            BiddingUDID = data[uc.ContractColLabels.index('招标识别码')]
            if BiddingUDID:
                UnitUDID_list = operateDB().get_Bidding_Unit_List(BiddingUDID)
                dlg = Company_GridDialog(limit=True, where_sql='WHERE 单位识别码 IN %s', where_list=[UnitUDID_list])
            elif InitUDID:
                UnitUDID_list = operateDB().get_Init_Unit_List(InitUDID)
                dlg = Company_GridDialog(limit=True, where_sql='WHERE 单位识别码 IN %s', where_list=[UnitUDID_list])
            else:
                dlg = Company_GridDialog()
            if dlg.ShowModal() == wx.ID_OK:
                UDID, company_name = dlg.GetValue()[:2]
                self.ctrl[('Textbox', '甲方识别码')].SetValue(str(UDID) or '')
                self.ctrl[('Textbox', '甲方单位名称')].SetValue(company_name or '')
            dlg.Destroy()
        elif name in '乙方识别码 乙方单位名称'.split():
            if isCtrl:
                self.ctrl[('Textbox', '乙方识别码')].SetValue('')
                self.ctrl[('Textbox', '乙方单位名称')].SetValue('')
                return
            BiddingUDID = data[uc.ContractColLabels.index('招标识别码')]
            if BiddingUDID:
                UnitUDID_list = operateDB().get_Bidding_Winner_Unit_List(BiddingUDID)
                dlg = Company_GridDialog(limit=True, where_sql='WHERE 单位识别码 IN %s', where_list=[UnitUDID_list])
            else:
                dlg = Company_GridDialog()
            if dlg.ShowModal() == wx.ID_OK:
                UDID, company_name = dlg.GetValue()[:2]
                self.ctrl[('Textbox', '乙方识别码')].SetValue(str(UDID) or '')
                self.ctrl[('Textbox', '乙方单位名称')].SetValue(company_name or '')
            dlg.Destroy()
        elif name in '丙方识别码 丙方单位名称'.split():
            if isCtrl:
                self.ctrl[('Textbox', '丙方识别码')].SetValue('')
                self.ctrl[('Textbox', '丙方单位名称')].SetValue('')
                return
            dlg = Company_GridDialog()
            if dlg.ShowModal() == wx.ID_OK:
                UDID, company_name = dlg.GetValue()[:2]
                self.ctrl[('Textbox', '丙方识别码')].SetValue(str(UDID) or '')
                self.ctrl[('Textbox', '丙方单位名称')].SetValue(company_name or '')
            dlg.Destroy()
        elif name in '丁方识别码 丁方单位名称'.split():
            if isCtrl:
                self.ctrl[('Textbox', '丁方识别码')].SetValue('')
                self.ctrl[('Textbox', '丁方单位名称')].SetValue('')
                return
            dlg = Company_GridDialog()
            if dlg.ShowModal() == wx.ID_OK:
                UDID, company_name = dlg.GetValue()[:2]
                self.ctrl[('Textbox', '丁方识别码')].SetValue(str(UDID) or '')
                self.ctrl[('Textbox', '丁方单位名称')].SetValue(company_name or '')
            dlg.Destroy()
        elif name == '合同签订时间':
            if isCtrl:
                self.ctrl[('Textbox', '合同签订时间')].SetValue('')
                return
            dlg = DateDialog()
            if dlg.ShowModal() == wx.ID_OK:
                yearmonthday = dlg.GetValue()
                self.ctrl[('Textbox', '合同签订时间')].SetValue(str(yearmonthday) or '')
            dlg.Destroy()
        elif name == '开工时间':
            if isCtrl:
                self.ctrl[('Textbox', '开工时间')].SetValue('')
                return
            dlg = DateDialog()
            if dlg.ShowModal() == wx.ID_OK:
                yearmonthday = dlg.GetValue()
                self.ctrl[('Textbox', '开工时间')].SetValue(str(yearmonthday) or '')
            dlg.Destroy()
        elif name == '竣工合格时间':
            if isCtrl:
                self.ctrl[('Textbox', '竣工合格时间')].SetValue('')
                return
            dlg = DateDialog()
            if dlg.ShowModal() == wx.ID_OK:
                yearmonthday = dlg.GetValue()
                self.ctrl[('Textbox', '竣工合格时间')].SetValue(str(yearmonthday) or '')
            dlg.Destroy()
        elif name == '保修结束时间':
            if isCtrl:
                self.ctrl[('Textbox', '保修结束时间')].SetValue('')
                return
            dlg = DateDialog()
            if dlg.ShowModal() == wx.ID_OK:
                yearmonthday = dlg.GetValue()
                self.ctrl[('Textbox', '保修结束时间')].SetValue(str(yearmonthday) or '')
            dlg.Destroy()
        elif name == '审计完成时间':
            if isCtrl:
                self.ctrl[('Textbox', '审计完成时间')].SetValue('')
                return
            dlg = DateDialog()
            if dlg.ShowModal() == wx.ID_OK:
                yearmonthday = dlg.GetValue()
                self.ctrl[('Textbox', '审计完成时间')].SetValue(str(yearmonthday) or '')
            dlg.Destroy()
    # methods
    def GetValue(self): return self.__value
    def SetValue(self):
        self.__value = []
        for each_ctrl_key, each_value_type in zip(self.__ctrl_key, self.__ctrl_value_type):
            value = self.ctrl[each_ctrl_key].GetValue()
            try:
                if value == '':
                    value = None
                elif each_value_type == '整数型':
                    value = int(value)
                elif each_value_type == '浮点型':
                    value = decimal.Decimal(value.strip().replace(',', ''))
                elif each_value_type == '百分比':
                    value = float(value.strip().replace('%', '')) / 100
            except:
                value = None
            self.__value.append(value)
        return self.__value
    def LoadTap(self): return self.__save_point
    def SaveTap(self, data=[]): self.__save_point = data
    def FormatInfoFromUI(self, ifReport=False):
        data = []
        for i, each_ctrl_key in zip(range(len(self.__ctrl_key)), self.__ctrl_key):
            value = self.ctrl[each_ctrl_key].GetValue()
            if len(value) == 0:
                value = None
            elif self.__ctrl_value_type[i] == '整数型':
                try:
                    value = int(value)
                except:
                    value = None
                    if ifReport:
                        dlg = wx.MessageDialog(self, message='<%s>中数据未能识别，将记录为NULL值' % each_ctrl_key[1], caption='警告', style=wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
            elif self.__ctrl_value_type[i] == '浮点型':
                try:
                    value = decimal.Decimal(value.strip().replace(',', ''))
                except:
                    value = None
                    if ifReport:
                        dlg = wx.MessageDialog(self, message='<%s>中数据未能识别，将记录为NULL值' % each_ctrl_key[1], caption='警告', style=wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
            elif self.__ctrl_value_type[i] == '百分比':
                try:
                    value = float(value.strip().replace('%', '')) / 100
                except:
                    value = None
                    if ifReport:
                        dlg = wx.MessageDialog(self, message='<%s>中数据未能识别，将记录为NULL值' % each_ctrl_key[1], caption='警告', style=wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
            elif self.__ctrl_value_type[i] == '日期型':
                try:
                    value = datetime.date(*time.strptime(value, "%Y-%m-%d")[:3])
                except:
                    value = None
                    if ifReport:
                        dlg = wx.MessageDialog(self, message='<%s>中数据未能识别，将记录为NULL值' % each_ctrl_key[1], caption='警告', style=wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
            data.append(value)
        return data
    def FormatInfoForDB(self):
        data = self.FormatInfoFromUI(True)
        result = []
        for key, value in zip(uc.ContractColLabels, data):
            if key in uc.ContractFields:
                result.append(value)
        return result
    def GetDataFromUDID(self, UDID):
        try:
            result = operateDB().read_For_Contract_GridDialog(where_sql='WHERE 合同识别码=%s', where_list=[UDID])[0]
        except:
            result = None
        return result
    def ChangeMode(self, mode, UDID=None):
        if mode == uc.Dialog_Check:
            self.__mode = mode
            data = self.GetDataFromUDID(UDID) if UDID else []
            self.SetTitle('查看合同信息')
            for each_ctrl_key in self.__ctrl_key:
                if each_ctrl_key[0] == 'Textbox':
                    self.ctrl[each_ctrl_key].SetEditable(False)
                elif each_ctrl_key[0] == 'Combobox':
                    self.ctrl[each_ctrl_key].Enable(False)
            self.ctrl[('Button', uc.新建)].Enable(True)
            self.ctrl[('Button', uc.修改)].Enable(True)
            self.ctrl[('Button', uc.保存)].Enable(False)
            self.ctrl[('Button', uc.取消)].Enable(False)
            self.ChoiceDialog(False)
            self.FillBlanks(data)
        elif mode == uc.Dialog_New:
            self.__mode = mode
            self.SetTitle('新建合同信息')
            for each_ctrl_key in self.__ctrl_key:
                if each_ctrl_key[0] == 'Textbox' and each_ctrl_key[1] in '合同编号 合同名称 合同主要内容 合同类别 合同值_签订时 合同值_最新值 合同值_最终值 形象进度 支付上限 合同备注'.split():
                    self.ctrl[each_ctrl_key].SetEditable(True)
                elif each_ctrl_key[0] == 'Combobox':
                    self.ctrl[each_ctrl_key].Enable(True)
            self.ctrl[('Button', uc.新建)].Enable(False)
            self.ctrl[('Button', uc.修改)].Enable(False)
            self.ctrl[('Button', uc.保存)].Enable(True)
            self.ctrl[('Button', uc.取消)].Enable(True)
            self.ChoiceDialog(True)
            self.FillBlanks()
        elif mode == uc.Dialog_Edit:
            try:
                data = self.GetDataFromUDID(UDID) if UDID else []
                assert data
            except:
                dlg = wx.MessageDialog(self, message='该合同识别码数据库中未记录，请检查', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            self.__mode = mode
            self.SetTitle('修改合同信息')
            for each_ctrl_key in self.__ctrl_key:
                if each_ctrl_key[0] == 'Textbox' and each_ctrl_key[1] in '合同编号 合同名称 合同主要内容 合同类别 合同值_签订时 合同值_最新值 合同值_最终值 形象进度 支付上限 合同备注'.split():
                    self.ctrl[each_ctrl_key].SetEditable(True)
                elif each_ctrl_key[0] == 'Combobox':
                    self.ctrl[each_ctrl_key].Enable(True)
            self.ctrl[('Button', uc.新建)].Enable(False)
            self.ctrl[('Button', uc.修改)].Enable(False)
            self.ctrl[('Button', uc.保存)].Enable(True)
            self.ctrl[('Button', uc.取消)].Enable(True)
            self.ChoiceDialog(True)
            self.FillBlanks(data)
    def FillBlanks(self, data=[]):
        def thousands(n): return '{:>,.2f}'.format(n)
        def percents(n): return '{:>.2f}'.format((n or 0) * 100) + '%'
        for each_ctrl_key in self.__ctrl_key:
            try:
                value = data[self.__ctrl_key.index(each_ctrl_key)]
                value_type = self.__ctrl_value_type[self.__ctrl_key.index(each_ctrl_key)]
                if value is None:
                    value = ''
                elif value_type == '浮点型':
                    value = thousands(value)
                elif value_type == '百分比':
                    value = percents(value)
                else:
                    value = str(value)
                self.ctrl[each_ctrl_key].SetValue(value)
            except:
                self.ctrl[each_ctrl_key].SetValue('')
    def ChoiceDialog(self, could_open): self.__choice_dialog_could_open = could_open

class Budget_TreeDialog(wx.Dialog):
    __result = None
    def __init__(self):
        self.init()
    def init(self):
        wx.Dialog.__init__(self, None, -1, '预算结构查看器', size=uc.Size_BigDialog, style=wx.CAPTION|wx.CLOSE_BOX|wx.MAXIMIZE_BOX)
        self.Centre(wx.BOTH)
        self.SetMinSize(uc.Size_BigDialog)
        # Create the tree
        self.tree = wx.dataview.TreeListCtrl(self, style = wx.dataview.TL_SINGLE|wx.TR_FULL_ROW_HIGHLIGHT, size=uc.Size_BaseDialog)
        self.tree.AppendColumn("预算名称-预算周期", align=wx.ALIGN_CENTER)
        self.tree.AppendColumn("预算额度", align=wx.ALIGN_RIGHT)
        self.tree.AppendColumn("预算已分配率", align=wx.ALIGN_RIGHT)
        self.tree.AppendColumn("层级", align=wx.ALIGN_CENTER)
        self.treeData = operateDB().format_Budget_Details_By_Tree()
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
    def makeTree(self, root, treeData):
        def thousands(n): return '{:>,.2f}'.format(n)
        def percents(n): return '{:>.2f}'.format((n or 0) * 100) + '%'
        child = root
        for item in treeData:
            if str(type(item[0])) == "<class 'int'>":
                child = self.tree.AppendItem(root, str(item[0]) + '-' + item[1] + ('-' + item[2] if item[2] else '')) # 预算识别码-预算名称-预算周期
                self.tree.SetItemText(child, 1, thousands(item[3]) if item[3] else '')                                # 预算总额
                self.tree.SetItemText(child, 2, percents(item[4]) if item[4] is not None else '')                     # 预算已分配率
                self.tree.SetItemText(child, 3, str(item[-1]))                                                        # 层级
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

class Budget_GridDialog(GridDialog):
    __value = None
    __colLabels = uc.BudgetColLabels
    __colLabels_type = uc.BudgetColLabels_Type
    filter_case = []
    def __init__(self, title='预算信息', data=None, size=uc.Size_BaseDialog, limit=False, where_sql='' ,where_list=[]):
        self.init(title, data, size)
        if limit:
            self.ctrl[('Button', uc.筛选)].Enable(False)
            self.ctrl[('Button', uc.查询结构)].Enable(False)
            self.ctrl[('Button', uc.刷新)].Enable(False)
        for eachEvent, eachHandler in self.gridBindData():
            self.ctrl[('Grid', None)].Bind(eachEvent, eachHandler)
        for key, eachEvent, eachHandler in self.ctrlBindData():
            self.ctrl[key].Bind(eachEvent, eachHandler)
        self.readDB_and_reFreshGrid(where_sql=where_sql, where_list=where_list)
        self.ctrl[('Grid', None)].SelectRow(0)
    # binder
    def gridBindData(self):
        return ((wx.grid.EVT_GRID_LABEL_LEFT_CLICK,  self.labelOnClick),
                (wx.grid.EVT_GRID_SELECT_CELL,       self.gridOnSelectACell),
                (wx.grid.EVT_GRID_LABEL_LEFT_DCLICK, self.labelOnDCLICK),
                (wx.grid.EVT_GRID_CELL_RIGHT_CLICK,  self.gridOnRClick),
                (wx.grid.EVT_GRID_CELL_LEFT_DCLICK,  self.gridOnDClick))
    def ctrlBindData(self):
        return ((('Button',  uc.新建),     wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.修改),     wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.筛选),     wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.查询结构), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.刷新),     wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.导出),     wx.EVT_BUTTON, self.clickOnButton),
               )
    # events
    def clickOnButton(self, event):
        label = wx.FindWindowById(event.Id, self).GetLabel()
        if label == uc.刷新:
            self.readDB_and_reFreshGrid()
            self.filter_case = []
        elif label == uc.新建:
            dlg = Budget_MaintainDialog(uc.Dialog_New)
            dlg.ShowModal()
            dlg.Destroy()
            self.readDB_and_reFreshGrid()
        elif label == uc.修改:
            data = self.GetValue()
            dlg = Budget_MaintainDialog(uc.Dialog_Edit, data[0])
            dlg.ShowModal()
            dlg.Destroy()
            self.readDB_and_reFreshGrid()
        elif label == uc.筛选:
            dlg = FilterDialog(self.__colLabels, self.__colLabels_type, self.filter_case)
            if dlg.ShowModal() == wx.ID_OK:
                self.filter_case = dlg.GetValue()
            dlg.Destroy()
            # 整理出where_sql和where_list
            if not self.filter_case:
                return
            where_sql = []
            where_list = []
            for each_filter in self.filter_case:
                where_sql.append(each_filter[1][0])
                where_list.extend(each_filter[1][1])
            where_sql = 'WHERE ' + ' AND '.join(where_sql)
            self.readDB_and_reFreshGrid(where_sql, where_list)
        elif label == uc.查询结构:
            dlg = Budget_TreeDialog()
            if dlg.ShowModal() == wx.ID_OK:
                data = dlg.GetValue()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return
            # 筛选树型框里传递来的记录
            UDID = data[0]
            where_sql = 'WHERE 预算识别码=%s'
            self.filter_case = [['【预算识别码 等于 %d】' % UDID, ['预算识别码=%s', [UDID], ['预算识别码', '整数型', '等于', UDID, '', '', '', '', 0]]]]
            self.readDB_and_reFreshGrid(where_sql, [UDID])
        elif label == uc.导出:
            wildcard = 'Excel files (*.xlsx)|*.xlsx'
            dlg = wx.FileDialog(None, "Choose a file", '', '', wildcard, 0)    #选择文件对话框
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            dlg.Destroy()
            filename = dlg.GetPath()
            if os.path.exists(filename):
                dlg = wx.MessageDialog(self, message='该文件已存在，点击<是>覆盖文件', caption='警告', style= wx.YES_NO | wx.NO_DEFAULT)
                if dlg.ShowModal() == wx.ID_NO:
                    dlg.Destroy()
                    return
                else:
                    dlg.Destroy()
            data = self.ctrl[('Grid', None)].GetTable().data
            try:
                Exporter().commonExport(filename, self.ctrl[('Grid', None)], self.__colLabels, data)
                dlg = wx.MessageDialog(self, message='文件导出成功', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except Exception as e:
                dlg = wx.MessageDialog(self, message='文件导出失败！\n%s' % str(e), caption='警告', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
    def labelOnClick(self, event):
        col = event.GetCol()
        isCtrl = event.ControlDown()
        isShift = event.ShiftDown()
        if col >= 0 and isCtrl:
            data = self.get_data_by_sortGrid(self.ctrl[('Grid', None)], col, False, self.__colLabels_type)
            self.reFreshGrid(self.ctrl[('Grid', None)], data, self.__colLabels)
        elif col >= 0 and isShift:
            data = self.get_data_by_sortGrid(self.ctrl[('Grid', None)], col, True, self.__colLabels_type)
            self.reFreshGrid(self.ctrl[('Grid', None)], data, self.__colLabels)
        else:
            return
    def gridOnSelectACell(self, event):
        row = event.GetRow()
        result = self.SetValue(row)
        if result:
            self.ctrl[('Textbox', uc.显示窗)].SetValue('%s-%s-%s' % (result[self.__colLabels.index('预算识别码')] or '', 
                      result[self.__colLabels.index('预算名称')] or '', result[self.__colLabels.index('预算周期')] or ''))
    def labelOnDCLICK(self, event):
        col = event.GetCol()
        data = self.ctrl[('Grid', None)].GetTable().data
        colLabels = self.ctrl[('Grid', None)].GetTable().colLabels
        values = []
        def thousands(n):
            return '{:>,.2f}'.format(n)
        if self.__colLabels_type[col] in '整数型 浮点型'.split():
            for key, value in data.items():
                if key[1] == col and value is not None:
                    values.append(value)
            try:
                dlg = wx.MessageDialog(self, message='<%s>列下：\n共有<%d>个值，\n和为<%s>，\n最大值为<%s>，\n最小值为<%s>' \
                                       % (colLabels[col], len(values), thousands(sum(values)), thousands(max(values)), thousands(min(values))),
                                       caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except:
                pass
        elif self.__colLabels_type[col] in ['日期型']:
            for key, value in data.items():
                if key[1] == col and value is not None:
                    values.append(value)
            try:
                dlg = wx.MessageDialog(self, message='<%s>列下：\n共有<%d>个值，\n最大值为<%s>，\n最小值为<%s>' % (colLabels[col], len(values), max(values), min(values)),
                                       caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except:
                pass
    def gridOnDClick(self, event):
        self.EndModal(wx.ID_OK)
    def gridOnRClick(self, event):
        row = event.GetRow()
        if row >= 0:
            self.SetValue(row)
            self.ctrl[('Grid', None)].SelectRow(row)
            self.checkBudget()
    # methods
    def checkBudget(self):
        data = self.GetValue()
        dlg = Budget_MaintainDialog(uc.Dialog_Check, data[0])
        dlg.ShowModal()
        dlg.Destroy()
        self.readDB_and_reFreshGrid()
    def GetValue(self):
        return self.__value
    def SetValue(self, row):
        data = self.ctrl[('Grid', None)].GetTable().data
        colLabels = self.ctrl[('Grid', None)].GetTable().colLabels
        try:
            rownum = max(data.keys())[0] + 1
        except:
            rownum = 0
        colnum = len(colLabels)
        result = []
        if rownum == 0:
            return
        for col in range(colnum):
            result.append(data.get((row, col)))
        self.__value = result
        return result
    def readDB(self, where_sql='', where_list=[], order_sql='', order_list=[]):
        return operateDB().read_For_Budget_GridDialog(where_sql, where_list, order_sql, order_list)
    def readDB_and_reFreshGrid(self, where_sql='', where_list=[], order_sql='', order_list=[]):
        data = self.format_DBdata2Griddata(self.readDB(where_sql, where_list, order_sql, order_list))
        self.reFreshGrid(self.ctrl[('Grid', None)], data, self.__colLabels, [uc.BudgetColLabels.index('预算已付比')])

class Budget_MaintainDialog(MaintainDialog):
    __mode = uc.Dialog_Check
    __choice_dialog_could_open = False
    __init_dialog_could_open = True
    __value = None
    __save_point = None
    __ctrl_key = list(zip(['Textbox'] * 10, 
                      uc.BudgetColLabels))
    __ctrl_value_type = uc.BudgetColLabels_Type
    def __init__(self, mode=uc.Dialog_Check, UDID=-1):
        self.init()
        self.ctrl[('Button', uc.会签表格)].Enable(False)
        little_sizer = {}
        def create_Label_Textbox_Pairs(key, size_Textbox, size_Label=uc.Size_Label_BaseDialog):
            little_sizer[key] = wx.BoxSizer(wx.HORIZONTAL)
            self.ctrl[('Label', key)] = wx.StaticText(self, -1, key+'：', size=size_Label, style=wx.ALIGN_RIGHT)
            self.ctrl[('Textbox', key)] = wx.TextCtrl(self, -1, '', size=size_Textbox, style=wx.TE_READONLY|wx.TE_CENTRE|wx.BORDER_STATIC, name=key)
            little_sizer[key].Add(self.ctrl[('Label', key)])
            little_sizer[key].Add(self.ctrl[('Textbox', key)])
        def create_Label_MultiTextbox_Pairs(key, size_Textbox, size_Label=uc.Size_Label_BaseDialog):
            little_sizer[key] = wx.BoxSizer(wx.HORIZONTAL)
            self.ctrl[('Label', key)] = wx.StaticText(self, -1, key+'：', size=size_Label, style=wx.ALIGN_RIGHT)
            self.ctrl[('Textbox', key)] = wx.TextCtrl(self, -1, '', size=size_Textbox, style=wx.TE_READONLY|wx.BORDER_STATIC|wx.TE_MULTILINE, name=key)
            little_sizer[key].Add(self.ctrl[('Label', key)])
            little_sizer[key].Add(self.ctrl[('Textbox', key)])
        def create_Label_Combobox_Pairs(key, size_Combobox, size_Label=uc.Size_Label_BaseDialog):
            little_sizer[key] = wx.BoxSizer(wx.HORIZONTAL)
            self.ctrl[('Label', key)] = wx.StaticText(self, -1, key+'：', size=size_Label, style=wx.ALIGN_RIGHT)
            style = wx.TE_PROCESS_ENTER|wx.CB_DROPDOWN|wx.TE_CENTER|wx.TE_READONLY
            self.ctrl[('Combobox', key)] = wx.ComboBox(self, -1, value='', size=size_Combobox, choices=[], style=style, name=key)
            little_sizer[key].Add(self.ctrl[('Label', key)])
            little_sizer[key].Add(self.ctrl[('Combobox', key)])
        # 重绘控件
        create_Label_Textbox_Pairs( '预算识别码'     , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '父项预算识别码' , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '父项预算名称'   , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '预算名称'       , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '预算周期'       , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '预算总额'       , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '预算已付额'     , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '预算余额'     , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '预算已付比'     , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_MultiTextbox_Pairs( '预算备注'    , uc.Size_Textbox_Note)
        core_sizer = wx.BoxSizer(wx.VERTICAL)
        row_sizer = []
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['预算识别码'])
        row_sizer[-1].Add(little_sizer['父项预算识别码'])
        row_sizer[-1].Add(little_sizer['父项预算名称'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['预算名称'])
        row_sizer[-1].Add(little_sizer['预算周期'])
        row_sizer[-1].Add(little_sizer['预算总额'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['预算已付额'])
        row_sizer[-1].Add(little_sizer['预算余额'])
        row_sizer[-1].Add(little_sizer['预算已付比'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['预算备注'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        self.sizer.Add(core_sizer, 0, wx.ALL, 10)
        self.SetSizer(self.all_sizer)
        self.all_sizer.Fit(self)
        for key, eachEvent, eachHandler in self.ctrlBindData():
            self.ctrl[key].Bind(eachEvent, eachHandler)
        # 检查模式
        self.ChangeMode(mode, UDID)    # 通过识别码读取信息
        self.SaveTap(self.FormatInfoFromUI())
    # binder
    def ctrlBindData(self):
        return ((('Button',  uc.新建), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.修改), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.保存), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.取消), wx.EVT_BUTTON, self.clickOnButton),
                (('Textbox', '父项预算识别码'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '父项预算名称'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox)
               )
    # events
    def clickOnButton(self, event):
        label = wx.FindWindowById(event.Id, self).GetLabel()
        if label == uc.新建:
            self.SaveTap(self.FormatInfoFromUI())
            self.ChangeMode(uc.Dialog_New)
        elif label == uc.修改:
            self.SaveTap(self.FormatInfoFromUI())
            try:
                UDID = int(self.ctrl[('Textbox', '预算识别码')].GetValue())
            except:
                UDID = 0
            self.ChangeMode(uc.Dialog_Edit, UDID)
        elif label == uc.取消:
            hasChanged = self.FormatInfoFromUI() != self.LoadTap()
            if hasChanged:
                dlg = wx.MessageDialog(self, message='更改的数据尚未保存，你确定要退出吗？', caption='警告', style= wx.YES_NO | wx.NO_DEFAULT)
                if dlg.ShowModal() == wx.ID_NO:
                    dlg.Destroy()
                    return
                else:
                    dlg.Destroy()
            self.ChangeMode(uc.Dialog_Check)
            self.FillBlanks(self.LoadTap())
        elif label == uc.保存:
            hasChanged = self.FormatInfoFromUI() != self.LoadTap()
            if not hasChanged:
                dlg = wx.MessageDialog(self, message='数据并未做任何更改，不需要保存。', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            dlg = wx.MessageDialog(self, message='点击确定保存数据。', caption='提示', style= wx.YES_NO | wx.NO_DEFAULT)
            if dlg.ShowModal() == wx.ID_NO:
                dlg.Destroy()
                return
            else:
                dlg.Destroy()
            data = self.FormatInfoForDB()
            UDID = data[0]
            save_result = operateDB().save_For_Budget_MaintainDialog(data)
            try:
                assert save_result
                dlg = wx.MessageDialog(self, message='数据保存成功。', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except Exception as e:
                dlg = wx.MessageDialog(self, message='数据保存失败\n%s' % str(e), caption='警告', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            self.ChangeMode(uc.Dialog_Check, UDID)
            self.SaveTap(data)
    def DclickOnTextbox(self, event):
        if not self.__choice_dialog_could_open:
            return
        def thousands(n): return '{:>,.2f}'.format(n)
        isCtrl = event.ControlDown()
        name = wx.FindWindowById(event.GetId()).GetName()
        data = self.FormatInfoFromUI()
        if name in '父项预算识别码 父项预算名称'.split() and self.__init_dialog_could_open:
            if isCtrl:
                self.ctrl[('Textbox', '父项预算识别码')].SetValue('')
                self.ctrl[('Textbox', '父项预算名称')].SetValue('')
                return
            dlg = Budget_GridDialog()
            if dlg.ShowModal() == wx.ID_OK:
                UDID, parent_UDID, x, parent_budget_name = dlg.GetValue()[:4]
                self.ctrl[('Textbox', '父项预算识别码')].SetValue(str(UDID))
                self.ctrl[('Textbox', '父项预算名称')].SetValue(parent_budget_name or '')
            dlg.Destroy()
    # methods
    def GetValue(self): return self.__value
    def SetValue(self):
        self.__value = []
        for each_ctrl_key, each_value_type in zip(self.__ctrl_key, self.__ctrl_value_type):
            value = self.ctrl[each_ctrl_key].GetValue()
            try:
                if value == '':
                    value = None
                elif each_value_type == '整数型':
                    value = int(value)
                elif each_value_type == '浮点型':
                    value = decimal.Decimal(value.strip().replace(',', ''))
                elif each_value_type == '百分比':
                    value = float(value.strip().replace('%', '')) / 100
            except:
                value = None
            self.__value.append(value)
        return self.__value
    def LoadTap(self): return self.__save_point
    def SaveTap(self, data=[]): self.__save_point = data
    def FormatInfoFromUI(self, ifReport=False):
        data = []
        for i, each_ctrl_key in zip(range(len(self.__ctrl_key)), self.__ctrl_key):
            value = self.ctrl[each_ctrl_key].GetValue()
            if len(value) == 0:
                value = None
            elif self.__ctrl_value_type[i] == '整数型':
                try:
                    value = int(value)
                except:
                    value = None
                    if ifReport:
                        dlg = wx.MessageDialog(self, message='<%s>中数据未能识别，将记录为NULL值' % each_ctrl_key[1], caption='警告', style=wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
            elif self.__ctrl_value_type[i] == '浮点型':
                try:
                    value = decimal.Decimal(value.strip().replace(',', ''))
                except:
                    value = None
                    if ifReport:
                        dlg = wx.MessageDialog(self, message='<%s>中数据未能识别，将记录为NULL值' % each_ctrl_key[1], caption='警告', style=wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
            elif self.__ctrl_value_type[i] == '百分比':
                try:
                    value = float(value.strip().replace('%', '').replace(',', '')) / 100
                except:
                    value = None
                    if ifReport:
                        dlg = wx.MessageDialog(self, message='<%s>中数据未能识别，将记录为NULL值' % each_ctrl_key[1], caption='警告', style=wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
            elif self.__ctrl_value_type[i] == '日期型':
                try:
                    value = datetime.date(*time.strptime(value, "%Y-%m-%d")[:3])
                except:
                    value = None
                    if ifReport:
                        dlg = wx.MessageDialog(self, message='<%s>中数据未能识别，将记录为NULL值' % each_ctrl_key[1], caption='警告', style=wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
            data.append(value)
        return data
    def FormatInfoForDB(self):
        data = self.FormatInfoFromUI(True)
        result = []
        for key, value in zip(uc.BudgetColLabels, data):
            if key in uc.BudgetFields:
                result.append(value)
        return result
    def GetDataFromUDID(self, UDID):
        try:
            result = operateDB().read_For_Budget_GridDialog(where_sql='WHERE 预算识别码=%s', where_list=[UDID])[0]
        except:
            result = None
        return result
    def ChangeMode(self, mode, UDID=None):
        if mode == uc.Dialog_Check:
            self.__mode = mode
            data = self.GetDataFromUDID(UDID) if UDID else []
            self.SetTitle('查看预算信息')
            for each_ctrl_key in self.__ctrl_key:
                if each_ctrl_key[0] == 'Textbox':
                    self.ctrl[each_ctrl_key].SetEditable(False)
                elif each_ctrl_key[0] == 'Combobox':
                    self.ctrl[each_ctrl_key].Enable(False)
            self.ctrl[('Button', uc.新建)].Enable(True)
            self.ctrl[('Button', uc.修改)].Enable(True)
            self.ctrl[('Button', uc.保存)].Enable(False)
            self.ctrl[('Button', uc.取消)].Enable(False)
            self.ChoiceDialog(False)
            self.FillBlanks(data)
        elif mode == uc.Dialog_New:
            self.__mode = mode
            self.SetTitle('新建预算信息')
            for each_ctrl_key in self.__ctrl_key:
                if each_ctrl_key[0] == 'Textbox' and each_ctrl_key[1] in '预算名称 预算周期 预算总额 预算备注'.split():
                    self.ctrl[each_ctrl_key].SetEditable(True)
                elif each_ctrl_key[0] == 'Combobox':
                    self.ctrl[each_ctrl_key].Enable(True)
            self.ctrl[('Button', uc.新建)].Enable(False)
            self.ctrl[('Button', uc.修改)].Enable(False)
            self.ctrl[('Button', uc.保存)].Enable(True)
            self.ctrl[('Button', uc.取消)].Enable(True)
            self.ChoiceDialog(True)
            self.FillBlanks()
        elif mode == uc.Dialog_Edit:
            try:
                data = self.GetDataFromUDID(UDID) if UDID else []
                assert data
            except:
                dlg = wx.MessageDialog(self, message='该预算识别码数据库中未记录，请检查', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            self.__mode = mode
            self.SetTitle('修改预算信息')
            for each_ctrl_key in self.__ctrl_key:
                if each_ctrl_key[0] == 'Textbox' and each_ctrl_key[1] in '预算名称 预算周期 预算总额 预算备注'.split():
                    self.ctrl[each_ctrl_key].SetEditable(True)
                elif each_ctrl_key[0] == 'Combobox':
                    self.ctrl[each_ctrl_key].Enable(True)
            self.ctrl[('Button', uc.新建)].Enable(False)
            self.ctrl[('Button', uc.修改)].Enable(False)
            self.ctrl[('Button', uc.保存)].Enable(True)
            self.ctrl[('Button', uc.取消)].Enable(True)
            self.ChoiceDialog(True)
            self.FillBlanks(data)
    def FillBlanks(self, data=[]):
        def thousands(n): return '{:>,.2f}'.format(n)
        def percents(n): return '{:>.2f}'.format((n or 0) * 100) + '%'
        for each_ctrl_key in self.__ctrl_key:
            try:
                value = data[self.__ctrl_key.index(each_ctrl_key)]
                value_type = self.__ctrl_value_type[self.__ctrl_key.index(each_ctrl_key)]
                if value is None:
                    value = ''
                elif value_type == '浮点型':
                    value = thousands(value)
                elif value_type == '百分比':
                    value = percents(value)
                else:
                    value = str(value)
                self.ctrl[each_ctrl_key].SetValue(value)
            except:
                self.ctrl[each_ctrl_key].SetValue('')
    def ChoiceDialog(self, could_open): self.__choice_dialog_could_open = could_open

class Payment_GridDialog(GridDialog):
    __value = None
    __colLabels = uc.PaymentColLabels
    __colLabels_type = uc.PaymentColLabels_Type
    filter_case = []
    def __init__(self, title='付款信息', data=None, size=uc.Size_BaseDialog, limit=False, where_sql='' ,where_list=[]):
        self.init(title, data, size)
        if limit:
            self.ctrl[('Button', uc.筛选)].Enable(False)
            self.ctrl[('Button', uc.查询结构)].Enable(False)
            self.ctrl[('Button', uc.刷新)].Enable(False)
        for eachEvent, eachHandler in self.gridBindData():
            self.ctrl[('Grid', None)].Bind(eachEvent, eachHandler)
        for key, eachEvent, eachHandler in self.ctrlBindData():
            self.ctrl[key].Bind(eachEvent, eachHandler)
        self.readDB_and_reFreshGrid(where_sql=where_sql, where_list=where_list)
        self.ctrl[('Grid', None)].SelectRow(0)
    # binder
    def gridBindData(self):
        return ((wx.grid.EVT_GRID_LABEL_LEFT_CLICK,  self.labelOnClick),
                (wx.grid.EVT_GRID_SELECT_CELL,       self.gridOnSelectACell),
                (wx.grid.EVT_GRID_LABEL_LEFT_DCLICK, self.labelOnDCLICK),
                (wx.grid.EVT_GRID_CELL_RIGHT_CLICK,  self.gridOnRClick),
                (wx.grid.EVT_GRID_CELL_LEFT_DCLICK,  self.gridOnDClick))
    def ctrlBindData(self):
        return ((('Button',  uc.新建),     wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.修改),     wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.筛选),     wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.查询结构), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.刷新),     wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.导出),     wx.EVT_BUTTON, self.clickOnButton),
               )
    # events
    def clickOnButton(self, event):
        label = wx.FindWindowById(event.Id, self).GetLabel()
        if label == uc.刷新:
            self.readDB_and_reFreshGrid()
            self.filter_case = []
        elif label == uc.新建:
            dlg = Payment_MaintainDialog(uc.Dialog_New)
            dlg.ShowModal()
            dlg.Destroy()
            self.readDB_and_reFreshGrid()
        elif label == uc.修改:
            data = self.GetValue()
            dlg = Payment_MaintainDialog(uc.Dialog_Edit, data[0])
            dlg.ShowModal()
            dlg.Destroy()
            self.readDB_and_reFreshGrid()
        elif label == uc.筛选:
            dlg = FilterDialog(self.__colLabels, self.__colLabels_type, self.filter_case)
            if dlg.ShowModal() == wx.ID_OK:
                self.filter_case = dlg.GetValue()
            dlg.Destroy()
            # 整理出where_sql和where_list
            if not self.filter_case:
                return
            where_sql = []
            where_list = []
            for each_filter in self.filter_case:
                where_sql.append(each_filter[1][0])
                where_list.extend(each_filter[1][1])
            where_sql = 'WHERE ' + ' AND '.join(where_sql)
            self.readDB_and_reFreshGrid(where_sql, where_list)
        elif label == uc.查询结构:
            dlg = TreeDialog()
            if dlg.ShowModal() == wx.ID_OK:
                data = dlg.GetValue()
                dlg.Destroy()
            else:
                dlg.Destroy()
                return
            # 筛选树型框里传递来的记录
            UDID = data[0]
            # 如果该节点为叶节点(无子项)，显示该立项下的付款记录；如果该节点非叶节点，则垂直穿透该节点，显示其下全部付款记录
            if operateDB().get_All_Children_Info_InitUDID(UDID):
                UDID = operateDB().get_All_Grandchildren(UDID)
                where_sql = 'WHERE 立项识别码 IN %s'
                self.filter_case = [['【立项识别码 属于 %s】' % '|'.join(map(str, UDID)), ['立项识别码 IN %s', [UDID], ['立项识别码', '整数型', '属于', '|'.join(map(str, UDID)), '', '', '', '', 0]]]]
                self.readDB_and_reFreshGrid(where_sql, [UDID])
            else:
                where_sql = 'WHERE 立项识别码=%s'
                self.filter_case = [['【立项识别码 等于 %d】' % UDID, ['立项识别码=%s', [UDID], ['立项识别码', '整数型', '等于', UDID, '', '', '', '', 0]]]]
                self.readDB_and_reFreshGrid(where_sql, [UDID])
        elif label == uc.导出:
            wildcard = 'Excel files (*.xlsx)|*.xlsx'
            dlg = wx.FileDialog(None, "Choose a file", '', '', wildcard, 0)    #选择文件对话框
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            dlg.Destroy()
            filename = dlg.GetPath()
            if os.path.exists(filename):
                dlg = wx.MessageDialog(self, message='该文件已存在，点击<是>覆盖文件', caption='警告', style= wx.YES_NO | wx.NO_DEFAULT)
                if dlg.ShowModal() == wx.ID_NO:
                    dlg.Destroy()
                    return
                else:
                    dlg.Destroy()
            data = self.ctrl[('Grid', None)].GetTable().data
            try:
                Exporter().commonExport(filename, self.ctrl[('Grid', None)], self.__colLabels, data)
                dlg = wx.MessageDialog(self, message='文件导出成功', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except Exception as e:
                dlg = wx.MessageDialog(self, message='文件导出失败！\n%s' % str(e), caption='警告', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
    def labelOnClick(self, event):
        col = event.GetCol()
        isCtrl = event.ControlDown()
        isShift = event.ShiftDown()
        if col >= 0 and isCtrl:
            data = self.get_data_by_sortGrid(self.ctrl[('Grid', None)], col, False, self.__colLabels_type)
            self.reFreshGrid(self.ctrl[('Grid', None)], data, self.__colLabels, [uc.PaymentColLabels.index('付款时预算已付比'),
                                                                                 uc.PaymentColLabels.index('付款时合同已付比'),
                                                                                 uc.PaymentColLabels.index('付款时概算已付比'),
                                                                                 uc.PaymentColLabels.index('预算本次付款比'),
                                                                                 uc.PaymentColLabels.index('合同本次付款比'),
                                                                                 uc.PaymentColLabels.index('概算本次付款比'),
                                                                                 uc.PaymentColLabels.index('预算累付比'),
                                                                                 uc.PaymentColLabels.index('合同累付比'),
                                                                                 uc.PaymentColLabels.index('概算累付比')])
        elif col >= 0 and isShift:
            data = self.get_data_by_sortGrid(self.ctrl[('Grid', None)], col, True, self.__colLabels_type)
            self.reFreshGrid(self.ctrl[('Grid', None)], data, self.__colLabels, [uc.PaymentColLabels.index('付款时预算已付比'),
                                                                                 uc.PaymentColLabels.index('付款时合同已付比'),
                                                                                 uc.PaymentColLabels.index('付款时概算已付比'),
                                                                                 uc.PaymentColLabels.index('预算本次付款比'),
                                                                                 uc.PaymentColLabels.index('合同本次付款比'),
                                                                                 uc.PaymentColLabels.index('概算本次付款比'),
                                                                                 uc.PaymentColLabels.index('预算累付比'),
                                                                                 uc.PaymentColLabels.index('合同累付比'),
                                                                                 uc.PaymentColLabels.index('概算累付比')])
        else:
            return
    def gridOnSelectACell(self, event):
        row = event.GetRow()
        result = self.SetValue(row)
        if result:
            self.ctrl[('Textbox', uc.显示窗)].SetValue('%s-%s%s-%s' % (result[self.__colLabels.index('付款识别码')] or '', 
                      result[self.__colLabels.index('项目名称')] or '', result[self.__colLabels.index('分项名称')] or '', 
                      result[self.__colLabels.index('付款事由')] or ''))
    def labelOnDCLICK(self, event):
        col = event.GetCol()
        data = self.ctrl[('Grid', None)].GetTable().data
        colLabels = self.ctrl[('Grid', None)].GetTable().colLabels
        values = []
        def thousands(n):
            return '{:>,.2f}'.format(n)
        if self.__colLabels_type[col] in '整数型 浮点型'.split():
            for key, value in data.items():
                if key[1] == col and value is not None:
                    values.append(value)
            try:
                dlg = wx.MessageDialog(self, message='<%s>列下：\n共有<%d>个值，\n和为<%s>，\n最大值为<%s>，\n最小值为<%s>' \
                                       % (colLabels[col], len(values), thousands(sum(values)), thousands(max(values)), thousands(min(values))),
                                       caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except:
                pass
        elif self.__colLabels_type[col] in ['日期型']:
            for key, value in data.items():
                if key[1] == col and value is not None:
                    values.append(value)
            try:
                dlg = wx.MessageDialog(self, message='<%s>列下：\n共有<%d>个值，\n最大值为<%s>，\n最小值为<%s>' % (colLabels[col], len(values), max(values), min(values)),
                                       caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except:
                pass
    def gridOnDClick(self, event):
        self.EndModal(wx.ID_OK)
    def gridOnRClick(self, event):
        row = event.GetRow()
        if row >= 0:
            self.SetValue(row)
            self.ctrl[('Grid', None)].SelectRow(row)
            self.checkPayment()
    # methods
    def checkPayment(self):
        data = self.GetValue()
        dlg = Payment_MaintainDialog(uc.Dialog_Check, data[0])
        dlg.ShowModal()
        dlg.Destroy()
        self.readDB_and_reFreshGrid()
    def GetValue(self):
        return self.__value
    def SetValue(self, row):
        data = self.ctrl[('Grid', None)].GetTable().data
        colLabels = self.ctrl[('Grid', None)].GetTable().colLabels
        try:
            rownum = max(data.keys())[0] + 1
        except:
            rownum = 0
        colnum = len(colLabels)
        result = []
        if rownum == 0:
            return
        for col in range(colnum):
            result.append(data.get((row, col)))
        self.__value = result
        return result
    def readDB(self, where_sql='', where_list=[], order_sql='', order_list=[]):
        return operateDB().read_For_Payment_GridDialog(where_sql, where_list, order_sql, order_list)
    def readDB_and_reFreshGrid(self, where_sql='', where_list=[], order_sql='', order_list=[]):
        data = self.format_DBdata2Griddata(self.readDB(where_sql, where_list, order_sql, order_list))
        self.reFreshGrid(self.ctrl[('Grid', None)], data, self.__colLabels, [uc.PaymentColLabels.index('付款时预算已付比'),
                                                                             uc.PaymentColLabels.index('付款时合同已付比'),
                                                                             uc.PaymentColLabels.index('付款时概算已付比'),
                                                                             uc.PaymentColLabels.index('预算本次付款比'),
                                                                             uc.PaymentColLabels.index('合同本次付款比'),
                                                                             uc.PaymentColLabels.index('概算本次付款比'),
                                                                             uc.PaymentColLabels.index('预算累付比'),
                                                                             uc.PaymentColLabels.index('合同累付比'),
                                                                             uc.PaymentColLabels.index('概算累付比')])

class Payment_MaintainDialog(MaintainDialog):
    __mode = uc.Dialog_Check
    __choice_dialog_could_open = False
    __init_dialog_could_open = True
    __value = None
    __save_point = None
    __ctrl_key = list(zip(['Textbox'] * 44, uc.PaymentColLabels))
    __ctrl_value_type = uc.PaymentColLabels_Type
    def __init__(self, mode=uc.Dialog_Check, UDID=-1):
        self.init()
        # 重新定位窗口位置，使之居中
        ScreenSizeX, ScreenSizeY = wx.DisplaySize()
        SizeX, SizeY = self.GetSize()
        PosX = int((ScreenSizeX - SizeX) / 10)
        PosY = int((ScreenSizeY - SizeY) / 10)
        self.SetPosition((PosX, PosY))
        # 添加控件
        little_sizer = {}
        def create_Label_Textbox_Pairs(key, size_Textbox, size_Label=uc.Size_Label_LongDialog):
            little_sizer[key] = wx.BoxSizer(wx.HORIZONTAL)
            self.ctrl[('Label', key)] = wx.StaticText(self, -1, key+'：', size=size_Label, style=wx.ALIGN_RIGHT)
            self.ctrl[('Textbox', key)] = wx.TextCtrl(self, -1, '', size=size_Textbox, style=wx.TE_READONLY|wx.TE_CENTRE|wx.BORDER_STATIC, name=key)
            little_sizer[key].Add(self.ctrl[('Label', key)])
            little_sizer[key].Add(self.ctrl[('Textbox', key)])
        def create_Label_MultiTextbox_Pairs(key, size_Textbox, size_Label=uc.Size_Label_BaseDialog):
            little_sizer[key] = wx.BoxSizer(wx.HORIZONTAL)
            self.ctrl[('Label', key)] = wx.StaticText(self, -1, key+'：', size=size_Label, style=wx.ALIGN_RIGHT)
            self.ctrl[('Textbox', key)] = wx.TextCtrl(self, -1, '', size=size_Textbox, style=wx.TE_READONLY|wx.BORDER_STATIC|wx.TE_MULTILINE, name=key)
            little_sizer[key].Add(self.ctrl[('Label', key)])
            little_sizer[key].Add(self.ctrl[('Textbox', key)])
        def create_Label_Combobox_Pairs(key, size_Combobox, size_Label=uc.Size_Label_BaseDialog):
            little_sizer[key] = wx.BoxSizer(wx.HORIZONTAL)
            self.ctrl[('Label', key)] = wx.StaticText(self, -1, key+'：', size=size_Label, style=wx.ALIGN_RIGHT)
            style = wx.TE_PROCESS_ENTER|wx.CB_DROPDOWN|wx.TE_CENTER|wx.TE_READONLY
            self.ctrl[('Combobox', key)] = wx.ComboBox(self, -1, value='', size=size_Combobox, choices=[], style=style, name=key)
            little_sizer[key].Add(self.ctrl[('Label', key)])
            little_sizer[key].Add(self.ctrl[('Combobox', key)])
        # 重绘控件
        create_Label_Textbox_Pairs( '付款识别码'        , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '付款登记时间'      , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '付款支付时间'      , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '付款批次'          , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '立项识别码'        , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '项目名称'          , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '分项名称'          , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '付款时项目概算'    , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '合同识别码'        , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '合同名称'          , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '合同类别'          , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '合同编号'          , uc.Size_Textbox_Long_BaseDialog)
        create_Label_Textbox_Pairs( '付款事由'          , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '付款时合同付款上限', uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '付款时合同值'      , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '付款单位识别码'    , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '付款单位名称'      , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '付款单位账号'      , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '收款单位识别码'    , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '收款单位名称'      , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '收款单位账号'      , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '预算识别码'        , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '预算名称'          , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '预算周期'          , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '付款时预算总额'    , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '付款时预算余额'    , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '付款时概算余额'    , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '付款时合同可付余额', uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '付款时合同未付额'  , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '付款时预算已付额'  , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '付款时合同已付额'  , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '付款时概算已付额'  , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '付款时预算已付比'  , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '付款时合同已付比'  , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '付款时概算已付比'  , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '付款时形象进度'    , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '本次付款额'        , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '预算本次付款比'    , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '合同本次付款比'    , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '概算本次付款比'    , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '预算累付比'        , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '合同累付比'        , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_Textbox_Pairs( '概算累付比'        , uc.Size_Textbox_Normal_BaseDialog)
        create_Label_MultiTextbox_Pairs( '付款备注'     , uc.Size_Textbox_Note)
        core_sizer = wx.BoxSizer(wx.VERTICAL)
        row_sizer = []
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['付款识别码'])
        row_sizer[-1].Add(little_sizer['付款登记时间'])
        row_sizer[-1].Add(little_sizer['付款支付时间'])
        row_sizer[-1].Add(little_sizer['付款批次'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['立项识别码'])
        row_sizer[-1].Add(little_sizer['项目名称'])
        row_sizer[-1].Add(little_sizer['分项名称'])
        row_sizer[-1].Add(little_sizer['付款时项目概算'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['合同识别码'])
        row_sizer[-1].Add(little_sizer['合同名称'])
        row_sizer[-1].Add(little_sizer['合同类别'])
        row_sizer[-1].Add(little_sizer['付款事由'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['付款时合同付款上限'])
        row_sizer[-1].Add(little_sizer['付款时合同值'])
        row_sizer[-1].Add(little_sizer['合同编号'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['付款单位识别码'])
        row_sizer[-1].Add(little_sizer['付款单位名称'])
        row_sizer[-1].Add(little_sizer['付款单位账号'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['收款单位识别码'])
        row_sizer[-1].Add(little_sizer['收款单位名称'])
        row_sizer[-1].Add(little_sizer['收款单位账号'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['预算识别码'])
        row_sizer[-1].Add(little_sizer['预算名称'])
        row_sizer[-1].Add(little_sizer['预算周期'])
        row_sizer[-1].Add(little_sizer['付款时预算总额'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['付款时预算余额'])
        row_sizer[-1].Add(little_sizer['付款时概算余额'])
        row_sizer[-1].Add(little_sizer['付款时合同可付余额'])
        row_sizer[-1].Add(little_sizer['付款时合同未付额'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['付款时预算已付额'])
        row_sizer[-1].Add(little_sizer['付款时合同已付额'])
        row_sizer[-1].Add(little_sizer['付款时概算已付额'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['付款时预算已付比'])
        row_sizer[-1].Add(little_sizer['付款时合同已付比'])
        row_sizer[-1].Add(little_sizer['付款时概算已付比'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['付款时形象进度'])
        row_sizer[-1].Add(little_sizer['本次付款额'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['预算本次付款比'])
        row_sizer[-1].Add(little_sizer['合同本次付款比'])
        row_sizer[-1].Add(little_sizer['概算本次付款比'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['预算累付比'])
        row_sizer[-1].Add(little_sizer['合同累付比'])
        row_sizer[-1].Add(little_sizer['概算累付比'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        row_sizer.append(wx.BoxSizer(wx.HORIZONTAL))
        row_sizer[-1].Add(little_sizer['付款备注'])
        core_sizer.AddSpacer(20)
        core_sizer.Add(row_sizer[-1])
        self.sizer.Add(core_sizer, 0, wx.ALL, 10)
        self.SetSizer(self.all_sizer)
        self.all_sizer.Fit(self)
        for key, eachEvent, eachHandler in self.ctrlBindData():
            self.ctrl[key].Bind(eachEvent, eachHandler)
        # 检查模式
        self.ChangeMode(mode, UDID)    # 通过识别码读取信息
        self.SaveTap(self.FormatInfoFromUI())
    # binder
    def ctrlBindData(self):
        return ((('Button',  uc.跳转), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.新建), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.修改), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.保存), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.会签表格), wx.EVT_BUTTON, self.clickOnButton),
                (('Button',  uc.取消), wx.EVT_BUTTON, self.clickOnButton),
                (('Textbox', '付款登记时间'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '付款支付时间'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '立项识别码'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '项目名称'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '分项名称'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '付款时项目概算'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '付款时概算余额'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '付款时概算已付额'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '付款时概算已付比'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '概算本次付款比'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '概算累付比'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '合同识别码'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '合同名称'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '合同类别'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '合同编号'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '付款时形象进度'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '付款时合同付款上限'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '付款时合同值'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '付款时合同可付余额'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '付款时合同未付额'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '付款时合同已付额'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '付款时合同已付比'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '合同本次付款比'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '合同累付比'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '付款单位识别码'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '付款单位名称'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '付款单位账号'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '收款单位识别码'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '收款单位名称'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '收款单位账号'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '预算识别码'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '预算名称'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '预算周期'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '付款时预算总额'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '付款时预算余额'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '付款时预算已付额'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '付款时预算已付比'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '预算本次付款比'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '预算累付比'), wx.EVT_LEFT_DCLICK, self.DclickOnTextbox),
                (('Textbox', '本次付款额'), wx.EVT_TEXT, self.ChangeOnTextbox)
               )
    # events
    def clickOnButton(self, event):        
        def thousands(n): return '{:>,.2f}'.format(n)
        def captital_thousand(n): 
            strNum =  '{:>,.2f}'.format(n)
            captitalNum = CpitalNumber().ChangeNum(float(n))
            return '大写：%s  ￥%s' % (captitalNum, strNum)
        def percents(n): return '{:>.2f}'.format((n or 0) * 100) + '%'
        label = wx.FindWindowById(event.Id, self).GetLabel()
        if label == uc.跳转:
            try:
                UDID = self.FormatInfoForDB()[uc.PaymentFields.index('立项识别码')]
            except:
                UDID = None
            self.Jump(event, UDID, '跳转至相应<立项>信息 跳转至相应<招标>信息 跳转至相应<合同>信息'.split(), 
                      Initiation_GridDialog, Bidding_GridDialog, Contract_GridDialog, Budget_GridDialog, Payment_GridDialog)
        elif label == uc.新建:
            self.SaveTap(self.FormatInfoFromUI())
            self.ChangeMode(uc.Dialog_New)
        elif label == uc.修改:
            self.SaveTap(self.FormatInfoFromUI())
            try:
                UDID = int(self.ctrl[('Textbox', '付款识别码')].GetValue())
            except:
                UDID = 0
            self.ChangeMode(uc.Dialog_Edit, UDID)
        elif label == uc.取消:
            hasChanged = self.FormatInfoFromUI() != self.LoadTap()
            if hasChanged:
                dlg = wx.MessageDialog(self, message='更改的数据尚未保存，你确定要退出吗？', caption='警告', style= wx.YES_NO | wx.NO_DEFAULT)
                if dlg.ShowModal() == wx.ID_NO:
                    dlg.Destroy()
                    return
                else:
                    dlg.Destroy()
            self.ChangeMode(uc.Dialog_Check)
            self.FillBlanks(self.LoadTap())
        elif label == uc.保存:
            hasChanged = self.FormatInfoFromUI() != self.LoadTap()
            if not hasChanged:
                dlg = wx.MessageDialog(self, message='数据并未做任何更改，不需要保存。', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            dlg = wx.MessageDialog(self, message='点击确定保存数据。', caption='提示', style= wx.YES_NO | wx.NO_DEFAULT)
            if dlg.ShowModal() == wx.ID_NO:
                dlg.Destroy()
                return
            else:
                dlg.Destroy()
            data = self.FormatInfoForDB()
            def Legitimacy(data):
                this_pay = data[uc.PaymentFields.index('本次付款额')] or 0
                budget_remaining = data[uc.PaymentFields.index('付款时预算余额')] or 0
                estimate_remaining = data[uc.PaymentFields.index('付款时概算余额')] or 0
                contract_remaining = data[uc.PaymentFields.index('付款时合同可付余额')]
                contract_stillnot = data[uc.PaymentFields.index('付款时合同未付额')]
                if not this_pay:
                    dlg = wx.MessageDialog(self, message='<%s>填写有误，请检查！' % '本次付款额', caption='警告', style=wx.OK)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
                if this_pay > budget_remaining:
                    dlg = wx.MessageDialog(self, message='<%s>超过<%s>，请查检' % ('本次付款额', '付款时预算余额'), caption='警告', style=wx.OK)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
                if this_pay > estimate_remaining:
                    dlg = wx.MessageDialog(self, message='<%s>超过<%s>，请查检' % ('本次付款额', '付款时概算余额'), caption='警告', style=wx.OK)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
                if contract_remaining is not None and this_pay > contract_remaining:
                    dlg = wx.MessageDialog(self, message='<%s>超过<%s>，请查检' % ('本次付款额', '付款时合同可付余额'), caption='警告', style=wx.OK)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
                if contract_stillnot is not None and this_pay > contract_stillnot:
                    dlg = wx.MessageDialog(self, message='<%s>超过<%s>，请查检' % ('本次付款额', '付款时合同未付额'), caption='警告', style=wx.OK)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
                return True
            # 如果合法性检查未通过，提示且不可保存
            if not Legitimacy(data):
                return
            PaymentUDID = data[0]
            save_result = operateDB().save_For_Payment_MaintainDialog(data)
            try:
                assert save_result
                dlg = wx.MessageDialog(self, message='数据保存成功。', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
            except Exception as e:
                dlg = wx.MessageDialog(self, message='数据保存失败\n%s' % str(e), caption='警告', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            self.ChangeMode(uc.Dialog_Check, PaymentUDID)
            self.SaveTap(data)
        elif label == uc.会签表格:
            # 取得数据，存入字典
            data = self.FormatInfoFromUI()
            sign_Keys = '付款事由 收款单位名称 本次付款额 合同名称 合同编号 付款时合同值 付款时合同已付额 付款时合同已付比 合同本次付款比 合同累付比'.split()
            sign_Dict = {}
            for i, value in enumerate(data):
                if uc.PaymentColLabels[i] in sign_Keys:
                    sign_Dict[uc.PaymentColLabels[i]] = value
            today = datetime.date.today()
            sign_Dict['提交日期'] = '%d年%d月%d日' % (today.year, today.month, today.day)
            if sign_Dict['付款时合同值'] is not None:
                sign_Dict['付款时合同值'] = captital_thousand(sign_Dict['付款时合同值'])
            if sign_Dict['本次付款额'] is not None:
                sign_Dict['本次付款额'] = captital_thousand(sign_Dict['本次付款额'])
            if sign_Dict['付款时合同已付额'] is not None:
                sign_Dict['付款时合同已付额'] = '￥' + thousands(sign_Dict['付款时合同已付额'])
            if sign_Dict['付款时合同已付比'] is not None:
                sign_Dict['付款时合同已付比'] = percents(sign_Dict['付款时合同已付比'])
            if sign_Dict['合同本次付款比'] is not None:
                sign_Dict['合同本次付款比'] = percents(sign_Dict['合同本次付款比'])
            if sign_Dict['合同累付比'] is not None:
                sign_Dict['合同累付比'] = percents(sign_Dict['合同累付比'])
            # 选取导出路径
            wildcard = 'Word files (*.docx)|*.docx'
            dlg = wx.FileDialog(None, "Choose a file", '', '', wildcard, 0)    #选择文件对话框
            if dlg.ShowModal() != wx.ID_OK:
                dlg.Destroy()
                return
            dlg.Destroy()
            filename = dlg.GetPath()
            if os.path.exists(filename):
                dlg = wx.MessageDialog(self, message='该文件已存在，点击<是>覆盖文件', caption='警告', style= wx.YES_NO | wx.NO_DEFAULT)
                if dlg.ShowModal() == wx.ID_NO:
                    dlg.Destroy()
                    return
                else:
                    dlg.Destroy()
            # 生成文件
            try:
                Exporter().docx_Payment_Export(OutputFile=filename, ContractDict=sign_Dict)
                os.startfile(filename)
            except Exception as e:
                dlg = wx.MessageDialog(self, message='付款会签表未能成功导出！错误代码：\n%s' % e, caption='警告', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
    def DclickOnTextbox(self, event):
        if not self.__choice_dialog_could_open:
            return
        def thousands(n): return '{:>,.2f}'.format(n)
        def percents(n): return '{:>.2f}'.format((n or 0) * 100) + '%'
        isCtrl = event.ControlDown()
        name = wx.FindWindowById(event.GetId()).GetName()
        data = self.FormatInfoFromUI()
        PaymentUDID = data[uc.PaymentColLabels.index('付款识别码')]
        this_pay = float(data[uc.PaymentColLabels.index('本次付款额')] or 0)
        if name in '立项识别码 项目名称 分项名称 付款时项目概算 付款时概算余额 付款时概算已付额 付款时概算已付比 概算本次付款比 概算累付比'.split() and self.__init_dialog_could_open:
            if isCtrl:
                self.ctrl[('Textbox', '立项识别码')].SetValue('')
                self.ctrl[('Textbox', '项目名称')].SetValue('')
                self.ctrl[('Textbox', '分项名称')].SetValue('')
                self.ctrl[('Textbox', '付款批次')].SetValue('')
                self.ctrl[('Textbox', '付款时项目概算')].SetValue('')
                self.ctrl[('Textbox', '付款时概算余额')].SetValue('')
                self.ctrl[('Textbox', '付款时概算已付额')].SetValue('')
                self.ctrl[('Textbox', '付款时概算已付比')].SetValue('')
                self.ctrl[('Textbox', '概算本次付款比')].SetValue('')
                self.ctrl[('Textbox', '概算累付比')].SetValue('')
                return
            dlg = Initiation_GridDialog()
            if dlg.ShowModal() == wx.ID_OK:
                InitUDID, project, subproject = dlg.GetValue()[:3]
                haschild = operateDB().get_All_Children_Info_InitUDID(InitUDID)
                if haschild:
                    dlg = wx.MessageDialog(self, message='该立项下有子项存在，请选择无子项立项', caption='警告', style=wx.OK)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
                estimate = float(dlg.GetValue()[uc.InitiationColLabels.index('项目概算')])
                estimate_payed = float(operateDB().get_Estimate_Payed(InitUDID))
                btach = operateDB().get_Payment_Batch(PaymentUDID, InitUDID)
                self.ctrl[('Textbox', '立项识别码')].SetValue(str(InitUDID))
                self.ctrl[('Textbox', '项目名称')].SetValue(project or '')
                self.ctrl[('Textbox', '分项名称')].SetValue(subproject or '')
                self.ctrl[('Textbox', '付款批次')].SetValue(str(btach))
                self.ctrl[('Textbox', '付款时项目概算')].SetValue(thousands(estimate) if estimate is not None else '')
                self.ctrl[('Textbox', '付款时概算余额')].SetValue(thousands(estimate - estimate_payed) if estimate is not None else '')
                self.ctrl[('Textbox', '付款时概算已付额')].SetValue(thousands(estimate_payed) if estimate_payed is not None else '')
                self.ctrl[('Textbox', '付款时概算已付比')].SetValue(percents(estimate_payed / estimate) if estimate is not None else '')
                self.ctrl[('Textbox', '概算本次付款比')].SetValue(percents(this_pay / estimate) if estimate is not None else '')
                self.ctrl[('Textbox', '概算累付比')].SetValue(percents((this_pay + estimate_payed) / estimate) if estimate is not None else '')
            dlg.Destroy()
        elif name in '预算识别码 预算名称 预算周期 付款时预算总额 付款时预算余额 付款时预算已付额 付款时预算已付比 预算本次付款比 预算累付比'.split() and self.__init_dialog_could_open:
            if isCtrl:
                self.ctrl[('Textbox', '预算识别码')].SetValue('')
                self.ctrl[('Textbox', '预算名称')].SetValue('')
                self.ctrl[('Textbox', '预算周期')].SetValue('')
                self.ctrl[('Textbox', '付款时预算总额')].SetValue('')
                self.ctrl[('Textbox', '付款时预算余额')].SetValue('')
                self.ctrl[('Textbox', '付款时预算已付额')].SetValue('')
                self.ctrl[('Textbox', '付款时预算已付比')].SetValue('')
                self.ctrl[('Textbox', '预算本次付款比')].SetValue('')
                self.ctrl[('Textbox', '预算累付比')].SetValue('')
                return
            dlg = Budget_GridDialog()
            if dlg.ShowModal() == wx.ID_OK:
                BudgetUDID, _, _, budget_name, budget_time = dlg.GetValue()[:5]
                haschild = operateDB().get_All_Children_Info_BudgetUDID(BudgetUDID)
                if haschild:
                    dlg = wx.MessageDialog(self, message='该预算下有子项存在，请选择无子项预算', caption='警告', style=wx.OK)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return                
                budget = float(dlg.GetValue()[uc.BudgetColLabels.index('预算总额')])
                budget_payed = float(operateDB().get_Budget_Payed(BudgetUDID))
                self.ctrl[('Textbox', '预算识别码')].SetValue(str(BudgetUDID))
                self.ctrl[('Textbox', '预算名称')].SetValue(budget_name or '')
                self.ctrl[('Textbox', '预算周期')].SetValue(budget_time or '')
                self.ctrl[('Textbox', '付款时预算总额')].SetValue(thousands(budget) if budget is not None else '')
                self.ctrl[('Textbox', '付款时预算余额')].SetValue(thousands(budget - budget_payed) if budget is not None else '')
                self.ctrl[('Textbox', '付款时预算已付额')].SetValue(thousands(budget_payed) if budget_payed is not None else '')
                self.ctrl[('Textbox', '付款时预算已付比')].SetValue(percents(budget_payed / budget) if budget is not None else '')
                self.ctrl[('Textbox', '预算本次付款比')].SetValue(percents(this_pay / budget) if budget is not None else '')
                self.ctrl[('Textbox', '预算累付比')].SetValue(percents((this_pay + budget_payed) / budget) if budget is not None else '')
            dlg.Destroy()
        elif name in '合同识别码 合同名称 合同类别 合同编号 付款时形象进度 付款时合同付款上限 付款时合同值 付款时合同可付余额 付款时合同未付额 付款时合同已付额 付款时合同已付比 合同本次付款比 合同累付比'.split() and self.__init_dialog_could_open:
            if isCtrl:
                self.ctrl[('Textbox', '合同识别码')].SetValue('')
                self.ctrl[('Textbox', '合同名称')].SetValue('')
                self.ctrl[('Textbox', '合同类别')].SetValue('')
                self.ctrl[('Textbox', '合同编号')].SetValue('')
                self.ctrl[('Textbox', '付款时形象进度')].SetValue('')
                self.ctrl[('Textbox', '付款时合同付款上限')].SetValue('')
                self.ctrl[('Textbox', '付款时合同值')].SetValue('')
                self.ctrl[('Textbox', '付款时合同可付余额')].SetValue('')
                self.ctrl[('Textbox', '付款时合同未付额')].SetValue('')
                self.ctrl[('Textbox', '付款时合同已付额')].SetValue('')
                self.ctrl[('Textbox', '付款时合同已付比')].SetValue('')
                self.ctrl[('Textbox', '合同本次付款比')].SetValue('')
                self.ctrl[('Textbox', '合同累付比')].SetValue('')
                return
            dlg = Contract_GridDialog()
            if dlg.ShowModal() == wx.ID_OK:
                ContractUDID, InitUDID = dlg.GetValue()[:2]
                # 填写概算内容
                project, subproject, estimate = operateDB().get_Pro_and_Subpro_and_Estimate(InitUDID)
                estimate = float(estimate or 0)
                btach = operateDB().get_Payment_Batch(PaymentUDID, InitUDID)
                haschild = operateDB().get_All_Children_Info_InitUDID(InitUDID)
                if haschild:
                    dlg = wx.MessageDialog(self, message='该立项下有子项存在，请选择无子项立项', caption='警告', style=wx.OK)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return
                estimate_payed = float(operateDB().get_Estimate_Payed(InitUDID))
                self.ctrl[('Textbox', '立项识别码')].SetValue(str(InitUDID))
                self.ctrl[('Textbox', '项目名称')].SetValue(project or '')
                self.ctrl[('Textbox', '分项名称')].SetValue(subproject or '')
                self.ctrl[('Textbox', '付款批次')].SetValue(str(btach))
                self.ctrl[('Textbox', '付款时项目概算')].SetValue(thousands(estimate) if estimate is not None else '')
                self.ctrl[('Textbox', '付款时概算余额')].SetValue(thousands(estimate - estimate_payed) if estimate is not None else '')
                self.ctrl[('Textbox', '付款时概算已付额')].SetValue(thousands(estimate_payed) if estimate_payed is not None else '')
                self.ctrl[('Textbox', '付款时概算已付比')].SetValue(percents(estimate_payed / estimate) if estimate is not None else '')
                self.ctrl[('Textbox', '概算本次付款比')].SetValue(percents(this_pay / estimate) if estimate is not None else '')
                self.ctrl[('Textbox', '概算累付比')].SetValue(percents((this_pay + estimate_payed) / estimate) if estimate is not None else '')
                # 填写合同
                contract_name = dlg.GetValue()[uc.ContractColLabels.index('合同名称')]
                contract_style = dlg.GetValue()[uc.ContractColLabels.index('合同类别')]
                contract_number = dlg.GetValue()[uc.ContractColLabels.index('合同类编号')]
                pay_limit = dlg.GetValue()[uc.ContractColLabels.index('支付上限')]
                contract_value = dlg.GetValue()[uc.ContractColLabels.index('合同值_最新值')]
                contract_payed = float(operateDB().get_Contract_Payed(ContractUDID))
                contract_could = float(pay_limit or 0) - float(contract_payed or 0)
                contract_stillnot = float(contract_value or 0) - float(contract_payed or 0)
                image_progress = dlg.GetValue()[uc.ContractColLabels.index('形象进度')]
                self.ctrl[('Textbox', '合同识别码')].SetValue(str(ContractUDID))
                self.ctrl[('Textbox', '合同名称')].SetValue(contract_name or '')
                self.ctrl[('Textbox', '合同类别')].SetValue(contract_style or '')
                self.ctrl[('Textbox', '合同编号')].SetValue(contract_number or '')
                self.ctrl[('Textbox', '付款时形象进度')].SetValue(image_progress or '')
                self.ctrl[('Textbox', '付款时合同付款上限')].SetValue(thousands(pay_limit) if pay_limit is not None else '')
                self.ctrl[('Textbox', '付款时合同值')].SetValue(thousands(contract_value) if contract_value is not None else '')
                self.ctrl[('Textbox', '付款时合同可付余额')].SetValue(thousands(contract_could) if contract_could is not None else '')
                self.ctrl[('Textbox', '付款时合同未付额')].SetValue(thousands(contract_stillnot) if contract_stillnot is not None else '')
                self.ctrl[('Textbox', '付款时合同已付额')].SetValue(thousands(contract_payed) if contract_payed is not None else '')
                self.ctrl[('Textbox', '付款时合同已付比')].SetValue(percents(contract_payed / float(contract_value)) if contract_value is not None else '')
                self.ctrl[('Textbox', '合同本次付款比')].SetValue(percents(this_pay / float(contract_value)) if contract_value is not None else '')
                self.ctrl[('Textbox', '合同累付比')].SetValue(percents((this_pay + contract_payed) / float(contract_value)) if contract_value is not None else '')
            dlg.Destroy()
        elif name in '付款单位识别码 付款单位名称 付款单位账号'.split():
            if isCtrl:
                self.ctrl[('Textbox', '付款单位识别码')].SetValue('')
                self.ctrl[('Textbox', '付款单位名称')].SetValue('')
                self.ctrl[('Textbox', '付款单位账号')].SetValue('')
                return
            data = self.FormatInfoFromUI()
            InitUDID = data[uc.PaymentColLabels.index('立项识别码')]
            ContractUDID = data[uc.PaymentColLabels.index('合同识别码')]
            if ContractUDID:
                UnitUDID_list = operateDB().get_Contract_Unit_List(ContractUDID)
                dlg = Company_GridDialog(limit=True, where_sql='WHERE 单位识别码 IN %s', where_list=[UnitUDID_list])
            else:
                dlg = Company_GridDialog()
            if dlg.ShowModal() == wx.ID_OK:
                UDID, company_name = dlg.GetValue()[:2]
                company_account = dlg.GetValue()[uc.CompanyColLabels.index('银行账号')]
                self.ctrl[('Textbox', '付款单位识别码')].SetValue(str(UDID) or '')
                self.ctrl[('Textbox', '付款单位名称')].SetValue(company_name or '')
                self.ctrl[('Textbox', '付款单位账号')].SetValue(company_account or '')
            dlg.Destroy()
        elif name in '收款单位识别码 收款单位名称 收款单位账号'.split():
            if isCtrl:
                self.ctrl[('Textbox', '收款单位识别码')].SetValue('')
                self.ctrl[('Textbox', '收款单位名称')].SetValue('')
                self.ctrl[('Textbox', '收款单位账号')].SetValue('')
                return
            data = self.FormatInfoFromUI()
            InitUDID = data[uc.PaymentColLabels.index('立项识别码')]
            ContractUDID = data[uc.PaymentColLabels.index('合同识别码')]
            if ContractUDID:
                UnitUDID_list = operateDB().get_Contract_Unit_List(ContractUDID)
                dlg = Company_GridDialog(limit=True, where_sql='WHERE 单位识别码 IN %s', where_list=[UnitUDID_list])
            else:
                dlg = Company_GridDialog()
            if dlg.ShowModal() == wx.ID_OK:
                UDID, company_name = dlg.GetValue()[:2]
                company_account = dlg.GetValue()[uc.CompanyColLabels.index('银行账号')]
                self.ctrl[('Textbox', '收款单位识别码')].SetValue(str(UDID) or '')
                self.ctrl[('Textbox', '收款单位名称')].SetValue(company_name or '')
                self.ctrl[('Textbox', '收款单位账号')].SetValue(company_account or '')
            dlg.Destroy()
        elif name == '付款登记时间':
            if isCtrl:
                self.ctrl[('Textbox', '付款登记时间')].SetValue('')
                return
            dlg = DateDialog()
            if dlg.ShowModal() == wx.ID_OK:
                yearmonthday = dlg.GetValue()
                self.ctrl[('Textbox', '付款登记时间')].SetValue(str(yearmonthday) or '')
            dlg.Destroy()
        elif name == '付款支付时间':
            if isCtrl:
                self.ctrl[('Textbox', '付款支付时间')].SetValue('')
                return
            dlg = DateDialog()
            if dlg.ShowModal() == wx.ID_OK:
                yearmonthday = dlg.GetValue()
                self.ctrl[('Textbox', '付款支付时间')].SetValue(str(yearmonthday) or '')
            dlg.Destroy()        
    def ChangeOnTextbox(self, event):
        def thousands(n): return '{:>,.2f}'.format(n)
        def percents(n): return '{:>.2f}'.format((n or 0) * 100) + '%'
        name = wx.FindWindowById(event.GetId()).GetName()
        data = self.FormatInfoFromUI()
        this_pay = float(data[uc.PaymentColLabels.index('本次付款额')] or 0)
        # 概算部分
        estimate = data[uc.PaymentColLabels.index('付款时项目概算')]
        estimate_payed = data[uc.PaymentColLabels.index('付款时概算已付额')]
        self.ctrl[('Textbox', '概算本次付款比')].SetValue(percents(this_pay / float(estimate)) if estimate is not None else '')
        self.ctrl[('Textbox', '概算累付比')].SetValue(percents((this_pay + float(estimate_payed)) / float(estimate)) if estimate is not None else '')
        # 预算部分
        budget = data[uc.PaymentColLabels.index('付款时预算总额')]
        budget_payed = data[uc.PaymentColLabels.index('付款时预算已付额')]
        self.ctrl[('Textbox', '预算本次付款比')].SetValue(percents(this_pay / float(budget)) if budget is not None else '')
        self.ctrl[('Textbox', '预算累付比')].SetValue(percents((this_pay + float(budget_payed)) / float(budget)) if budget is not None else '')
        # 合同部分
        contract_value = data[uc.PaymentColLabels.index('付款时合同值')]
        contract_payed = data[uc.PaymentColLabels.index('付款时合同已付额')]
        self.ctrl[('Textbox', '合同本次付款比')].SetValue(percents(this_pay / float(contract_value)) if contract_value is not None else '')
        self.ctrl[('Textbox', '合同累付比')].SetValue(percents((this_pay + float(contract_payed)) / float(contract_value)) if contract_value is not None else '')
    # methods
    def GetValue(self): return self.__value
    def SetValue(self):
        self.__value = []
        for each_ctrl_key, each_value_type in zip(self.__ctrl_key, self.__ctrl_value_type):
            value = self.ctrl[each_ctrl_key].GetValue()
            try:
                if value == '':
                    value = None
                elif each_value_type == '整数型':
                    value = int(value)
                elif each_value_type == '浮点型':
                    value = decimal.Decimal(value.strip().replace(',', ''))
                elif each_value_type == '百分比':
                    value = float(value.strip().replace('%', '')) / 100
            except:
                value = None
            self.__value.append(value)
        return self.__value
    def LoadTap(self): return self.__save_point
    def SaveTap(self, data=[]): self.__save_point = data
    def FormatInfoFromUI(self, ifReport=False):
        data = []
        for i, each_ctrl_key in zip(range(len(self.__ctrl_key)), self.__ctrl_key):
            value = self.ctrl[each_ctrl_key].GetValue()
            if len(value) == 0:
                value = None
            elif self.__ctrl_value_type[i] == '整数型':
                try:
                    value = int(value)
                except:
                    value = None
                    if ifReport:
                        dlg = wx.MessageDialog(self, message='<%s>中数据未能识别，将记录为NULL值' % each_ctrl_key[1], caption='警告', style=wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
            elif self.__ctrl_value_type[i] == '浮点型':
                try:
                    value = decimal.Decimal(value.strip().replace(',', ''))
                except:
                    value = None
                    if ifReport:
                        dlg = wx.MessageDialog(self, message='<%s>中数据未能识别，将记录为NULL值' % each_ctrl_key[1], caption='警告', style=wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
            elif self.__ctrl_value_type[i] == '百分比':
                try:
                    value = float(value.strip().replace('%', '')) / 100
                except:
                    value = None
                    if ifReport:
                        dlg = wx.MessageDialog(self, message='<%s>中数据未能识别，将记录为NULL值' % each_ctrl_key[1], caption='警告', style=wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
            elif self.__ctrl_value_type[i] == '日期型':
                try:
                    value = datetime.date(*time.strptime(value, "%Y-%m-%d")[:3])
                except:
                    value = None
                    if ifReport:
                        dlg = wx.MessageDialog(self, message='<%s>中数据未能识别，将记录为NULL值' % each_ctrl_key[1], caption='警告', style=wx.OK)
                        dlg.ShowModal()
                        dlg.Destroy()
            data.append(value)
        return data
    def FormatInfoForDB(self, ifReport=False):
        data = self.FormatInfoFromUI(ifReport)
        result = []
        for key, value in zip(uc.PaymentColLabels, data):
            if key in uc.PaymentFields:
                result.append(value)
        return result
    def GetDataFromUDID(self, UDID):
        try:
            result = operateDB().read_For_Payment_GridDialog(where_sql='WHERE 付款识别码=%s', where_list=[UDID])[0]
        except:
            result = None
        return result
    def ChangeMode(self, mode, UDID=None):
        if mode == uc.Dialog_Check:
            self.__mode = mode
            data = self.GetDataFromUDID(UDID) if UDID else []
            self.SetTitle('查看付款信息')
            for each_ctrl_key in self.__ctrl_key:
                if each_ctrl_key[0] == 'Textbox':
                    self.ctrl[each_ctrl_key].SetEditable(False)
                elif each_ctrl_key[0] == 'Combobox':
                    self.ctrl[each_ctrl_key].Enable(False)
            self.ctrl[('Button', uc.新建)].Enable(True)
            self.ctrl[('Button', uc.修改)].Enable(True)
            self.ctrl[('Button', uc.保存)].Enable(False)
            self.ctrl[('Button', uc.取消)].Enable(False)
            self.ChoiceDialog(False)
            self.FillBlanks(data)
        elif mode == uc.Dialog_New:
            self.__mode = mode
            self.SetTitle('新建付款信息')
            for each_ctrl_key in self.__ctrl_key:
                if each_ctrl_key[0] == 'Textbox' and each_ctrl_key[1] in '付款事由 本次付款额 付款备注'.split():
                    self.ctrl[each_ctrl_key].SetEditable(True)
                elif each_ctrl_key[0] == 'Combobox':
                    self.ctrl[each_ctrl_key].Enable(True)
            self.ctrl[('Button', uc.新建)].Enable(False)
            self.ctrl[('Button', uc.修改)].Enable(False)
            self.ctrl[('Button', uc.保存)].Enable(True)
            self.ctrl[('Button', uc.取消)].Enable(True)
            self.ChoiceDialog(True)
            self.FillBlanks()
        elif mode == uc.Dialog_Edit:
            try:
                data = self.GetDataFromUDID(UDID) if UDID else []
                assert data
            except:
                dlg = wx.MessageDialog(self, message='该付款识别码数据库中未记录，请检查', caption='提示', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            self.__mode = mode
            self.SetTitle('修改付款信息')
            for each_ctrl_key in self.__ctrl_key:
                if each_ctrl_key[0] == 'Textbox' and each_ctrl_key[1] in '付款事由 本次付款额 付款备注'.split():
                    self.ctrl[each_ctrl_key].SetEditable(True)
                elif each_ctrl_key[0] == 'Combobox':
                    self.ctrl[each_ctrl_key].Enable(True)
            self.ctrl[('Button', uc.新建)].Enable(False)
            self.ctrl[('Button', uc.修改)].Enable(False)
            self.ctrl[('Button', uc.保存)].Enable(True)
            self.ctrl[('Button', uc.取消)].Enable(True)
            self.ChoiceDialog(True)
            self.FillBlanks(data)
    def FillBlanks(self, data=[]):
        def thousands(n): return '{:>,.2f}'.format(n)
        def percents(n): return '{:>.2f}'.format((n or 0) * 100) + '%'
        for each_ctrl_key in self.__ctrl_key:
            try:
                value = data[self.__ctrl_key.index(each_ctrl_key)]
                value_type = self.__ctrl_value_type[self.__ctrl_key.index(each_ctrl_key)]
                if value is None:
                    value = ''
                elif value_type == '浮点型':
                    value = thousands(value)
                elif value_type == '百分比':
                    value = percents(value)
                else:
                    value = str(value)
                self.ctrl[each_ctrl_key].SetValue(value)
            except:
                self.ctrl[each_ctrl_key].SetValue('')
    def ChoiceDialog(self, could_open): self.__choice_dialog_could_open = could_open

if __name__ == '__main__':
    app = wx.App()
    # dlg = Initiation_TreeDialog()
    dlg = Payment_GridDialog()
    if dlg.ShowModal() == wx.ID_OK:
        print(dlg.GetValue())
    dlg.Destroy()
    app.Destroy()
    pass