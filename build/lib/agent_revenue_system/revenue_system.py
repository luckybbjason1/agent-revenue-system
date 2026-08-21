#!/usr/bin/env python3
"""
Agent Revenue System - 自动化收入系统
整合所有赚钱项目，实现被动收入

作者: AI Revenue Architect
许可证: MIT
"""

import os
import sys
import json
import time
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional

# 配置
PROJECT_NAME = "agent-revenue-system"
VERSION = "1.0.0"
CONFIG_DIR = Path.home() / ".agent-revenue"
PROJECTS_DIR = Path.home() / "桌面"
LOG_FILE = CONFIG_DIR / "revenue.log"
STATE_FILE = CONFIG_DIR / "state.json"

@dataclass
class RevenueProject:
    name: str
    path: str
    type: str  # opensource, saas, subscription, marketplace
    status: str  # active, paused, error
    monthly_revenue: float = 0.0
    stars: int = 0
    last_updated: str = ""
    
    def to_dict(self):
        return {
            'name': self.name,
            'path': self.path,
            'type': self.type,
            'status': self.status,
            'monthly_revenue': self.monthly_revenue,
            'stars': self.stars,
            'last_updated': self.last_updated
        }

class RevenueSystem:
    def __init__(self):
        self.config_dir = CONFIG_DIR
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.projects = []
        self.revenue_history = []
        self.state = {"total_earnings": 0, "start_date": datetime.now().isoformat()}
        self.load_data()
    
    def load_data(self):
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                data = json.load(f)
                self.state = data
                self.projects = [RevenueProject(**p) for p in data.get('projects', [])]
                self.revenue_history = data.get('revenue_history', [])
    
    def save_data(self):
        data = {
            **self.state,
            'projects': [p.to_dict() for p in self.projects],
            'revenue_history': self.revenue_history
        }
        with open(STATE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_project(self, name: str, path: str, project_type: str):
        """添加项目"""
        project = RevenueProject(
            name=name,
            path=path,
            type=project_type,
            status="active",
            last_updated=datetime.now().isoformat()
        )
        self.projects.append(project)
        self.save_data()
        print(f"[+] 已添加项目: {name}")
    
    def remove_project(self, name: str):
        """移除项目"""
        self.projects = [p for p in self.projects if p.name != name]
        self.save_data()
        print(f"[-] 已移除项目: {name}")
    
    def detect_projects(self):
        """自动检测项目目录"""
        detected = []
        
        # 检测桌面目录
        desktop = Path.home() / "桌面"
        if desktop.exists():
            for item in desktop.iterdir():
                if item.is_dir() and (item / "README.md").exists():
                    detected.append({
                        'name': item.name,
                        'path': str(item),
                        'type': self._detect_type(item)
                    })
        
        return detected
    
    def _detect_type(self, project_dir: Path) -> str:
        """检测项目类型"""
        # 检查是否有 pyproject.toml 或 setup.py
        if (project_dir / "pyproject.toml").exists():
            return "python_package"
        if (project_dir / "package.json").exists():
            return "npm_package"
        if (project_dir / "requirements.txt").exists():
            return "python_package"
        return "general"
    
    def get_revenue_summary(self) -> Dict:
        """获取收入汇总"""
        total_monthly = sum(p.monthly_revenue for p in self.projects)
        total_lifetime = self.state.get('total_earnings', 0) + total_monthly
        
        # 按类型统计
        by_type = {}
        for p in self.projects:
            if p.type not in by_type:
                by_type[p.type] = {'count': 0, 'revenue': 0}
            by_type[p.type]['count'] += 1
            by_type[p.type]['revenue'] += p.monthly_revenue
        
        # 计算增长
        if len(self.revenue_history) >= 2:
            current = self.revenue_history[-1]
            previous = self.revenue_history[-2]
            growth = ((current - previous) / previous * 100) if previous > 0 else 0
        else:
            growth = 0
        
        return {
            "total_projects": len(self.projects),
            "active_projects": sum(1 for p in self.projects if p.status == "active"),
            "monthly_revenue": total_monthly,
            "lifetime_revenue": total_lifetime,
            "growth_rate": growth,
            "by_type": by_type,
            "last_updated": datetime.now().isoformat()
        }
    
    def update_revenue(self, project_name: str, amount: float):
        """更新项目收入"""
        for p in self.projects:
            if p.name == project_name:
                p.monthly_revenue = amount
                p.last_updated = datetime.now().isoformat()
                break
        
        # 添加到历史记录
        self.revenue_history.append(amount)
        if len(self.revenue_history) > 30:  # 保留30天
            self.revenue_history = self.revenue_history[-30:]
        
        self.state['total_earnings'] = sum(self.revenue_history)
        self.save_data()
        print(f"[+] 已更新 {project_name} 收入: ${amount:.2f}")
    
    def generate_report(self) -> str:
        """生成收入报告"""
        summary = self.get_revenue_summary()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.config_dir / f"report_{timestamp}.json"
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": summary,
            "projects": [p.to_dict() for p in self.projects]
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return str(report_file)
    
    def create_automation(self):
        """创建自动化任务"""
        # 创建定时任务脚本
        script = """#!/bin/bash
# Agent Revenue System - 自动化脚本
# 每日运行，更新收入数据

LOG_FILE="$HOME/.agent-revenue/automation.log"
echo "[$(date)] 运行收入更新..." >> $LOG_FILE

# 更新 GitHub Stars
for project in ~/桌面/*/; do
    if [ -f "$project/README.md" ]; then
        repo_name=$(basename "$project")
        # 这里可以调用 GitHub API 获取 stars
        echo "  更新 $repo_name stars..." >> $LOG_FILE
    fi
done

# 生成日报
python3 -c "
from revenue_system import RevenueSystem
system = RevenueSystem()
report = system.generate_report()
print(f'报告已生成: $report')
"

echo "[$(date)] 完成" >> $LOG_FILE
"""
        
        script_file = self.config_dir / "daily_update.sh"
        with open(script_file, 'w') as f:
            f.write(script)
        os.chmod(script_file, 0o755)
        
        # 设置 cron 任务
        cron_job = "0 9 * * * $HOME/.agent-revenue/daily_update.sh"
        
        print("[+] 自动化脚本已创建")
        print(f"[+] Cron 任务: {cron_job}")
        print("[+] 请运行: crontab -e 添加此任务")

def main():
    parser = argparse.ArgumentParser(
        description="Agent Revenue System - 自动化收入管理系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  revenue-system scan
  revenue-system add "kali-tools" ~/桌面/kali-tools-automation
  revenue-system revenue update kali-tools 100
  revenue-system report
  revenue-system automation
        """
    )
    
    parser.add_argument('action', nargs='?',
                       choices=['scan', 'add', 'remove', 'revenue', 'report', 'automation', 'status'],
                       default='status',
                       help='要执行的操作')
    parser.add_argument('args', nargs='*', help='额外参数')
    parser.add_argument('--json', action='store_true', help='JSON 格式输出')
    
    args = parser.parse_args()
    
    system = RevenueSystem()
    
    if args.action == 'scan':
        print("\n扫描项目目录...")
        projects = system.detect_projects()
        print(f"发现 {len(projects)} 个项目:\n")
        for p in projects:
            print(f"  • {p['name']} ({p['type']})")
            print(f"    路径: {p['path']}")
            print()
        
        # 询问是否添加
        for p in projects:
            existing = any(proj.name == p['name'] for proj in system.projects)
            if not existing:
                system.add_project(p['name'], p['path'], p['type'])
    
    elif args.action == 'add':
        if len(args.args) < 2:
            print("错误: 添加项目需要名称和路径")
            sys.exit(1)
        system.add_project(args.args[0], args.args[1], "python_package")
    
    elif args.action == 'remove':
        if not args.args:
            print("错误: 请指定项目名")
            sys.exit(1)
        system.remove_project(args.args[0])
    
    elif args.action == 'revenue':
        if args.args[0] == 'update' and len(args.args) >= 3:
            system.update_revenue(args.args[1], float(args.args[2]))
        else:
            print("用法: revenue-system revenue update <project> <amount>")
    
    elif args.action == 'report':
        report_file = system.generate_report()
        if args.json:
            with open(report_file) as f:
                print(json.dumps(json.load(f), indent=2))
        else:
            summary = system.get_revenue_summary()
            print("\n" + "="*60)
            print("收入报告")
            print("="*60)
            print(f"项目总数:   {summary['total_projects']}")
            print(f"活跃项目:   {summary['active_projects']}")
            print(f"月收入:     ${summary['monthly_revenue']:.2f}")
            print(f"总收入:     ${summary['lifetime_revenue']:.2f}")
            print(f"增长率:     {summary['growth_rate']:+.1f}%")
            print("="*60)
            print(f"\n报告已保存: {report_file}")
    
    elif args.action == 'automation':
        system.create_automation()
    
    elif args.action == 'status':
        summary = system.get_revenue_summary()
        
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print("\n" + "="*60)
            print("Agent Revenue System 状态")
            print("="*60)
            print(f"项目总数:   {summary['total_projects']}")
            print(f"活跃项目:   {summary['active_projects']}")
            print(f"月收入:     ${summary['monthly_revenue']:.2f}")
            print(f"总收入:     ${summary['lifetime_revenue']:.2f}")
            print(f"增长率:     {summary['growth_rate']:+.1f}%")
            print("="*60)
            
            if system.projects:
                print("\n项目列表:")
                for p in system.projects:
                    status_icon = "✅" if p.status == "active" else "⏸️"
                    print(f"  {status_icon} {p.name} - ${p.monthly_revenue:.2f}/月")

if __name__ == '__main__':
    main()
