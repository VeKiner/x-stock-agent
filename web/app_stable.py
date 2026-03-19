"""
X-Stock Agent - 超级稳定版
真实数据优先，备用数据保障显示
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# 页面配置
st.set_page_config(page_title="🦞 X-Stock", page_icon="🦞", layout="wide")

st.markdown("""
<style>
.main-header { font-size: 2.5rem; color: #1f77b4; text-align: center; }
.up { color: #ff0000; } .down { color: #00cc00; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🦞 X-Stock 自主交易智体</p>', unsafe_allow_html=True)
st.markdown(f"**更新时间：{datetime.now().strftime('%H:%M:%S')}**")
st.markdown("---")

# ===== 数据获取 =====
def get_stock_data():
    """获取股票数据 - 真实优先，备用保障"""
    
    # 方法1: 尝试 AKShare
    try:
        import akshare as ak
        df = ak.stock_zh_a_spot()
        
        watchlist = ['600000', '600519', '000001', '600036', '601318', '601398', '000333', '300750']
        df = df[df['code'].isin(watchlist)].copy()
        
        for col in ['latest_price', 'change_percent', 'volume', 'amount']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        stocks = []
        for _, row in df.iterrows():
            stocks.append({
                'code': row.get('code', ''),
                'name': row.get('name', ''),
                'price': float(row.get('latest_price', 0)),
                'change': float(row.get('change_percent', 0)),
                'volume': row.get('volume', 0),
                'source': '📡 AKShare'
            })
        
        if len(stocks) > 0:
            return stocks, True
    except Exception as e:
        pass
    
    # 方法2: 备用数据（确保显示）
    st.warning("⚠️ 实时数据暂时无法获取，显示备用数据")
    
    return [
        {'code': '600519', 'name': '贵州茅台', 'price': 1720.0, 'change': 1.25, 'volume': 123456, 'source': '📱 备用数据'},
        {'code': '600036', 'name': '招商银行', 'price': 35.80, 'change': 0.85, 'volume': 234567, 'source': '📱 备用数据'},
        {'code': '601318', 'name': '中国平安', 'price': 48.50, 'change': -0.52, 'volume': 345678, 'source': '📱 备用数据'},
        {'code': '600000', 'name': '浦发银行', 'price': 10.85, 'change': 1.12, 'volume': 456789, 'source': '📱 备用数据'},
        {'code': '000001', 'name': '平安银行', 'price': 15.60, 'change': 0.38, 'volume': 567890, 'source': '📱 备用数据'},
        {'code': '601398', 'name': '工商银行', 'price': 5.23, 'change': 0.19, 'volume': 678901, 'source': '📱 备用数据'},
    ], False

# ===== 获取数据 =====
stocks, data_ok = get_stock_data()

# ===== 侧边栏 =====
with st.sidebar:
    st.success("🟢 系统运行中")
    st.write(f"数据源: {'📡 AKShare 实时' if data_ok else '📱 备用数据'}")
    
    st.markdown("---")
    st.markdown("### 📊 自选股")
    st.code("600519 贵州茅台\n600036 招商银行\n601318 中国平安")
    
    st.markdown("---")
    st.caption("⚠️ 风险提示：本页面仅供模拟参考，不构成投资建议")

# ===== 核心指标 =====
portfolio = [
    {'code': '600519', 'name': '贵州茅台', 'volume': 50, 'cost': 1650.0},
    {'code': '600000', 'name': '浦发银行', 'volume': 5000, 'cost': 10.5},
]

total_value = 1000000
positions = []

stock_dict = {s['code']: s for s in stocks}

for pos in portfolio:
    if pos['code'] in stock_dict:
        s = stock_dict[pos['code']]
        profit = (s['price'] - pos['cost']) * pos['volume']
        positions.append({
            'code': pos['code'],
            'name': pos['name'],
            'volume': pos['volume'],
            'cost': pos['cost'],
            'price': s['price'],
            'change': s['change'],
            'profit': profit,
            'profit_pct': (s['price'] - pos['cost']) / pos['cost'] * 100
        })
        total_value += profit

total_profit = total_value - 1000000

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 总资产", f"¥{total_value:,.0f}", f"{total_profit/1000000*100:.2f}%")
col2.metric("📈 今日盈亏", f"¥{total_profit:+,.0f}")
col3.metric("🎯 累计收益", f"¥{total_profit:+,.0f}")
col4.metric("📊 持仓数", len(positions))

st.markdown("---")

# ===== 实时行情 =====
st.subheader("📈 A 股实时行情")

df_display = pd.DataFrame(stocks)
df_display['涨跌幅'] = df_display['change'].apply(lambda x: f'<span class="{"up" if x > 0 else "down"}">{x:+.2f}%</span>')
df_display['现价'] = df_display['price'].apply(lambda x: f"¥{x:.2f}")
df_display['成交量'] = df_display['volume'].apply(lambda x: f"{x/10000:.1f}万")

st.write(df_display[['code', 'name', '涨跌幅', '现价', '成交量', 'source']].to_html(index=False, escape=False), unsafe_allow_html=True)

st.markdown("---")

# ===== 持仓 =====
col5, col6 = st.columns(2)

with col5:
    st.subheader("📦 当前持仓")
    if positions:
        df_pos = pd.DataFrame(positions)
        df_pos['盈亏'] = df_pos['profit'].apply(lambda x: f"¥{x:+,.0f}")
        df_pos['盈亏率'] = df_pos['profit_pct'].apply(lambda x: f"{x:+.2f}%")
        st.dataframe(df_pos[['code', 'name', 'volume', 'cost', 'price', '盈亏', '盈亏率']], hide_index=True, use_container_width=True)

with col6:
    st.subheader("🔔 交易信号")
    for s in sorted(stocks, key=lambda x: x['change'], reverse=True)[:4]:
        if s['change'] > 2:
            st.markdown(f"🟢 **买入** `{s['code']}` {s['name']} @ ¥{s['price']:.2f} (+{s['change']:.2f}%)")
        elif s['change'] < -2:
            st.markdown(f"🔴 **关注** `{s['code']}` {s['name']} @ ¥{s['price']:.2f} ({s['change']:.2f}%)")

st.markdown("---")
st.caption("🦞 X-Stock 自主交易智体 | 7×24小时运行 | 数据来源：AKShare")
