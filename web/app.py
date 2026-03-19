"""
X-Stock Agent - Web Dashboard (Streamlit)
7×24 小时实时监控界面
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os

# 页面配置
st.set_page_config(
    page_title="🦞 X-Stock 交易智体",
    page_icon="🦞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
    }
    .profit-positive {
        color: #00cc00;
        font-weight: bold;
    }
    .profit-negative {
        color: #ff0000;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def load_mock_data():
    """加载模拟数据（后续替换为真实数据）"""
    
    # 模拟总资产曲线
    dates = pd.date_range(end=datetime.now(), periods=30)
    base_value = 1000000
    cumulative_returns = [0]
    for i in range(1, 30):
        daily_return = (0.02 if i % 3 == 0 else -0.01) + (0.005 * (i % 5 - 2))
        cumulative_returns.append(cumulative_returns[-1] + daily_return * 100)
    
    equity_curve = base_value * (1 + pd.Series(cumulative_returns) / 100)
    
    # 模拟持仓
    positions = [
        {'symbol': '600000', 'name': '浦发银行', 'volume': 5000, 'cost': 10.5, 'current_price': 10.8},
        {'symbol': '000001', 'name': '平安银行', 'volume': 3000, 'cost': 15.2, 'current_price': 15.5},
        {'symbol': '600519', 'name': '贵州茅台', 'volume': 100, 'cost': 1800, 'current_price': 1850},
    ]
    
    # 计算持仓盈亏
    for pos in positions:
        pos['profit'] = (pos['current_price'] - pos['cost']) * pos['volume']
        pos['profit_ratio'] = (pos['current_price'] - pos['cost']) / pos['cost'] * 100
    
    # 模拟交易信号
    recent_signals = [
        {'time': '2026-03-19 14:30', 'symbol': '600000', 'action': 'BUY', 'price': 10.5, 'reason': '动量突破'},
        {'time': '2026-03-19 13:15', 'symbol': '000030', 'action': 'SELL', 'price': 25.3, 'reason': '止损触发'},
        {'time': '2026-03-19 10:00', 'symbol': '000001', 'action': 'BUY', 'price': 15.2, 'reason': '均线金叉'},
    ]
    
    # 策略表现
    strategy_stats = [
        {'strategy': '动量策略', 'win_rate': 65.5, 'total_signals': 42, 'profit': 12500},
        {'strategy': '均值回归', 'win_rate': 58.2, 'total_signals': 38, 'profit': 8900},
        {'strategy': 'ML 预测', 'win_rate': 61.0, 'total_signals': 35, 'profit': 10200},
        {'strategy': '情绪分析', 'win_rate': 55.0, 'total_signals': 28, 'profit': 5600},
    ]
    
    return {
        'dates': dates,
        'equity_curve': equity_curve,
        'positions': positions,
        'recent_signals': recent_signals,
        'strategy_stats': strategy_stats,
        'initial_capital': base_value,
        'current_capital': equity_curve.iloc[-1],
        'daily_profit': 3200
    }


def render_header():
    """渲染头部"""
    st.markdown('<p class="main-header">🦞 X-Stock 自主交易智体</p>', unsafe_allow_html=True)
    st.markdown("---")


def render_metrics(data):
    """渲染核心指标"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="💰 总资产",
            value=f"¥{data['current_capital']:,.0f}",
            delta=f"{((data['current_capital']/data['initial_capital'])-1)*100:.2f}%"
        )
    
    with col2:
        profit_class = "profit-positive" if data['daily_profit'] > 0 else "profit-negative"
        st.metric(
            label="📈 今日盈亏",
            value=f"¥{data['daily_profit']:+,.0f}",
            delta=None
        )
    
    with col3:
        total_profit = data['current_capital'] - data['initial_capital']
        st.metric(
            label="🎯 累计收益",
            value=f"¥{total_profit:+,.0f}",
            delta=f"{(total_profit/data['initial_capital'])*100:.2f}%"
        )
    
    with col4:
        st.metric(
            label="📊 持仓数量",
            value=len(data['positions']),
            delta=None
        )


