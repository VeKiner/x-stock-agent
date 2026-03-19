"""
X-Stock Agent - 极简版 Web 看板
Streamlit Cloud 专用，确保能部署成功
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random

# 页面配置
st.set_page_config(
    page_title="🦞 X-Stock 交易智体",
    page_icon="🦞",
    layout="wide"
)

# 自定义样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


def get_mock_data():
    """生成模拟数据"""
    # 资产曲线
    dates = pd.date_range(end=datetime.now(), periods=30)
    base = 1000000
    returns = [random.uniform(-0.02, 0.03) for _ in range(30)]
    equity = [base * (1 + sum(returns[:i+1])/100) for i in range(30)]
    
    # 持仓
    positions = [
        {'symbol': '600000', 'name': '浦发银行', 'volume': 5000, 'cost': 10.5, 'price': 10.8},
        {'symbol': '000001', 'name': '平安银行', 'volume': 3000, 'cost': 15.2, 'price': 15.5},
        {'symbol': '600519', 'name': '贵州茅台', 'volume': 100, 'cost': 1800, 'price': 1850},
    ]
    for p in positions:
        p['profit'] = (p['price'] - p['cost']) * p['volume']
        p['profit_pct'] = (p['price'] - p['cost']) / p['cost'] * 100
    
    # 信号
    signals = [
        {'time': '14:30', 'symbol': '600000', 'action': 'BUY', 'price': 10.5, 'reason': '动量突破'},
        {'time': '13:15', 'symbol': '000030', 'action': 'SELL', 'price': 25.3, 'reason': '止损触发'},
        {'time': '10:00', 'symbol': '000001', 'action': 'BUY', 'price': 15.2, 'reason': '均线金叉'},
    ]
    
    # 策略
    strategies = [
        {'name': '动量策略', 'win_rate': 65.5, 'signals': 42, 'profit': 12500},
        {'name': '均值回归', 'win_rate': 58.2, 'signals': 38, 'profit': 8900},
        {'name': 'ML 预测', 'win_rate': 61.0, 'signals': 35, 'profit': 10200},
        {'name': '情绪分析', 'win_rate': 55.0, 'signals': 28, 'profit': 5600},
    ]
    
    return dates, equity, positions, signals, strategies


# 主界面
st.markdown('<p class="main-header">🦞 X-Stock 自主交易智体</p>', unsafe_allow_html=True)
st.markdown("---")

# 侧边栏
with st.sidebar:
    st.markdown("### ⚙️ 系统状态")
    st.success("🟢 运行中")
    st.markdown("### 📅 最后更新")
    st.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    st.markdown("---")
    st.markdown("### 📖 说明")
    st.info("数据源: AKShare\n\n交易模式: 模拟盘\n\n风险等级: 零风险")

# 加载数据
dates, equity, positions, signals, strategies = get_mock_data()

# 核心指标
current_value = equity[-1]
initial_capital = 1000000
total_profit = current_value - initial_capital
daily_profit = random.uniform(-5000, 10000)

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 总资产", f"¥{current_value:,.0f}", f"{total_profit/initial_capital*100:.2f}%")
col2.metric("📈 今日盈亏", f"¥{daily_profit:+,.0f}")
col3.metric("🎯 累计收益", f"¥{total_profit:+,.0f}", f"{total_profit/initial_capital*100:.2f}%")
col4.metric("📊 持仓数量", len(positions))

st.markdown("---")

# 资产曲线
st.subheader("📈 资产曲线")
chart_data = pd.DataFrame({'日期': dates, '资产': equity})
st.line_chart(chart_data.set_index('日期'))

# 持仓和信号
col5, col6 = st.columns(2)

with col5:
    st.subheader("📦 当前持仓")
    df_pos = pd.DataFrame(positions)
    if not df_pos.empty:
        df_pos['盈亏'] = df_pos['profit'].apply(lambda x: f"¥{x:+,.0f}")
        df_pos['盈亏率'] = df_pos['profit_pct'].apply(lambda x: f"{x:+.2f}%")
        st.dataframe(df_pos[['symbol', 'name', 'volume', 'cost', 'price', '盈亏', '盈亏率']], use_container_width=True)

with col6:
    st.subheader("🔔 最近交易信号")
    for s in signals:
        icon = "🟢" if s['action'] == "BUY" else "🔴"
        st.markdown(f"**{icon} {s['time']}** {s['symbol']} **{s['action']}** @ ¥{s['price']:.2f} - {s['reason']}")

st.markdown("---")

# 策略表现
st.subheader("🧠 策略表现")
df_strat = pd.DataFrame(strategies)
st.dataframe(df_strat, use_container_width=True)

# 页脚
st.markdown("---")
st.markdown(f"<div style='text-align: center; color: #888;'>🦞 X-Stock 自主交易智体 | 7×24 小时智能监控 | 模拟盘运行中</div>", unsafe_allow_html=True)
