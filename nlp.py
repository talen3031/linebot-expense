from db import get_category_keywords_dict, insert_category, add_keyword_to_category
import jieba
import re
def nlp_classify(desc):
    category_keywords = get_category_keywords_dict()

    # 1. 先看是不是標準「XXX(YYY)」或「XXX（YYY）」格式
    m = re.match(r"(.+)[（(](.+)[）)]", desc)
    if m:
        item = m.group(1).strip()
        new_cat = m.group(2).strip()
        # 如果主類別已存在且 item 已在這個主類別關鍵字裡，直接回傳
        if new_cat in category_keywords and item in category_keywords[new_cat]:
            return new_cat, item
        # 若主類別存在但 item 不在裡面，幫他加進去
        if new_cat in category_keywords:
            add_keyword_to_category(item, new_cat)
            return new_cat, item
        # 若主類別不存在，自動新建
        insert_category(new_cat, [item])
        return new_cat, item

    # 2. 如果不是括號語法，走原本分詞判斷
    tokens = set(jieba.cut(desc))
    for cat, keywords in category_keywords.items():
        if tokens & keywords:
            return cat, desc
        for kw in keywords:
            if kw in desc:
                return cat, desc

    return "其他", desc
