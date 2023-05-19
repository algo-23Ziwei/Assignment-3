 # 每月第一个交易日进行操作
    # 开盘前运行
    run_daily(before_market_open,time='before_open', reference_security='000300.XSHG') 
    # 开盘时运行
    run_daily(market_open,time='open', reference_security='000300.XSHG')
    
## 开盘前运行函数     
def before_market_open(context):
    if g.trade_days%g.days == 0:
        g.trade = True
        #获取行业指数指定g.days日收益最高的行业
        date = context.previous_date
        s_date = ShiftTradingDay(date,-g.days)
        hy_df = get_hy_pct(s_date,date)
        #获取行业指数的成分股
        temp_list = get_industry_stocks(hy_df.index[0],date=date)
        #剔除停牌股
        all_data = get_current_data()
        temp_list = [stock for stock in temp_list if not all_data[stock].paused]
        #按市值进行排序
        g.buy_list = get_check_stocks_sort(context,temp_list)
        
    g.trade_days += 1
        
## 开盘时运行函数
def market_open(context):
    if g.trade:
        #卖出不在买入列表中的股票
        sell(context,g.buy_list)
        #买入不在持仓中的股票，按要操作的股票平均资金
        buy(context,g.buy_list)
        g.trade = False
#交易函数 - 买入
def buy(context, buy_lists):
    # 获取最终的 buy_lists 列表
    Num = g.max_hold_stocknum - len(context.portfolio.positions.keys())
    buy_lists = buy_lists[:Num]
    # 买入股票
    if len(buy_lists)>0:
        # 分配资金
        cash = context.portfolio.total_value/(g.max_hold_stocknum*1.0)
        # 进行买入操作
        for s in buy_lists:
            order_value(s,cash)
       
# 交易函数 - 出场
def sell(context, buy_lists):
    # 获取 sell_lists 列表
    hold_stock = context.portfolio.positions.keys()
    for s in hold_stock:
        #卖出不在买入列表中的股票
        if s not in buy_lists:
            order_target_value(s,0)   

#按市值进行排序    
def get_check_stocks_sort(context,check_out_lists):
    df = get_fundamentals(query(valuation.circulating_cap,valuation.code).filter(valuation.code.in_(check_out_lists)),date=context.previous_date)
    #asc值为0，从大到小
    df = df.sort('circulating_cap',ascending=0)
    out_lists = list(df['code'].values)[:g.max_hold_stocknum]
    return out_lists
    
#统计各指数当天涨跌
#输入日期
#返回df
def get_hy_pct(date_s,date):
    #指数涨跌幅统计
    #总数据
    sw_hy = jqdata.get_industries(name='sw_l1')
    sw_hy_dict  = {}
    for i in sw_hy.index:
        value = get_SW_index(i,start_date=date_s,end_date=date)
        sw_hy_dict[i] = value
    pl_hy = pd.Panel(sw_hy_dict)
    pl = pl_hy.transpose(2,1,0)
    pl = pl.loc[['PrevClosePrice','OpenPrice','HighPrice','LowPrice','ClosePrice','TurnoverVolume','TurnoverValue'],:,:]
    #涨跌幅数据
    pl_pct = (pl.iloc[:,-1,:]/pl.iloc[:,-2,:]-1)*100
    pl_pct_5 = (pl.iloc[:,-1,:]/pl.iloc[:,-1-g.days,:]-1)*100
    
    df_fin = pd.concat([pl_pct['ClosePrice'],pl_pct_5['ClosePrice']],axis=1)
    df_fin.columns = ['涨跌幅%','n日涨跌幅%']
    return df_fin.sort('n日涨跌幅%',ascending=0)

#获取N天前的交易日日期
def ShiftTradingDay(date,shift=5):
    # 获取所有的交易日，返回一个包含所有交易日的 list,元素值为 datetime.date 类型.
    tradingday = jqdata.get_all_trade_days()
    # 得到date之后shift天那一天在列表中的行标号 返回一个数
    shiftday_index = list(tradingday).index(date)+shift
    # 根据行号返回该日日期 为datetime.date类型
    return tradingday[shiftday_index]  

#行业涨跌幅
#直接用申万的行业指数数据进行说明了
def get_SW_index(SW_index = 801010,start_date = '2017-01-31',end_date = '2018-01-31'):
    index_list = ['PrevClosePrice','OpenPrice','HighPrice','LowPrice','ClosePrice','TurnoverVolume','TurnoverValue','TurnoverDeals','ChangePCT','UpdateTime']
    jydf = jy.run_query(query(jy.SecuMain).filter(jy.SecuMain.SecuCode==str(SW_index)))
    link=jydf[jydf.SecuCode==str(SW_index)]
    rows=jydf[jydf.SecuCode==str(SW_index)].index.tolist()
    result=link['InnerCode'][rows]

    df = jy.run_query(query(jy.QT_SYWGIndexQuote).filter(jy.QT_SYWGIndexQuote.InnerCode==str(result[0]),\
                                                   jy.QT_SYWGIndexQuote.TradingDay>=start_date,\
                                                         jy.QT_SYWGIndexQuote.TradingDay<=end_date
                                                        ))
    df.index = df['TradingDay']
    df = df[index_list]
    return df
