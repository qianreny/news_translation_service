from flask import Flask, request, jsonify
import openai
import os
from typing import Dict, Any
import logging
from datetime import datetime
from dotenv import load_dotenv
from collections import defaultdict
import json
import re
import sys
import io

# 设置标准输出为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
# 设置错误输出
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# 加载环境变量
load_dotenv()

from config import Config, LanguageConfig

# 配置日志
logging.basicConfig(level=getattr(logging, Config.LOG_LEVEL))
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 获取语言配置
TARGET_LANGUAGES = LanguageConfig.get_target_languages()


class TranslationService:
    """翻译服务类"""

    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)

    def translate_content(self, news_id: str, title: str, description: str, content: str, target_language: str) -> Dict[
        str, Any]:
        """
        翻译内容到指定目标语言
        
        Args:
            news_id: 新闻ID
            title: 标题
            description: 描述
            content: 正文
            target_language: 目标语言代码
            
        Returns:
            翻译结果字典
        """
        if target_language not in TARGET_LANGUAGES:
            raise ValueError(f"不支持的目标语言: {target_language}")

        language_config = TARGET_LANGUAGES[target_language]
        prompt = language_config['prompt_template'].format(
            title=title,
            description=description,
            content=content
        )

        try:
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=Config.OPENAI_TEMPERATURE,
                max_tokens=Config.OPENAI_MAX_TOKENS
            )

            translation_result = response.choices[0].message.content

            # 尝试解析JSON响应
            import json
            import re
            try:
                match = re.search(r"```json\s*(\{.*?\})\s*```", translation_result, re.DOTALL)
                parsed_result = json.loads(match.group(1))
                return {
                    'news_id': news_id,
                    'target_language': target_language,
                    'language_name': language_config['name'],
                    'language_code': language_config['code'],
                    'translated_title': parsed_result.get('title', ''),
                    'translated_description': parsed_result.get('description', ''),
                    'translated_content': parsed_result.get('content', ''),
                    'original_title': title,
                    'original_description': description,
                    'original_content': content,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success'
                }
            except json.JSONDecodeError:
                # 如果无法解析JSON，返回原始响应
                return {
                    'news_id': news_id,
                    'target_language': target_language,
                    'language_name': language_config['name'],
                    'language_code': language_config['code'],
                    'raw_translation': translation_result,
                    'original_title': title,
                    'original_description': description,
                    'original_content': content,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'success_raw'
                }

        except Exception as e:
            logger.error(f"翻译失败 - 新闻ID: {news_id}, 目标语言: {target_language}, 错误: {str(e)}")
            return {
                'news_id': news_id,
                'target_language': target_language,
                'language_name': language_config['name'],
                'language_code': language_config['code'],
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'status': 'error'
            }


# 初始化翻译服务
translation_service = TranslationService()


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'supported_languages': list(TARGET_LANGUAGES.keys())
    })


@app.route('/translate', methods=['POST'])
def translate():
    """
    翻译接口
    
    请求参数:
    {
        "news_id": "新闻ID",
        "title": "标题",
        "description": "描述",
        "content": "正文",
        "target_language": "目标语言代码"
    }
    """
    try:
        data = request.get_json()

        # 验证必需参数
        required_fields = ['news_id', 'title', 'description', 'content', 'target_language']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'缺少必需参数: {field}',
                    'status': 'error'
                }), 400

        news_id = data['news_id']
        title = data['title']
        description = data['description']
        content = data['content']
        target_language = data['target_language']
        print('ssssssssssssssssssssss', target_language)
        # 验证目标语言
        if target_language not in TARGET_LANGUAGES:
            return jsonify({
                'error': f'不支持的目标语言: {target_language}',
                'supported_languages': list(TARGET_LANGUAGES.keys()),
                'status': 'error'
            }), 400

        # 执行翻译
        result = translation_service.translate_content(
            news_id=news_id,
            title=title,
            description=description,
            content=content,
            target_language=target_language
        )

        if result['status'] == 'error':
            return jsonify(result), 500

        return jsonify(result)

    except Exception as e:
        logger.error(f"翻译请求处理失败: {str(e)}")
        return jsonify({
            'error': '服务器内部错误',
            'details': str(e),
            'status': 'error'
        }), 500


@app.route('/translate/batch', methods=['POST'])
def translate_batch():
    """
    批量翻译接口
    
    请求参数:
    {
        "news_id": "新闻ID",
        "title": "标题",
        "description": "描述",
        "content": "正文",
        "target_languages": ["目标语言代码1", "目标语言代码2"]
    }
    """
    try:
        data = request.get_json()

        # 验证必需参数
        required_fields = ['news_id', 'title', 'description', 'content', 'target_languages']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': f'缺少必需参数: {field}',
                    'status': 'error'
                }), 400

        news_id = data['news_id']
        title = data['title']
        description = data['description']
        content = data['content']
        target_languages = data['target_languages']

        if not isinstance(target_languages, list):
            return jsonify({
                'error': 'target_languages 必须是数组',
                'status': 'error'
            }), 400

        # 验证所有目标语言
        unsupported_languages = [lang for lang in target_languages if lang not in TARGET_LANGUAGES]
        if unsupported_languages:
            return jsonify({
                'error': f'不支持的目标语言: {unsupported_languages}',
                'supported_languages': list(TARGET_LANGUAGES.keys()),
                'status': 'error'
            }), 400

        # 执行批量翻译
        results = []
        for target_language in target_languages:
            result = translation_service.translate_content(
                news_id=news_id,
                title=title,
                description=description,
                content=content,
                target_language=target_language
            )
            results.append(result)

        return jsonify({
            'news_id': news_id,
            'total_translations': len(results),
            'results': results,
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        })

    except Exception as e:
        logger.error(f"批量翻译请求处理失败: {str(e)}")
        return jsonify({
            'error': '服务器内部错误',
            'details': str(e),
            'status': 'error'
        }), 500


