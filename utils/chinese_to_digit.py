CHINESE_DIGITS = {"零":0, "一":1, "二":2, "兩":2, "三":3, "四":4, "五":5, "六":6, "七":7, "八":8, "九":9}

def chinese_to_digit(cn:str):
    # 支援一～九九
    cn = cn.strip()
    if cn.isdigit():
        return int(cn)
    n = 0
    if '十' in cn:
        parts = cn.split('十')
        if parts[0]=='':
            n += 10
        else:
            n += CHINESE_DIGITS.get(parts[0],0)*10
        if len(parts)==2 and parts[1]!='':
            n += CHINESE_DIGITS.get(parts[1],0)
        elif len(parts)==1 or parts[1]=='':
            pass
    else:
        n += CHINESE_DIGITS.get(cn,0)
    return n


