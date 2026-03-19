#!/usr/bin/env python3
"""
X-Stock Agent - Main Entry Point
主启动入口
"""

import sys
import os
from loguru import logger
import yaml

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def setup_logging():
    """配置日志"""
    log_dir = "./logs"
    os.makedirs(log_dir, exist_ok=True)
    
    logger.remove()  # 移除默认处理器
    
    # 控制台输出
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )
    
    # 文件输出
    logger.add(
        f"{log_dir}/xstock.log",
        rotation="100 MB",
        retention="30 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    logger.info("=" * 60)
    logger.info("🦞 X-Stock 自主交易智体 启动中...")
    logger.info("=" * 60)


def load_config():
    """加载配置文件"""
    config_path = "./config.yaml"
    
    if not os.path.exists(config_path):
        logger.warning(f"配置文件不存在：{config_path}，使用默认配置")
        return {}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    logger.info(f"配置文件加载成功：{config_path}")
    return config


def main():
    """主函数"""
    # 设置日志
    setup_logging()
    
    # 加载配置
    config = load_config()
    
    logger.info("系统初始化完成")
    logger.info(f"交易模式：{config.get('trading', {}).get('mode', 'paper')}")
    logger.info(f"初始资金：¥{config.get('trading', {}).get('initial_capital', 1000000):,}")
    
    # 显示可用命令
    print("\n")
    print("=" * 60)
    print("🦞 X-Stock 自主交易智体")
    print("=" * 60)
    print("\n可用命令:")
    print("  python run.py web          - 启动 Web 看板")
    print("  python run.py trade        - 启动交易引擎")
    print("  python run.py backtest     - 运行回测")
    print("  python run.py evolve       - 运行自我进化模块")
    print("  python run.py all          - 启动所有服务（推荐）")
    print("\n")
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "web":
            start_web()
        elif command == "trade":
            start_trade_engine(config)
        elif command == "backtest":
            run_backtest(config)
        elif command == "evolve":
            start_evolution(config)
        elif command == "all":
            start_all_services(config)
        else:
            logger.error(f"未知命令：{command}")
            print_usage()
    else:
        print_usage()


def print_usage():
    """打印使用说明"""
    print("💡 提示：请指定要启动的模块")
    print("   首次运行建议使用：python run.py web")
    print("   查看 Web 看板效果")


def start_web():
    """启动 Web 看板"""
    logger.info("启动 Web 看板...")
    os.system("streamlit run web/app.py --server.address=0.0.0.0 --server.port=8501")


def start_trade_engine(config):
    """启动交易引擎"""
    logger.info("启动交易引擎...")
    from core.trading_engine import TradingEngine
    engine = TradingEngine(config)
    engine.run()


def run_backtest(config):
    """运行回测"""
    logger.info("运行回测...")
    from evolution.backtest_engine import BacktestEngine
    backtester = BacktestEngine(config)
    backtester.run()


def start_evolution(config):
    """启动进化模块"""
    logger.info("启动自我进化模块...")
    from evolution.evolution_engine import EvolutionEngine
    engine = EvolutionEngine(config)
    engine.run()


def start_all_services(config):
    """启动所有服务"""
    logger.info("启动所有服务...")
    import subprocess
    
    processes = []
    
    # 启动 Web 看板
    p_web = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run",
        "web/app.py",
        "--server.address=0.0.0.0",
        "--server.port=8501"
    ])
    processes.append(p_web)
    
    logger.info("所有服务已启动")
    logger.info("Web 看板地址：http://localhost:8501")
    
    # 等待所有进程
    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        logger.info("正在关闭服务...")
        for p in processes:
            p.terminate()


if __name__ == "__main__":
    main()
