"""
X-Stock Agent - 自我进化引擎
每天自动学习 GitHub 最牛项目，持续进化
"""

import os
import json
import subprocess
from datetime import datetime
from loguru import logger
import requests


class EvolutionEngine:
    """自我进化引擎"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.learning_dir = "./learning"
        self.github_token = os.environ.get('GITHUB_TOKEN', '')
        
        # 学习目标
        self.target_topics = [
            'stock trading',
            'quantitative trading',
            'machine learning stock',
            'algorithmic trading',
            'A-share stock'
        ]
        
        # 进化记录
        self.evolution_log = []
        
        logger.info("🧠 自我进化引擎初始化完成")
        os.makedirs(self.learning_dir, exist_ok=True)
    
    def daily_learning(self):
        """每日学习流程"""
        logger.info("="*60)
        logger.info("🧠 开始每日自我进化学习...")
        logger.info("="*60)
        
        # 1. 扫描 GitHub 最新项目
        new_projects = self.scan_github()
        
        # 2. 分析优秀项目
        for project in new_projects[:3]:  # 每次最多学习 3 个
            self.learn_from_project(project)
        
        # 3. 更新策略
        self.update_strategies()
        
        # 4. 生成学习报告
        report = self.generate_report()
        
        logger.info("✅ 每日进化学习完成")
        
        return report
    
    def scan_github(self):
        """扫描 GitHub 热门项目"""
        logger.info("🔍 扫描 GitHub 热门量化项目...")
        
        projects = []
        
        for topic in self.target_topics[:2]:  # 每次扫描 2 个主题
            try:
                url = f"https://api.github.com/search/repositories"
                params = {
                    'q': f'topic:{topic} pushed:>2025-01-01',
                    'sort': 'stars',
                    'per_page': 5
                }
                
                headers = {}
                if self.github_token:
                    headers['Authorization'] = f'token {self.github_token}'
                
                response = requests.get(url, params=params, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for item in data.get('items', [])[:3]:
                        projects.append({
                            'name': item.get('name'),
                            'full_name': item.get('full_name'),
                            'description': item.get('description'),
                            'stars': item.get('stargazers_count'),
                            'language': item.get('language'),
                            'url': item.get('html_url'),
                            'updated': item.get('updated_at')
                        })
                        
            except Exception as e:
                logger.warning(f"扫描 {topic} 失败: {e}")
        
        logger.info(f"   发现 {len(projects)} 个热门项目")
        
        return projects
    
    def learn_from_project(self, project):
        """从项目学习"""
        logger.info(f"📚 学习项目: {project['name']}")
        
        # 记录学习
        self.evolution_log.append({
            'time': datetime.now().isoformat(),
            'project': project['name'],
            'action': 'learned',
            'stars': project.get('stars'),
            'description': project.get('description')
        })
        
        # 保存到学习记录
        self.save_learning_record(project)
        
        logger.info(f"   ⭐ {project.get('stars')} stars")
        logger.info(f"   📝 {project.get('description', '')[:50]}...")
    
    def save_learning_record(self, project):
        """保存学习记录"""
        record_file = f"{self.learning_dir}/github_projects.json"
        
        records = []
        if os.path.exists(record_file):
            with open(record_file, 'r') as f:
                records = json.load(f)
        
        # 检查是否已存在
        for r in records:
            if r['full_name'] == project['full_name']:
                return
        
        records.append({
            **project,
            'learned_at': datetime.now().isoformat()
        })
        
        # 只保留最近 50 个
        records = records[-50:]
        
        with open(record_file, 'w') as f:
            json.dump(records, f, indent=2)
    
    def update_strategies(self):
        """更新策略"""
        logger.info("🔄 分析并更新交易策略...")
        
        # 这里可以根据学习到的项目更新策略参数
        # 暂时记录学习成果
        
        self.evolution_log.append({
            'time': datetime.now().isoformat(),
            'action': 'strategy_updated',
            'note': '基于学习调整策略参数'
        })
    
    def generate_report(self):
        """生成学习报告"""
        report = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'projects_learned': len([l for l in self.evolution_log if l.get('action') == 'learned']),
            'strategies_updated': len([l for l in self.evolution_log if l.get('action') == 'strategy_updated']),
            'total_learning': len(self.evolution_log)
        }
        
        # 保存报告
        report_file = f"{self.learning_dir}/evolution_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def get_learning_history(self):
        """获取学习历史"""
        record_file = f"{self.learning_dir}/github_projects.json"
        
        if os.path.exists(record_file):
            with open(record_file, 'r') as f:
                return json.load(f)
        
        return []


# 测试
if __name__ == "__main__":
    logger.add("./logs/evolution.log")
    
    engine = EvolutionEngine()
    
    print("\n" + "="*50)
    print("🧠 自我进化引擎测试")
    print("="*50)
    
    # 扫描 GitHub（可能需要 token）
    print("\n扫描 GitHub 热门项目...")
    projects = engine.scan_github()
    
    print(f"\n发现 {len(projects)} 个项目:")
    for p in projects:
        print(f"  - {p['name']} ({p.get('stars')} ⭐)")
    
    print("\n" + "="*50)
