import requests
import json
from datetime import datetime, timedelta

def get_sports_data():
    # 准备存储昨天、今天和明天比赛的列表
    yesterday_matches = []
    today_matches = []
    tomorrow_matches = []
    
    # 考虑到 GitHub Actions 服务器在海外（UTC时间），转换为北京时间 (UTC+8)
    now_utc = datetime.utcnow()
    now_bj = now_utc + timedelta(hours=8)
    
    # 【更新】精确计算昨天、今天、明天的日期字符串
    yesterday_str = (now_bj - timedelta(days=1)).strftime('%Y-%m-%d')
    today_str = now_bj.strftime('%Y-%m-%d')
    tomorrow_str = (now_bj + timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"正在获取北京时间 {yesterday_str}、{today_str} 和 {tomorrow_str} 的全量赛程...")
    
    # 体育联赛 ID 映射表 (TheSportsDB 官方标准英文字符串)
    leagues = {
        "English Premier League": "英超",
        "French Ligue 1": "法甲",
        "Spanish La Liga": "西甲",
        "Italian Serie A": "意甲",
        "German Bundesliga": "德甲",
        "NBA": "NBA",
        "NFL": "NFL",
        "FIFA World Cup": "世界杯"
    }
    
    # 【更新】循环范围增加昨天（yesterday_str）
    for target_date in [yesterday_str, today_str, tomorrow_str]:
        try:
            url = f"https://www.thesportsdb.com/api/v1/json/123/eventsday.php?d={target_date}"
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                continue
                
            data = response.json()
            events = data.get('events')
            if not events:
                continue
                
            for event in events:
                league_name_en = event.get('strLeague')
                
                if league_name_en in leagues:
                    match_time = event.get('strTime', '00:00:00')[:5] 
                    
                    # 抓取比分信息（用于昨天的完赛显示，若没比分则显示为空或未开赛）
                    home_score = event.get('intHomeScore')
                    away_score = event.get('intAwayScore')
                    
                    # 组装数据结构
                    match_item = {
                        "time": match_time,
                        "league": leagues[league_name_en],
                        "homeTeam": event.get('strHomeTeam'),
                        "awayTeam": event.get('strAwayTeam'),
                        "homeScore": home_score if home_score is not None else "",
                        "awayScore": away_score if away_score is not None else ""
                    }
                    
                    # 根据日期分流
                    if target_date == yesterday_str:
                        yesterday_matches.append(match_item)
                    elif target_date == today_str:
                        today_matches.append(match_item)
                    else:
                        tomorrow_matches.append(match_item)
                        
        except Exception as e:
            print(f"获取 {target_date} 数据失败: {e}")
            
    # 【更新】组装包含天、今、明三天的格式
    result = {
        "yesterday": yesterday_matches,
        "today": today_matches,
        "tomorrow": tomorrow_matches
    }
    
    with open('schedule.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("schedule.json 更新成功！")

if __name__ == "__main__":
    get_sports_data()