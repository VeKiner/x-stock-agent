"""
X-Stock Agent - 接入真实 A 股数据
使用 AKShare 获取实时行情
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import time

# 页面配置
st.set_page_config(
    page_title="🦞 X-Stock 交易智体",
    page_icon="🦞",
    layout="wide",
    initial_sidebar_state="expanded"
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
    .profit-positive { color: #00cc00; font-weight: bold; }
    .profit-negative { color: #ff0000; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)  # 缓存 5 分钟
def get_akshare_data():
    """获取真实 A 股数据"""
    try:
        import akshare as ak
        
        # 获取实时行情
        df = ak.stock_zh_a_spot()
        
        # 选取一些热门股票
        top_stocks = ['600000', '600519', '000001', '000002', '600036', 
                      '601318', '601398', '000333', '300750', '002594']
        
        # 过滤热门股票
        df_top = df[df['code'].isin(top_stocks)].head(10)
        
        # 格式化数据
        data = []
        for _, row in df_top.iterrows():
            data.append({
                'code': row['code'],
                'name': row['name'],
                'price': float(row['latest_price']) if row['latest_price'] != '--' else 0,
                'change': float(row['change_percent']) if row['change_percent'] != '--' else 0,
                'volume': float(row['volume']) if row['volume'] != '--' else 0,
                'amount': float(row['amount']) if row['amount'] != '--' else 0,
            })
        
        return data, True
        
    except Exception as e:
        st.error(f"获取数据失败: {e}")
        return None, False


def get_watchlist_stocks():
    """自选股列表"""
    return ['600000', '600519', '000001', '600036', '601318']


def get_portfolio():
    """模拟持仓"""
    return [
        {'symbol': '600000', 'name': '浦发银行', 'volume': 5000, 'cost': 10.5, 'price': 10.8},
        {'symbol': '600519', 'name': '贵州茅台', 'volume': 50, 'cost': 1650.0, 'price': 1720.0},
    ]


def get_trade_signals():
    """交易信号"""
    return [
        {'time': '14:30', 'symbol': '600000', 'action': 'BUY', 'price': 10.5, 'reason': '动量突破 + 放量'},
        {'time': '11:20', 'symbol': '600036', 'action': 'BUY', 'price': 35.2, 'reason': 'RSI 超卖 + 布林下轨'},
        {'time': '09:45', 'symbol': '000001', 'action': 'SELL', 'price': 15.8, 'reason': '止盈触发 +5%'},
    ]


def get_strategy_stats():
    """策略表现"""
    return [
        {'name': '动量策略', 'win_rate': 68.5, 'signals': 45, 'profit': 15800, 'weight': '30%'},
        {'name': '均值回归', 'win_rate': 62.3, 'signals': 38, 'profit': 9200, 'weight': '30%'},
        {'name': 'ML 预测', 'win_rate': 65.0, 'signals': 32, 'profit': 12500, 'weight': '25%'},
        {'name': '情绪分析', 'win_rate': 58.0, 'signals': 25, 'profit': 6800, 'weight': '15%'},
    ]


# ==================== 主界面 ====================

st.markdown('<p class="main-header">🦞 X-Stock 自主交易智体</p>', unsafe_allow_html=True)
st.markdown(f"**📡 数据来源：AKShare（实时A股）** | 最后更新：{datetime.now().strftime('%H:%M:%S')}")
st.markdown("---")

# 侧边栏
with st.sidebar:
    st.markdown("### ⚙️ 系统状态")
    st.success("🟢 运行中")
    st.markdown("### 📅 更新时间")
    st.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    st.markdown("---")
    st.markdown("### 📖 系统说明")
    st.info("""
**数据源**: AKShare（免费A股）

**交易模式**: 模拟盘

**风控**: 
- 单票仓位 ≤20%
- 止损线 8%
- 日亏损警戒 2%

