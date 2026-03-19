"""
X-Stock Agent - 真实数据版 v2
基于 GitHub 最牛开源项目优化，接入真实 A 股数据
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="🦞 X-Stock 交易智体",
    page_icon="🦞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 样式
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: bold; color: #1f77b4; text-align: center; }
    .positive { color: #ff0000; }  /* A股涨是红色 */
    .negative { color: #00cc00; } /* A股跌是绿色 */
</style>
""", unsafe_allow_html=True)


# ==================== 数据获取 ====================
@st.cache_data(ttl=60)  # 缓存 1 分钟
def get_realtime_data():
    """获取真实 A 股数据 - 使用 AKShare"""
    try:
        import akshare as ak
        
        # 获取全市场实时行情
        df = ak.stock_zh_a_spot()
        
        # 热门自选股
        watchlist = ['600000', '600519', '000001', '600036', '601318', 
                     '601398', '000333', '300750', '002594', '000002']
        
        # 过滤
        df_watch = df[df['code'].isin(watchlist)].copy()
        
        # 转换数值类型
        for col in ['latest_price', 'change_percent', 'volume', 'amount']:
            if col in df_watch.columns:
                df_watch[col] = pd.to_numeric(df_watch[col], errors='coerce')
        
        return df_watch
        
    except Exception as e:
        st.error(f"数据获取失败: {str(e)[:100]}")
        return None


@st.cache_data(ttl=3600)
def get_stock_history(symbol, days=30):
    """获取历史K线数据"""
    try:
        import akshare as ak
        
        end = datetime.now().strftime('%Y%m%d')
        start = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        df = ak.stock_zh_a_daily(symbol=symbol, start_date=start, end_date=end)
        return df
        
    except Exception as e:
        return None


# ==================== 数据处理 ====================
def process_stock_data(df):
    """处理股票数据"""
    if df is None or df.empty:
        return []
    
    stocks = []
    for _, row in df.iterrows():
        try:
            price = float(row.get('latest_price', 0))
            change = float(row.get('change_percent', 0))
            
            stocks.append({
                'code': row.get('code', ''),
                'name': row.get('name', ''),
                'price': price,
                'change': change,
                'volume': row.get('volume', 0),
                'amount': row.get('amount', 0),
            })
        except:
            continue
    
    return stocks


# ==================== 主界面 ====================
st.markdown('<p class="main-header">🦞 X-Stock 自主交易智体</p>', unsafe_allow_html=True)
st.markdown(f"**📡 数据来源：AKShare（真实A股） | 更新时间：{datetime.now().strftime('%H:%M:%S')}**")
st.markdown("---")

# 侧边栏
with st.sidebar:
    st.markdown("### ⚙️ 系统状态")
    st.success("🟢 运行中")
    st.markdown("### 📅 最后更新")
    st.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    st.markdown("---")
    st.markdown("### 📊 自选股")
    watchlist = st.multiselect(
        "添加自选股",
        ['600000', '600519', '000001', '600036', '601318', '601398', '000333', '300750'],
        default=['600000', '600519', '000001', '600036']
    )
    
    st.markdown("---")
    st.markdown("### ⚠️ 风险提示")
    st.caption("本页面仅供模拟交易参考，不构成投资建议。投资有风险，入市需谨慎。")
    
    if st.button("🔄 刷新数据"):
        st.rerun()

# ==================== 核心指标 ====================
# 模拟持仓（后续对接真实持仓）
portfolio = {
    '600000': {'volume': 5000, 'cost': 10.5},
    '600519': {'volume': 50, 'cost': 1650.0},
}

# 获取实时数据
df_realtime = get_realtime_data()
stocks = process_stock_data(df_realtime)

# 计算持仓价值
total_value = 1000000  # 初始资金
positions = []

if stocks:
    stock_dict = {s['code']: s for s in stocks}
    
    for symbol, pos in portfolio.items():
        if symbol in stock_dict:
            s = stock_dict[symbol]
            value = s['price'] * pos['volume']
            profit = (s['price'] - pos['cost']) * pos['volume']
            profit_pct = (s['price'] - pos['cost']) / pos['cost'] * 100
            
            positions.append({
                'code': symbol,
                'name': s['name'],
                'volume': pos['volume'],
                'cost': pos['cost'],
                'price': s['price'],
                'change': s['change'],
                'value': value,
                'profit': profit,
                'profit_pct': profit_pct,
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

# ==================== 实时行情 ====================
st.subheader("📈 实时 A 股行情")

if stocks:
    # 创建 DataFrame
    df_display = pd.DataFrame(stocks)
    
    # 格式化
    df_display['涨跌幅'] = df_display['change'].apply(
        lambda x: f'<span class="{"positive" if x > 0 else "negative"}">{x:+.2f}%</span>'
    )
    df_display['现价'] = df_display['price'].apply(lambda x: f"¥{x:.2f}")
    df_display['成交量'] = df_display['volume'].apply(lambda x: f"{x/10000:.1f}万")
    df_display['成交额'] = df_display['amount'].apply(lambda x: f"¥{x/100000000:.2f}亿")
    
    # 显示
    st.write(
        df_display[['code', 'name', '涨跌幅', '现价', '成交量', '成交额']].to_html(index=False, escape=False),
        unsafe_allow_html=True
    )
else:
    st.warning("⚠️ 暂时无法获取实时数据，请检查网络连接")

st.markdown("---")

# ==================== 持仓 ====================
col5, col6 = st.columns(2)

with col5:
    st.subheader("📦 当前持仓")
    if positions:
        df_pos = pd.DataFrame(positions)
        df_pos['盈亏'] = df_pos['profit'].apply(lambda x: f"¥{x:+,.0f}")
        df_pos['盈亏率'] = df_pos['profit_pct'].apply(lambda x: f"{x:+.2f}%")
        
        st.dataframe(
            df_pos[['code', 'name', 'volume', 'cost', 'price', '盈亏', '盈亏率']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("暂无持仓")

with col6:
    st.subheader("🔔 交易信号")
    
    # 基于数据的信号
    if stocks:
        # 动量信号
        for s in sorted(stocks, key=lambda x: x['change'], reverse=True)[:3]:
            if s['change'] > 2:
                st.markdown(f"🟢 **买入** `{s['code']}` {s['name']} @ ¥{s['price']:.2f} (+{s['change']:.2f}%)")
                st.caption(f"   动量强劲，连续上涨")
            elif s['change'] < -3:
                st.markdown(f"🔴 **关注** `{s['code']}` {s['name']} @ ¥{s['price']:.2f} ({s['change']:.2f}%)")
                st.caption(f"   超跌反弹机会")

# ==================== 页脚 ====================
st.markdown("---")
st.markdown(
    f"""<div style='text-align: center; color: #888;'>
    🦞 X-Stock 自主交易智体 | 7×24 小时运行 | 数据来源：AKShare<br>
    <small>本页面仅供模拟交易参考，不构成投资建议</small>
    </div>""", 
    unsafe_allow_html=True
)
