import random
import streamlit as st
from datetime import datetime

# ==========================================
# 純數學版本 - 完全獨立事件
# ==========================================

def calculate_ac(nums):
    diffs = set()
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            diffs.add(abs(nums[i] - nums[j]))
    return len(diffs) - (len(nums) - 1)

def get_consecutive_info(nums):
    nums = sorted(nums)
    max_streak = 1
    current = 1
    for i in range(1, len(nums)):
        if nums[i] == nums[i-1] + 1:
            current += 1
            max_streak = max(max_streak, current)
        else:
            current = 1
    return max_streak

def generate_combo():
    while True:
        combo = sorted(random.sample(range(1, 40), 5))
        
        # 1. 避開生日陷阱
        if not any(n > 31 for n in combo):
            continue
        
        # 2. 避免 3 連號以上
        if get_consecutive_info(combo) >= 3:
            continue
        
        # 3. 提升組合複雜度
        if calculate_ac(combo) < 5:
            continue
        
        return combo

# ==========================================
# Streamlit UI
# ==========================================

st.set_page_config(page_title="Gauss Pure Random v1.0", page_icon="🎲")

st.title("🎲 Gauss Pure Random v1.0")
st.markdown("完全獨立事件模型，不使用任何歷史資料。")

num_sets = st.slider("產生組數", 1, 10, 5)

if st.button("生成隨機組合"):
    results = []
    for _ in range(num_sets):
        combo = generate_combo()
        results.append({
            "號碼": ", ".join(map(str, combo)),
            "AC值": calculate_ac(combo),
            "總和": sum(combo)
        })
    
    st.table(results)
    st.success("✅ 本模型未使用任何歷史數據。")

st.caption("Pure Probability Model | Independent Event System")