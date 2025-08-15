import os
from typing import Dict, Any

class Config:
    """应用配置类"""
    
    # OpenAI配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o')
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.3'))
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '4000'))
    
    # Flask配置
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', '5000'))
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

class LanguageConfig:
    """语言配置管理类"""
    
    @staticmethod
    def get_target_languages() -> Dict[str, Dict[str, Any]]:
        """获取目标语言配置"""
        return {
            'tw': {
                'name': '繁体中文（台湾）',
                'code': 'tw',
                'prompt_template': LanguageConfig._get_traditional_tw_prompt()
            },
            'zh_hk': {
                'name': '繁体中文（香港）',
                'code': 'zh_hk',
                'prompt_template': LanguageConfig._get_traditional_hk_prompt()
            },
            'vi': {
                'name': '越南语',
                'code': 'vi',
                'prompt_template': LanguageConfig._get_vietnamese_prompt()
            },
            'ja': {
                'name': '日语',
                'code': 'ja',
                'prompt_template': LanguageConfig._get_japanese_prompt()
            },
            'en': {
                'name': '英语',
                'code': 'en',
                'prompt_template': LanguageConfig._get_english_prompt()
            },
            'hi':{
                'name': '印度语',
                'code': 'hi',
                'prompt_template': LanguageConfig._get_english_prompt()
            }
        }
    
    @staticmethod
    def _get_traditional_tw_prompt() -> str:
        """获取繁体中文（台湾）翻译提示词"""
        return '''
你是一个专业的翻译专家，请将以下简体中文内容翻译成繁体中文（台湾用法）。

翻译要求：
1. 使用台湾地区的繁体中文用词习惯
2. 保持原文的语气和风格
3. 确保翻译准确、自然、流畅
4. 对于专有名词，使用台湾地区的常用译法
5. 保持原文的格式和结构
6. 注意台湾地区的表达习惯，如：软件→軟體、网络→網路、信息→資訊等

请翻译以下内容：
标题：{title}
描述：{description}
正文：{content}

请按照以下JSON格式返回翻译结果：
{{
    "title": "翻译后的标题",
    "description": "翻译后的描述",
    "content": "翻译后的正文"
}}
'''
    
    @staticmethod
    def _get_traditional_hk_prompt() -> str:
        """获取繁体中文（香港）翻译提示词"""
        return '''
你是一个专业的翻译专家，请将以下简体中文内容翻译成繁体中文（香港用法）。

翻译要求：
1. 使用香港地区的繁体中文用词习惯
2. 保持原文的语气和风格
3. 确保翻译准确、自然、流畅
4. 对于专有名词，使用香港地区的常用译法
5. 保持原文的格式和结构
6. 适当使用香港地区的表达方式，如：出租车→的士、公交车→巴士、手机→手提電話等
7. 注意港式中文的特色用词

请翻译以下内容：
标题：{title}
描述：{description}
正文：{content}

请按照以下JSON格式返回翻译结果：
{{
    "title": "翻译后的标题",
    "description": "翻译后的描述",
    "content": "翻译后的正文"
}}
'''
    
    @staticmethod
    def _get_vietnamese_prompt() -> str:
        """获取越南语翻译提示词"""
        return '''
你是一个专业的翻译专家，请将以下简体中文内容翻译成越南语。

翻译要求：
1. 使用标准的越南语表达
2. 保持原文的语气和风格
3. 确保翻译准确、自然、流畅
4. 对于专有名词，使用越南语的常用译法
5. 保持原文的格式和结构
6. 注意越南语的语法特点和表达习惯
7. 使用适当的敬语和礼貌用语
8. 注意越南语的声调标记

请翻译以下内容：
标题：{title}
描述：{description}
正文：{content}

请按照以下JSON格式返回翻译结果：
{{
    "title": "翻译后的标题",
    "description": "翻译后的描述",
    "content": "翻译后的正文"
}}
'''
    
    @staticmethod
    def _get_japanese_prompt() -> str:
        """获取日语翻译提示词"""
        return '''
你是一个专业的翻译专家，请将以下简体中文内容翻译成日语。

翻译要求：
1. 使用标准的日语表达，包含适当的敬语
2. 保持原文的语气和风格
3. 确保翻译准确、自然、流畅
4. 对于专有名词，使用日语的常用译法
5. 保持原文的格式和结构
6. 注意日语的语法特点和表达习惯
7. 根据内容性质选择合适的敬语级别
8. 正确使用平假名、片假名和汉字
9. 注意日语的语序和助词使用

请翻译以下内容：
标题：{title}
描述：{description}
正文：{content}

请按照以下JSON格式返回翻译结果：
{{
    "title": "翻译后的标题",
    "description": "翻译后的描述",
    "content": "翻译后的正文"
}}
'''
    
    @staticmethod
    def _get_english_prompt() -> str:
        """获取英语翻译提示词"""
        return '''
你是一个专业的翻译专家，请将以下简体中文内容翻译成英语。

翻译要求：
1. 使用标准的英语表达
2. 保持原文的语气和风格
3. 确保翻译准确、自然、流畅
4. 对于专有名词，使用英语的常用译法
5. 保持原文的格式和结构
6. 注意英语的语法特点和表达习惯
7. 使用适当的英语写作风格
8. 确保语法正确，用词准确
9. 根据内容类型选择合适的正式程度

请翻译以下内容：
标题：{title}
描述：{description}
正文：{content}

请按照以下JSON格式返回翻译结果：
{{
    "title": "翻译后的标题",
    "description": "翻译后的描述",
    "content": "翻译后的正文"
}}
'''
    
    @staticmethod
    def add_custom_language(language_key: str, language_config: Dict[str, Any]) -> bool:
        """添加自定义语言配置（扩展功能）"""
        # 这里可以实现动态添加语言的逻辑
        # 例如保存到数据库或配置文件
        required_fields = ['name', 'code', 'prompt_template']
        
        if not all(field in language_config for field in required_fields):
            return False
        
        # 实际实现中可以将配置保存到持久化存储
        # 这里只是示例
        return True
    
    @staticmethod
    def validate_language_config(language_config: Dict[str, Any]) -> bool:
        """验证语言配置的有效性"""
        required_fields = ['name', 'code', 'prompt_template']
        
        # 检查必需字段
        if not all(field in language_config for field in required_fields):
            return False
        
        # 检查提示词模板是否包含必要的占位符
        template = language_config['prompt_template']
        required_placeholders = ['{title}', '{description}', '{content}']
        
        if not all(placeholder in template for placeholder in required_placeholders):
            return False
        
        return True