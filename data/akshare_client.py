"""
X-Stock Agent - Core Data Client
基于 AKShare 的 A 股数据获取模块
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger
import time


class AKShareClient:
    """AKShare 数据客户端"""
    
    def __init__(self, cache_manager=None):
        self.cache = cache_manager
        logger.info("AKShare 客户端初始化完成")
    
    def get_realtime_quotes(self, symbol_list=None):
        """
        获取实时行情
        
        Args:
            symbol_list: 股票代码列表，如 ['600000', '000001']
                        如果为 None，返回全市场数据
            
        Returns:
            DataFrame: 实时行情数据
        """
        try:
            logger.info(f"获取实时行情，代码列表：{symbol_list}")
            
            # 获取全市场实时行情
            df = ak.stock_zh_a_spot()
            
            if symbol_list:
                # 过滤指定股票
                df = df[df['code'].isin(symbol_list)]
            
            logger.info(f"成功获取 {len(df)} 只股票行情")
            return df
            
        except Exception as e:
            logger.error(f"获取实时行情失败：{e}")
            return pd.DataFrame()
    
    def get_daily_history(self, symbol, start_date, end_date):
        """
        获取历史日线数据
        
        Args:
            symbol: 股票代码，如 '600000'
            start_date: 开始日期，格式 '20240101'
            end_date: 结束日期，格式 '20241231'
            
        Returns:
            DataFrame: 历史行情数据
        """
        try:
            logger.info(f"获取 {symbol} 历史数据：{start_date} - {end_date}")
            
            df = ak.stock_zh_a_daily(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date
            )
            
            logger.info(f"成功获取 {len(df)} 条历史记录")
            return df
            
        except Exception as e:
            logger.error(f"获取历史数据失败：{e}")
            return pd.DataFrame()
    
    def get_stock_info(self, symbol):
        """
        获取股票基本信息
        
        Args:
            symbol: 股票代码
            
        Returns:
            dict: 股票基本信息
        """
        try:
            # 获取个股信息
            df = ak.stock_individual_info_em(symbol=symbol)
            info = df.to_dict('records')[0] if not df.empty else {}
            
            logger.info(f"成功获取 {symbol} 基本信息")
            return info
            
        except Exception as e:
            logger.error(f"获取股票信息失败：{e}")
            return {}
    
    def get_financial_report(self, symbol, report_type='annual'):
        """
        获取财务报表
        
        Args:
            symbol: 股票代码
            report_type: 报表类型 (annual/quarterly)
            
        Returns:
            DataFrame: 财务数据
        """
        try:
            if report_type == 'annual':
                df = ak.stock_financial_analysis_indicator(symbol=symbol)
            else:
                df = ak.stock_financial_abstract(symbol=symbol)
            
            logger.info(f"成功获取 {symbol} 财务报表")
            return df
            
        except Exception as e:
            logger.error(f"获取财务报表失败：{e}")
            return pd.DataFrame()
    
    def get_market_index(self, index_code='000001'):
        """
        获取大盘指数数据
        
        Args:
            index_code: 指数代码，默认上证指数
            
        Returns:
            DataFrame: 指数数据
        """
        try:
            df = ak.stock_zh_index_daily(symbol=f"sh{index_code}")
            logger.info(f"成功获取指数 {index_code} 数据")
            return df
            
        except Exception as e:
            logger.error(f"获取指数数据失败：{e}")
            return pd.DataFrame()
    
    def get_concept_hot(self):
        """
        获取概念板块热度
        
        Returns:
            DataFrame: 概念板块数据
        """
        try:
            df = ak.stock_board_concept_name_em()
            logger.info(f"成功获取概念板块数据，共 {len(df)} 个板块")
            return df
            
        except Exception as e:
            logger.error(f"获取概念板块失败：{e}")
            return pd.DataFrame()
    
    def get_news_sentiment(self, symbol):
        """
        获取个股相关新闻
        
        Args:
            symbol: 股票代码
            
        Returns:
            list: 新闻列表
        """
        try:
            df = ak.stock_news_em(symbol=symbol)
            news_list = df.to_dict('records') if not df.empty else []
            logger.info(f"成功获取 {symbol} 相关新闻 {len(news_list)} 条")
            return news_list
            
        except Exception as e:
            logger.error(f"获取新闻失败：{e}")
            return []


# 测试函数
if __name__ == "__main__":
    logger.add("./logs/data_client_test.log")
    
    client = AKShareClient()
    
    # 测试获取实时行情
    print("\n=== 测试实时行情 ===")
    df = client.get_realtime_quotes(['600000', '000001'])
    if not df.empty:
        print(df[['code', 'name', 'latest_price', 'change_percent']].head())
    
    # 测试历史数据
    print("\n=== 测试历史数据 ===")
    end = datetime.now().strftime('%Y%m%d')
    start = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
    df = client.get_daily_history('600000', start, end)
    if not df.empty:
        print(df.head())
    
    print("\n测试完成！")
