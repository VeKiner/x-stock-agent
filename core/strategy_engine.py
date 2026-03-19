"""
X-Stock Agent - 多策略投票引擎
基于 GitHub 最牛开源项目优化
4策略投票决策：动量 + 均值回归 + ML预测 + 情绪分析
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger
import random


class StrategyEngine:
    """多策略投票引擎"""
    
    def __init__(self, config=None):
        self.config = config or {}
        
        # 策略配置
        self.strategies = {
            'momentum': {
                'enabled': True,
                'weight': 0.30,
                'name': '动量策略'
            },
            'mean_reversion': {
                'enabled': True,
                'weight': 0.30,
                'name': '均值回归'
            },
            'ml_predict': {
                'enabled': True,
                'weight': 0.25,
                'name': 'ML预测'
            },
            'sentiment': {
                'enabled': True,
                'weight': 0.15,
                'name': '情绪分析'
            }
        }
        
        # 策略性能记录
        self.performance = {
            'momentum': {'signals': 0, 'correct': 0},
            'mean_reversion': {'signals': 0, 'correct': 0},
            'ml_predict': {'signals': 0, 'correct': 0},
            'sentiment': {'signals': 0, 'correct': 0}
        }
        
        logger.info("🎯 多策略引擎初始化完成")
        logger.info(f"   动量策略权重: {self.strategies['momentum']['weight']}")
        logger.info(f"   均值回归权重: {self.strategies['mean_reversion']['weight']}")
        logger.info(f"   ML预测权重: {self.strategies['ml_predict']['weight']}")
        logger.info(f"   情绪分析权重: {self.strategies['sentiment']['weight']}")
    
    def get_signal(self, stock_code, stock_data, market_data=None):
        """
        获取综合交易信号
        
        Args:
            stock_code: 股票代码
            stock_data: 股票数据 (dict)
            market_data: 大盘数据 (dict, optional)
            
        Returns:
            dict: {
                'signal': 'buy'/'sell'/'hold',
                'confidence': 0.0-1.0,
                'votes': {strategy: signal},
                'reason': str
            }
        """
        votes = {}
        total_weight = 0
        weighted_score = 0
        
        # 1. 动量策略
        if self.strategies['momentum']['enabled']:
            signal = self._momentum_strategy(stock_data)
            votes['momentum'] = signal
            weight = self.strategies['momentum']['weight']
            total_weight += weight
            
            if signal == 'buy':
                weighted_score += weight
            elif signal == 'sell':
                weighted_score -= weight
        
        # 2. 均值回归策略
        if self.strategies['mean_reversion']['enabled']:
            signal = self._mean_reversion_strategy(stock_data)
            votes['mean_reversion'] = signal
            weight = self.strategies['mean_reversion']['weight']
            total_weight += weight
            
            if signal == 'buy':
                weighted_score += weight
            elif signal == 'sell':
                weighted_score -= weight
        
        # 3. ML预测策略
        if self.strategies['ml_predict']['enabled']:
            signal = self._ml_predict_strategy(stock_data)
            votes['ml_predict'] = signal
            weight = self.strategies['ml_predict']['weight']
            total_weight += weight
            
            if signal == 'buy':
                weighted_score += weight
            elif signal == 'sell':
                weighted_score -= weight
        
        # 4. 情绪分析策略
        if self.strategies['sentiment']['enabled']:
            signal = self._sentiment_strategy(stock_code, stock_data)
            votes['sentiment'] = signal
            weight = self.strategies['sentiment']['weight']
            total_weight += weight
            
            if signal == 'buy':
                weighted_score += weight
            elif signal == 'sell':
                weighted_score -= weight
        
        # 计算最终信号
        if weighted_score > 0.3:
            final_signal = 'buy'
            confidence = min(0.95, weighted_score)
        elif weighted_score < -0.3:
            final_signal = 'sell'
            confidence = min(0.95, abs(weighted_score))
        else:
            final_signal = 'hold'
            confidence = 0.3
        
        # 生成原因
        buy_votes = sum(1 for s in votes.values() if s == 'buy')
        sell_votes = sum(1 for s in votes.values() if s == 'sell')
        
        if final_signal == 'buy':
            reason = f"买入信号 ({buy_votes}票支持)"
        elif final_signal == 'sell':
            reason = f"卖出信号 ({sell_votes}票支持)"
        else:
            reason = f"观望 ({buy_votes}买/{sell_votes}卖)"
        
        return {
            'signal': final_signal,
            'confidence': confidence,
            'votes': votes,
            'reason': reason,
            'weighted_score': weighted_score
        }
    
    def _momentum_strategy(self, data):
        """动量策略 - 追涨杀跌"""
        try:
            change = data.get('change', 0)
            volume_ratio = data.get('volume_ratio', 1.0)
            
            # 强势上涨 + 放量 = 买入
            if change > 2 and volume_ratio > 1.5:
                return 'buy'
            # 强势下跌 = 卖出
            elif change < -3:
                return 'sell'
            else:
                return 'hold'
        except:
            return 'hold'
    
    def _mean_reversion_strategy(self, data):
        """均值回归策略 - 低买高卖"""
        try:
            change = data.get('change', 0)
            rsi = data.get('rsi', 50)
            
            # 超跌反弹
            if rsi < 30 or change < -4:
                return 'buy'
            # 超涨回落
            elif rsi > 70 or change > 4:
                return 'sell'
            else:
                return 'hold'
        except:
            return 'hold'
    
    def _ml_predict_strategy(self, data):
        """ML预测策略 - 基于模型预测"""
        try:
            # 模拟 ML 预测结果
            # 实际项目中这里会是真实的模型预测
            prediction = data.get('ml_prediction', 0)
            
            if prediction > 0.6:
                return 'buy'
            elif prediction < 0.4:
                return 'sell'
            else:
                return 'hold'
        except:
            return 'hold'
    
    def _sentiment_strategy(self, code, data):
        """情绪分析策略 - 基于新闻情感"""
        try:
            # 模拟情感分析结果
            sentiment = data.get('sentiment', 0.5)
            
            if sentiment > 0.7:
                return 'buy'
            elif sentiment < 0.3:
                return 'sell'
            else:
                return 'hold'
        except:
            return 'hold'
    
    def update_performance(self, strategy_name, signal, actual_result):
        """更新策略表现"""
        if strategy_name in self.performance:
            self.performance[strategy_name]['signals'] += 1
            if (signal == 'buy' and actual_result > 0) or (signal == 'sell' and actual_result < 0):
                self.performance[strategy_name]['correct'] += 1
    
    def get_performance_report(self):
        """获取策略表现报告"""
        report = []
        
        for name, stats in self.performance.items():
            if stats['signals'] > 0:
                win_rate = stats['correct'] / stats['signals'] * 100
            else:
                win_rate = 0
            
            report.append({
                'strategy': self.strategies[name]['name'],
                'signals': stats['signals'],
                'correct': stats['correct'],
                'win_rate': win_rate,
                'weight': self.strategies[name]['weight']
            })
        
        return sorted(report, key=lambda x: x['win_rate'], reverse=True)
    
    def auto_optimize(self):
        """自动优化策略权重 - 基于表现"""
        logger.info("🔄 开始自动优化策略权重...")
        
        for name, stats in self.performance.items():
            if stats['signals'] > 10:  # 至少10个信号
                win_rate = stats['correct'] / stats['signals']
                
                # 根据胜率调整权重
                if win_rate > 0.7:
                    self.strategies[name]['weight'] *= 1.1
                    logger.info(f"   {name}: 权重提升 10%")
                elif win_rate < 0.4:
                    self.strategies[name]['weight'] *= 0.9
                    logger.info(f"   {name}: 权重降低 10%")
        
        # 归一化权重
        total = sum(s['weight'] for s in self.strategies.values())
        for name in self.strategies:
            self.strategies[name]['weight'] /= total
        
        logger.info("✅ 权重优化完成")


# 测试
if __name__ == "__main__":
    logger.add("./logs/strategy_engine.log")
    
    engine = StrategyEngine()
    
    # 模拟股票数据
    test_data = {
        'code': '600000',
        'change': 2.5,
        'volume_ratio': 1.8,
        'rsi': 65,
        'ml_prediction': 0.7,
        'sentiment': 0.6
    }
    
    # 获取信号
    result = engine.get_signal('600000', test_data)
    
    print("\n" + "="*50)
    print("🎯 策略引擎测试")
    print("="*50)
    print(f"股票: 600000")
    print(f"各策略投票: {result['votes']}")
    print(f"最终信号: {result['signal']}")
    print(f"置信度: {result['confidence']:.2%}")
    print(f"原因: {result['reason']}")
    print("="*50)
