from fastmcp import FastMCP
from datetime import datetime, timezone, timedelta
from typing import Optional, List
import pytz

mcp = FastMCP("日期时间服务 📅")

@mcp.tool
def get_current_date(timezone_str: Optional[str] = None) -> str:
    """获取当前日期
    
    Args:
        timezone_str: 时区，如 'Asia/Shanghai', 'UTC'，默认本地时区
    
    Returns:
        当前日期字符串 (YYYY-MM-DD)
    """
    try:
        if timezone_str:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)
        else:
            now = datetime.now()
        return now.strftime("%Y-%m-%d")
    except Exception as e:
        return f"错误: {str(e)}"

@mcp.tool
def get_current_time(timezone_str: Optional[str] = None) -> str:
    """获取当前时间
    
    Args:
        timezone_str: 时区，如 'Asia/Shanghai', 'UTC'，默认本地时区
    
    Returns:
        当前时间字符串 (HH:MM:SS)
    """
    try:
        if timezone_str:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)
        else:
            now = datetime.now()
        return now.strftime("%H:%M:%S")
    except Exception as e:
        return f"错误: {str(e)}"

@mcp.tool
def get_current_datetime(timezone_str: Optional[str] = None) -> str:
    """获取当前日期和时间
    
    Args:
        timezone_str: 时区，如 'Asia/Shanghai', 'UTC'，默认本地时区
    
    Returns:
        当前日期时间字符串 (YYYY-MM-DD HH:MM:SS)
    """
    try:
        if timezone_str:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)
        else:
            now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        return f"错误: {str(e)}"

@mcp.tool
def get_date_info(timezone_str: Optional[str] = None) -> dict:
    """获取详细的日期信息
    
    Args:
        timezone_str: 时区，如 'Asia/Shanghai', 'UTC'，默认本地时区
    
    Returns:
        包含详细日期信息的字典
    """
    try:
        if timezone_str:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)
        else:
            now = datetime.now()
        
        return {
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "year": now.year,
            "month": now.month,
            "day": now.day,
            "hour": now.hour,
            "minute": now.minute,
            "second": now.second,
            "weekday": now.weekday(),  # 0=周一, 6=周日
            "weekday_name": now.strftime("%A"),
            "weekday_name_zh": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][now.weekday()],
            "day_of_year": now.timetuple().tm_yday,
            "week_of_year": now.isocalendar()[1],
            "is_leap_year": (now.year % 4 == 0 and now.year % 100 != 0) or (now.year % 400 == 0),
            "timezone": str(now.tzinfo) if now.tzinfo else "本地时区"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def format_date(date_str: str, format_str: str = "%Y-%m-%d", timezone_str: Optional[str] = None) -> str:
    """格式化日期
    
    Args:
        date_str: 日期字符串
        format_str: 格式化字符串，如 "%Y-%m-%d", "%Y年%m月%d日", "%m/%d/%Y"
        timezone_str: 时区，如 'Asia/Shanghai', 'UTC'，默认本地时区
    
    Returns:
        格式化后的日期字符串
    """
    try:
        if timezone_str:
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)
        else:
            now = datetime.now()
        
        # 如果date_str是"today"或"now"，使用当前日期
        if date_str.lower() in ["today", "now", "当前", "今天"]:
            return now.strftime(format_str)
        
        # 尝试解析输入日期
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        if timezone_str:
            date_obj = tz.localize(date_obj)
        
        return date_obj.strftime(format_str)
    except Exception as e:
        return f"错误: {str(e)}"

@mcp.tool
def list_common_timezones() -> List[str]:
    """列出常用时区
    
    Returns:
        常用时区列表
    """
    return [
        "UTC",
        "Asia/Shanghai",
        "Asia/Tokyo",
        "Asia/Hong_Kong",
        "Asia/Singapore",
        "Europe/London",
        "Europe/Paris",
        "Europe/Berlin",
        "America/New_York",
        "America/Los_Angeles",
        "America/Chicago",
        "Australia/Sydney",
        "Pacific/Auckland"
    ]

if __name__ == "__main__":
    mcp.run()