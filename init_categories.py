from pymongo import MongoClient
from config import MONGO_URI, DB_NAME
category_keywords = {
    "娛樂購物": {"電影", "美容美髮", "數位服務", "遊戲", "音樂", "唱歌", "旅遊", "按摩",
             "服飾", "3c產品", "美妝保養", "精品","夾娃娃", "網路購物"},
    "飲食": {"早餐", "飯","麵", "午餐","晚餐","便當", "炒飯", "炒麵","拉麵", "牛肉麵","蛋餅", "漢堡", "吐司", "麥當勞"},
    "醫療": {"掛號","醫療用品", "藥品", "牙醫", "眼科", "健康檢查", "保健食品", "健身運動"},
    "金融": set(),
    "稅金": set(),
    "其他": set(),
    "電信": set(),
    "住家": {"水費","電費", "瓦斯", "管理費","房貸", "洗衣費","居家服務", "日常用品", "房租"},
    "交通": {"捷運","火車", "公車", "計程車","uber", "高鐵","租車", "車票", "YouBike"},
    "學習": {"線上課程","課程","課","上課" },
}

# 依你的 config 修改
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

for name, keywords in category_keywords.items():
    db.categories.update_one(
        {"name": name},
        {"$set": {
            "keywords": list(keywords),
            "desc": "",
        }},
        upsert=True
    )

print("初始化主類別寫入完成！")
