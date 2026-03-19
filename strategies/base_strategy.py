"""
X-Stock Agent - Base Strategy Class
所有策略的基类
"""

from abc import ABC, abstractmethod
from datetime import datetime
from loguru import logger


class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, name, config=None):
        self.name = name
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        self.weight = self.config.get('weight', 1.0)
        
        # 性能统计
        self.total_signals = 0
        self.correct_signals = 0
        self.last_update = datetime.now()
        
        logger.info(f"策略 [{self.name}] 初始化完成，权重：{self.weight}")
    
    @abstractmethod
    def generate_signal(self, stock_data, context=None):
        """
        生成交易信号
        
        Args:
            stock_data: 股票数据（DataFrame 或 dict）
            context: 上下文信息（大盘、板块等）
            
        Returns:
            dict: {
                'symbol': str,
                'signal': str,  # 'buy', 'sell', 'hold'
                'confidence': float,  # 0-1
                'reason': str,
                'suggested_price': float,
                'suggested_volume': int
            }
        """
        pass
    
    def update_performance(self, signal, actual_outcome):
        """
        更新策略表现
        
        Args:
            signal: 之前发出的信号 ('buy', 'sell', 'hold')
            actual_outcome: 实际结果 (1=盈利，-1=亏损，0=持平)
        """
        self.total_signals += 1
        
        if signal == 'hold':
            return
        
        # 判断是否正确
        if (signal == 'buy' and actual_outcome > 0) or \
           (signal == 'sell' and actual_outcome < 0):
            self.correct_signals += 1
    
    def get_win_rate(self):
        """获取胜率"""
        if self.total_signals == 0:
            return 0.0
        return self.correct_signals / self.total_signals
    
    def get_stats(self):
        """获取策略统计信息"""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'weight': self.weight,
            'total_signals': self.total_signals,
            'correct_signals': self.correct_signals,
            'win_rate': self.get_win_rate(),
            'last_update': self.last_update.isoformat()
        }
    
    def validate_data(self, stock_data):
        """验证数据完整性"""
        if stock_data is None:
            return False, "数据为空"
        
        if isinstance(stock_data, dict) and len(stock_data) == 0:
            return False, "数据字典为空"
        
        return True, "数据有效"
    
    def log_signal(self, symbol, signal, confidence, reason):
        """记录信号日志"""
        signal_icon = {'buy': '🟢', 'sell': '🔴', 'hold': '⚪'}.get(signal, '⚪')
        logger.info(f"[{self.name}] {signal_icon} {symbol} {signal.upper()} "
                   f"(置信度：{confidence:.2f}) - {reason}")
