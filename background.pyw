#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    如： 千分位、浮点数、填充字符、对齐的组合使用：
    输入： '{:>18,.2f}'.format(70305084.0)     # :冒号+空白填充+右对齐+固定宽度18+浮点精度.2+浮点数声明f
    输出：'     70,305,084.00'
    自符串转日期：datetime.date(*time.strptime('2017-03-07', "%Y-%m-%d")[:3])
    Excel日期：1899年12月31,datetime.date(1899,12,31)+datetime.timedelta(days=42000)
'''
import wx, wx.grid
import oss2
import datetime
import tkinter
import tkinter.filedialog
import six
import time
import os
import hashlib
import pymysql
import sys
import re
import pdb
import decimal
import webbrowser
import xlrd
import xlsxwriter
import calendar
import matplotlib.pyplot as plt
import userConst as uc

def set_trace():
    import pdb
    pdb.set_trace()

class operateDB():
    def __init__(self):
        pass
    def newCurs(self):
        'Connect to the database'
        conn = pymysql.connect(host='127.0.0.1',
                                     port=3306,
                                     user='root',
                                     password='44332211',
                                     charset='utf8')
        curs = conn.cursor()
        curs.execute('use ERP')
        conn.commit()
        return (conn, curs)
    def createAllTables(self):
        conn, curs = self.newCurs()
        curs.execute('CREATE SCHEMA IF NOT EXISTS ERP DEFAULT CHARACTER SET utf8')
        # user
        curs.execute('''CREATE TABLE IF NOT EXISTS TABEL_USER     (DB_id                BIGINT PRIMARY KEY AUTO_INCREMENT, 
                                                                   用户名               VARCHAR(255), 
                                                                   密码                 VARCHAR(255), 
                                                                   权限                 TINYINT, 
                                                                   UNIQUE(用户名))'''
                    )
        # 单位信息表
        curs.execute('''CREATE TABLE IF NOT EXISTS TABEL_单位信息 (单位识别码           BIGINT PRIMARY KEY AUTO_INCREMENT,
                                                                   单位名称             VARCHAR(255),
                                                                   单位类别             VARCHAR(255),
                                                                   单位性质             VARCHAR(255),
                                                                   法定代表人           VARCHAR(255),
                                                                   注册资金             DECIMAL(12, 2),
                                                                   单位资质             VARCHAR(255),
                                                                   银行账号             VARCHAR(255),
                                                                   联系人               VARCHAR(255),
                                                                   联系方式             VARCHAR(255),
                                                                   单位备注             TEXT, 
                                                                   UNIQUE(单位名称))
                                                                   '''
                    )
        # 立项信息表
        curs.execute('''CREATE TABLE IF NOT EXISTS TABEL_立项信息 (立项识别码           BIGINT PRIMARY KEY AUTO_INCREMENT, 
                                                                   项目名称             VARCHAR(255), 
                                                                   分项名称             VARCHAR(255),
                                                                   父项立项识别码       BIGINT,
                                                                   建设单位识别码       BIGINT,
                                                                   代建单位识别码       BIGINT,
                                                                   立项文件名称         VARCHAR(255),
                                                                   立项时间             DATE,
                                                                   项目概算             DECIMAL(12, 2),
                                                                   立项备注             TEXT, 
                                                                   UNIQUE(项目名称, 分项名称))
                                                                   '''
                    )
        # 招标信息表
        curs.execute('''CREATE TABLE IF NOT EXISTS TABEL_招标信息 (招标识别码           BIGINT PRIMARY KEY AUTO_INCREMENT, 
                                                                   立项识别码           BIGINT,
                                                                   招标方式             VARCHAR(255),
                                                                   招标单位识别码       BIGINT,
                                                                   招标代理识别码       BIGINT,
                                                                   预算控制价           DECIMAL(12, 2),
                                                                   招标文件定稿时间     DATE,
                                                                   公告邀请函发出时间   DATE,
                                                                   开标时间             DATE,
                                                                   中标通知书发出时间   DATE,
                                                                   中标单位识别码       BIGINT,
                                                                   中标价               DECIMAL(12, 2),
                                                                   招标备注             TEXT)
                                                                   '''
                    )
        # 合同信息表
        curs.execute('''CREATE TABLE IF NOT EXISTS TABEL_合同信息 (合同识别码           BIGINT PRIMARY KEY AUTO_INCREMENT, 
                                                                   立项识别码           BIGINT,
                                                                   招标识别码           BIGINT,
                                                                   合同编号             VARCHAR(255),
                                                                   合同名称             VARCHAR(255),
                                                                   合同主要内容         VARCHAR(255),
                                                                   合同类别             VARCHAR(255),
                                                                   甲方识别码           BIGINT,
                                                                   乙方识别码           BIGINT,
                                                                   丙方识别码           BIGINT,
                                                                   丁方识别码           BIGINT,
                                                                   合同签订时间         DATE,
                                                                   合同值_签订时        DECIMAL(12, 2),
                                                                   合同值_最新值        DECIMAL(12, 2),
                                                                   合同值_最终值        DECIMAL(12, 2),
                                                                   形象进度             TEXT,
                                                                   支付上限             DECIMAL(12, 2),
                                                                   开工时间             DATE,
                                                                   竣工合格时间         DATE,
                                                                   保修结束时间         DATE,
                                                                   审计完成时间         DATE,
                                                                   合同备注             TEXT)
                                                                   '''
                    )
        # 预算信息表
        curs.execute('''CREATE TABLE IF NOT EXISTS TABEL_预算信息 (预算识别码           BIGINT PRIMARY KEY AUTO_INCREMENT, 
                                                                   父项预算识别码       BIGINT,
                                                                   预算名称             VARCHAR(255),
                                                                   预算周期             VARCHAR(255),
                                                                   预算总额             DECIMAL(12, 2),
                                                                   预算备注             TEXT,
                                                                   UNIQUE(预算名称, 预算周期))
                                                                   '''
                    )
        # 付款信息表
        curs.execute('''CREATE TABLE IF NOT EXISTS TABEL_付款信息 (付款识别码           BIGINT PRIMARY KEY AUTO_INCREMENT,
                                                                   付款登记时间         DATE,
                                                                   付款支付时间         DATE,
                                                                   立项识别码           BIGINT,
                                                                   合同识别码           BIGINT,
                                                                   付款事由             TEXT,
                                                                   付款单位识别码       BIGINT,
                                                                   收款单位识别码       BIGINT,
                                                                   预算识别码           BIGINT,
                                                                   付款时预算总额       DECIMAL(12, 2),
                                                                   付款时项目概算       DECIMAL(12, 2),
                                                                   付款时合同付款上限   DECIMAL(12, 2),
                                                                   付款时合同值         DECIMAL(12, 2),
                                                                   付款时预算余额       DECIMAL(12, 2),
                                                                   付款时概算余额       DECIMAL(12, 2),
                                                                   付款时合同可付余额   DECIMAL(12, 2),
                                                                   付款时合同未付额     DECIMAL(12, 2),
                                                                   付款时预算已付额     DECIMAL(12, 2),
                                                                   付款时合同已付额     DECIMAL(12, 2),
                                                                   付款时概算已付额     DECIMAL(12, 2),
                                                                   付款时形象进度       TEXT,
                                                                   本次付款额           DECIMAL(12, 2),
                                                                   付款备注             TEXT)
                                                                   '''
                    )
        
        # log
        # curs.execute('''CREATE TABLE IF NOT EXISTS log       (DB_id                    BIGINT PRIMARY KEY AUTO_INCREMENT, 
        #                                                       gmt_create               DATETIME, 
        #                                                       gmt_modified             DATETIME,
        #                                                       username                 VARCHAR(255)    DEFAULT '',        # 谁
        #                                                       how                      VARCHAR(255)    DEFAULT '',        # 用何种方式
        #                                                       what                     TEXT)                              # 操作了哪个表
        #              '''
        #             )
        conn.commit()
        conn.close()
    # Company
    def read_For_Company_GridDialog(self, where_sql='', where_list=[], order_sql='', order_list=[]):
        conn, curs = self.newCurs()
        sql = 'SELECT {} FROM tabel_单位信息 '.format(', '.join(uc.CompanyColLabels)) + where_sql + ' ' + order_sql
        sql_list = where_list + order_list
        curs.execute(sql, sql_list)
        fetchall = curs.fetchall()
        conn.close()
        return fetchall
    def save_For_Company_MaintainDialog(self, data=[]):
        if not data:
            return
        UDID = data[0]
        conn, curs = self.newCurs()
        sql = 'SELECT COUNT(*) FROM tabel_单位信息 WHERE 单位识别码=%s'
        curs.execute(sql, [UDID])
        isExist = curs.fetchall()[0][0]
        def insert_Data(data):
            sql = 'INSERT INTO tabel_单位信息 ({}) VALUES ({})'.format(', '.join(uc.CompanyFields), ', '.join(len(uc.CompanyFields)*['%s']))
            sql_list = data
            curs.execute(sql, sql_list)
        def update_Data(data):
            sql = 'UPDATE tabel_单位信息 SET {} WHERE 单位识别码=%s'.format('=%s, '.join(uc.CompanyFields[1:]) + '=%s ')
            sql_list = data[1:] + [data[0]]
            curs.execute(sql, sql_list)
        if isExist:
            update_Data(data)
        else:
            insert_Data(data)
        conn.commit()
        conn.close()
        return True
    # Initiation
    def read_For_Initiation_GridDialog(self, where_sql='', where_list=[], order_sql='', order_list=[]):
        conn, curs = self.newCurs()
        sql = '''SELECT {} FROM 
                 (SELECT            A.立项识别码, A.项目名称, A.分项名称, A.父项立项识别码, B.项目名称 AS 父项项目名称, B.分项名称 AS 父项分项名称,
                                   A.建设单位识别码, U1.单位名称 AS 建设单位名称, A.代建单位识别码, U2.单位名称 AS 代建单位名称, 
                                   A.立项文件名称, A.立项时间, A.项目概算, 已付款/A.项目概算 AS 概算付款比, A.立项备注
                  FROM             tabel_立项信息 AS A
                       LEFT JOIN   tabel_立项信息 AS B  ON A.父项立项识别码=B.立项识别码
                       LEFT JOIN   tabel_单位信息 AS U1 ON A.建设单位识别码=U1.单位识别码
                       LEFT JOIN   tabel_单位信息 AS U2 ON A.代建单位识别码=U2.单位识别码
                       LEFT JOIN  (SELECT 立项识别码, SUM(本次付款额) AS 已付款 FROM tabel_付款信息 GROUP BY 立项识别码) AS P ON A.立项识别码=P.立项识别码) AS Origin
              '''.format(', '.join(uc.InitiationColLabels)) + where_sql + ' ' + order_sql
        sql_list = where_list + order_list
        curs.execute(sql, sql_list)
        result = list(map(list, curs.fetchall()))
        for i in range(len(result)):
            InitUDID = result[i][0]
            estimate = result[i][uc.InitiationColLabels.index('项目概算')]
            AGC = self.get_All_Grandchildren(InitUDID)    # All Grandchildren
            if not AGC:
                continue
            sql = '''SELECT SUM(本次付款额) FROM tabel_付款信息 WHERE 立项识别码 IN %s'''
            sql_list = [AGC]
            curs.execute(sql, sql_list)
            payed = decimal.Decimal(curs.fetchall()[0][0] or 0)
            try:
                result[i][uc.InitiationColLabels.index('概算付款比')] = payed / estimate
            except:
                pass
        conn.close()
        return result
    def save_For_Initiation_MaintainDialog(self, data=[]):
        if not data:
            return
        UDID = data[0] 
        try:
            parent_UDID = int(data[uc.InitiationFields.index('父项立项识别码')])
        except:
            parent_UDID = None
        #合法性检查
        if parent_UDID:
            estimate = float(data[uc.InitiationFields.index('项目概算')] or 0.0)
            brothers_sum_estimate = float(self.get_All_Children_Sum_Estimate_Without_One(parent_UDID, UDID or 0) or 0.0)
            parent_estimate = float(self.get_Estimate(parent_UDID) or 0.0)
            if estimate + brothers_sum_estimate > parent_estimate:
                dlg = wx.MessageDialog(None, message='本项目及其兄弟分项的概算和超出父项概算，本项目允许的最高概算为：{:>,.2f}，请检查'.format(float(parent_estimate) - float(brothers_sum_estimate)), caption='警告', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
        conn, curs = self.newCurs()
        sql = 'SELECT COUNT(*) FROM tabel_立项信息 WHERE 立项识别码=%s'
        curs.execute(sql, [UDID])
        isExist = curs.fetchall()[0][0]
        def insert_Data(data):
            sql = 'INSERT INTO tabel_立项信息 ({}) VALUES ({})'.format(', '.join(uc.InitiationFields), ', '.join(len(uc.InitiationFields)*['%s']))
            sql_list = data
            curs.execute(sql, sql_list)
        def update_Data(data):
            sql = 'UPDATE tabel_立项信息 SET {} WHERE 立项识别码=%s'.format('=%s, '.join(uc.InitiationFields[1:]) + '=%s ')
            sql_list = data[1:] + [data[0]]
            curs.execute(sql, sql_list)
        if isExist:
            update_Data(data)
        else:
            insert_Data(data)
        conn.commit()
        conn.close()
        return True
    def get_Parent_InitUDID(self, UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT 父项立项识别码 FROM tabel_立项信息 WHERE 立项识别码=%s'
        curs.execute(sql, [UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0]
        except:
            return
    def get_Estimate(self, UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT 项目概算 FROM tabel_立项信息 WHERE 立项识别码=%s'
        curs.execute(sql, [UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0]
        except:
            return
    def get_All_Children_Sum_Estimate_Without_One(self, parent_UDID, UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT SUM(项目概算) FROM tabel_立项信息 WHERE 父项立项识别码=%s AND 立项识别码<>%s'
        curs.execute(sql, [parent_UDID, UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0]
        except:
            return
    def get_All_Children_Sum_Estimate(self, UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT sum(项目概算) FROM tabel_立项信息 WHERE 父项立项识别码=%s'
        curs.execute(sql, [UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0] or 0.0
        except:
            return
    def get_All_Brothers_Sum_Estimate(self, UDID):
        conn, curs = self.newCurs()
        sql = '''SELECT sum(项目概算) FROM tabel_立项信息 
                 WHERE 立项识别码<>%s AND 父项立项识别码=(SELECT 父项立项识别码 FROM tabel_立项信息 WHERE 立项识别码=%s)'''
        curs.execute(sql, [UDID, UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0] or 0.0
        except:
            return
    # TreeList-Initiation
    def format_Initiation_Details_By_Tree(self):
        '取得含立项识别码、项目概算、层级的树形序列'
        # 得到全部根节点
        roots_info = self.get_All_Roots_Info_Initiation()
        # 访问这些根节点，取得每个根节点的所有子项，存入其中
        def zipLeaves(roots_info):
            for i in range(len(roots_info)):
                children_sum_estimate = self.get_All_Children_Sum_Estimate(roots_info[i][0])
                estimate = roots_info[i][3]
                children = self.get_All_Children_Info_InitUDID(roots_info[i][0], roots_info[i][-1])
                try:
                    assert children
                    rate_estimate = float(children_sum_estimate) / float(estimate)
                except:
                    rate_estimate = None
                roots_info[i].insert(4, rate_estimate)
                roots_info[i] = [roots_info[i]]
                if children:
                    roots_info[i].append(children)
                    zipLeaves(children)
        zipLeaves(roots_info)
        return roots_info
    def get_All_Roots_Info_Initiation(self):
        conn, curs = self.newCurs()
        sql = 'SELECT 立项识别码, 项目名称, 分项名称, 项目概算, 0 FROM tabel_立项信息 WHERE 父项立项识别码 IS NULL'
        curs.execute(sql)
        result = curs.fetchall()
        conn.close()
        return list(map(list, result))
    def get_All_Children_Info_InitUDID(self, UDID, deep=0):
        conn, curs = self.newCurs()
        sql = 'SELECT 立项识别码, 项目名称, 分项名称, 项目概算, %s+1 FROM tabel_立项信息 WHERE 父项立项识别码=%s'
        curs.execute(sql, [deep, UDID])
        result = curs.fetchall()
        conn.close()
        return list(map(list, result))
    # Bidding
    def read_For_Bidding_GridDialog(self, where_sql='', where_list=[], order_sql='', order_list=[]):
        conn, curs = self.newCurs()
        sql = '''SELECT {} FROM 
                 (SELECT           招标识别码, A.立项识别码 AS 立项识别码, 项目名称, 分项名称, 招标方式, 招标单位识别码, 
                                   U1.单位名称 AS 招标单位名称, 招标代理识别码, U2.单位名称 AS 招标代理单位名称, 项目概算,
                                   预算控制价, 招标文件定稿时间, 公告邀请函发出时间, 开标时间, 中标通知书发出时间, 
                                   中标单位识别码, U3.单位名称 AS 中标单位名称, 中标价, 招标备注
                  FROM             tabel_招标信息 AS A
                       LEFT JOIN   tabel_立项信息 AS I ON A.立项识别码=I.立项识别码
                       LEFT JOIN   tabel_单位信息 AS U1 ON A.招标单位识别码=U1.单位识别码
                       LEFT JOIN   tabel_单位信息 AS U2 ON A.招标代理识别码=U2.单位识别码
                       LEFT JOIN   tabel_单位信息 AS U3 ON A.中标单位识别码=U3.单位识别码) AS Origin
              '''.format(', '.join(uc.BiddingColLabels)) + where_sql + ' ' + order_sql
        sql_list = where_list + order_list
        curs.execute(sql, sql_list)
        fetchall = curs.fetchall()
        conn.close()
        return fetchall
    def get_Init_Unit_List(self, UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT 建设单位识别码, 代建单位识别码 FROM tabel_立项信息 WHERE 立项识别码=%s'
        curs.execute(sql, [UDID])
        fetchall = curs.fetchall()
        conn.close()
        return list(fetchall[0])
    def save_For_Bidding_MaintainDialog(self, data=[]):
        if not data:
            return
        UDID, Init_UDID = data[0:2]
        price_budget, price_winner = data[uc.BiddingFields.index('预算控制价')], data[uc.BiddingFields.index('中标价')]
        has_Child = self.get_All_Children_Info_InitUDID(Init_UDID)
        if has_Child:
            dlg = wx.MessageDialog(None, message='请保证所选立项无子立项', caption='警告', style=wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        conn, curs = self.newCurs()
        sql = 'SELECT COUNT(*) FROM tabel_招标信息 WHERE 招标识别码=%s'
        curs.execute(sql, [UDID])
        isExist = curs.fetchall()[0][0]
        if (price_budget or 0.0) < (price_winner or 0.0):    #若控制价<中标价，则报警
            dlg = wx.MessageDialog(None, message='中标价不得高于预算控制价，请检查', caption='警告', style=wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        def insert_Data(data):
            sql = 'INSERT INTO tabel_招标信息 ({}) VALUES ({})'.format(', '.join(uc.BiddingFields), ', '.join(len(uc.BiddingFields)*['%s']))
            sql_list = data
            curs.execute(sql, sql_list)
        def update_Data(data):
            sql = 'UPDATE tabel_招标信息 SET {} WHERE 招标识别码=%s'.format('=%s, '.join(uc.BiddingFields[1:]) + '=%s ')
            sql_list = data[1:] + [data[0]]
            curs.execute(sql, sql_list)
        if isExist:
            other_prices_budget = self.get_Sum_of_Other_Prices_Budget(Init_UDID, UDID)
            estimate = self.get_Estimate(Init_UDID)
            if (estimate or 0.0) < float(other_prices_budget or 0.0) + float(price_budget or 0.0):    #若项目概算<同级控制价和，则报警
                dlg = wx.MessageDialog(None, message='同一立项下各招标预算控制价之和不得高于该项目概算<{:>,.2f}>，本项目允许的最高预算控制价为<{:>,.2f}>，请检查'.format(estimate, float((estimate or 0.0)) - float(other_prices_budget or 0.0)), caption='警告', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            update_Data(data)
        else:
            prices_budget = self.get_Sum_of_Prices_Budget(Init_UDID)
            estimate = self.get_Estimate(Init_UDID)
            if (estimate or 0.0) < float(prices_budget or 0.0) + float(price_budget or 0.0):    #若项目概算<同级控制价和，则报警
                dlg = wx.MessageDialog(None, message='同一立项下各招标预算控制价之和不得高于该项目概算<{:>,.2f}>，本项目允许的最高预算控制价为<{:>,.2f}>，请检查'.format(estimate, float((estimate or 0.0)) - float(prices_budget or 0.0)), caption='警告', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
            insert_Data(data)
        conn.commit()
        conn.close()
        return True
    def get_Sum_of_Prices_Budget(self, Init_UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT SUM(预算控制价) FROM tabel_招标信息 WHERE 立项识别码=%s'
        curs.execute(sql, [Init_UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0] or 0.0
        except:
            return
    def get_Sum_of_Other_Prices_Budget(self, Init_UDID, Bid_UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT SUM(预算控制价) FROM tabel_招标信息 WHERE 立项识别码=%s AND 招标识别码<>%s'
        curs.execute(sql, [Init_UDID, Bid_UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0] or 0.0
        except:
            return
    # TreeList-Bidding
    def format_Bidding_Details_By_Tree(self):
        # 得到全部根节点
        roots_info = self.get_All_Roots_Info_Bidding()
        # 访问这些根节点，取得每个根节点的所有子项，存入其中
        def zipLeaves(roots_info):
            for i in range(len(roots_info)):
                children_sum_estimate = self.get_All_Children_Sum_Estimate(roots_info[i][0])
                estimate = roots_info[i][4]
                children = self.get_All_Children_Info_BidUDID(roots_info[i][0], roots_info[i][-1])
                try:
                    assert children
                    rate_estimate = float(children_sum_estimate) / float(estimate)
                except:
                    rate_estimate = None
                roots_info[i].insert(5, rate_estimate)
                roots_info[i] = [roots_info[i]]
                if children:
                    roots_info[i].append(children)
                    zipLeaves(children)
        zipLeaves(roots_info)
        return roots_info
    def get_All_Roots_Info_Bidding(self):
        conn, curs = self.newCurs()
        sql = '''SELECT           I.立项识别码 AS 立项识别码, 项目名称, 分项名称, 招标方式, 项目概算, 预算控制价, 中标价, 0
                 FROM             (SELECT * FROM tabel_立项信息 WHERE 父项立项识别码 IS NULL) AS I
                       LEFT JOIN  tabel_招标信息 AS B ON I.立项识别码=B.立项识别码
              '''
        curs.execute(sql)
        result = curs.fetchall()
        conn.close()
        return list(map(list, result))
    def get_All_Children_Info_BidUDID(self, UDID, deep=0):
        conn, curs = self.newCurs()
        sql = '''SELECT           I.立项识别码 AS 立项识别码, 项目名称, 分项名称, 招标方式, 项目概算, 预算控制价, 中标价, %s+1
                 FROM             (SELECT * FROM tabel_立项信息 WHERE 父项立项识别码=%s) AS I
                       LEFT JOIN  tabel_招标信息 AS B ON I.立项识别码=B.立项识别码
              '''
        curs.execute(sql, [deep, UDID])
        result = curs.fetchall()
        conn.close()
        return list(map(list, result))
    # Contract
    def read_For_Contract_GridDialog(self, where_sql='', where_list=[], order_sql='', order_list=[]):
        conn, curs = self.newCurs()
        sql = '''SELECT {} FROM 
                 (SELECT           A.合同识别码, A.立项识别码, 项目名称, 分项名称, 项目概算, A.招标识别码, 招标方式, 合同编号, 合同名称,
                                   合同主要内容, 合同类别, 甲方识别码, U1.单位名称 AS 甲方单位名称, 乙方识别码, U2.单位名称 AS 乙方单位名称, 
                                   丙方识别码, U3.单位名称 AS 丙方单位名称, 丁方识别码, U4.单位名称 AS 丁方单位名称,
                                   中标价, 合同值_签订时, 合同值_最新值, 合同值_最终值, 
                                   已付款, 已付款/项目概算 AS 已付款占概算, 
                                   已付款/合同值_最新值 AS 已付款占合同, 形象进度, 支付上限, 合同签订时间, 
                                   开工时间, 竣工合格时间, 保修结束时间, 审计完成时间, 合同备注
                  FROM             tabel_合同信息 AS A
                       LEFT JOIN   tabel_立项信息 AS I ON A.立项识别码=I.立项识别码
                       LEFT JOIN   tabel_单位信息 AS U1 ON A.甲方识别码=U1.单位识别码
                       LEFT JOIN   tabel_单位信息 AS U2 ON A.乙方识别码=U2.单位识别码
                       LEFT JOIN   tabel_单位信息 AS U3 ON A.丙方识别码=U3.单位识别码
                       LEFT JOIN   tabel_单位信息 AS U4 ON A.丁方识别码=U3.单位识别码
                       LEFT JOIN   tabel_招标信息 AS B ON A.招标识别码=B.招标识别码
                       LEFT JOIN   (SELECT 合同识别码, SUM(本次付款额) AS 已付款 FROM tabel_付款信息 GROUP BY 合同识别码) AS P ON A.合同识别码=P.合同识别码) AS Origin
              '''.format(', '.join(uc.ContractColLabels)) + where_sql + ' ' + order_sql
        sql_list = where_list + order_list
        curs.execute(sql, sql_list)
        fetchall = curs.fetchall()
        conn.close()
        return fetchall
    def save_For_Contract_MaintainDialog(self, data=[]):
        if not data:
            return
        UDID, Init_UDID, Bidding_UDID = data[0:3]
        price_sign, price_last, price_final, price_limit = data[uc.ContractFields.index('合同值_签订时')] or 0, \
                  data[uc.ContractFields.index('合同值_最新值')] or 0, data[uc.ContractFields.index('合同值_最终值')] or 0, data[uc.ContractFields.index('支付上限')] or 0
        # 合法性检查
        has_Child = self.get_All_Children_Info_InitUDID(Init_UDID)
        if has_Child:
            dlg = wx.MessageDialog(None, message='请保证所选立项无子立项', caption='警告', style=wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if float(price_limit) > float(price_last):
            dlg = wx.MessageDialog(None, message='支付上限不得高于合同值_最新值，请检查', caption='警告', style=wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if Bidding_UDID:
            prices_sign  = self.get_Sum_of_Other_Prices_Sign_By_Bidding(Bidding_UDID, UDID)
            prices_last  = self.get_Sum_of_Other_Prices_Last_By_Bidding(Bidding_UDID, UDID)
            prices_final = self.get_Sum_of_Other_Prices_Final_By_Bidding(Bidding_UDID, UDID)
            price_winner = self.get_Price_Winner(Bidding_UDID)
            if float(prices_sign) + float(price_sign) > float(price_winner):    #若同级签约价和>中标价，则报警
                dlg = wx.MessageDialog(None, message='同一招标下各<合同价_签订时>之和不得高于中标价<{:>,.2f}>，本项目允许的最高<合同价_签订时>为<{:>,.2f}>，请检查'.format(float(price_winner), float(price_winner) - float(prices_sign)), caption='警告', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
        prices_sign  = self.get_Sum_of_Other_Prices_Sign_By_Init(Init_UDID, UDID)
        prices_last  = self.get_Sum_of_Other_Prices_Last_By_Init(Init_UDID, UDID)
        prices_final = self.get_Sum_of_Other_Prices_Final_By_Init(Init_UDID, UDID)
        estimate = self.get_Estimate(Init_UDID)
        if float(prices_sign) + float(price_sign) > float(estimate):    #若同级签约价和>项目概算，则报警
            dlg = wx.MessageDialog(None, message='同一招标下各<合同价_签订时>之和不得高于项目概算<{:>,.2f}>，本项目允许的最高<合同价_签订时>为<{:>,.2f}>，请检查'.format(float(estimate), float(estimate) - float(prices_sign)), caption='警告', style=wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if float(prices_last) + float(price_last) > float(estimate):    #若同级最新价和>项目概算，则报警
            dlg = wx.MessageDialog(None, message='同一招标下各<合同价_最新价>之和不得高于项目概算<{:>,.2f}>，本项目允许的最高<合同价_最新价>为<{:>,.2f}>，请检查'.format(float(estimate), float(estimate) - float(prices_last)), caption='警告', style=wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if float(prices_final) + float(price_last) > float(estimate):    #若同级最终价和>项目概算，则报警
            dlg = wx.MessageDialog(None, message='同一招标下各<合同价_最终价>之和不得高于项目概算<{:>,.2f}>，本项目允许的最高<合同价_最终价>为<{:>,.2f}>，请检查'.format(float(estimate), float(estimate) - float(prices_final)), caption='警告', style=wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        # 插入/更新？
        conn, curs = self.newCurs()
        sql = 'SELECT COUNT(*) FROM tabel_合同信息 WHERE 合同识别码=%s'
        curs.execute(sql, [UDID])
        isExist = curs.fetchall()[0][0]
        def insert_Data(data):
            sql = 'INSERT INTO tabel_合同信息 ({}) VALUES ({})'.format(', '.join(uc.ContractFields), ', '.join(len(uc.ContractFields)*['%s']))
            sql_list = data
            curs.execute(sql, sql_list)
        def update_Data(data):
            sql = 'UPDATE tabel_合同信息 SET {} WHERE 合同识别码=%s'.format('=%s, '.join(uc.ContractFields[1:]) + '=%s ')
            sql_list = data[1:] + [data[0]]
            curs.execute(sql, sql_list)
        if isExist:
            update_Data(data)
        else:            
            insert_Data(data)
        conn.commit()
        conn.close()
        return True
    def get_Bidding_Unit_List(self, UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT 招标单位识别码 FROM tabel_招标信息 WHERE 招标识别码=%s'
        curs.execute(sql, [UDID])
        fetchall = curs.fetchall()
        conn.close()
        return list(fetchall[0])
    def get_Bidding_Winner_Unit_List(self, UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT 中标单位识别码 FROM tabel_招标信息 WHERE 招标识别码=%s'
        curs.execute(sql, [UDID])
        fetchall = curs.fetchall()
        conn.close()
        return list(fetchall[0])
    def get_Sum_of_Prices_Sign_By_Init(self, UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT SUM(合同值_签订时) FROM tabel_合同信息 WHERE 立项识别码=%s'
        curs.execute(sql, [UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0] or 0.0
        except:
            return
    def get_Sum_of_Prices_Sign_By_Bidding(self, UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT SUM(合同值_签订时) FROM tabel_合同信息 WHERE 招标识别码=%s'
        curs.execute(sql, [UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0] or 0.0
        except:
            return
    def get_Sum_of_Prices_Last_By_Init(self, UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT SUM(合同值_最新值) FROM tabel_合同信息 WHERE 立项识别码=%s'
        curs.execute(sql, [UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0] or 0.0
        except:
            return
    def get_Sum_of_Prices_Last_By_Bidding(self, UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT SUM(合同值_最新值) FROM tabel_合同信息 WHERE 招标识别码=%s'
        curs.execute(sql, [UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0] or 0.0
        except:
            return
    def get_Sum_of_Prices_Final_By_Init(self, UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT SUM(合同值_最终值) FROM tabel_合同信息 WHERE 立项识别码=%s'
        curs.execute(sql, [UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0] or 0.0
        except:
            return
    def get_Sum_of_Prices_Final_By_Bidding(self, UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT SUM(合同值_最终值) FROM tabel_合同信息 WHERE 招标识别码=%s'
        curs.execute(sql, [UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0] or 0.0
        except:
            return    
    def get_Sum_of_Other_Prices_Sign_By_Init(self, Init_UDID, Contract_UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT SUM(合同值_签订时) FROM tabel_合同信息 WHERE 立项识别码=%s AND 合同识别码<>%s'
        curs.execute(sql, [Init_UDID, Contract_UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0] or 0.0
        except:
            return
    def get_Sum_of_Other_Prices_Sign_By_Bidding(self, Bid_UDID, Contract_UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT SUM(合同值_签订时) FROM tabel_合同信息 WHERE 招标识别码=%s AND 合同识别码<>%s'
        curs.execute(sql, [Bid_UDID, Contract_UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0] or 0.0
        except:
            return
    def get_Sum_of_Other_Prices_Last_By_Init(self, Init_UDID, Contract_UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT SUM(合同值_最新值) FROM tabel_合同信息 WHERE 立项识别码=%s AND 合同识别码<>%s'
        curs.execute(sql, [Init_UDID, Contract_UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0] or 0.0
        except:
            return
    def get_Sum_of_Other_Prices_Last_By_Bidding(self, Bid_UDID, Contract_UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT SUM(合同值_最新值) FROM tabel_合同信息 WHERE 招标识别码=%s AND 合同识别码<>%s'
        curs.execute(sql, [Bid_UDID, Contract_UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0] or 0.0
        except:
            return
    def get_Sum_of_Other_Prices_Final_By_Init(self, Init_UDID, Contract_UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT SUM(合同值_最终值) FROM tabel_合同信息 WHERE 立项识别码=%s AND 合同识别码<>%s'
        curs.execute(sql, [Init_UDID, Contract_UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0] or 0.0
        except:
            return
    def get_Sum_of_Other_Prices_Final_By_Bidding(self, Bid_UDID, Contract_UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT SUM(合同值_最终值) FROM tabel_合同信息 WHERE 招标识别码=%s AND 合同识别码<>%s'
        curs.execute(sql, [Bid_UDID, Contract_UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0] or 0.0
        except:
            return
    def get_Price_Winner(self, Bidding_UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT 中标价 FROM tabel_招标信息 WHERE 招标识别码=%s'
        curs.execute(sql, [Bidding_UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0] or 0.0
        except:
            return
    # TreeList-Contract
    def format_Contract_Details_By_Tree(self):
        # 得到全部根节点
        roots_info = self.get_All_Roots_Info_Contract()
        # 访问这些根节点，取得每个根节点的所有子项，存入其中
        def zipLeaves(roots_info):
            for i in range(len(roots_info)):
                children_sum_estimate = self.get_All_Children_Sum_Estimate(roots_info[i][0])
                estimate = roots_info[i][4]
                children = self.get_All_Children_Info_ContractUDID(roots_info[i][0], roots_info[i][-1])
                try:
                    assert children
                    rate_estimate = float(children_sum_estimate) / float(estimate)
                except:
                    rate_estimate = None
                roots_info[i].insert(5, rate_estimate)
                roots_info[i] = [roots_info[i]]
                if children:
                    roots_info[i].append(children)
                    zipLeaves(children)
        zipLeaves(roots_info)
        return roots_info
    def get_All_Roots_Info_Contract(self):
        conn, curs = self.newCurs()
        sql = '''SELECT           I.立项识别码 AS 立项识别码, 项目名称, 分项名称, 合同名称, 项目概算, 已付款/项目概算 AS 概算付款比, 
                                  招标方式, 中标价, 合同值_最新值, 已付款/合同值_最新值 AS 合同付款比, 已付款, 0
                 FROM             (SELECT * FROM tabel_立项信息 WHERE 父项立项识别码 IS NULL) AS I
                       LEFT JOIN  tabel_招标信息 AS B ON I.立项识别码=B.立项识别码
                       LEFT JOIN  tabel_合同信息 AS C ON I.立项识别码=C.立项识别码
                       LEFT JOIN  (SELECT 立项识别码, SUM(本次付款额) AS 已付款 FROM tabel_付款信息 GROUP BY 立项识别码) AS P ON I.立项识别码=P.立项识别码
              '''
        curs.execute(sql)
        result = list(map(list, curs.fetchall()))
        for i in range(len(result)):
            InitUDID = result[i][0]
            estimate = result[i][4]
            AGC = self.get_All_Grandchildren(InitUDID)    # All Grandchildren
            if not AGC:
                continue
            sql = '''SELECT SUM(本次付款额) FROM tabel_付款信息 WHERE 立项识别码 IN %s'''
            sql_list = [AGC]
            curs.execute(sql, sql_list)
            payed = decimal.Decimal(curs.fetchall()[0][0] or 0)
            try:
                result[i][5] = payed / estimate
            except:
                pass
        conn.close()
        return result
    def get_All_Children_Info_ContractUDID(self, UDID, deep=0):
        conn, curs = self.newCurs()
        sql = '''SELECT           I.立项识别码 AS 立项识别码, 项目名称, 分项名称, 合同名称, 项目概算, 已付款/项目概算 AS 概算付款比, 
                                  招标方式, 中标价, 合同值_最新值, 已付款/合同值_最新值 AS 合同付款比, 已付款, %s+1
                 FROM             (SELECT * FROM tabel_立项信息 WHERE 父项立项识别码=%s) AS I
                       LEFT JOIN  tabel_招标信息 AS B ON I.立项识别码=B.立项识别码
                       LEFT JOIN  tabel_合同信息 AS C ON I.立项识别码=C.立项识别码
                       LEFT JOIN  (SELECT 立项识别码, SUM(本次付款额) AS 已付款 FROM tabel_付款信息 GROUP BY 立项识别码) AS P ON I.立项识别码=P.立项识别码
              '''
        curs.execute(sql, [deep, UDID])
        result = list(map(list, curs.fetchall()))
        for i in range(len(result)):
            InitUDID = result[i][0]
            estimate = result[i][4]
            AGC = self.get_All_Grandchildren(InitUDID)    # All Grandchildren
            if not AGC:
                continue
            sql = '''SELECT SUM(本次付款额) FROM tabel_付款信息 WHERE 立项识别码 IN %s'''
            sql_list = [AGC]
            curs.execute(sql, sql_list)
            payed = decimal.Decimal(curs.fetchall()[0][0] or 0)
            try:
                result[i][5] = payed / estimate
            except:
                pass
        conn.close()
        return result
    # Budget
    def read_For_Budget_GridDialog(self, where_sql='', where_list=[], order_sql='', order_list=[]):
        conn, curs = self.newCurs()
        sql = '''SELECT {} FROM 
                 (SELECT           A.预算识别码, A.父项预算识别码, B.预算名称 AS 父项预算名称, A.预算名称, A.预算周期, A.预算总额,
                                   已付款 AS 预算已付额, A.预算总额-已付款 AS 预算余额, 已付款/A.预算总额 AS 预算已付比,
                                   A.预算备注
                  FROM             tabel_预算信息 AS A
                       LEFT JOIN   tabel_预算信息 AS B ON A.父项预算识别码=B.预算识别码
                       LEFT JOIN   (SELECT 预算识别码, SUM(本次付款额) AS 已付款 FROM tabel_付款信息 GROUP BY 预算识别码) AS P ON A.预算识别码=P.预算识别码) AS Origin
              '''.format(', '.join(uc.BudgetColLabels)) + where_sql + ' ' + order_sql
        sql_list = where_list + order_list
        curs.execute(sql, sql_list)
        fetchall = curs.fetchall()
        conn.close()
        return fetchall
    def save_For_Budget_MaintainDialog(self, data=[]):
        if not data:
            return
        UDID, parent_UDID, budget_name, budget_period, budget_total, budget_note = data
        # 合法性检查
        if parent_UDID:
            budget = float(data[uc.BudgetFields.index('预算总额')] or 0.0)
            brothers_sum_budget = float(self.get_All_Children_Sum_Budgets_Without_One(parent_UDID, UDID or 0) or 0.0)
            parent_budget = float(self.get_Budget(parent_UDID) or 0.0)
            if budget + brothers_sum_budget > parent_budget:
                dlg = wx.MessageDialog(None, message='本预算及其兄弟的预算和超出父项预算，本项目允许的最高预算为：{:>,.2f}，请检查'.format(float(parent_budget) - float(brothers_sum_budget)), caption='警告', style=wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
                return
        conn, curs = self.newCurs()
        sql = 'SELECT COUNT(*) FROM tabel_预算信息 WHERE 预算识别码=%s'
        curs.execute(sql, [UDID])
        isExist = curs.fetchall()[0][0]
        def insert_Data(data):
            sql = 'INSERT INTO tabel_预算信息 ({}) VALUES ({})'.format(', '.join(uc.BudgetFields), ', '.join(len(uc.BudgetFields)*['%s']))
            sql_list = data
            curs.execute(sql, sql_list)
        def update_Data(data):
            sql = 'UPDATE tabel_预算信息 SET {} WHERE 预算识别码=%s'.format('=%s, '.join(uc.BudgetFields[1:]) + '=%s ')
            sql_list = data[1:] + [data[0]]
            curs.execute(sql, sql_list)
        if isExist:
            update_Data(data)
        else:
            insert_Data(data)
        conn.commit()
        conn.close()
        return True
    def get_Parent_BudgetUDID(self, UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT 父项预算识别码 FROM tabel_预算信息 WHERE 预算识别码=%s'
        curs.execute(sql, [UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0]
        except:
            return
    def get_Budget(self, UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT 预算总额 FROM tabel_预算信息 WHERE 预算识别码=%s'
        curs.execute(sql, [UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0]
        except:
            return
    def get_All_Children_Sum_Budgets_Without_One(self, parent_UDID, UDID):
        conn, curs = self.newCurs()
        sql = 'SELECT SUM(预算总额) FROM tabel_预算信息 WHERE 父项预算识别码=%s AND 预算识别码<>%s'
        curs.execute(sql, [parent_UDID, UDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0]
        except:
            return
    # TreeList-Budget
    def format_Budget_Details_By_Tree(self):
        '取得含预存识别码、预算名称、预算周期、层级的树形序列'
        # 得到全部根节点
        roots_info = self.get_All_Roots_Info_Budget()
        # 访问这些根节点，取得每个根节点的所有子项，存入其中
        def zipLeaves(roots_info):
            for i in range(len(roots_info)):
                children_sum_budget = self.get_All_Children_Sum_Budget(roots_info[i][0])
                budget = roots_info[i][3]
                children = self.get_All_Children_Info_BudgetUDID(roots_info[i][0], roots_info[i][-1])
                try:
                    assert children
                    rate_budget = float(children_sum_budget) / float(budget)
                except:
                    rate_budget = None
                roots_info[i].insert(4, rate_budget)
                roots_info[i] = [roots_info[i]]
                if children:
                    roots_info[i].append(children)
                    zipLeaves(children)
        zipLeaves(roots_info)
        return roots_info
    def get_All_Roots_Info_Budget(self):
        conn, curs = self.newCurs()
        sql = 'SELECT 预算识别码, 预算名称, 预算周期, 预算总额, 0 FROM tabel_预算信息 WHERE 父项预算识别码 IS NULL'
        curs.execute(sql)
        result = curs.fetchall()
        conn.close()
        return list(map(list, result))
    def get_All_Children_Info_BudgetUDID(self, BudgetUDID, deep=0):
        conn, curs = self.newCurs()
        sql = 'SELECT 预算识别码, 预算名称, 预算周期, 预算总额, %s+1 FROM tabel_预算信息 WHERE 父项预算识别码=%s'
        curs.execute(sql, [deep, BudgetUDID])
        result = curs.fetchall()
        conn.close()
        return list(map(list, result))
    def get_All_Children_Sum_Budget(self, BudgetUDID):
        conn, curs = self.newCurs()
        sql = 'SELECT sum(预算总额) FROM tabel_预算信息 WHERE 父项预算识别码=%s'
        curs.execute(sql, [BudgetUDID])
        result = curs.fetchall()
        conn.close()
        try:
            return result[0][0] or 0.0
        except:
            return
    # Payment
    def read_For_Payment_GridDialog(self, where_sql='', where_list=[], order_sql='', order_list=[]):
        conn, curs = self.newCurs()
        sql = '''SELECT {} FROM 
                 (SELECT           A.付款识别码, 付款登记时间, 付款支付时间, A.立项识别码, I.项目名称, I.分项名称,
                                   A.合同识别码, 合同名称, 合同类别, 合同编号, 付款批次, 付款事由,
                                   A.付款单位识别码, U1.单位名称 AS 付款单位名称, U1.银行账号 AS 付款单位账号,
                                   A.收款单位识别码, U2.单位名称 AS 收款单位名称, U2.银行账号 AS 收款单位账号,
                                   A.预算识别码, 预算名称, 预算周期, 付款时预算总额, 付款时项目概算, 付款时合同付款上限,
                                   付款时合同值, 付款时预算余额, 付款时概算余额, 付款时合同可付余额, 付款时合同未付额,
                                   付款时预算已付额, 付款时合同已付额, 付款时概算已付额,
                                   付款时预算已付额/付款时预算总额 AS 付款时预算已付比,
                                   付款时合同已付额/付款时合同值 AS 付款时合同已付比, 
                                   付款时概算已付额/付款时项目概算 AS 付款时概算已付比,
                                   付款时形象进度, 本次付款额,
                                   本次付款额/付款时预算总额 AS 预算本次付款比,
                                   本次付款额/付款时合同值 AS 合同本次付款比,
                                   本次付款额/付款时项目概算 AS 概算本次付款比,
                                   (本次付款额+付款时预算已付额)/付款时预算总额 AS 预算累付比,
                                   (本次付款额+付款时合同已付额)/付款时合同值 AS 合同累付比,
                                   (本次付款额+付款时概算已付额)/付款时项目概算 AS 概算累付比,
                                   付款备注
                  FROM             tabel_付款信息 AS A
                        LEFT JOIN  tabel_立项信息 AS I ON A.立项识别码=I.立项识别码
                        LEFT JOIN  tabel_合同信息 AS C ON A.合同识别码=C.合同识别码
                        LEFT JOIN  (SELECT 立项识别码, 付款识别码, convert(rank , SIGNED) AS 付款批次
                                    FROM (SELECT ff.立项识别码, ff.付款识别码, IF(@pa = ff.立项识别码, @rank:=@rank + 1, @rank:=1) AS rank, @pa:=ff.立项识别码
                                          FROM   (SELECT 立项识别码, 付款识别码
                                                  FROM   tabel_付款信息
                                                  GROUP BY 立项识别码 , 付款识别码
                                                  ORDER BY 立项识别码 , 付款识别码) ff, (SELECT @rank:=0, @pa := NULL) tt) result) AS BP ON A.付款识别码=BP.付款识别码
                        LEFT JOIN  tabel_单位信息 AS U1 ON A.付款单位识别码=U1.单位识别码
                        LEFT JOIN  tabel_单位信息 AS U2 ON A.收款单位识别码=U2.单位识别码
                        LEFT JOIN  tabel_预算信息 AS B ON A.预算识别码=B.预算识别码) AS Origin
              '''.format(', '.join(uc.PaymentColLabels)) + where_sql + ' ' + order_sql
        sql_list = where_list + order_list
        curs.execute(sql, sql_list)
        result = curs.fetchall()
        conn.close()
        return result
    def save_For_Payment_MaintainDialog(self, data=[]):
        if not data:
            return
        UDID = data[0]
        # 插入/更新？
        conn, curs = self.newCurs()
        sql = 'SELECT COUNT(*) FROM tabel_付款信息 WHERE 付款识别码=%s'
        curs.execute(sql, [UDID])
        isExist = curs.fetchall()[0][0]
        def insert_Data(data):
            sql = 'INSERT INTO tabel_付款信息 ({}) VALUES ({})'.format(', '.join(uc.PaymentFields), ', '.join(len(uc.PaymentFields)*['%s']))
            sql_list = data
            curs.execute(sql, sql_list)
        def update_Data(data):
            sql = 'UPDATE tabel_付款信息 SET {} WHERE 付款识别码=%s'.format('=%s, '.join(uc.PaymentFields[1:]) + '=%s ')
            sql_list = data[1:] + [data[0]]
            curs.execute(sql, sql_list)
        if isExist:
            update_Data(data)
        else:            
            insert_Data(data)
        conn.commit()
        conn.close()
        return True
    def get_Payment_Batch(self, Payment_UDID, Init_UDID):
        conn, curs = self.newCurs()
        # 如果Payment_UDID存在（更新时）
        # 如果Payment_UDID不存在（新建时），batch=max(该立项下付款数+1)
        if Payment_UDID:
            sql = 'SELECT COUNT(*) FROM tabel_付款信息 WHERE 付款识别码<=%s AND 立项识别码=%s'
            sql_list = [Payment_UDID, Init_UDID]
        else:
            sql = 'SELECT COUNT(*)+1 FROM tabel_付款信息 WHERE 立项识别码=%s'
            sql_list = [Init_UDID]
        curs.execute(sql, sql_list)
        fetchall = curs.fetchall()
        conn.close()
        return fetchall[0][0]
    def get_Pro_and_Subpro_and_Estimate(self, UDID):
        conn, curs = self.newCurs()
        sql = '''SELECT 项目名称, 分项名称, 项目概算 FROM tabel_立项信息 WHERE 立项识别码=%s'''
        sql_list = [UDID]
        curs.execute(sql, sql_list)
        fetchall = curs.fetchall()
        conn.close()
        return fetchall[0]
    def get_Estimate_Payed(self, UDID):
        conn, curs = self.newCurs()
        sql = '''SELECT SUM(本次付款额) FROM tabel_付款信息 WHERE 立项识别码=%s'''
        sql_list = [UDID]
        curs.execute(sql, sql_list)
        fetchall = curs.fetchall()
        conn.close()
        return fetchall[0][0] or 0.0
    def get_Budget_Payed(self, BudgetUDID):
        conn, curs = self.newCurs()
        sql = '''SELECT SUM(本次付款额) FROM tabel_付款信息 WHERE 预算识别码=%s'''
        sql_list = [BudgetUDID]
        curs.execute(sql, sql_list)
        fetchall = curs.fetchall()
        conn.close()
        return fetchall[0][0] or 0.0
    def get_Contract_Payed(self, ContractUDID):
        conn, curs = self.newCurs()
        sql = '''SELECT SUM(本次付款额) FROM tabel_付款信息 WHERE 合同识别码=%s'''
        sql_list = [ContractUDID]
        curs.execute(sql, sql_list)
        fetchall = curs.fetchall()
        conn.close()
        return fetchall[0][0] or 0.0
    def get_Contract_Unit_List(self, ContractUDID):
        conn, curs = self.newCurs()
        sql = 'SELECT 甲方识别码, 乙方识别码, 丙方识别码, 丁方识别码 FROM tabel_合同信息 WHERE 合同识别码=%s'
        curs.execute(sql, [ContractUDID])
        fetchall = curs.fetchall()
        conn.close()
        return list(fetchall[0])
    # TreeList-Payment
    def get_All_Grandchildren(self, UDIDs):
        '取得某项下全部子项、孙项等的立项识别码'
        def OneStep(UDIDs):
            if str(type(UDIDs)) != "<class 'list'>":
                UDIDs = [UDIDs]
            conn, curs = self.newCurs()
            sql = '''SELECT 立项识别码 FROM tabel_立项信息 WHERE 父项立项识别码 IN %s'''
            sql_list = [UDIDs]
            curs.execute(sql, sql_list)
            fetchall = list(map(lambda x:x[0], curs.fetchall()))
            conn.close()
            if fetchall:
                self.GAG_result.extend(fetchall)
                return OneStep(fetchall)
        self.GAG_result = []
        OneStep(UDIDs)
        return self.GAG_result
    # Chart
    def get_Pie_Data(self, UDID):
        info = operateDB().read_For_Initiation_GridDialog('WHERE 立项识别码=%s', [UDID])
        if info:
            title = '<%s%s>概算分配' % (info[0][uc.InitiationColLabels.index('项目名称')], info[0][uc.InitiationColLabels.index('分项名称')] or '')
            estimate = info[0][uc.InitiationColLabels.index('项目概算')]
        else:
            title = ''
            estimate = 0
        children_Infos = self.get_All_Children_Info_InitUDID(UDID)
        if children_Infos:    # 枝节点
            labels, sizes = list(zip(*children_Infos))[2:4]
            labels = list(labels) + ['未分配']
            if estimate:
                sizes = list(map(lambda x: x/estimate, list(sizes)))
                sizes = sizes + [1 - sum(sizes)]
            else:
                sizes = list(map(lambda x: 0, list(sizes))) + [0]
            explode = [0] * (len(labels) - 1) + [0.2]
            if sizes[-1] < 0.0001:
                labels.pop()
                sizes.pop()
                explode.pop()
        else:                 # 叶节点
            Payment_Infos = operateDB().read_For_Payment_GridDialog('WHERE 立项识别码=%s', [UDID])
            Payment_Infos = list(map(list, list(zip(*Payment_Infos))))
            try:
                labels = list(map(lambda x, y: '%d-%s' % (x, y), Payment_Infos[uc.PaymentColLabels.index('付款批次')], Payment_Infos[uc.PaymentColLabels.index('付款事由')])) + ['未付款']
                sizes = Payment_Infos[uc.PaymentColLabels.index('概算本次付款比')]
                sizes = sizes + [1-sum(sizes)]
                explode = [0] * (len(labels) - 1) + [0.2]
            except:
                labels = ['']
                sizes = [1]
                explode = [0]
            if sizes[-1] < 0.0001:
                labels.pop()
                sizes.pop()
                explode.pop()
        return (labels, sizes, explode, title)
    # TextInfo
    def get_Init_Leaf_Payed(self, UDID):
    	conn, curs = self.newCurs()
    	sql = '''SELECT SUM(本次付款额), COUNT(本次付款额) FROM tabel_付款信息 WHERE 立项识别码=%s'''
    	sql_list = [UDID]
    	curs.execute(sql, sql_list)
    	fetchall = curs.fetchall()[0]
    	conn.close()
    	return fetchall
    def get_Init_Branch_Payed(self, UDID):
    	All_Children_UDID = operateDB().get_All_Grandchildren(UDID)
    	conn, curs = self.newCurs()
    	sql = '''SELECT SUM(本次付款额), COUNT(本次付款额) FROM tabel_付款信息 WHERE 立项识别码 IN %s'''
    	sql_list = [All_Children_UDID]
    	curs.execute(sql, sql_list)
    	fetchall = curs.fetchall()[0]
    	conn.close()
    	return fetchall

class CpitalNumber():  
    cdict={}  
    gdict={}  
    xdict={}  
    def __init__(self):
        self.cdict={1:u'',2:u'拾',3:u'佰',4:u'仟'}  
        self.xdict={1:u'元',2:u'万',3:u'亿',4:u'兆'} #数字标识符  
        self.gdict={0:u'零',1:u'壹',2:u'贰',3:u'叁',4:u'肆',5:u'伍',6:u'陆',7:u'柒',8:u'捌',9:u'玖'}
    def csplit(self,cdata): #拆分函数，将整数字符串拆分成[亿，万，仟]的list  
        g=len(cdata)%4  
        csdata=[]  
        lx=len(cdata)-1  
        if g>0:  
            csdata.append(cdata[0:g])  
        k=g  
        while k<=lx:  
            csdata.append(cdata[k:k+4])  
            k+=4  
        return csdata      
    def cschange(self,cki): #对[亿，万，仟]的list中每个字符串分组进行大写化再合并  
        lenki=len(cki)  
        i=0  
        lk=lenki  
        chk=u''  
        for i in range(lenki):  
            if int(cki[i])==0:  
                if i<lenki-1:  
                    if int(cki[i+1])!=0:  
                        chk=chk+self.gdict[int(cki[i])]                      
            else:  
                chk=chk+self.gdict[int(cki[i])]+self.cdict[lk]  
            lk-=1  
        return chk          
    def ChangeNum(self, data):
        cdata=str(data).split('.')  
        cki=cdata[0]  
        ckj=cdata[1]  
        i=0  
        chk=u''  
        cski=self.csplit(cki) #分解字符数组[亿，万，仟]三组List:['0000','0000','0000']  
        ikl=len(cski) #获取拆分后的List长度  
        #大写合并  
        for i in range(ikl):  
            if self.cschange(cski[i])=='': #有可能一个字符串全是0的情况  
                chk=chk+self.cschange(cski[i]) #此时不需要将数字标识符引入  
            else:  
                chk=chk+self.cschange(cski[i])+self.xdict[ikl-i] #合并：前字符串大写+当前字符串大写+标识符  
        #处理小数部分  
        lenkj=len(ckj)  
        if lenkj==1: #若小数只有1位  
            if int(ckj[0])==0:   
                chk=chk+u'整'  
            else:  
                chk=chk+self.gdict[int(ckj[0])]+u'角整'  
        else: #若小数有两位的四种情况  
            if int(ckj[0])==0 and int(ckj[1])!=0:  
                chk=chk+u'零'+self.gdict[int(ckj[1])]+u'分'  
            elif int(ckj[0])==0 and int(ckj[1])==0:  
                chk=chk+u'整'  
            elif int(ckj[0])!=0 and int(ckj[1])!=0:  
                chk=chk+self.gdict[int(ckj[0])]+u'角'+self.gdict[int(ckj[1])]+u'分'  
            else:  
                chk=chk+self.gdict[int(ckj[0])]+u'角整'  
        return chk  

class Exporter():
    def __init__(self):
        pass
    def setFormat(self, work_name, fontname='微软雅黑', fontsize=8, fontcolor=None, fontbold=False,
                  fontitalic=False, fontunderline=0, format_style=0x00, ifwarp=True, Halignstyle='justify',
                  Valignstyle='vcenter', setindent=0, setshrink=False, setborder=0, settop=0,
                  setbottom=0, setleft=0, setright=0
                  ):
        f = work_name.add_format({
            'font_name': fontname,
            'font_size': fontsize,
            'font_color': fontcolor,
            'bold': fontbold,
            'italic':fontitalic,
            'text_wrap':ifwarp
                                 })
        f.set_underline(fontunderline)     #1 = Single underline (the default)、2 = Double underline、33 = Single accounting underline、34 = Double accounting underline
        f.set_num_format(format_style)
        f.set_align(Halignstyle)           #center、right、fill、justify、center_across
        f.set_align(Valignstyle)           #top、vcenter、bottom、vjustify
        f.set_indent(setindent)            #设置缩进
        f.set_shrink(setshrink)            #文本自动收缩适合列宽
        #设置格线
        if setborder:
            f.set_border(setborder)
        else:
            f.set_top(settop)
            f.set_bottom(setbottom)
            f.set_left(setleft)
            f.set_right(setright)
        return f
    def commonExport(self, filename, grid, colLabels=[], datas={}):
        if os.path.exists(filename):
            dlg = wx.MessageDialog(None, message='已存在同名文件，确认要覆盖吗？', caption='提示', style= wx.YES_NO | wx.NO_DEFAULT)
            if dlg.ShowModal() == wx.ID_NO:
                return
            dlg.Destroy()
        rownum, colnum = max(datas.keys())[0] + 1, max(datas.keys())[1] + 1
        with xlsxwriter.Workbook(filename) as workbook:
            worksheet = workbook.add_worksheet()
            format_Label = self.setFormat(workbook, fontbold=True, setborder=1, Halignstyle='center')
            format_Str = self.setFormat(workbook, setborder=1, Halignstyle='center')
            format_Int = self.setFormat(workbook, setborder=1, format_style=0x03, Halignstyle='center')
            format_Float = self.setFormat(workbook, setborder=1, format_style=0x04, Halignstyle='right')
            format_Date = self.setFormat(workbook, setborder=1, format_style=0x0e, Halignstyle='center')
            format_YearMonth = self.setFormat(workbook, setborder=1)
            format_Dict = {"<class 'decimal.Decimal'>": format_Float,
                           "<class 'float'>":           format_Float,
                           "<class 'int'>":             format_Int,
                           "<class 'datetime.date'>":   format_Date,
                           "<class 'NoneType'>":        format_Str,
                           "<class 'str'>":             format_Str
                          }
            worksheet.write_row(0, 0, colLabels, format_Label)
            for col in range(colnum):
                data = []
                for row in range(rownum):
                    data.append(datas[row, col])
                typeData = str(type(data[0]))
                worksheet.write_column(1, col, data, format_Dict[typeData])
    def docx_Contract_Export(self, OutputFile=None, ContractDict={}):
        OriginalFile = os.getcwd() + '\\countersign\\Contract.docx'
        OutputFile = OutputFile or os.getcwd() + '\\countersign\\1.docx'
        def SaveNewDoc():
            import win32com
            from win32com.client import Dispatch, constants
            w = win32com.client.Dispatch('Word.Application')
            w.Visible = 0
            w.DisplayAlerts = 0
            doc = w.Documents.Open(OriginalFile)
            w.Selection.Find.ClearFormatting()
            w.Selection.Find.Replacement.ClearFormatting()
            def repalaceWord(key):
                w.Selection.Find.Execute('{<%s>}' % key, False, False, False, False, False, True, 1, True, ContractDict.get(key) or '', 2)
            repalaceWord('合同名称')
            repalaceWord('合同编号')
            repalaceWord('甲方单位名称')
            repalaceWord('乙方单位名称')
            repalaceWord('提交日期')
            repalaceWord('合同主要内容')
            repalaceWord('合同值_签订时')
            repalaceWord('履行期限')
            w.ActiveDocument.SaveAs(FileName=OutputFile)
            doc.Close()
            w.Quit()
        SaveNewDoc()
    def docx_Payment_Export(self, OutputFile=None, ContractDict={}):
        OriginalFile = os.getcwd() + '\\countersign\\Payment.docx'
        OutputFile = OutputFile or os.getcwd() + '\\countersign\\1.docx'
        def SaveNewDoc():
            import win32com
            from win32com.client import Dispatch, constants
            w = win32com.client.Dispatch('Word.Application')
            w.Visible = 0
            w.DisplayAlerts = 0
            doc = w.Documents.Open(OriginalFile)
            w.Selection.Find.ClearFormatting()
            w.Selection.Find.Replacement.ClearFormatting()
            def repalaceWord(key):
                w.Selection.Find.Execute('{<%s>}' % key, False, False, False, False, False, True, 1, True, ContractDict.get(key) or '', 2)
            repalaceWord('付款事由')
            repalaceWord('收款单位名称')
            repalaceWord('本次付款额')
            repalaceWord('合同名称')
            repalaceWord('合同编号')
            repalaceWord('付款时合同值')
            repalaceWord('付款时合同已付额')
            repalaceWord('付款时合同已付比')
            repalaceWord('合同本次付款比')
            repalaceWord('合同累付比')
            repalaceWord('提交日期')
            w.ActiveDocument.SaveAs(FileName=OutputFile)
            doc.Close()
            w.Quit()
        SaveNewDoc()

class operateOSS():
    def __init__(self):
        auth = oss2.Auth('LTAIiM9nh4F41qKR', 'FIWNICi6h6mJxaPFz5nU4Zu32yraIn')
        service = oss2.Service(auth, 'http://oss-cn-shanghai.aliyuncs.com')
        print([b.name for b in oss2.BucketIterator(service)])

if __name__ == '__main__':
    # print(Exporter().docx_Payment_Export(ContractDict={'付款事由':'进度款', '合同累付比':'90.00%'}))
    # print(CpitalNumber().ChangeNum((35732151.15)))
    operateOSS()
    pass