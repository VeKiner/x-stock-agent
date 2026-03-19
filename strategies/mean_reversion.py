"""
X-Stock Agent - Mean Reversion Strategy
均值回归策略：低买高卖，逆向操作
"""

from strategies.base_strategy import BaseStrategy
from loguru import logger
import pandas as pd
import numpy as np


class MeanReversionStrategy(BaseStrategy):
    """均值回归策略"""
    
    def __init__(self, config=None):
        super().__init__('mean_reversion', config)
        
        # 策略参数
        self.lookback_days = self.config.get('lookback_days', 20)
        self.overbought_threshold = self.config.get('overbought_threshold', 2.0)  # RSI 超买线
        self.oversold_threshold = self.config.get('oversold_threshold', 80.0)  # RSI 超卖线
        self.bollinger_std = self.config.get('bollinger_std', 2.0)  # 布林带标准差
    
    def calculate_rsi(self, prices, period=14):
        """计算 RSI 指标"""
        delta = np.diff(prices)
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        
        if len(gain) < period:
            return 50.0
        
        avg_gain = np.mean(gain[-period:])
        avg_loss = np.mean(loss[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_bollinger_bands(self, prices, period=20, std_dev=2.0):
        """计算布林带"""
        if len(prices) < period:
            return None, None, None
        
        ma = np.mean(prices[-period:])
        std = np.std(prices[-period:])
        
        upper = ma + std_dev * std
        lower = ma - std_dev * std
        
        return upper, ma, lower
    
    def generate_signal(self, stock_data, context=None):
        """
        生成均值回归交易信号
        
        买入条件：
        1. RSI 超卖 (<30)
        2. 价格触及布林带下轨
        3. 偏离均线过大
        
        卖出条件：
        1. RSI 超买 (>70)
        2. 价格触及布林带上轨
        """
        try:
            if not self.enabled:
                return {'signal': 'hold', 'confidence': 0.0, 'reason': '策略未启用'}
            
            valid, msg = self.validate_data(stock_data)
            if not valid:
                return {'signal': 'hold', 'confidence': 0.0, 'reason': msg}
            
            symbol = stock_data.get('code', 'UNKNOWN')
            current_price = stock_data.get('latest_price', 0)
            
            history = stock_data.get('history', None)
            if history is None or len(history) < self.lookback_days:
                return {'signal': 'hold', 'confidence': 0.0, 'reason': '历史数据不足'}
            
            # 获取收盘价
            close_prices = history['close'].values if 'close' in history.columns else history.iloc[:, 3].values
            
            if len(close_prices) < self.lookback_days:
                return {'signal': 'hold', 'confidence': 0.0, 'reason': '数据长度不足'}
            
            # 计算技术指标
            rsi = self.calculate_rsi(close_prices, 14)
            upper, ma, lower = self.calculate_bollinger_bands(close_prices, 20, self.bollinger_std)
            
            # 计算价格偏离度
            price_deviation = (current_price - ma) / ma if ma > 0 else 0
            
            # 判断信号
            signal = 'hold'
            confidence = 0.0
            reason = ''
            
            # 买入信号：超卖 + 触及下轨
            if rsi < 30 and current_price <= lower:
                signal = 'buy'
                confidence = min(0.85, 0.5 + (30 - rsi) / 60 + (lower - current_price) / lower * 10)
                reason = f"RSI 超卖 ({rsi:.1f}) + 触及布林下轨 (¥{lower:.2f})"
            
            # 卖出信号：超买 + 触及上轨
            elif rsi > 70 and current_price >= upper:
                signal = 'sell'
                confidence = min(0.85, 0.5 + (rsi - 70) / 60 + (current_price - upper) / upper * 10)
                reason = f"RSI 超买 ({rsi:.1f}) + 触及布林上轨 (¥{upper:.2f})"
            
            # 持有信号
            else:
                signal = 'hold'
                confidence = 0.3
                reason = f"RSI 中性 ({rsi:.1f})，价格在布林带内"
            
            self.last_update = pd.Timestamp.now()
            self.log_signal(symbol, signal, confidence, reason)
            
            return {
                'symbol': symbol,
                'signal': signal,
                'confidence': confidence,
                'reason': reason,
                'suggested_price': current_price,
                'metrics': {
                    'rsi': rsi,
                    'bollinger_upper': upper,
                    'bollinger_ma': ma,
                    'bollinger_lower': lower,
                    'price_deviation': price_deviation
                }
            }
            
        except Exception as e:
            logger.error(f"[MeanReversionStrategy] 生成信号失败：{e}")
            return {
                'symbol': 'UNKNOWN',
                'signal': 'hold',
                'confidence': 0.0,
                'reason': f'策略执行错误：{str(e)}'
            }


# 测试
if __name__ == "__main__":
    logger.add("./logs/mean_reversion_test.log")
    
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
        'code': '000001',
        'name': '平安银行',
        'latest_price': 11.5,
        'history': test_history
    }
    
    strategy = MeanReversionStrategy({
        'enabled': True,
        'weight': 0.3
    })
    
    signal = strategy.generate_signal(test_stock_data)
    print(f"\n生成的信号：{signal}")
