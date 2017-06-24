#!/usr/bin/env python
# -*- coding: utf-8 -*-

会签表格 = '会签表格'
跳转 = '跳转'
附件 = '附件'
下载 = '下载'
上传 = '上传'
打开 = '打开'
另存为 = '另存为'
新建 = '新建'
修改 = '修改'
删除 = '删除'
筛选 = '筛选'
刷新 = '刷新'
导出 = '导出文件'
清空 = '清空'
查询结构 = '查询结构'
OK = 'OK'
CANCEL = 'CANCEL'
退出 = '退出'
保存 = '保存'
取消 = '取消'
显示窗 = '显示窗'
Size_Button_MiniDialog = (20, 20)
Size_Button_BaseDialog = (60, 20)
Size_Label_BaseDialog = (100, 20)
Size_Label_LongDialog = (125, 20)
Size_Textbox_Normal_BaseDialog = (100, 20)
Size_Textbox_Short_BaseDialog = (50, 20)
Size_Textbox_Long_BaseDialog = (200, 20)
Size_Textbox_VeryLong_BaseDialog = (460, 20)
Size_Combobox_Normal_BaseDialog = (130, 30)
Size_Combobox_Short_BaseDialog = (100, 30)
Size_Combobox_Long_BaseDialog = (230, 30)
Size_BaseDialog = (800, 600)
Size_BigDialog = (1200, 600)
Size_Button_BaseFrame = (100, 20)
Size_BaseFrame = (800, 600)
Dialog_Check = 0
Dialog_New = 1
Dialog_Edit = 2

# FilterDialog
筛选器 = '筛选器'
Size_Listbox_FilterDialog = (400, 250)
新增筛选条件 = '<--新增筛选条件--'
修改筛选条件 = '<--修改筛选条件--'
Size_Button_Case_FilterDialog = (120, 20)
筛选字段 = ['筛选字段_0', '筛选字段_1']
比较符 = ['比较符_0', '比较符_1']
逻辑符 = '逻辑符'
数据类型 = ['数据类型_0', '数据类型_1']
筛选值 = ['筛选值_0', '筛选值_1']
Size_Label_FilterDialog = (80, 20)
Size_Combobox_Normal_FilterDialog = (140, 30)
Size_Combobox_Short_FilterDialog = (80, 30)
ForListbox = 0
ForVar = 1
Size_Textbox_Note = (460, 60)

# Company
Size_Label_Company_MaintainDialog = (80, 20)
CompanyColLabels = '单位识别码 单位名称 单位类别 单位性质 法定代表人 注册资金 单位资质 银行账号 联系人 联系方式 单位备注'.split()
CompanyColLabels_Type = '整数型 字符串型 字符串型 字符串型 字符串型 浮点型 字符串型 字符串型 字符串型 字符串型 字符串型'.split()
CompanyFields = '单位识别码 单位名称 单位类别 单位性质 法定代表人 注册资金 单位资质 银行账号 联系人 联系方式 单位备注'.split()
CompanyFields_Type = '整数型 字符串型 字符串型 字符串型 字符串型 浮点型 字符串型 字符串型 字符串型 字符串型 字符串型'.split()

# Initiation
InitiationColLabels = '立项识别码 项目名称 分项名称 父项立项识别码 父项项目名称 父项分项名称 建设单位识别码 建设单位名称 代建单位识别码 代建单位名称 立项文件名称 立项时间 项目概算 概算付款比 立项备注'.split()
InitiationColLabels_Type = '整数型 字符串型 字符串型 整数型 字符串型 字符串型 整数型 字符串型 整数型 字符串型 字符串型 日期型 浮点型 百分比 字符串型'.split()
InitiationFields = '立项识别码 项目名称 分项名称 父项立项识别码 建设单位识别码 代建单位识别码 立项文件名称 立项时间 项目概算 立项备注'.split()
InitiationFields_Type = '整数型 字符串型 字符串型 整数型 整数型 整数型 字符串型 日期型 浮点型 字符串型'.split()

# Bidding
Size_Label_Bidding_MaintainDialog = (130, 20)
BiddingColLabels = '招标识别码 立项识别码 项目名称 分项名称 招标方式 招标单位识别码 招标单位名称 招标代理识别码 招标代理单位名称 项目概算 预算控制价 招标文件定稿时间 公告邀请函发出时间 开标时间 中标通知书发出时间 中标单位识别码 中标单位名称 中标价 招标备注'.split()
BiddingColLabels_Type = '整数型 整数型 字符串型 字符串型 字符串型 整数型 字符串型 整数型 字符串型 浮点型 浮点型 日期型 日期型 日期型 日期型 整数型 字符串型 浮点型 字符串型'.split()
BiddingFields = '招标识别码 立项识别码 招标方式 招标单位识别码 招标代理识别码 预算控制价 招标文件定稿时间 公告邀请函发出时间 开标时间 中标通知书发出时间 中标单位识别码 中标价 招标备注'.split()
BiddingFields_Type = '整数型 整数型 字符串型 整数型 整数型 浮点型 日期型 日期型 日期型 日期型 整数型 浮点型 字符串型'.split()