def render_equity_chart(data):
    """渲染资产曲线"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['dates'],
        y=data['equity_curve'],
        mode='lines+markers',
        name='总资产',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        title='📈 资产曲线',
        xaxis_title='日期',
        yaxis_title='资产 (元)',
        hovermode='x unified',
        height=400,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_positions(data):
    """渲染持仓信息"""
    st.subheader("📦 当前持仓")
    
    if data['positions']:
        df = pd.DataFrame(data['positions'])
        
        # 格式化显示
        display_df = df.copy()
        display_df['成本'] = display_df['cost'].apply(lambda x: f"¥{x:.2f}")
        display_df['现价'] = display_df['current_price'].apply(lambda x: f"¥{x:.2f}")
        display_df['盈亏'] = display_df['profit'].apply(lambda x: f"¥{x:,.0f}")
        display_df['盈亏率'] = display_df['profit_ratio'].apply(lambda x: f"{x:+.2f}%")
        
        # 着色
        def color_profit(val):
            color = '#00cc00' if val > 0 else '#ff0000' if val < 0 else '#000000'
            return f'color: {color}; font-weight: bold'
        
        styled_df = display_df[['symbol', 'name', 'volume', '成本', '现价', '盈亏', '盈亏率']].style \
            .applymap(color_profit, subset=['盈亏']) \
            .applymap(color_profit, subset=['盈亏率'])
        
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("暂无持仓")


def render_signals(data):
    """渲染交易信号"""
    st.subheader("🔔 最近交易信号")
    
    if data['recent_signals']:
        for signal in data['recent_signals']:
            icon = '🟢' if signal['action'] == 'BUY' else '🔴'
            st.markdown(f"**{icon} {signal['time']}** - {signal['symbol']} **{signal['action']}** "
                       f"@ ¥{signal['price']:.2f} - {signal['reason']}")
    else:
        st.info("暂无交易信号")


def render_strategy_performance(data):
    """渲染策略表现"""
    st.subheader("🧠 策略表现")
    
    if data['strategy_stats']:
        df = pd.DataFrame(data['strategy_stats'])
        
        # 胜率着色
        def color_winrate(val):
            color = '#00cc00' if val > 60 else '#ffa500' if val > 50 else '#ff0000'
            return f'color: {color}; font-weight: bold'
        
        styled_df = df.style \
            .applymap(color_winrate, subset=['win_rate']) \
            .format({'win_rate': '{:.1f}%', 'profit': '¥{:,.0f}'})
        
        st.dataframe(styled_df, use_container_width=True)
        
        # 策略胜率柱状图
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['strategy'],
            y=df['win_rate'],
            text=df['win_rate'].apply(lambda x: f'{x:.1f}%'),
            textposition='auto',
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        ))
        
        fig.update_layout(
            title='策略胜率对比',
            xaxis_title='策略',
            yaxis_title='胜率 (%)',
            height=300,
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.markdown("### ⚙️ 系统状态")
        st.info("🟢 运行中")
        
        st.markdown("### 📅 最后更新")
        st.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        st.markdown("### 🔄 自动刷新")
        auto_refresh = st.checkbox("启用自动刷新", value=True)
        if auto_refresh:
            st.autorun = True
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📖 说明")
        st.markdown("""
        - **数据源**: AKShare
        - **更新频率**: 5 分钟
        - **交易模式**: 模拟盘
        - **风险等级**: 零风险
        
        点击下面的按钮手动刷新：
        """)
        
        if st.button("🔄 刷新数据"):
            st.rerun()


def main():
    """主函数"""
    render_header()
    render_sidebar()
    
    # 加载数据
    with st.spinner('正在加载最新数据...'):
        data = load_mock_data()
    
    # 渲染各模块
    render_metrics(data)
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        render_equity_chart(data)
    with col2:
        render_strategy_performance(data)
    
    st.markdown("---")
    
    col3, col4 = st.columns(2)
    with col3:
        render_positions(data)
    with col4:
        render_signals(data)
    
    # 页脚
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #888;'>"
        "🦞 X-Stock 自主交易智体 | 7×24 小时智能监控 | 模拟盘运行中"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
