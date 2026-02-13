import pandas as pd
from collections import Counter
import random
import streamlit as st
from datetime import datetime

# ==========================================
# 網頁配置與環境設定
# ==========================================
st.set_page_config(
    page_title="大樂透分析師", 
    page_icon="🧧",
    layout="centered"
)

def calculate_ac_value(nums):
    """
    計算 AC 值 (算術複雜度)
    大樂透建議值需 >= 7，代表號碼分佈較為隨機。
    """
    differences = set()
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            differences.add(abs(nums[i] - nums[j]))
    return len(differences) - (len(nums) - 1)

def count_consecutive_groups(nums):
    """
    計算連號組數 (例如 01, 02 為一組連號)
    """
    groups = 0
    i = 0
    while i < len(nums) - 1:
        if nums[i] + 1 == nums[i+1]:
            groups += 1
            while i < len(nums) - 1 and nums[i] + 1 == nums[i+1]:
                i += 1
        else:
            i += 1
    return groups

def check_history_match(target_nums, history_list):
    """
    比對大樂透歷史資料庫
    計算推薦組合與歷史紀錄的碰撞次數（中 2 碼至 6 碼）。
    """
    results = {6: 0, 5: 0, 4: 0, 3: 0, 2: 0}
    target_set = set(target_nums)
    for h_nums in history_list:
        match_count = len(target_set.intersection(set(h_nums)))
        if match_count >= 2:
            results[match_count] += 1
    return results

# ==========================================
# 主介面 UI 設計
# ==========================================
st.title("🧧 大樂透分析師")
st.markdown("""
本工具利用蒙地卡羅模擬法與權重分析，結合歷史碰撞偵測與現場樣本校正，為您的投注提供數據支持。
---
""")

# 1. 檔案上傳區
uploaded_file = st.file_uploader("📂 請上傳大樂透歷史數據 (Excel 格式)", type=["xlsx"])

if uploaded_file:
    try:
        # 讀取 Excel 數據
        df = pd.read_excel(uploaded_file, header=None, engine='openpyxl')
        history_rows = []
        all_nums = []
        
        # 數據清理邏輯
        for val in df.iloc[:, 1].dropna().astype(str):
            clean = val.replace(' ', ',').replace('，', ',').replace('?', '')
            nums = sorted([int(n) for n in clean.split(',') if n.strip().isdigit()])
            if len(nums) == 6:
                history_rows.append(nums)
                all_nums.extend(nums)
        
        if not history_rows:
            st.error("無法從檔案中解析出有效的 6 碼數據，請檢查 Excel 格式。")
            st.stop()

        # --- 歷史規律掃描 ---
        st.subheader("🕵️ 歷史規律掃描 (最近 30 期)")
        
        cols = st.columns(5)
        for i in range(min(5, len(history_rows))):
            h_nums = history_rows[i]
            h_sum = sum(h_nums)
            h_ac = calculate_ac_value(h_nums)
            cols[i].metric(f"前 {i+1} 期", f"Sum: {h_sum}", f"AC: {h_ac}")
            cols[i].caption(f"{h_nums}")

        with st.expander("查看完整最近 30 期數據明細"):
            history_data = []
            max_hist = min(30, len(history_rows))
            for i in range(max_hist):
                history_data.append({
                    "期數": f"前 {i+1} 期",
                    "開獎號碼": str(history_rows[i]),
                    "總和": sum(history_rows[i]),
                    "AC值": calculate_ac_value(history_rows[i]),
                    "連號": f"{count_consecutive_groups(history_rows[i])} 組"
                })
            st.table(pd.DataFrame(history_data))
        
        st.markdown("---")

        # --- 側邊欄：趨勢校正模式 ---
        st.sidebar.header("📝 趨勢校正模式")
        sample_sum = st.sidebar.number_input(
            "現場電腦選號總和", 
            min_value=0, 
            value=0, 
            help="輸入您在投注站看到的電腦選號總和，幫助程式校正當前出牌區間。"
        )
        
        if sample_sum > 0:
            st.sidebar.success(f"✅ 已鎖定區間：{sample_sum-20} ~ {sample_sum+20}")
        else:
            st.sidebar.info("提示：輸入現場樣本可提高模擬精準度。")

        # --- 核心分析運算 ---
        if st.button("🚀 執行 8000 次大樂透模擬分析", use_container_width=True):
            f_counts = Counter(all_nums)
            weighted_pool = []
            for n, count in f_counts.items():
                weighted_pool.extend([n] * count)
            
            # 決定總和區間
            if sample_sum > 0:
                target_min, target_max = sample_sum - 20, sample_sum + 20
            else:
                target_min, target_max = 120, 180 

            last_draw = set(history_rows[0]) if history_rows else set()
            candidates = []
            
            with st.spinner('蒙地卡羅運算中，請稍候...'):
                for _ in range(8000):
                    res_set = set()
                    while len(res_set) < 6:
                        res_set.add(random.choice(weighted_pool))
                    
                    res_list = sorted(list(res_set))
                    f_sum = sum(res_list)
                    ac_val = calculate_ac_value(res_list)
                    overlap = len(set(res_list).intersection(last_draw))
                    
                    # 篩選條件：避開四連號
                    has_quad = any(res_list[j]+3 == res_list[j+1]+2 == res_list[j+2]+1 == res_list[j+3] for j in range(len(res_list)-3))

                    if (target_min <= f_sum <= target_max and 
                        ac_val >= 7 and overlap <= 2 and not has_quad):
                        candidates.append((res_list, f_sum, ac_val))
                        if len(candidates) >= 10: break

            if candidates:
                rec_f, f_sum, ac_val = random.choice(candidates)
                
                # 執行歷史碰撞檢查
                match_results = check_history_match(rec_f, history_rows)

                st.success("✨ 分析完成！推薦組合：")
                st.markdown(f"## 推薦號碼：\n`{rec_f}`")

                # 顯示歷史回測結果
                st.markdown("### 📜 歷史碰撞紀錄 (資料庫比對)")
                m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                m_col1.metric("中頭獎", f"{match_results[6]} 次")
                m_col2.metric("中貳/參獎", f"{match_results[5]} 次")
                m_col3.metric("中肆/伍獎", f"{match_results[4]} 次")
                m_col4.metric("中陸/柒獎", f"{match_results[3]} 次")

                if match_results[6] > 0:
                    st.warning("⚠️ 注意：這組 6 碼在歷史中曾開過頭獎！")
                else:
                    st.info("✅ 安全：這組號碼未曾開過頭獎。")

                st.markdown("---")
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("預測總和", f_sum)
                col_b.metric("AC 複雜度", ac_val)
                col_c.metric("連號組數", count_consecutive_groups(rec_f))
                
                # 下載報告內容
                report_content = (
                    f"大樂透 6/49 大數據分析報告\n"
                    f"產生時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"----------------------------------\n"
                    f"推薦號碼: {rec_f}\n"
                    f"組合總和: {f_sum}\n"
                    f"AC 值: {ac_val}\n"
                    f"歷史碰撞: {match_results}\n"
                )
                st.download_button(
                    label="📥 下載分析報告 (.txt)",
                    data=report_content,
                    file_name=f"lotto_report_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
            else:
                st.error("❌ 在當前區間內找不到理想組合，請嘗試調整「現場樣本總和」。")

    except Exception as e:
        st.error(f"應用程式運行錯誤: {e}")
else:
    st.info("💡 歡迎使用！請先上傳大樂透歷史數據 Excel 檔案（lotto_649.xlsx）以開始分析。")

st.markdown("---")
st.caption("免責聲明：本工具僅供統計學分析與學術研究參考，投注請保持理性。")