@app.route('/translate/multi', methods=['POST'])
def translate_multi():
    """
    多语言翻译接口
    
    请求参数:
    {
        "news_id": "新闻ID",
        "title": "标题",
        "description": "描述",
        "content": "正文",
        "target_languages": ["目标语言代码1", "目标语言代码2"]
    }
    
    返回格式:
    {
        "news_id": "新闻编号",
        "status": "状态",
        "timestamp": "时间戳",
        "translations": [
            {
                "title_en": "英文标题",
                "description_en": "英文描述",
                "content_en": "英文正文"
            },
            {
                "title_zh": "中文标题",
                "description_zh": "中文描述",
                "content_zh": "中文正文"
            }
        ]
    }
    """
    try:
        data = request.get_json()
        # print(data)

        # 验证必需参数
        required_fields = ['news_id', 'title', 'description', 'content', 'target_languages']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'news_id': data.get('news_id', ''),
                    'status': 'error',
                    'timestamp': datetime.now().isoformat(),
                    'error': f'缺少必需参数: {field}'
                }), 400

        news_id = data['news_id']
        title = data['title']
        description = data['description']
        content = data['content']
        target_languages = data['target_languages']

        if not isinstance(target_languages, list):
            return jsonify({
                'news_id': news_id,
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': 'target_languages 必须是数组'
            }), 400

        # 验证所有目标语言
        unsupported_languages = [lang for lang in target_languages if lang not in TARGET_LANGUAGES]

        if unsupported_languages:
            return jsonify({
                'news_id': news_id,
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': f'不支持的目标语言: {unsupported_languages}',
                'supported_languages': list(TARGET_LANGUAGES.keys())
            }), 400

        # 执行多语言翻译
        translations = []
        has_error = False

        for target_language in target_languages:
            result = translation_service.translate_content(
                news_id=news_id,
                title=title,
                description=description,
                content=content,
                target_language=target_language
            )
            print(f'target_language:{target_language}  结果:{result}')

            # 获取语言代码缩写
            language_code = TARGET_LANGUAGES[target_language]['code']

            if result['status'] == 'success':
                translation_dict = {
                    f'title_{language_code}': result.get('translated_title', ''),
                    f'description_{language_code}': result.get('translated_description', ''),
                    f'content_{language_code}': result.get('translated_content', '')
                }
            elif result['status'] == 'success_raw':
                # 如果是原始翻译结果，尝试使用raw_translation
                translation_dict = {
                    f'title_{language_code}': result.get('raw_translation', ''),
                    f'description_{language_code}': result.get('raw_translation', ''),
                    f'content_{language_code}': result.get('raw_translation', '')
                }
            else:
                # 翻译失败的情况
                translation_dict = {
                    f'title_{language_code}': f"翻译失败: {result.get('error', '未知错误')}",
                    f'description_{language_code}': f"翻译失败: {result.get('error', '未知错误')}",
                    f'content_{language_code}': f"翻译失败: {result.get('error', '未知错误')}"
                }
                has_error = True

            translations.append(translation_dict)

        # 数据转换
        translations_dict = defaultdict(dict)
        for translation in translations:
            key_list = list(translation.keys())
            key_0, code = key_list[0].split('_')
            key_1 = key_list[1].split('_')[0]
            key_2 = key_list[2].split('_')[0]
            if '翻译失败' not in translation[key_list[0]]:
                translations_dict[key_0][code] = translation[key_list[0]]
                translations_dict[key_1][code] = translation[key_list[1]]
                translations_dict[key_2][code] = translation[key_list[2]]
            # 繁体（台），繁体（港），越南，handi，日文，英文
            # TW  ZH_HK VI HI JA EN
        if len(translations_dict) == 0:
            return jsonify({
                'news_id': data.get('news_id', '') if 'data' in locals() else '',
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': '翻译完全失败'
            }), 500
        # 确定整体状态
        overall_status = 'partial_success' if has_error else 'success'

        return jsonify({
            'news_id': news_id,
            'status': overall_status,
            'timestamp': datetime.now().isoformat(),
            'data': translations_dict
        })

    except Exception as e:
        logger.error(f"多语言翻译请求处理失败: {str(e)}")
        return jsonify({
            'news_id': data.get('news_id', '') if 'data' in locals() else '',
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': '服务器内部错误',
            'details': str(e)
        }), 500


@app.route('/languages', methods=['GET'])
def get_supported_languages():
    """获取支持的语言列表"""
    return jsonify({
        'supported_languages': {
            code: {
                'name': config['name'],
                'code': config['code']
            }
            for code, config in TARGET_LANGUAGES.items()
        },
        'total_count': len(TARGET_LANGUAGES)
    })


if __name__ == '__main__':
    # 检查环境变量
    if not Config.OPENAI_API_KEY:
        logger.warning("警告: 未设置 OPENAI_API_KEY 环境变量")

    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
