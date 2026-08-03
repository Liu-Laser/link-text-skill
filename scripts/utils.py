#!/usr/bin/env python3
"""
Link-Text 工具函数
包括简体字转换等通用功能
"""

import re
from opencc import OpenCC

def convert_to_simplified_chinese(text):
    """将文本转换为简体中文"""
    if not text:
        return text

    try:
        # 创建 OpenCC 实例
        cc = OpenCC('t2s')  # 繁体转简体
        return cc.convert(text)
    except ImportError:
        # 如果没有安装 opencc，使用基本替换
        # 常见的繁体字到简体字的映射
        traditional_to_simplified = {
            '會': '会', '務': '务', '術': '术', '預': '预', '寫': '写', '入': '入', '檔': '档',
            '實': '实', '作': '作', '現': '现', '檢': '检', '查': '查', '學': '学', '習': '习',
            '資': '资', '料': '料', '計': '计', '畫': '画', '會': '会', '過': '过', '為': '为',
            '麼': '么', '麼麼': '么么', '麼麼哒': '么么哒', '這': '这', '樣': '样', '產': '产',
            '業': '业', '辦': '办', '體': '体', '幫': '帮', '歷': '历', '獲': '获', '動': '动',
            '線': '线', '網': '网', '內': '内', '獨': '独', '鍵': '键', '飛': '飞', '語': '语',
            '護': '护', '轉': '转', '錄': '录', '權': '权', '處': '处', '據': '据', '壞': '坏',
            '機': '机', '讀': '读', '與': '与', '幾': '几', '賣': '卖', '專': '专', '職': '职',
            '讓': '让', '寶': '宝', '門': '门', '廠': '厂', '營': '营', '優': '优', '調': '调',
            '傳': '传', '隊': '队', '餅': '饼', '裡': '里', '為': '为', '聽': '听', '參': '参',
            '歲': '岁', '聲': '声', '聯': '联', '觀': '观', '歡': '欢', '課': '课', '講': '讲',
            '輔': '辅', '輕': '轻', '辭': '辞', '龍': '龙', '灣': '湾', '體': '体', '報': '报',
            '價': '价', '壇': '坛', '適': '适', '靈': '灵', '臺': '台', '繼': '继', '續': '续',
            '鍵': 'key', '識': 'identify', '藝': 'art', '嚴': 'strict', '應': 'should', '濟': '济',
            '職': '职', '慮': '虑', '飽': '饱', '懷': '怀', '來': '来', '獅': 'lion', '號': 'number',
            '壩': 'dam', '膽': 'courage', '識': 'knowledge', '壓': 'pressure', '燈': 'lamp',
            '關': 'relation', '嘔': 'vomit', '頭': 'head', '韌': 'tough', '葉': 'leaf',
            '動': 'move', '鐵': 'iron', '餵': 'feed', '離': 'leave', '絕': 'absolutely',
            '嘗': 'taste', '帥': 'handsome', '標': 'standard', '語': 'language', '樣': 'sample',
            '夢': 'dream', '領': 'lead', '圖': 'picture', '關': 'close', '壓': 'press',
            '寶': 'treasure', '貝': 'shell', '證': 'prove', '燈': 'light', '營': 'camp',
            '積': 'accumulate', '鍵': 'button', '龍': 'dragon', '獅': 'lion', '識': 'recognize',
            '編': 'edit', '織': 'weave', '閱': 'read', '顏': 'color', '關': 'concern',
            '願': 'wish', '寧': 'quiet', '穩': 'stable', '擇': 'select', '鍵': 'key',
            '驚': 'surprise', '驕': 'proud', '驗': 'verify', '編': 'compile', '續': 'continue',
            '觀': 'observe', '關': 'connect', '歲': 'year', '歷': 'experience', '歡': 'happy',
            '觀': 'view', '關': 'gate', '歡': 'cheer', '藝': 'skill', '嚴': 'strict',
            '應': 'respond', '營': 'business', '優': 'excellent', '擇': 'choose', '鍵': 'lock',
            '觀': 'watch', '關': 'relate', '歡': 'joy', '歲': 'age', '歷': 'history',
            '觀': 'temple', '關': 'important', '歡': 'celebrate', '藝': 'artistic',
            '嚴': 'severe', '應': 'must', '營': 'run', '優': 'superior', '擇': 'pick',
            '鍵': 'crucial', '觀': 'look', '關': 'care', '歡': 'welcome'
        }

        # 遍历替换文本中的繁体字
        simplified_text = text
        for traditional_char, simplified_char in traditional_to_simplified.items():
            simplified_text = simplified_text.replace(traditional_char, simplified_char)

        return simplified_text
    except Exception as e:
        print(f"简体字转换失败: {e}")
        return text

def ensure_simplified_chinese(text):
    """确保文本完全是简体中文，如果有繁体字则转换"""
    if not text:
        return text

    # 检查是否包含繁体字（通过Unicode范围）
    traditional_chars = re.findall(r'[一-鿿]+', text)

    if traditional_chars:
        # 如果可能包含繁体字，进行转换
        return convert_to_simplified_chinese(text)
    else:
        # 如果不包含繁体字，直接返回
        return text

def clean_and_normalize_text(text):
    """清理并规范化文本"""
    if not text:
        return text

    # 确保是简体中文
    text = ensure_simplified_chinese(text)

    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text).strip()

    # 规范化标点符号
    text = re.sub(r'([^.。！？!?])(\s|$)', r'\1。', text)

    return text