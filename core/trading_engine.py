"""
X-Stock Agent - 交易执行引擎
"""

import yaml
import pandas as pd
from datetime import datetime
from loguru import logger
import json
import os


class TradingEngine:
    """交易执行引擎"""
    
    def __init__(self, config_path='config.yaml'):
        # 加载配置
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = self._default_config()
        
        # 初始化组件
        from core.risk_manager import RiskManager
        from core.strategy_engine import StrategyEngine
        
        self.risk_manager = RiskManager(self.config)
        self.strategy_engine = StrategyEngine(self.config.get('strategies', {}))
        
        # 持仓和资金
        self.initial_capital = self.config.get('trading', {}).get('initial_capital', 1000000)
        self.cash = self.initial_capital
        self.positions = {}
        self.trade_history = []
        
        # 状态
        self.is_running = False
        self.last_update = None
        
        logger.info("="*60)
        logger.info("🎰 交易引擎初始化完成")
        logger.info(f"   初始资金: ¥{self.initial_capital:,.0f}")
        logger.info(f"   交易模式: {self.config.get('trading', {}).get('mode', 'paper')}")
        logger.info("="*60)
    
    def _default_config(self):
        """默认配置"""
        return {
            'trading': {
                'mode': 'paper',
                'initial_capital': 1000000
            },
            'risk': {
                'max_position_per_stock': 0.20,
                'max_daily_loss': 0.02,
                'max_drawdown_warning': 0.10,
                'stop_loss_per_stock': 0.08
            },
            'strategies': {
                'momentum': {'enabled': True, 'weight': 0.30},
                'mean_reversion': {'enabled': True, 'weight': 0.30},
                'ml_predict': {'enabled': True, 'weight': 0.25},
                'sentiment': {'enabled': True, 'weight': 0.15}
            }
        }
    
    def run(self):
        """运行交易引擎"""
        self.is_running = True
        logger.info("▶️ 交易引擎启动")
        
        # 这里会是主循环
        # 1. 获取市场数据
        # 2. 生成交易信号
        # 3. 执行风控检查
        # 4. 执行交易
        
        self.is_running = False
    
    def analyze_and_trade(self, stock_data_list):
        """
        分析并交易
        
        Args:
            stock_data_list: 股票数据列表
            
        Returns:
            dict: 交易结果
        """
        signals = []
        
        for stock_data in stock_data_list:
            code = stock_data.get('code')
            
            # 获取交易信号
            signal_result = self.strategy_engine.get_signal(code, stock_data)
            
            # 风控检查
            if signal_result['signal'] == 'buy':
                allowed, reason = self.risk_manager.check_buy_allowed(
                    code,
                    self.cash * 0.1,  # 假设买入 10% 仓位
                    stock_data.get('price', 0)
                )
                
                if not allowed:
                    signal_result['signal'] = 'hold'
                    signal_result['reason'] = f"风控拦截: {reason}"
            
            signals.append({
                'code': code,
                'name': stock_data.get('name'),
                **signal_result
            })
        
        # 返回信号
        return {
            'signals': signals,
            'cash': self.cash,
            'positions': self.positions,
            'timestamp': datetime.now().isoformat()
        }
    
    def execute_buy(self, code, price, volume):
        """执行买入"""
        cost = price * volume
        
        if cost > self.cash:
            logger.warning(f"资金不足，无法买入 {code}")
            return False
        
        self.cash -= cost
        self.positions[code] = {
            'volume': volume,
            'cost': price,
            'buy_time': datetime.now().isoformat()
        }
        
        self.trade_history.append({
            'time': datetime.now().isoformat(),
            'code': code,
            'action': 'BUY',
            'price': price,
            'volume': volume,
            'cost': cost
        })
        
        logger.info(f"🟢 买入 {code} {volume}股 @ ¥{price:.2f}")
        
        return True
    
    def execute_sell(self, code, price, volume=None):
        """执行卖出"""
        if code not in self.positions:
            logger.warning(f"没有持仓 {code}")
            return False
        
        position = self.positions[code]
        sell_volume = volume or position['volume']
        
        revenue = price * sell_volume
        
        self.cash += revenue
        
        # 更新持仓
        if volume and volume < position['volume']:
            position['volume'] -= volume
        else:
            del self.positions[code]
        
        self.trade_history.append({
            'time': datetime.now().isoformat(),
            'code': code,
            'action': 'SELL',
            'price': price,
            'volume': sell_volume,
            'revenue': revenue,
            'profit': revenue - (position['cost'] * sell_volume)
        })
        
        logger.info(f"🔴 卖出 {code} {sell_volume}股 @ ¥{price:.2f}")
        
        return True
    
    def get_portfolio_value(self, current_prices):
        """获取组合市值"""
        value = self.cash
        
        for code, position in self.positions.items():
            if code in current_prices:
                value += current_prices[code] * position['volume']
        
        return value
    
    def get_status(self):
        """获取状态"""
        return {
            'is_running': self.is_running,
            'cash': self.cash,
            'positions': self.positions,
            'trade_count': len(self.trade_history),
            'last_update': self.last_update
        }
    
    def save_state(self, filepath='trading_state.json'):
        """保存状态"""
        state = {
            'cash': self.cash,
            'positions': self.positions,
            'trade_history': self.trade_history,
            'saved_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"💾 状态已保存到 {filepath}")
    
    def load_state(self, filepath='trading_state.json'):
        """加载状态"""
        if not os.path.exists(filepath):
            return
        
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        self.cash = state.get('cash', self.initial_capital)
        self.positions = state.get('positions', {})
        self.trade_history = state.get('trade_history', [])
        
        logger.info(f"💾 状态已从 {filepath} 加载")


# 测试
if __name__ == "__main__":
    logger.add("./logs/trading_engine.log")
    
    engine = TradingEngine()
    
    # 模拟交易
    test_stocks = [
        {'code': '600000', 'name': '浦发银行', 'price': 10.85, 'change': 2.5, 'volume_ratio': 1.8},
        {'code': '600519', 'name': '贵州茅台', 'price': 1720.0, 'change': 1.2, 'volume_ratio': 1.2},
    ]
    
    result = engine.analyze_and_trade(test_stocks)
    
    print("\n" + "="*60)
    print("🎰 交易引擎测试")
    print("="*60)
    
    for signal in result['signals']:
        print(f"\n股票: {signal['code']} {signal['name']}")
        print(f"信号: {signal['signal']} (置信度: {signal['confidence']:.2%})")
        print(f"投票: {signal['votes']}")
        print(f"原因: {signal['reason']}")
    
    print(f"\n现金: ¥{result['cash']:,.0f}")
    print("="*60)
