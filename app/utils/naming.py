"""命名格式处理工具"""
import re
import os
from typing import Dict, Any


# 可用的变量列表
AVAILABLE_VARIABLES = ["student_id", "name", "gender", "dormitory"]


def apply_naming_format(format_template: str, member_data: Dict[str, Any], file_ext: str = "") -> str:
    """
    应用命名格式模板
    
    Args:
        format_template: 格式模板，如 "{student_id}_{name}"
        member_data: 成员数据字典，包含 student_id, name, gender, dormitory
        file_ext: 文件扩展名（包含点号）
    
    Returns:
        格式化后的文件名
    """
    result = format_template
    
    # 替换所有变量
    for var in AVAILABLE_VARIABLES:
        placeholder = "{" + var + "}"
        value = member_data.get(var, "") or ""
        # 清理文件名中的非法字符
        value = sanitize_filename(str(value))
        result = result.replace(placeholder, value)
    
    # 添加扩展名
    if file_ext and not result.endswith(file_ext):
        result += file_ext
    
    return result


def sanitize_filename(filename: str) -> str:
    """
    清理文件名中的非法字符
    
    Args:
        filename: 原始文件名
    
    Returns:
        清理后的文件名
    """
    # 移除或替换非法字符
    illegal_chars = r'[<>:"/\\|?*]'
    result = re.sub(illegal_chars, "_", filename)
    
    # 移除首尾空格和点号
    result = result.strip(". ")
    
    # 限制长度
    if len(result) > 200:
        result = result[:200]
    
    return result


def validate_naming_format(format_template: str) -> tuple[bool, str]:
    """
    验证命名格式模板
    
    Args:
        format_template: 格式模板
    
    Returns:
        (是否有效, 错误信息)
    """
    if not format_template:
        return False, "格式模板不能为空"
    
    # 检查是否包含至少一个变量
    has_variable = False
    for var in AVAILABLE_VARIABLES:
        if "{" + var + "}" in format_template:
            has_variable = True
            break
    
    if not has_variable:
        return False, f"格式模板必须包含至少一个变量: {AVAILABLE_VARIABLES}"
    
    # 检查是否有未知变量
    pattern = r'\{(\w+)\}'
    matches = re.findall(pattern, format_template)
    for match in matches:
        if match not in AVAILABLE_VARIABLES:
            return False, f"未知变量: {match}，可用变量: {AVAILABLE_VARIABLES}"
    
    return True, ""


def generate_unique_filename(base_name: str, existing_names: set, file_ext: str = "") -> str:
    """
    生成唯一文件名（处理同名冲突）
    
    Args:
        base_name: 基础文件名（不含扩展名）
        existing_names: 已存在的文件名集合
        file_ext: 文件扩展名
    
    Returns:
        唯一的文件名
    """
    full_name = base_name + file_ext
    
    if full_name not in existing_names:
        return full_name
    
    # 添加序号
    counter = 1
    while True:
        new_name = f"{base_name}_{counter}{file_ext}"
        if new_name not in existing_names:
            return new_name
        counter += 1
