"""PromptManager用于build_prompt"""
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from typing import List, Any
import yaml
import re

class PromptManager:
    def __init__(self, base_path: str):
        """PromptManager用于build_prompt, base_path为 prompt 所在的相对路径"""
        self.base_path = Path(base_path)
        self.cache = {}
        self.variables = {}
        self.load_config()
    
    def load_config(self, config_path: Optional[str] = None):
        """加载配置文件"""
        if config_path is None:
            config_path = self.base_path / 'config.yaml'
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self.variables.update(yaml.safe_load(f))

    def read_module(self, module_name: str) -> str:
        """读取单个模块文件"""
        if module_name in self.cache:
            return self.cache[module_name]
        
        module_path = self.base_path / 'modules' / f'{module_name}'
        if not module_path.exists():
            raise FileNotFoundError(f"Module not found: {module_name}")
        
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # self.cache[module_name] = content.strip('\n')
            self.cache[module_name] = content
            return content

    def process_includes(self, content: str) -> str:
        """按module_sequence顺序加载模块"""
        new_content = ''
        if 'module_sequence' in self.variables:
            for module_name in self.variables['module_sequence']:
                new_content += '\n\n' + self.read_module(module_name)
        return new_content.strip('\n')

    def process_variables(self, content: str) -> str:
        """处理变量替换"""
        for key, value in self.variables.items():
            content = content.replace(f"{{{key}}}", str(value))
        return content

    def build_prompt(self, variables: Optional[Dict] = None) -> str:
        """构建完整的 prompt"""
        if variables:
            self.variables.update(variables)
        # 初始化空内容并按模块顺序拼接
        content = ''
        
        # 处理包含指令
        content = self.process_includes(content)
        
        # 处理变量
        content = self.process_variables(content)
        
        return content

    def clear_cache(self):
        """清除缓存"""
        self.cache.clear()

if __name__ == '__main__':
    manager = PromptManager('prompt_system/prompt/')
    prompt = manager.build_prompt()
    print(prompt)