# Contract
ContractColLabels = '合同识别码 立项识别码 项目名称 分项名称 招标识别码 招标方式 项目概算 中标价 合同编号 合同名称 合同主要内容 合同类别 甲方识别码 甲方单位名称 乙方识别码 乙方单位名称 丙方识别码 丙方单位名称 丁方识别码 丁方单位名称 合同签订时间 合同值_签订时 合同值_最新值 合同值_最终值 已付款 已付款占概算 已付款占合同 形象进度 支付上限 开工时间 竣工合格时间 保修结束时间 审计完成时间 合同备注'.split()
ContractColLabels_Type = '整数型 整数型 字符串型 字符串型 整数型 字符串型 浮点型 浮点型 字符串型 字符串型 字符串型 字符串型 整数型 字符串型 整数型 字符串型 整数型 字符串型 整数型 字符串型 日期型 浮点型 浮点型 浮点型 浮点型 百分比 百分比 字符串型 浮点型 日期型 日期型 日期型 日期型 字符串型'.split()
ContractFields = '合同识别码 立项识别码 招标识别码 合同编号 合同名称 合同主要内容 合同类别 甲方识别码 乙方识别码 丙方识别码 丁方识别码 合同签订时间 合同值_签订时 合同值_最新值 合同值_最终值 形象进度 支付上限 开工时间 竣工合格时间 保修结束时间 审计完成时间 合同备注'.split()
ContractFields_Type = '整数型 整数型 整数型 字符串型 字符串型 字符串型 字符串型 整数型 整数型 整数型 整数型 日期型 浮点型 浮点型 浮点型 字符串型 浮点型 日期型 日期型 日期型 日期型 字符串型'.split()

# Budget
BudgetColLabels = '预算识别码 父项预算识别码 父项预算名称 预算名称 预算周期 预算总额 预算已付额 预算余额 预算已付比 预算备注'.split()
BudgetColLabels_Type = '整数型 整数型 字符串型 字符串型 字符串型 浮点型 浮点型 浮点型 百分比 字符串型'.split()
BudgetFields = '预算识别码 父项预算识别码 预算名称 预算周期 预算总额 预算备注'.split()
BudgetFields_Type = '整数型 整数型 字符串型 字符串型 浮点型 字符串型'.split()

# Payment
PaymentColLabels = '付款识别码 付款登记时间 付款支付时间 立项识别码 项目名称 分项名称 合同识别码 合同名称 合同类别 合同编号 付款批次 付款事由 付款单位识别码 付款单位名称 付款单位账号 收款单位识别码 收款单位名称 收款单位账号 预算识别码 预算名称 预算周期 付款时预算总额 付款时项目概算 付款时合同付款上限 付款时合同值 付款时预算余额 付款时概算余额 付款时合同可付余额 付款时合同未付额 付款时预算已付额 付款时合同已付额 付款时概算已付额 付款时预算已付比 付款时合同已付比 付款时概算已付比 付款时形象进度 本次付款额 预算本次付款比 合同本次付款比 概算本次付款比 预算累付比 合同累付比 概算累付比 付款备注'.split()
PaymentColLabels_Type = '整数型 日期型 日期型 整数型 字符串型 字符串型 整数型 字符串型 字符串型 字符串型 整数型 字符串型 整数型 字符串型 字符串型 整数型 字符串型 字符串型 整数型 字符串型 字符串型 浮点型 浮点型 浮点型 浮点型 浮点型 浮点型 浮点型 浮点型 浮点型 浮点型 浮点型 百分比 百分比 百分比 字符串型 浮点型 百分比 百分比 百分比 百分比 百分比 百分比 字符串型'.split()
PaymentFields = '付款识别码 付款登记时间 付款支付时间 立项识别码 合同识别码 付款事由 付款单位识别码 收款单位识别码 预算识别码 付款时预算总额 付款时项目概算 付款时合同付款上限 付款时合同值 付款时预算余额 付款时概算余额 付款时合同可付余额 付款时合同未付额 付款时预算已付额 付款时合同已付额 付款时概算已付额 付款时形象进度 本次付款额 付款备注'.split()
PaymentFields_Type = '整数型 日期型 日期型 整数型 整数型 字符串型 整数型 整数型 整数型 浮点型 浮点型 浮点型 浮点型 浮点型 浮点型 浮点型 浮点型 浮点型 浮点型 浮点型 字符串型 浮点型 字符串型'.split()

# Main_Frame
Window_Size = (1000, 800)