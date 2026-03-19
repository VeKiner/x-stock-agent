"""
X-Stock Agent - 新闻情绪分析模块
基于 NLP 的市场情绪分析
"""

import requests
from datetime import datetime
from loguru import logger
import random


class SentimentAnalyzer:
    """新闻情绪分析器"""
    
    def __init__(self):
        self.cache = {}
        self.cache_time = 300  # 缓存5分钟
        
        logger.info("💭 情绪分析器初始化完成")
    
    def analyze(self, stock_code):
        """
        分析股票情绪
        
        Args:
            stock_code: 股票代码
            
        Returns:
            dict: 情绪结果
        """
        # 检查缓存
        if stock_code in self.cache:
            cached = self.cache[stock_code]
            if (datetime.now() - cached['time']).seconds < self.cache_time:
                return cached['result']
        
        try:
            # 尝试获取新闻
            sentiment = self._get_news_sentiment(stock_code)
            
            # 缓存结果
            self.cache[stock_code] = {
                'time': datetime.now(),
                'result': sentiment
            }
            
            return sentiment
            
        except Exception as e:
            logger.error(f"情绪分析失败: {e}")
            return {
                'sentiment': 0.5,
                'label': 'neutral',
                'confidence': 0.3,
                'reason': f'分析异常: {str(e)[:30]}'
            }
    
    def _get_news_sentiment(self, stock_code):
        """获取新闻情绪（简化版）"""
        # 实际项目中会调用新闻API或使用NLP模型
        
        # 模拟分析结果
        # 基于代码生成一些随机但合理的情绪值
        
        # 热门股票通常情绪较高
        popular_stocks = ['600519', '000001', '601318']
        
        if stock_code in popular_stocks:
            base_sentiment = 0.55
        else:
            base_sentiment = 0.50
        
        # 添加一些随机波动
        sentiment = base_sentiment + random.uniform(-0.1, 0.1)
        sentiment = max(0, min(1, sentiment))
        
        # 判断标签
        if sentiment > 0.6:
            label = 'positive'
            reason = '市场关注度高，情绪偏多'
        elif sentiment < 0.4:
            label = 'negative'
            reason = '市场情绪谨慎，情绪偏空'
        else:
            label = 'neutral'
            reason = '情绪中性，观望为主'
        
        return {
            'sentiment': sentiment,
            'label': label,
            'confidence': abs(sentiment - 0.5) * 2,
            'reason': reason,
            'stock_code': stock_code
        }
    
    def batch_analyze(self, stock_codes):
        """批量分析"""
        results = {}
        for code in stock_codes:
            results[code] = self.analyze(code)
        return results


# 测试
if __name__ == "__main__":
    logger.add("./logs/sentiment.log")
    
    analyzer = SentimentAnalyzer()
    
    # 测试
    stocks = ['600519', '000001', '601318', '600000']
    
    print("\n" + "="*50)
    print("💭 情绪分析测试")
    print("="*50)
    
    for code in stocks:
        result = analyzer.analyze(code)
        print(f"\n{code}:")
        print(f"  情绪值: {result['sentiment']:.2f}")
        print(f"  标签: {result['label']}")
        print(f"  原因: {result['reason']}")
    
    print("="*50)
