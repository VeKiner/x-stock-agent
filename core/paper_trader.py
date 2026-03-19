"""
X-Stock Agent - 模拟交易执行模块
"""

import json
from datetime import datetime
from loguru import logger


class PaperTrader:
    """模拟交易执行器"""
    
    def __init__(self, initial_capital=1000000):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions = {}  # {code: {'volume': x, 'cost': y}}
        self.trade_history = []
        
        logger.info("📝 模拟交易初始化")
        logger.info(f"   初始资金: ¥{initial_capital:,.0f}")
    
    def can_buy(self, price, volume):
        """检查是否可以买入"""
        cost = price * volume
        return self.cash >= cost
    
    def buy(self, code, price, volume, reason=""):
        """执行买入"""
        cost = price * volume
        
        if not self.can_buy(price, volume):
            logger.warning(f"资金不足，无法买入 {code}")
            return False
        
        # 扣除资金
        self.cash -= cost
        
        # 记录持仓
        if code in self.positions:
            old_vol = self.positions[code]['volume']
            old_cost = self.positions[code]['cost']
            new_vol = old_vol + volume
            new_cost = (old_cost * old_vol + cost) / new_vol
            self.positions[code] = {'volume': new_vol, 'cost': new_cost}
        else:
            self.positions[code] = {'volume': volume, 'cost': price}
        
        # 记录交易
        self.trade_history.append({
            'time': datetime.now().isoformat(),
            'code': code,
            'action': 'BUY',
            'price': price,
            'volume': volume,
            'cost': cost,
            'reason': reason
        })
        
        logger.info(f"🟢 买入 {code} {volume}股 @ ¥{price:.2f} (理由: {reason})")
        return True
    
    def sell(self, code, price, volume=None, reason=""):
        """执行卖出"""
        if code not in self.positions:
            logger.warning(f"没有持仓 {code}")
            return False
        
        position = self.positions[code]
        sell_volume = volume or position['volume']
        
        # 检查数量
        if sell_volume > position['volume']:
            logger.warning(f"持仓不足: {code}")
            return False
        
        # 计算收入
        revenue = price * sell_volume
        self.cash += revenue
        
        # 更新持仓
        if sell_volume == position['volume']:
            del self.positions[code]
        else:
            position['volume'] -= sell_volume
        
        # 计算盈亏
        profit = revenue - (position['cost'] * sell_volume)
        
        # 记录交易
        self.trade_history.append({
            'time': datetime.now().isoformat(),
            'code': code,
            'action': 'SELL',
            'price': price,
            'volume': sell_volume,
            'revenue': revenue,
            'profit': profit,
            'reason': reason
        })
        
        logger.info(f"🔴 卖出 {code} {sell_volume}股 @ ¥{price:.2f} (盈利: ¥{profit:,.0f})")
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
            'cash': self.cash,
            'positions': self.positions,
            'trade_count': len(self.trade_history),
            'initial_capital': self.initial_capital
        }
    
    def save_state(self, filepath="trading_state.json"):
        """保存状态"""
        state = {
            'cash': self.cash,
            'positions': self.positions,
            'trade_history': self.trade_history,
            'saved_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"💾 交易状态已保存")


# 测试
if __name__ == "__main__":
    logger.add("./logs/paper_trader.log")
    
    trader = PaperTrader(1000000)
    
    # 测试买入
    trader.buy('600519', 1720.0, 50, '动量策略信号')
    trader.buy('600000', 10.5, 5000, '均线金叉')
    
    # 测试状态
    status = trader.get_status()
    print(f"\n资金: ¥{status['cash']:,.0f}")
    print(f"持仓: {status['positions']}")
    
    # 测试卖出
    trader.sell('600519', 1750.0, reason='止盈')
    
    # 保存
    trader.save_state()