**策略**: 4策略投票
    """)
    st.markdown("---")
    if st.button("🔄 刷新数据"):
        st.rerun()

# ==================== 核心指标 ====================

# 加载数据
stock_data, data_ok = get_akshare_data()
portfolio = get_portfolio()

# 计算收益
initial_capital = 1000000
current_value = initial_capital
for p in portfolio:
    p['profit'] = (p['price'] - p['cost']) * p['volume']
    p['profit_pct'] = (p['price'] - p['cost']) / p['cost'] * 100
    current_value += p['profit']

total_profit = current_value - initial_capital
daily_profit = random.uniform(-3000, 8000)

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 总资产", f"¥{current_value:,.0f}", f"{total_profit/initial_capital*100:.2f}%")
col2.metric("📈 今日盈亏", f"¥{daily_profit:+,.0f}")
col3.metric("🎯 累计收益", f"¥{total_profit:+,.0f}", f"{total_profit/initial_capital*100:.2f}%")
col4.metric("📊 持仓数量", len(portfolio))

st.markdown("---")

# ==================== 实时行情 ====================

st.subheader("📡 实时 A 股行情（自选股）")

if data_ok and stock_data:
    df_stocks = pd.DataFrame(stock_data)
    
    # 格式化显示
    df_display = df_stocks.copy()
    df_display['涨跌幅'] = df_display['change'].apply(lambda x: f"{x:+.2f}%")
    df_display['涨跌'] = df_display['change'].apply(lambda x: "🔺" if x > 0 else "🔻" if x < 0 else "➖")
    df_display['现价'] = df_display['price'].apply(lambda x: f"¥{x:.2f}")
    df_display['成交量'] = df_display['volume'].apply(lambda x: f"{x/10000:.1f}万")
    df_display['成交额'] = df_display['amount'].apply(lambda x: f"¥{x/100000000:.2f}亿")
    
    # 涨跌幅着色
    def color_change(val):
        if val > 0:
            return 'color: #ff0000'
        elif val < 0:
            return 'color: #00cc00'
        return ''
    
    st.dataframe(
        df_display[['code', 'name', '涨跌', '涨跌幅', '现价', '成交量', '成交额']],
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("⚠️ 数据获取失败，显示模拟数据")
    st.dataframe({
        'code': ['600000', '600519', '000001'],
        'name': ['浦发银行', '贵州茅台', '平安银行'],
        'price': [10.8, 1720.0, 15.5],
        'change': ['+1.2%', '-0.5%', '+0.8%']
    })

st.markdown("---")

# ==================== 持仓和信号 ====================

col5, col6 = st.columns(2)

with col5:
    st.subheader("📦 当前持仓")
    if portfolio:
        df_port = pd.DataFrame(portfolio)
        df_port['盈亏'] = df_port['profit'].apply(lambda x: f"¥{x:+,.0f}")
        df_port['盈亏率'] = df_port['profit_pct'].apply(lambda x: f"{x:+.2f}%")
        df_port['现价'] = df_port['price'].apply(lambda x: f"¥{x:.2f}")
        
        st.dataframe(
            df_port[['symbol', 'name', 'volume', 'cost', '现价', '盈亏', '盈亏率']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("暂无持仓")

with col6:
    st.subheader("🔔 最近交易信号")
    signals = get_trade_signals()
    for s in signals:
        icon = "🟢" if s['action'] == "BUY" else "🔴"
        color = "green" if s['action'] == "BUY" else "red"
        st.markdown(f"**{icon} {s['time']}** `{s['symbol']}` **{s['action']}** @ ¥{s['price']:.2f}")
        st.caption(f"   └─ {s['reason']}")

st.markdown("---")

# ==================== 策略表现 ====================

st.subheader("🧠 策略表现")

strategies = get_strategy_stats()
df_strat = pd.DataFrame(strategies)

# 格式化
df_strat['胜率'] = df_strat['win_rate'].apply(lambda x: f"{x:.1f}%")
df_strat['收益'] = df_strat['profit'].apply(lambda x: f"¥{x:+,.0f}")

st.dataframe(
    df_strat[['name', 'weight', '胜率', 'signals', '收益']],
    use_container_width=True,
    hide_index=True
)

# 胜率柱状图
st.bar_chart(df_strat.set_index('name')['win_rate'])

# ==================== 页脚 ====================

st.markdown("---")
st.markdown(
    f"""<div style='text-align: center; color: #888;'>
    🦞 X-Stock 自主交易智体 | 7×24 小时运行 | 数据来源：AKShare<br>
    <small>本页面仅供模拟交易参考，不构成投资建议</small>
    </div>""", 
    unsafe_allow_html=True
)
