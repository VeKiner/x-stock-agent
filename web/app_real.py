"""
X-Stock Agent - 真实数据版（强制真实）
"""

import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="🦞 X-Stock 交易智体", page_icon="🦞", layout="wide")

st.markdown("""
<style>
.main-header { font-size: 2.5rem; color: #1f77b4; text-align: center; }
.up { color: #ff0000; font-weight: bold; }
.down { color: #00cc00; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🦞 X-Stock 自主交易智体</p>', unsafe_allow_html=True)
st.markdown(f"**更新时间：{datetime.now().strftime('%H:%M:%S')}**")
st.markdown("---")

# ===== 真实数据获取 =====
@st.cache_data(ttl=60)
def get_real_stock_data():
    """强制获取真实A股数据"""
    import akshare as ak
    
    # 获取全市场实时行情
    df = ak.stock_zh_a_spot()
    
    # 热门股票
    codes = ['600000', '600519', '000001', '600036', '601318', '601398', '000333', '300750']
    df = df[df['code'].isin(codes)].copy()
    
    # 转换类型
    df['latest_price'] = pd.to_numeric(df['latest_price'], errors='coerce')
    df['change_percent'] = pd.to_numeric(df['change_percent'], errors='coerce')
    df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    
    # 返回列表
    stocks = []
    for _, r in df.iterrows():
        stocks.append({
            'code': r['code'],
            'name': r['name'],
            'price': r['latest_price'],
            'change': r['change_percent'],
            'volume': r['volume'],
            'amount': r['amount']
        })
    
    return stocks

# 获取数据
try:
    stocks = get_real_stock_data()
    data_source = "📡 AKShare 真实数据"
except Exception as e:
    st.error(f"数据获取失败: {e}")
    st.stop()

# 侧边栏
with st.sidebar:
    st.success("🟢 运行中")
    st.write(f"数据源: {data_source}")
    st.write(f"股票数: {len(stocks)}")
    st.markdown("---")
    st.caption("⚠️ 风险提示")

# 核心指标
portfolio = [
    {'code': '600519', 'name': '贵州茅台', 'volume': 50, 'cost': 1650.0},
    {'code': '600000', 'name': '浦发银行', 'volume': 5000, 'cost': 10.5},
]

stock_dict = {s['code']: s for s in stocks}
total_value = 1000000

positions = []
for pos in portfolio:
    if pos['code'] in stock_dict:
        s = stock_dict[pos['code']]
        profit = (s['price'] - pos['cost']) * pos['volume']
        positions.append({
            'code': pos['code'], 'name': pos['name'],
            'volume': pos['volume'], 'cost': pos['cost'],
            'price': s['price'], 'change': s['change'],
            'profit': profit,
            'profit_pct': (s['price'] - pos['cost']) / pos['cost'] * 100
        })
        total_value += profit

total_profit = total_value - 1000000

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 总资产", f"¥{total_value:,.0f}", f"{total_profit/1000000*100:.2f}%")
col2.metric("📈 今日盈亏", f"¥{total_profit:+,.0f}")
col3.metric("🎯 累计收益", f"¥{total_profit:+,.0f}")
col4.metric("📊 持仓", len(positions))

st.markdown("---")

# 实时行情
st.subheader("📈 A股实时行情")

df_display = pd.DataFrame(stocks)
df_display['涨跌幅'] = df_display['change'].apply(lambda x: f'<span class="{"up" if x > 0 else "down"}">{x:+.2f}%</span>')
df_display['现价'] = df_display['price'].apply(lambda x: f"¥{x:.2f}")
df_display['成交量'] = df_display['volume'].apply(lambda x: f"{x/10000:.1f}万")

st.write(df_display[['code', 'name', '涨跌幅', '现价', '成交量']].to_html(index=False, escape=False), unsafe_allow_html=True)

st.markdown("---")

# 持仓
col5, col6 = st.columns(2)
with col5:
    st.subheader("📦 持仓")
    if positions:
        dfp = pd.DataFrame(positions)
        dfp['盈亏'] = dfp['profit'].apply(lambda x: f"¥{x:+,.0f}")
        dfp['盈亏率'] = dfp['profit_pct'].apply(lambda x: f"{x:+.2f}%")
        st.dataframe(dfp[['code', 'name', 'volume', 'cost', 'price', '盈亏', '盈亏率']], hide_index=True, use_container_width=True)

with col6:
    st.subheader("🔔 信号")
    for s in sorted(stocks, key=lambda x: x['change'], reverse=True)[:4]:
        if s['change'] > 2:
            st.markdown(f"🟢 买入 {s['code']} {s['name']} @ ¥{s['price']:.2f} (+{s['change']:.2f}%)")
        elif s['change'] < -2:
            st.markdown(f"🔴 关注 {s['code']} {s['name']} @ ¥{s['price']:.2f} ({s['change']:.2f}%)")

st.markdown("---")
st.caption("🦞 X-Stock | 真实数据驱动")
