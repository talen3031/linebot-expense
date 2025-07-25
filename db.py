from pymongo import MongoClient
from config import MONGO_URI, DB_NAME
from datetime import datetime

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def insert_expense(line_user_id, category, amount, desc, created_at):
    db.expenses.insert_one({
        "line_user_id": line_user_id,
        "category": category,
        "amount": amount,
        "desc": desc,
        "created_at": created_at
    })

def get_last_expenses(line_user_id, limit=5):
    return list(db.expenses.find({"line_user_id": line_user_id}).sort("created_at", -1).limit(limit))
def get_all_expenses(line_user_id):
    return list(db.expenses.find({"line_user_id": line_user_id}).sort("created_at", -1))
def delete_all_expenses(line_user_id):
    result = db.expenses.delete_many({"line_user_id": line_user_id})
    return result.deleted_count
def delete_expenses_by_range(line_user_id, start_idx, end_idx, limit=20):
    """
    刪除最近 limit 筆中的 start_idx ~ end_idx（包含）的紀錄。
    start_idx, end_idx 均從 0 開始計算（即第1筆是 0）
    """
    recs = get_all_expenses(line_user_id)
    # 範圍安全判斷
    if start_idx < 0 or end_idx >= len(recs) or start_idx > end_idx:
        return 0
    ids_to_delete = [recs[i]['_id'] for i in range(start_idx, end_idx+1)]
    result = db.expenses.delete_many({"_id": {"$in": ids_to_delete}})
    return result.deleted_count

def delete_expense_by_index(line_user_id, idx, limit=5):
    recs = get_all_expenses(line_user_id)
    if 0 <= idx < len(recs):
        db.expenses.delete_one({"_id": recs[idx]['_id']})
        return True
    return False

def _summary(line_user_id, week_start):
    pipeline = [
        {"$match": {"line_user_id": line_user_id, "created_at": {"$gte": week_start}}},
        {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}}
    ]
    return list(db.expenses.aggregate(pipeline))
def insert_category(name, keywords=None):
    db.categories.update_one(
        {"name": name},
        {"$setOnInsert": {"name": name, "keywords": keywords or []}},
        upsert=True
    )

def add_keyword_to_category(keyword, cat_name):
    db.categories.update_one(
        {"name": cat_name},
        {"$addToSet": {"keywords": keyword}}
    )

def get_category_keywords_dict():
    cats = db.categories.find()
    return {c["name"]: set(c.get("keywords", [])) for c in cats}
# db.py

def insert_user(line_user_id, display_name=None):
    db.users.update_one(
        {"line_user_id": line_user_id},
        {"$setOnInsert": {
            "line_user_id": line_user_id,
            "display_name": display_name,
            "created_at": datetime.utcnow(),
            "last_active": datetime.utcnow()
        }},
        upsert=True #當 line_user_id 不存在時，才會真正執行插入。
    )

def update_user_last_active(line_user_id):
    from datetime import datetime
    db.users.update_one(
        {"line_user_id": line_user_id},
        {"$set": {"last_active": datetime.utcnow()}}
    )

def get_user(line_user_id):
    return db.users.find_one({"line_user_id": line_user_id})
