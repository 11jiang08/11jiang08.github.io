import requests
import json
from datetime import datetime, timedelta

def get_sports_data():
    # 准备存储今天和明天比赛的列表
    today_matches = []
    tomorrow_matches = []
    
    # 获取今天和明天的日期字符串 (YYYY-MM-DD)
    # 考虑到 GitHub Actions 服务器在海外（UTC时间），我们转换为北京时间 (UTC+8)
    now_utc = datetime.utcnow()
    now_bj = now_utc + timedelta(hours=8)
    today_str = now_bj.strftime('%Y-%m-%d')
    tomorrow_str = (now_bj + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 体育联赛 ID 映射表 (TheSportsDB 免费开放接口 ID)
    # 4328: 英超, 4334: 法甲, 4335: 西甲, 4332: 意甲, 4331: 德甲, 4387: NBA, 4391: NFL, 4432: 世界杯
    leagues = {
        "英超": "4328",
        "法甲": "4334",
        "西甲": "4335",
        "意甲": "4332",
        "德甲": "4331",
        "NBA": "4387",
        "NFL": "4391",
        "世界杯": "4432"
    }
    
    for league_name, league_id in leagues.items():
        try:
            # 调用 TheSportsDB 开放接口获取该联赛的近期赛程
            url = f"https://www.thesportsdb.com/api/v1/json/3/eventsnextleague.php?id={league_id}"
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                continue
                
            data = response.json()
            events = data.get('events')
            if not events:
                continue
                
            for event in events:
                match_date = event.get('dateEvent') # 格式通常为 YYYY-MM-DD
                
                if match_date in [today_str, tomorrow_str]:
                    # 格式化时间 (取出 HH:MM)
                    match_time = event.get('strTime', '00:00:00')[:5] 
                    
                    match_item = {
                        "time": match_time,
                        "league": league_name,
                        "homeTeam": event.get('strHomeTeam'),
                        "awayTeam": event.get('strAwayTeam')
                    }
                    
                    if match_date == today_str:
                        today_matches.append(match_item)
                    else:
                        tomorrow_matches.append(match_item)
                        
        except Exception as e:
            print(f"获取 {league_name} 数据失败: {e}")
            
    # 组装最终写入 json 的格式
    result = {
        "today": today_matches,
        "tomorrow": tomorrow_matches
    }
    
    # 将数据写入 schedule.json
    with open('schedule.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("schedule.json 更新成功！")

if __name__ == "__main__":
    get_sports_data()