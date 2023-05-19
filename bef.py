import pandas as pd
import numpy as np
from jqdata import jy
import jqdata

# 初始化函数，设定基准等等
def initialize(context):
    # 设定沪深300作为基准
    set_benchmark('000300.XSHG')
    # 开启动态复权模式(真实价格)
    set_option('use_real_price', True)
    # 输出内容到日志 log.info()
    log.info('初始函数开始运行且全局只运行一次')
    # 过滤掉order系列API产生的比error级别低的log
    # log.set_level('order', 'error')
    #策略参数设置
    #行业统计天数
    g.days = 10
    #运行天数
    g.trade_days = 0
    #行业内最大持仓股数
    g.max_hold_stocknum = 5
    #操作的股票列表
    g.buy_list = []
    #标记是否交易
    g.trade = False
    ### 股票相关设定 ###
    # 股票类每笔交易时的手续费是：买入时佣金万分之三，卖出时佣金万分之三加千分之一印花税, 每笔交易佣金最低扣5块钱
    set_order_cost(OrderCost(close_tax=0.001, open_commission=0.0003, close_commission=0.0003, min_commission=5), type='stock')
