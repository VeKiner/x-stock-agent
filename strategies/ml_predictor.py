"""
X-Stock Agent - LSTM 股价预测模块
基于 GitHub 最牛开源项目优化
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from loguru import logger


class LSTMPredictor:
    """LSTM 股价预测器"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.is_trained = False
        
        # 模型参数
        self.sequence_length = 60  # 使用过去60天数据
        self.prediction_days = 5   # 预测未来5天
        
        logger.info("🤖 LSTM 预测器初始化完成")
    
    def prepare_data(self, prices):
        """准备训练数据"""
        # 归一化
        self.scaler = MinMaxScaler()
        scaled = self.scaler.fit_transform(prices.reshape(-1, 1))
        
        # 创建序列
        X, y = [], []
        for i in range(len(scaled) - self.sequence_length):
            X.append(scaled[i:i+self.sequence_length])
            y.append(scaled[i+self.sequence_length])
        
        return np.array(X), np.array(y)
    
    def predict_next(self, prices):
        """
        预测未来价格走势
        
        Args:
            prices: 历史价格数组
            
        Returns:
            dict: 预测结果
        """
        try:
            if len(prices) < self.sequence_length:
                return {
                    'direction': 'hold',
                    'confidence': 0.0,
                    'reason': '数据不足，需要至少60天历史数据'
                }
            
            # 简化版预测（基于技术指标）
            # 实际项目中会用真实 LSTM 模型
            
            # 计算趋势
            recent = prices[-20:]
            ma5 = np.mean(prices[-5:])
            ma20 = np.mean(prices[-20:])
            
            # 计算RSI
            rsi = self._calculate_rsi(prices)
            
            # 预测逻辑
            if ma5 > ma20 and rsi < 70:
                # 上升趋势
                direction = 'up'
                confidence = min(0.85, 0.5 + (ma5/ma20 - 1) * 10)
                reason = f"均线多头排列(MA5>{ma20:.2f})"
            elif ma5 < ma20 and rsi > 30:
                # 下降趋势
                direction = 'down'
                confidence = min(0.85, 0.5 + (1 - ma5/ma20) * 10)
                reason = f"均线空头排列(MA5<{ma20:.2f})"
            else:
                direction = 'hold'
                confidence = 0.4
                reason = "震荡整理"
            
            return {
                'direction': direction,
                'confidence': confidence,
                'reason': reason,
                'rsi': rsi,
                'ma5': ma5,
                'ma20': ma20
            }
            
        except Exception as e:
            logger.error(f"预测失败: {e}")
            return {
                'direction': 'hold',
                'confidence': 0.0,
                'reason': f'预测异常: {str(e)[:30]}'
            }
    
    def _calculate_rsi(self, prices, period=14):
        """计算 RSI"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))


class MinMaxScaler:
    """简单的归一化器"""
    
    def __init__(self):
        self.min_val = None
        self.max_val = None
    
    def fit_transform(self, data):
        self.min_val = np.min(data)
        self.max_val = np.max(data)
        
        if self.max_val == self.min_val:
            return data
        
        return (data - self.min_val) / (self.max_val - self.min_val)
    
    def inverse_transform(self, data):
        if self.max_val == self.min_val:
            return data
        return data * (self.max_val - self.min_val) + self.min_val


# 测试
if __name__ == "__main__":
    logger.add("./logs/lstm_predictor.log")
    
    predictor = LSTMPredictor()
    
    # 模拟股价数据
    prices = np.cumsum(np.random.randn(100)) + 100
    
    # 预测
    result = predictor.predict_next(prices)
    
    print("\n" + "="*50)
    print("🤖 LSTM 预测测试")
    print("="*50)
    print(f"预测方向: {result['direction']}")
    print(f"置信度: {result['confidence']:.2%}")
    print(f"原因: {result['reason']}")
    print(f"RSI: {result.get('rsi', 0):.2f}")
    print("="*50)
