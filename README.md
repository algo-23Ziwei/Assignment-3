# Assignment-3
申万宏源-行业轮动策略
--------------------
策略思路：
选股：统计申万一级行业指数，每月固定时间选取涨幅最大的指数，
选取指数成分股中流通市值最大的5只股票作为操作标的
择时：每月第一个交易日进行买卖操作，默认开盘卖出不在股票池中股票，买入选出的股票
仓位：平均分配仓位
