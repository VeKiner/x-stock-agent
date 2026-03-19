"""
X-Stock Agent - Momentum Strategy
动量策略：追涨杀跌，顺势而为
"""

from strategies.base_strategy import BaseStrategy
from loguru import logger
import pandas as pd
import numpy as np


class MomentumStrategy(BaseStrategy):
    """动量策略"""
    
    def __init__(self, config=None):
        super().__init__('momentum', config)
        
        # 策略参数
        self.lookback_days = self.config.get('lookback_days', 20)  # 回看天数
        self.momentum_threshold = self.config.get('momentum_threshold', 0.05)  # 动量阈值 5%
        self.volume_ratio_threshold = self.config.get('volume_ratio_threshold', 1.5)  # 放量阈值
    
    def generate_signal(self, stock_data, context=None):
        """
        生成动量交易信号
        
        买入条件：
        1. 近 N 日涨幅超过阈值
        2. 成交量放大
        3. 价格在均线上方
        
        卖出条件：
        1. 动量反转（从涨转跌）
        2. 跌破关键均线
        """
        try:
            if not self.enabled:
                return {'signal': 'hold', 'confidence': 0.0, 'reason': '策略未启用'}
            
            # 验证数据
            valid, msg = self.validate_data(stock_data)
            if not valid:
                return {'signal': 'hold', 'confidence': 0.0, 'reason': msg}
            
            symbol = stock_data.get('code', 'UNKNOWN')
            current_price = stock_data.get('latest_price', 0)
            
            # 获取历史数据
            history = stock_data.get('history', None)
            if history is None or len(history) < self.lookback_days:
                return {'signal': 'hold', 'confidence': 0.0, 'reason': '历史数据不足'}
            
            # 计算动量指标
            close_prices = history['close'].values if 'close' in history.columns else history.iloc[:, 3].values
            volumes = history['volume'].values if 'volume' in history.columns else history.iloc[:, 5].values
            
            if len(close_prices) < self.lookback_days:
                return {'signal': 'hold', 'confidence': 0.0, 'reason': '数据长度不足'}
            
            # 计算 N 日收益率
            momentum = (close_prices[-1] - close_prices[-self.lookback_days]) / close_prices[-self.lookback_days]
            
            # 计算均量
            avg_volume = np.mean(volumes[-self.lookback_days:-1])
            current_volume = volumes[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            # 计算均线
            ma5 = np.mean(close_prices[-5:])
            ma10 = np.mean(close_prices[-10:])
            ma20 = np.mean(close_prices[-20:]) if len(close_prices) >= 20 else ma10
            
            # 判断信号
            signal = 'hold'
            confidence = 0.0
            reason = ''
            
            # 买入信号：强势上涨 + 放量
            if momentum > self.momentum_threshold and volume_ratio > self.volume_ratio_threshold:
                if current_price > ma5 > ma10:  # 多头排列
                    signal = 'buy'
                    confidence = min(0.9, 0.5 + momentum * 2 + (volume_ratio - 1) * 0.1)
                    reason = f"动量强劲 ({momentum*100:.1f}%) + 放量 ({volume_ratio:.1f}x) + 多头排列"
            
            # 卖出信号：动量反转或跌破均线
            elif momentum < -self.momentum_threshold * 0.5:
                if current_price < ma5:
                    signal = 'sell'
                    confidence = min(0.8, 0.4 + abs(momentum) * 2)
                    reason = f"动量反转 ({momentum*100:.1f}%) + 跌破 5 日线"
            
            # 持有信号
            else:
                signal = 'hold'
                confidence = 0.3
                reason = f"动量中性 ({momentum*100:.1f}%)，观望"
            
            self.last_update = pd.Timestamp.now()
            self.log_signal(symbol, signal, confidence, reason)
            
            return {
                'symbol': symbol,
                'signal': signal,
                'confidence': confidence,
                'reason': reason,
                'suggested_price': current_price,
                'metrics': {
                    'momentum': momentum,
                    'volume_ratio': volume_ratio,
                    'ma5': ma5,
                    'ma10': ma10,
                    'ma20': ma20
                }
            }
            
        except Exception as e:
            logger.error(f"[MomentumStrategy] 生成信号失败：{e}")
            return {
                'symbol': 'UNKNOWN',
                'signal': 'hold',
                'confidence': 0.0,
                'reason': f'策略执行错误：{str(e)}'
            }


# 测试
if __name__ == "__main__":
    logger.add("./logs/momentum_test.log")
    
    # 构造测试数据
    import numpy as np
    
    dates = pd.date_range(end=pd.Timestamp.now(), periods=30)
    test_history = pd.DataFrame({
        'open': np.random.uniform(10, 12, 30),
        'high': np.random.uniform(12, 13, 30),
        'low': np.random.uniform(9, 11, 30),
        'close': np.random.uniform(10, 12, 30),
        'volume': np.random.randint(1000, 5000, 30)
    })
    
    test_stock_data = {
        'code': '600000',
        'name': '浦发银行',
        'latest_price': 11.5,
        'history': test_history
    }
    
    strategy = MomentumStrategy({
        'enabled': True,
        'weight': 0.3,
        'lookback_days': 20,
        'momentum_threshold': 0.05
    })
    
    signal = strategy.generate_signal(test_stock_data)
    print(f"\n生成的信号：{signal}")
