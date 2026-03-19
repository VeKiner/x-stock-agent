"""
X-Stock Agent - Risk Management Module
严格的风险控制模块，确保零风险原则
"""

from loguru import logger
from datetime import datetime
import pandas as pd


class RiskManager:
    """风险管理器"""
    
    def __init__(self, config):
        self.config = config
        self.risk_config = config.get('risk', {})
        
        # 风险参数
        self.max_position_per_stock = self.risk_config.get('max_position_per_stock', 0.20)
        self.max_daily_loss = self.risk_config.get('max_daily_loss', 0.02)
        self.max_drawdown_warning = self.risk_config.get('max_drawdown_warning', 0.10)
        self.stop_loss_per_stock = self.risk_config.get('stop_loss_per_stock', 0.08)
        
        # 状态追踪
        self.daily_profit = 0.0
        self.total_capital = 0.0
        self.peak_capital = 0.0
        self.position_dict = {}  # {symbol: {'cost': x, 'volume': y, 'current_price': z}}
        
        logger.info(f"风险管理器初始化完成")
        logger.info(f"  - 单票最大仓位：{self.max_position_per_stock*100}%")
        logger.info(f"  - 单日最大亏损：{self.max_daily_loss*100}%")
        logger.info(f"  - 总回撤警戒线：{self.max_drawdown_warning*100}%")
        logger.info(f"  - 单票止损线：{self.stop_loss_per_stock*100}%")
    
    def set_initial_capital(self, capital):
        """设置初始资金"""
        self.total_capital = capital
        self.peak_capital = capital
        logger.info(f"初始资金设置为：{capital:,.2f}")
    
    def update_capital(self, current_capital):
        """更新当前资金"""
        self.total_capital = current_capital
        if current_capital > self.peak_capital:
            self.peak_capital = current_capital
    
    def update_daily_profit(self, profit):
        """更新当日盈亏"""
        self.daily_profit = profit
    
    def check_buy_allowed(self, symbol, amount, current_price):
        """
        检查是否允许买入
        
        Args:
            symbol: 股票代码
            amount: 买入金额
            current_price: 当前价格
            
        Returns:
            tuple: (allowed: bool, reason: str)
        """
        # 1. 检查单日亏损限制
        if self.daily_profit < -self.total_capital * self.max_daily_loss:
            return False, f"触发单日亏损限制（{self.max_daily_loss*100}%）"
        
        # 2. 检查总回撤警戒线
        drawdown = (self.peak_capital - self.total_capital) / self.peak_capital
        if drawdown >= self.max_drawdown_warning:
            return False, f"触发总回撤警戒线（{self.max_drawdown_warning*100}%）"
        
        # 3. 检查单票仓位限制
        current_position_value = self.position_dict.get(symbol, {}).get('volume', 0) * \
                                self.position_dict.get(symbol, {}).get('current_price', 0)
        new_position_value = current_position_value + amount
        
        if new_position_value > self.total_capital * self.max_position_per_stock:
            return False, f"超过单票最大仓位限制（{self.max_position_per_stock*100}%）"
        
        # 4. 检查总仓位（可选：可以添加最大总仓位限制）
        total_position = sum(
            pos.get('volume', 0) * pos.get('current_price', 0) 
            for pos in self.position_dict.values()
        )
        if total_position + amount > self.total_capital * 0.95:
            return False, "总仓位过高（>95%）"
        
        return True, "通过风控检查"
    
    def check_sell_triggered(self, symbol, current_price):
        """
        检查是否触发卖出（止损）
        
        Args:
            symbol: 股票代码
            current_price: 当前价格
            
        Returns:
            tuple: (should_sell: bool, reason: str, sell_ratio: float)
        """
        if symbol not in self.position_dict:
            return False, "", 0.0
        
        position = self.position_dict[symbol]
        cost_price = position['cost']
        
        # 计算亏损比例
        loss_ratio = (cost_price - current_price) / cost_price
        
        # 检查止损
        if loss_ratio >= self.stop_loss_per_stock:
            return True, f"触发止损线（亏损{loss_ratio*100:.2f}%）", 1.0
        
        return False, "", 0.0
    
    def update_position(self, symbol, volume, cost_price, current_price):
        """更新持仓信息"""
        self.position_dict[symbol] = {
            'volume': volume,
            'cost': cost_price,
            'current_price': current_price,
            'update_time': datetime.now()
        }
    
    def remove_position(self, symbol):
        """移除持仓"""
        if symbol in self.position_dict:
            del self.position_dict[symbol]
    
    def get_risk_report(self):
        """生成风险报告"""
        drawdown = (self.peak_capital - self.total_capital) / self.peak_capital if self.peak_capital > 0 else 0
        
        report = {
            'total_capital': self.total_capital,
            'peak_capital': self.peak_capital,
            'daily_profit': self.daily_profit,
            'daily_profit_ratio': self.daily_profit / self.total_capital if self.total_capital > 0 else 0,
            'max_drawdown': drawdown,
            'position_count': len(self.position_dict),
            'risk_status': 'normal'
        }
        
        # 风险评估
        if drawdown >= self.max_drawdown_warning:
            report['risk_status'] = 'warning'
        elif self.daily_profit < -self.total_capital * self.max_daily_loss:
            report['risk_status'] = 'danger'
        
        return report
    
    def log_risk_check(self, action, symbol, result, reason=''):
        """记录风控检查日志"""
        status = "✅" if result else "❌"
        logger.info(f"[风控检查] {status} {action} {symbol}: {reason}")


# 测试
if __name__ == "__main__":
    logger.add("./logs/risk_manager_test.log")
    
    config = {
        'risk': {
            'max_position_per_stock': 0.20,
            'max_daily_loss': 0.02,
            'max_drawdown_warning': 0.10,
            'stop_loss_per_stock': 0.08
        }
    }
    
    rm = RiskManager(config)
    rm.set_initial_capital(1000000)
    
    # 测试买入检查
    allowed, reason = rm.check_buy_allowed('600000', 100000, 10.5)
    print(f"买入检查：{allowed}, {reason}")
    
    # 模拟持仓
    rm.update_position('600000', 10000, 10.5, 10.5)
    
    # 测试止损检查
    should_sell, reason, ratio = rm.check_sell_triggered('600000', 9.5)
    print(f"止损检查：{should_sell}, {reason}, {ratio}")
    
    # 获取风险报告
    report = rm.get_risk_report()
    print(f"\n风险报告：{report}")
