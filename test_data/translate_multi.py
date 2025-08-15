#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：读取test_news.csv文件并调用/translate/multi接口
"""
import time

import pandas as pd
import requests
import json
from typing import List, Dict, Any

def read_news_data(csv_file_path: str) -> pd.DataFrame:
    """
    读取新闻CSV文件
    
    Args:
        csv_file_path: CSV文件路径
        
    Returns:
        包含新闻数据的DataFrame
    """
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_file_path,encoding='utf-8')
        
        # 选择需要的列：id, subject, brief, body
        # 根据CSV文件结构，对应的列名为：id, subject, brief, body
        required_columns = ['id', 'customSubject', 'customBrief', 'customBody']
        
        # 检查列是否存在
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"CSV文件缺少必需的列: {missing_columns}")
        
        # 选择需要的列并重命名
        news_df = df[required_columns].copy()
        news_df.columns = ['news_id', 'title', 'description', 'content']
        
        # 移除空值行
        news_df = news_df.dropna(subset=['news_id', 'title', 'description', 'content'])
        
        print(f"成功读取 {len(news_df)} 条新闻数据")
        return news_df
        
    except Exception as e:
        print(f"读取CSV文件失败: {str(e)}")
        raise

def call_translate_multi_api(news_data: Dict[str, Any], target_languages: List[str], api_url: str = "http://localhost:8571/translate/multi") -> Dict[str, Any]:
    """
    调用/translate/multi接口
    
    Args:
        news_data: 新闻数据字典，包含news_id, title, description, content
        target_languages: 目标语言列表
        api_url: API接口地址
        
    Returns:
        API响应结果
    """
    try:
        # 准备请求数据
        request_data = {
            "news_id": str(news_data['news_id']),
            "title": news_data['title'],
            "description": news_data['description'],
            "content": news_data['content'],
            "target_languages": target_languages
        }
        
        # 发送POST请求
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.post(
            api_url,
            json=request_data,
            headers=headers,
            timeout=300  # 5分钟超时
        )
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            print(f"新闻ID {news_data['news_id']} 翻译成功，状态: {result.get('status')}")
            return result
        else:
            error_msg = f"API调用失败，状态码: {response.status_code}"
            if response.text:
                error_msg += f"，错误信息: {response.text}"
            print(error_msg)
            return {
                'news_id': str(news_data['news_id']),
                'status': 'api_error',
                'error': error_msg
            }
            
    except requests.exceptions.Timeout:
        error_msg = "API调用超时"
        print(f"新闻ID {news_data['news_id']} {error_msg}")
        return {
            'news_id': str(news_data['news_id']),
            'status': 'timeout_error',
            'error': error_msg
        }
    except requests.exceptions.ConnectionError:
        error_msg = "无法连接到API服务器"
        print(f"新闻ID {news_data['news_id']} {error_msg}")
        return {
            'news_id': str(news_data['news_id']),
            'status': 'connection_error',
            'error': error_msg
        }
    except Exception as e:
        error_msg = f"调用API时发生错误: {str(e)}"
        print(f"新闻ID {news_data['news_id']} {error_msg}")
        return {
            'news_id': str(news_data['news_id']),
            'status': 'unknown_error',
            'error': error_msg
        }

def process_news_translation(csv_file_path: str, target_languages: List[str], output_file: str = None, max_records: int = None):
    """
    处理新闻翻译的主函数
    
    Args:
        csv_file_path: CSV文件路径
        target_languages: 目标语言列表
        output_file: 输出结果文件路径（可选）
        max_records: 最大处理记录数（可选，用于测试）
    """
    try:
        # 读取新闻数据
        news_df = read_news_data(csv_file_path)
        
        if max_records:
            news_df = news_df.head(max_records)
            print(f"限制处理前 {max_records} 条记录")
        news_df=news_df.head(1)
        # 存储所有翻译结果
        all_results = []
        
        # 逐条处理新闻
        for index, row in news_df.iterrows():
            print(f"\n处理第 {index + 1}/{len(news_df)} 条新闻，ID: {row['news_id']}")
            
            # 准备新闻数据
            news_data = {
                'news_id': row['news_id'],
                'title': row['title'],
                'description': row['description'],
                'content': row['content']
            }
            print(news_data)
            # 调用翻译API
            start_time = time.time()
            result = call_translate_multi_api(news_data, target_languages)
            end_time = time.time()
            print('耗时：{}'.format(end_time-start_time))
            all_results.append(result)
            
            # 打印简要结果
            if result.get('status') == 'success':
                translations_count = len(result.get('translations', []))
                print(f"  ✓ 成功翻译到 {translations_count} 种语言")
            else:
                print(f"  ✗ 翻译失败: {result.get('error', '未知错误')}")
        
        # 保存结果到文件
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)
            print(f"\n结果已保存到: {output_file}")
        
        # 统计结果
        success_count = sum(1 for r in all_results if r.get('status') == 'success')
        partial_success_count = sum(1 for r in all_results if r.get('status') == 'partial_success')
        error_count = len(all_results) - success_count - partial_success_count
        
        print(f"\n=== 处理完成 ===")
        print(f"总计处理: {len(all_results)} 条")
        print(f"完全成功: {success_count} 条")
        print(f"部分成功: {partial_success_count} 条")
        print(f"失败: {error_count} 条")
        
        return all_results
        
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")
        raise

def main():
    """
    主函数
    """
    # 配置参数
    csv_file_path = "test_news.csv"  # CSV文件路径
    target_languages = ["zh_TW","zh_HK","vi","ja","en","hi"]  # 目标语言列表，根据实际支持的语言调整
    output_file = "translation_results.json"  # 输出文件
    max_records = 5  # 限制处理条数，用于测试
    
    print("=== 新闻多语言翻译测试脚本 ===")
    print(f"CSV文件: {csv_file_path}")
    print(f"目标语言: {target_languages}")
    print(f"输出文件: {output_file}")
    print(f"最大处理条数: {max_records}")
    
    try:
        # 执行翻译处理
        results = process_news_translation(
            csv_file_path=csv_file_path,
            target_languages=target_languages,
            output_file=output_file,
            max_records=max_records
        )
        
        print("\n脚本执行完成！")
        
    except Exception as e:
        print(f"\n脚本执行失败: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())