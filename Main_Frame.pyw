#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Main_Dialogs import *
from matplotlib.backends import backend_wxagg
from matplotlib.figure import Figure

class Main_Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, '新城镇公司工程合同管理系统', size=uc.Window_Size)
        panel = wx.Panel(self)
        self.SetMinSize((uc.Window_Size))
        self.Center(wx.BOTH)
        # 菜单栏
        menuBar = wx.MenuBar()                  # 创建一个菜单栏
        menu = {}
        key = '系统'
        menu[key] = wx.Menu()                   # 创建一个菜单
        menuBar.Append(menu[key], key)          # 添加菜单到菜单栏
        key = '帮助'
        menu[key] = wx.Menu()                   
        menuBar.Append(menu[key], key)
        change_password = menu['系统'].Append(-1, '修改密码', '打开<修改密码>对话框')
        menu['系统'].AppendSeparator()
        change_password = menu['系统'].Append(-1, '注销登陆', '退出<主界面>，返回登陆界面重新登录')
        self.SetMenuBar(menuBar)
        # 状态栏
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetFieldsCount(3)
        self.statusbar.SetStatusWidths([-1, -2, -3])
        self.statusbar.SetStatusText('我是状态栏', 0)
        # 控件群
            # 工具栏
        def AddBitmapButton(key):
            '添加一个bitmapButton'
            bm = wx.Bitmap('icon\\%s.png' % key)
            return wx.BitmapButton(panel, -1, bm, size=(100, 80), name=key)
        bitmapButtons = {}
        for key in 'Company Init Bidding Contract Budget Payment'.split():
            bitmapButtons[key] = AddBitmapButton(key)
            # 树形结构
        def AddTreeListCtrl():
            '添加一组树形结构相关控件'
            self.treeLabel = wx.StaticText(panel, -1, '系统数据概览')
            self.tree = wx.dataview.TreeListCtrl(panel, style = wx.dataview.TL_SINGLE|wx.TR_FULL_ROW_HIGHLIGHT, size=uc.Size_BigDialog)
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
            self.button_Collapse = []
            for i in range(1, 8):
                self.button_Collapse.append(wx.Button(panel, -1, label=str(i), size=uc.Size_Button_MiniDialog))
        AddTreeListCtrl()
            # 图表组件
        def AddChart():
            plt.rcParams['font.sans-serif'] = ['simhei']
            plt.rcParams['axes.unicode_minus'] = False
            labels, sizes, explode, title = operateDB().get_Pie_Data(1)
            fig = Figure((1, 3.5))
            self.chartPannel = backend_wxagg.FigureCanvasWxAgg(panel, -1, fig)
            self.axes = fig.add_subplot(1, 1, 1)
            self.axes.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=135)
            self.axes.set_title(title)
        AddChart()
            # 详情文本
        self.multiText = wx.TextCtrl(panel, -1, '', size=(280, -1), style=wx.TE_MULTILINE|wx.TE_RICH2|wx.TE_READONLY)
        # 控件组合
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        for key in 'Company Init Bidding Contract Budget Payment'.split():
            buttonSizer.Add(bitmapButtons[key], 0, wx.ALL|wx.EXPAND, 0)
        mainSizer.Add(buttonSizer, 0, wx.ALL|wx.EXPAND, 0)
        bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        mainSizer.Add(bottomSizer, 1, wx.ALL|wx.EXPAND, 0)
        treeSizer = wx.BoxSizer(wx.VERTICAL)
        treeTitleSizer = wx.BoxSizer(wx.HORIZONTAL)
        treeTitleSizer.AddSpacer(50)
        treeTitleSizer.Add(self.treeLabel, 0, wx.ALL, 5)
        treeTitleSizer.AddSpacer(350)
        for eachButton in self.button_Collapse:
            treeTitleSizer.Add(eachButton, 0, wx.ALL, 5)
        treeSizer.Add(treeTitleSizer, 0, wx.RIGHT|wx.EXPAND, 0)
        treeSizer.Add(self.tree, 1, wx.RIGHT|wx.EXPAND, 0)
        bottomSizer.Add(treeSizer, 1, wx.RIGHT|wx.EXPAND, 0)
        chartSizer = wx.BoxSizer(wx.VERTICAL)
        chartSizer.Add(self.chartPannel, 0, wx.EXPAND, 0)
        chartSizer.Add(self.multiText, 1, wx.EXPAND, 0)
        bottomSizer.Add(chartSizer, 0, wx.RIGHT|wx.EXPAND, 0)
        panel.SetSizer(mainSizer)
        panel.Fit()
        # events binder
        self.Bind(wx.EVT_CLOSE, self.clickOnClose)
        for key in 'Company Init Bidding Contract Budget Payment'.split():
            bitmapButtons[key].Bind(wx.EVT_BUTTON, self.clickOnbitmapButton)
        for i in range(7):
            self.button_Collapse[i].Bind(wx.EVT_BUTTON, self.clickOnCollapse)
        self.tree.Bind(wx.dataview.EVT_TREELIST_SELECTION_CHANGED, self.ClickOnItem)
        self.tree.Bind(wx.dataview.EVT_TREELIST_ITEM_ACTIVATED, self.Jump)

    # events
    def clickOnClose(self, event):
        dlg = wx.MessageDialog(self, message='您确定要退出吗？点击<是>退出系统', caption='警告', style= wx.YES_NO | wx.NO_DEFAULT)
        if dlg.ShowModal() == wx.ID_NO:
            dlg.Destroy()
            return
        else:
            dlg.Destroy()
        self.Destroy()
    def Jump(self, event):
        dlg = JumpDialog(Label='跳转选项列表', Choices='跳转至相应<立项>信息 跳转至相应<招标>信息 跳转至相应<合同>信息 跳转至相应<付款>信息'.split())
        if dlg.ShowModal() != wx.ID_OK:
            dlg.Destroy()
            return
        result = dlg.GetValue()
        dlg.Destroy()
        try:
            UDID = int(self.tree.GetItemText(event.Item).split('-')[0])
        except:
            UDID = None
        if UDID:
            if result.find('立项') > 0:
                where_sql = 'WHERE 立项识别码 IN %s'
                if operateDB().get_All_Children_Info_InitUDID(UDID):
                    UDIDs = operateDB().get_All_Grandchildren(UDID)
                    dlg = Initiation_GridDialog(where_sql='WHERE 立项识别码 IN %s', where_list=[UDIDs])
                else:
                    UDID = UDID
                    dlg = Initiation_GridDialog(where_sql='WHERE 立项识别码 IN %s', where_list=[[UDID]])
                dlg.ShowModal()
                dlg.Destroy()
            elif result.find('招标') > 0:
                where_sql = 'WHERE 立项识别码 IN %s'
                if operateDB().get_All_Children_Info_InitUDID(UDID):
                    UDIDs = operateDB().get_All_Grandchildren(UDID)
                    dlg = Bidding_GridDialog(where_sql='WHERE 立项识别码 IN %s', where_list=[UDIDs])
                else:
                    UDID = UDID
                    dlg = Bidding_GridDialog(where_sql='WHERE 立项识别码 IN %s', where_list=[[UDID]])
                dlg.ShowModal()
                dlg.Destroy()
            elif result.find('合同') > 0:
                where_sql = 'WHERE 立项识别码 IN %s'
                if operateDB().get_All_Children_Info_InitUDID(UDID):
                    UDIDs = operateDB().get_All_Grandchildren(UDID)
                    dlg = Contract_GridDialog(where_sql='WHERE 立项识别码 IN %s', where_list=[UDIDs])
                else:
                    UDID = UDID
                    dlg = Contract_GridDialog(where_sql='WHERE 立项识别码 IN %s', where_list=[[UDID]])
                dlg.ShowModal()
                dlg.Destroy()
            elif result.find('付款') > 0:
                where_sql = 'WHERE 立项识别码 IN %s'
                if operateDB().get_All_Children_Info_InitUDID(UDID):
                    UDIDs = operateDB().get_All_Grandchildren(UDID)
                    dlg = Payment_GridDialog(where_sql='WHERE 立项识别码 IN %s', where_list=[UDIDs])
                else:
                    UDID = UDID
                    dlg = Payment_GridDialog(where_sql='WHERE 立项识别码 IN %s', where_list=[[UDID]])
                dlg.ShowModal()
                dlg.Destroy()
    def clickOnbitmapButton(self, event):
        name = wx.FindWindowById(event.Id, self).GetName()
        if name == 'Company':
            dlg = Company_GridDialog()
        elif name =='Init':
            dlg = Initiation_GridDialog()
        elif name =='Bidding':
            dlg = Bidding_GridDialog()
        elif name =='Contract':
            dlg = Contract_GridDialog()
        elif name =='Budget':
            dlg = Budget_GridDialog()
        elif name =='Payment':
            dlg = Payment_GridDialog()
        if dlg.ShowModal() == wx.ID_OK:
            print(dlg.GetValue())
            # 刷新一下主界面的树形结构器
            self.treeData = operateDB().format_Contract_Details_By_Tree()
            self.tree.DeleteAllItems()
            root = self.tree.GetRootItem()
            self.makeTree(root, self.treeData)
        dlg.Destroy()
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
    def ClickOnItem(self, event):
        try:
            UDID = int(self.tree.GetItemText(event.Item).split('-')[0])
        except:
            UDID = None
        # 绘制图表
        sytle = 'Pie'
        if sytle == 'Pie':
            labels, sizes, explode, title = operateDB().get_Pie_Data(UDID)
            self.axes.clear()
            if labels:
                self.axes.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=135)
                self.axes.set_title(title)
            self.chartPannel.draw()
        # 生成文本
        if not UDID:
            return
        Init_Infos = operateDB().read_For_Initiation_GridDialog('WHERE 立项识别码=%s', [UDID])
        estimate = round(float(Init_Infos[0][uc.InitiationColLabels.index('项目概算')] or 0)/10000, 2)
        Parent_UDID = operateDB().get_Parent_InitUDID(UDID)
        Count_Children = len(operateDB().get_All_Children_Info_InitUDID(UDID))
        if Parent_UDID:
            Parent_Infos = operateDB().read_For_Initiation_GridDialog('WHERE 立项识别码=%s', [Parent_UDID])
        Bid_Infos = operateDB().read_For_Bidding_GridDialog('WHERE 立项识别码=%s', [UDID])
        Contract_Infos = operateDB().read_For_Contract_GridDialog('WHERE 立项识别码=%s', [UDID])
        if Count_Children:
            payed, Count_Payment = operateDB().get_Init_Branch_Payed(UDID)
            payed = round(float((payed or 0)/10000), 2)
        else:
            payed, Count_Payment = operateDB().get_Init_Leaf_Payed(UDID)
            payed = round(float((payed or 0)/10000), 2)
        mystring = '本项目编号：{}，项目名称：{}{}'.format(UDID, 
                                                           Init_Infos[0][uc.InitiationColLabels.index('项目名称')], 
                                                           Init_Infos[0][uc.InitiationColLabels.index('分项名称')] or '')
        if Parent_UDID:
            mystring += '\n本项目父项：{}{}'.format(Parent_Infos[0][uc.InitiationColLabels.index('项目名称')], 
                                                    Parent_Infos[0][uc.InitiationColLabels.index('分项名称')] or '')
        mystring += '\n建设单位：{}，代建单位：{}'.format(Init_Infos[0][uc.InitiationColLabels.index('建设单位名称')], 
                                                          Init_Infos[0][uc.InitiationColLabels.index('代建单位名称')] or '')
        if Count_Children:
            mystring += '\n本项目共有{}个子项'.format(Count_Children)
        else:
            mystring += '\n本项目无子项'
        if Contract_Infos:
            mystring += '\n本项目签订的合同名称：{}，合同类别：{}'.format(Contract_Infos[0][uc.ContractColLabels.index('合同名称')],
                                                                          Contract_Infos[0][uc.ContractColLabels.index('合同类别')])
        else:
            mystring += '\n本项目未签订合同'
        if Bid_Infos:
            mystring += '\n通过{}方式确定了供应商：{}'.format(Bid_Infos[0][uc.BiddingColLabels.index('招标方式')],
                                                              Bid_Infos[0][uc.BiddingColLabels.index('中标单位名称')])
        mystring += '\n本项目概算：{}万元'.format(estimate)
        if Count_Payment:
            mystring += '\n截至目前，本项目已付款{}次，共支付{}万元'.format(Count_Payment, payed)
        else:
            mystring += '\n截至目前，本项目尚未开始付款'
        mystring += '。'
                   
        self.multiText.SetValue(mystring)
    # methods
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

if __name__ == '__main__':
    app = wx.App()
    frame = Main_Frame()
    frame.Show()
    app.MainLoop()