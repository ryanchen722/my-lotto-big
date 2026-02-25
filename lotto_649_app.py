import random
import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# 核心演算法：純粹獨立事件過濾器
# ==========================================

def get_metrics(nums):
    """一次性計算 AC 值與最大連號長度，提升效率"""
    nums = sorted(nums)
    
    # 計算 AC 值 (Arithmetic Complexity)
    diffs = set()
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            diffs.add(abs(nums[i] - nums[j]))
    ac = len(diffs) - (len(nums) - 1)
    
    # 計算連號長度
    max_streak = 1
    current = 1
    for i in range(1, len(nums)):
        if nums[i] == nums[i-1] + 1:
            current += 1
            max_streak = max(max_streak, current)
        else:
            current = 1
            
    return ac, max_streak

def generate_pure_combo():
    """生成完全隨機但符合結構美感的組合"""
    while True:
        combo = sorted(random.sample(range(1, 40), 5))
        ac, streak = get_metrics(combo)
        
        # 過濾標準：基於大數法則
        # 1. 避開日期陷阱 (至少一個號碼 > 31)
        if not any(n > 31 for n in combo):
            continue
        
        # 2. 避免低機率的三連號
        if streak >= 3:
            continue
        
        # 3. 確保複雜度 (避開等差數列或過於整齊的組合)
        if ac < 5:
            continue
        
        return combo, ac

# ==========================================
# Streamlit UI 介面
# ==========================================

st.set_page_config(page_title="Gauss Pure Random v1.1", page_icon="🎲", layout="centered")

st.title("🎲 Gauss Pure Random v1.1")
st.markdown("""
### 獨立事件模型 (Independent Event Model)
本模型遵循**「機率無記憶性」**原則，不參考任何歷史開獎數據。
其唯一目標是從數學角度過濾掉「人為特徵」過強的低機率組合。
""")

with st.sidebar:
    st.header("⚙️ 生成設定")
    num_sets = st.slider("產生組數", 1, 10, 5)
    st.divider()
    st.markdown("#### 數學約束條件：")
    st.write("✅ AC 值 ≥ 5 (確保隨機性)")
    st.write("✅ 最大連號 < 3 (避開極端值)")
    st.write("✅ 包含 > 31 號碼 (避開日期熱區)")

if st.button("✨ 生成純粹隨機組合", use_container_width=True):
    final_results = []
    
    # 模擬生成過程
    for i in range(num_sets):
        combo, ac = generate_pure_combo()
        combo_sum = sum(combo)
        
        # 呈現格式化
        final_results.append({
            "組別": f"第 {i+1} 組",
            "隨機號碼": "  |  ".join([f"{n:02d}" for n in combo]),
            "AC 複雜度": ac,
            "組合總和": combo_sum
        })
    
    # 顯示結果表格
    df = pd.DataFrame(final_results)
    st.dataframe(df, hide_index=True, use_container_width=True)
    
    st.success("✅ 已排除人為規律，保留純粹隨機性。")
    
    # 下載報告
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    report_text = f"Gauss Pure Random v1.1 生成報告\n時間: {datetime.now()}\n" + "="*40 + "\n"
    for r in final_results:
        report_text += f"{r['組別']}: {r['隨機號碼']} (AC:{r['AC 複雜度']}, Sum:{r['組合總和']})\n"
    
    st.download_button("📥 下載結果", report_text, file_name=f"PureRandom_{timestamp}.txt")

st.markdown("---")
st.caption("Pure Probability | No Bias | High Entropy Selection")

