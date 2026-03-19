"""
X-Stock Agent - 最终稳定版
无需外部依赖，自动适配
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import random

# 页面配置
st.set_page_config(page_title="🦞 X-Stock 交易智体", page_icon="🦞", layout="wide")

# 样式
st.markdown("""
<style>
.main-header { font-size: 2.5rem; color: #1f77b4; text-align: center; margin-bottom: 1rem; }
.up { color: #ff0000; font-weight: bold; }
.down { color: #00cc00; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 标题
st.markdown('<p class="main-header">🦞 X-Stock 自主交易智体</p>', unsafe_allow_html=True)
st.markdown(f"**更新时间：{datetime.now().strftime('%H:%M:%S')}**")
st.markdown("---")

# ===== 数据获取 =====
def get_stock_data():
    """获取股票数据 - 多重保障"""
    
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
                'code': str(row.get('code', '')),
                'name': str(row.get('name', '')),
                'price': float(row.get('latest_price', 0)),
                'change': float(row.get('change_percent', 0)),
                'volume': float(row.get('volume', 0)),
                'source': '📡 AKShare实时'
            })
        
        if len(stocks) >= 5:
            return stocks, True
    except Exception as e:
        pass
    
    # 方法2: 备用 - 使用确定的静态数据
    return [
        {'code': '600519', 'name': '贵州茅台', 'price': 1720.00, 'change': 1.25, 'volume': 123456, 'source': '✅ 备用数据'},
        {'code': '600036', 'name': '招商银行', 'price': 35.80, 'change': 0.85, 'volume': 234567, 'source': '✅ 备用数据'},
        {'code': '601318', 'name': '中国平安', 'price': 48.50, 'change': -0.52, 'volume': 345678, 'source': '✅ 备用数据'},
        {'code': '600000', 'name': '浦发银行', 'price': 10.85, 'change': 1.12, 'volume': 456789, 'source': '✅ 备用数据'},
        {'code': '000001', 'name': '平安银行', 'price': 15.60, 'change': 0.38, 'volume': 567890, 'source': '✅ 备用数据'},
        {'code': '601398', 'name': '工商银行', 'price': 5.23, 'change': 0.19, 'volume': 678901, 'source': '✅ 备用数据'},
        {'code': '000333', 'name': '美的集团', 'price': 62.50, 'change': -0.35, 'volume': 234567, 'source': '✅ 备用数据'},
        {'code': '300750', 'name': '宁德时代', 'price': 185.60, 'change': 2.15, 'volume': 345678, 'source': '✅ 备用数据'},
    ], False

# 获取数据
stocks, data_ok = get_stock_data()

# ===== 侧边栏 =====
with st.sidebar:
    st.success("🟢 系统运行中")
    st.markdown("---")
    st.markdown("### 📊 系统状态")
    st.write(f"数据源: {'📡 AKShare 实时' if data_ok else '✅ 备用数据'}")
    st.write(f"更新时间: {datetime.now().strftime('%H:%M:%S')}")
    
    st.markdown("---")
    st.markdown("### 📈 自选股")
    st.code("600519 贵州茅台\n600036 招商银行\n601318 中国平安\n600000 浦发银行\n000001 平安银行")
    
    st.markdown("---")
    st.caption("⚠️ 风险提示：本页面仅供模拟参考，不构成投资建议")

# ===== 核心指标 =====
# 持仓
portfolio = [
    {'code': '600519', 'name': '贵州茅台', 'volume': 50, 'cost': 1650.0},
    {'code': '600000', 'name': '浦发银行', 'volume': 5000, 'cost': 10.5},
]

# 计算
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

# 显示指标
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 总资产", f"¥{total_value:,.0f}", f"{total_profit/1000000*100:.2f}%")
col2.metric("📈 今日盈亏", f"¥{total_profit:+,.0f}")
col3.metric("🎯 累计收益", f"¥{total_profit:+,.0f}")
col4.metric("📊 持仓数", len(positions))

st.markdown("---")

# ===== 实时行情 =====

st.subheader("📈 A 股实时行情")

df = pd.DataFrame(stocks)
df['涨跌幅'] = df['change'].apply(lambda x: f'<span class="{"up" if x > 0 else "down"}">{x:+.2f}%</span>')
df['现价'] = df['price'].apply(lambda x: f"¥{x:.2f}")
df['成交量'] = df['volume'].apply(lambda x: f"{x/10000:.1f}万")

cols = ['code', 'name', '涨跌幅', '现价', '成交量', 'source']
st.write(df[cols].to_html(index=False, escape=False), unsafe_allow_html=True)

st.markdown("---")

# ===== 持仓和信号 =====
col5, col6 = st.columns(2)

with col5:
    st.subheader("📦 当前持仓")
    if positions:
        df_pos = pd.DataFrame(positions)
        df_pos['盈亏'] = df_pos['profit'].apply(lambda x: f"¥{x:+,.0f}")
        df_pos['盈亏率'] = df_pos['profit_pct'].apply(lambda x: f"{x:+.2f}%")
        st.dataframe(df_pos[['code', 'name', 'volume', 'cost', 'price', '盈亏', '盈亏率']], hide_index=True, use_container_width=True)
    else:
        st.info("暂无持仓")

with col6:
    st.subheader("🔔 交易信号")
    
    # 动态生成信号
    sorted_stocks = sorted(stocks, key=lambda x: x['change'], reverse=True)
    
    for s in sorted_stocks[:5]:
        if s['change'] > 2:
            st.markdown(f"🟢 **{s['code']}** {s['name']} @ ¥{s['price']:.2f} **+{s['change']:.2f}%**")
            st.caption("   → 动量强劲，建议关注")
        elif s['change'] < -2:
            st.markdown(f"🔴 **{s['code']}** {s['name']} @ ¥{s['price']:.2f} **{s['change']:.2f}%**")
            st.caption("   → 超跌反弹机会")

st.markdown("---")

# ===== 页脚 =====
st.caption("🦞 X-Stock 自主交易智体 | 7×24小时运行 | 数据来源：AKShare + 备用保障")
