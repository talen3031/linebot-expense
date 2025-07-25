
import matplotlib.pyplot as plt
import uuid
import os
import tempfile

def generate_weekly_chart(stats):
    import matplotlib
    matplotlib.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial Unicode MS']
    matplotlib.rcParams['axes.unicode_minus'] = False

    categories = [r['_id'] for r in stats]
    amounts = [r['total'] for r in stats]
    plt.figure(figsize=(6,3))
    plt.bar(categories, amounts)
    plt.title("本週各類支出")
    plt.xlabel("類別")
    plt.ylabel("金額")
    plt.tight_layout()
    # 用 uuid 保證英文檔名，且存在 temp 英文資料夾
    temp_name = os.path.join(tempfile.gettempdir(), f"chart_{uuid.uuid4().hex}.png")
    plt.savefig(temp_name)
    plt.close()
    return temp_name