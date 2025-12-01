import streamlit as st
import os
import sys
import time

# ==========================================
# 🛑 网络配置
# ==========================================
for k in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'all_proxy']:
    if k in os.environ:
        del os.environ[k]

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import tushare as ts 
import re
from datetime import datetime, timedelta

# ==========================================
# 系统配置
# ==========================================
st.set_page_config(layout="wide", page_title="AlphaTrace Pro | 天蓝雅致")

st.markdown("""
<style>
    .stApp {background-color: #FFFFFF;}
    h1, h2, h3, h4, h5, h6, p, div {color: #333333; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;}
    
    /* 股票头部信息 */
    .stock-header {font-size: 28px; font-weight: 900;} 
    .stock-price {font-size: 28px; font-weight: bold; margin-left: 15px;}
    .stock-pct {font-size: 22px; font-weight: bold; margin-left: 10px;}
    .stock-info {font-size: 16px; color: #666; margin-left: 20px; font-family: monospace;}
    
    /* 左侧分析框 */
    .analysis-box {
        background-color: #f8f9fa; padding: 25px; border-radius: 12px; border-left: 8px solid #3B82F6; height: 100%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .analysis-title {font-weight: 900; font-size: 22px; margin-bottom: 15px; color: #3B82F6;}
    .analysis-content {font-size: 20px; line-height: 1.8; color: #2c3e50; font-weight: 500;}
    
    /* 右侧评分卡 */
    .score-card {
        background-color: #fff; padding: 20px; border-radius: 12px; border: 1px solid #eee; height: 100%;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .score-val {font-size: 56px; font-weight: 900; line-height: 1;}
    .score-grade {font-size: 22px; font-weight: bold; margin-top: 5px; padding: 4px 16px; border-radius: 20px; color: white;}
    .score-conclusion {margin-top: 15px; font-size: 16px; font-weight: bold; color: #333; text-align: center; border-top: 1px dashed #eee; width: 100%; padding-top: 10px;}
    .score-neg {color: #d32f2f; font-weight: bold; margin-top: 8px; font-size: 14px; text-align: center;}

    /* 🟢 核心美化：将 Primary 按钮 (红色) 强制改为 天蓝色 */
    div.stButton > button[kind="primary"] {
        background-color: #00a8ff; /* 天蓝色 */
        border-color: #00a8ff;
        color: white;
        font-weight: bold;
        font-size: 16px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #008ecc; /* 悬停深一点 */
        border-color: #008ecc;
        box-shadow: 0 4px 8px rgba(0, 168, 255, 0.3);
    }
    div.stButton > button[kind="primary"]:active {
        background-color: #0077aa;
    }

    section[data-testid="stSidebar"] {background-color: #f8f9fa;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

HISTORY_FILE = 'strategy_history.csv'

if 'stock_list' not in st.session_state:
    my_portfolio = [
        {"code": "300188.SZ", "name": "国投智能"},
        {"code": "300811.SZ", "name": "铂科新材"}, 
        {"code": "002270.SZ", "name": "华明装备"}, 
        {"code": "002353.SZ", "name": "杰瑞股份"},
        {"code": "002230.SZ", "name": "科大讯飞"}, 
        {"code": "600276.SH", "name": "恒瑞医药"},
        {"code": "300487.SZ", "name": "蓝晓科技"}, 
        {"code": "002683.SZ", "name": "广东宏大"},
        {"code": "002436.SZ", "name": "兴森科技"}, 
        {"code": "300563.SZ", "name": "神宇股份"},
        {"code": "002463.SZ", "name": "沪电股份"}, 
        {"code": "300450.SZ", "name": "先导智能"},
        {"code": "000737.SZ", "name": "北方铜业"}, 
        {"code": "605358.SH", "name": "立昂微"},
        {"code": "600366.SH", "name": "宁波韵升"}, 
        {"code": "300748.SZ", "name": "金力永磁"},
        {"code": "300572.SZ", "name": "安车检测"}, 
        {"code": "603019.SH", "name": "中科曙光"},
        {"code": "603893.SH", "name": "瑞芯微"}, 
        {"code": "300533.SZ", "name": "冰川网络"},
        {"code": "002558.SZ", "name": "巨人网络"}, 
        {"code": "600580.SH", "name": "卧龙电驱"},
        {"code": "002472.SZ", "name": "双环传动"}, 
        {"code": "002896.SZ", "name": "中大力德"},
        {"code": "600143.SH", "name": "金发科技"}, 
        {"code": "002182.SZ", "name": "宝武镁业"},
        {"code": "600111.SH", "name": "北方稀土"}, 
        {"code": "300496.SZ", "name": "中科创达"},
        {"code": "300604.SZ", "name": "长川科技"}, 
        {"code": "002837.SZ", "name": "英维克"},
        {"code": "600309.SH", "name": "万华化学"}, 
        {"code": "600489.SH", "name": "中金黄金"},
        {"code": "300769.SZ", "name": "德方纳米"}, 
        {"code": "301358.SZ", "name": "湖南裕能"},
        {"code": "600506.SH", "name": "统一股份"}, 
        {"code": "002428.SZ", "name": "云南锗业"},
        {"code": "300015.SZ", "name": "爱尔眼科"}, 
        {"code": "002714.SZ", "name": "牧原股份"},
        {"code": "600598.SH", "name": "北大荒"}, 
        {"code": "000568.SZ", "name": "泸州老窖"},
        {"code": "000661.SZ", "name": "长春高新"}, 
        {"code": "300059.SZ", "name": "东方财富"},
        {"code": "600036.SH", "name": "招商银行"}, 
        {"code": "601398.SH", "name": "工商银行"},
        {"code": "600900.SH", "name": "长江电力"}, 
        {"code": "601138.SH", "name": "工业富联"},
        {"code": "300476.SZ", "name": "胜宏科技"}, 
        {"code": "300502.SZ", "name": "新易盛"},
        {"code": "300394.SZ", "name": "天孚通信"}, 
        {"code": "688256.SH", "name": "寒武纪-U"},
        {"code": "688981.SH", "name": "中芯国际"}
    ]
    st.session_state.stock_list = pd.DataFrame(my_portfolio)

# ==========================================
# 🟢 辅助函数
# ==========================================
def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext.replace('**', '').strip()

def save_to_history(code, name, score, grade, conclusion, vol_ratio, rr_display):
    if os.path.exists(HISTORY_FILE):
        df_hist = pd.read_csv(HISTORY_FILE)
    else:
        df_hist = pd.DataFrame(columns=['更新时间', '代码', '名称', '得分', '评级', '战术建议', '量比', '盈亏比'])
    
    df_hist = df_hist[df_hist['代码'] != code]
    new_record = {
        '更新时间': datetime.now().strftime("%Y-%m-%d %H:%M"),
        '代码': code, '名称': name, '得分': score, '评级': grade,
        '战术建议': conclusion, '量比': round(vol_ratio, 2), '盈亏比': clean_html(rr_display)
    }
    df_hist = pd.concat([df_hist, pd.DataFrame([new_record])], ignore_index=True)
    df_hist = df_hist.sort_values(by='得分', ascending=False)
    df_hist.to_csv(HISTORY_FILE, index=False)
    return df_hist

def auto_fix_code(code):
    code = code.strip()
    if "." in code: return code.upper()
    if code.startswith("6"): return code + ".SH"
    elif code.startswith("8") or code.startswith("4"): return code + ".BJ"
    else: return code + ".SZ"

# ==========================================
# 🟢 核心算法集
# ==========================================
def calculate_tb_alpha_score(row, prev_row, view_high, rr_ratio, is_golden_spider, has_pressure, is_divergence):
    score = 0
    breakdown = []
    negatives = [] 
    
    close = row['Close']
    ma5, ma10, ma20, ma60 = row['MA5'], row['MA10'], row['MA20'], row['MA60']
    prev_ma60 = prev_row['MA60']
    vol_ratio = row['Vol_Ratio']
    pct_change = row['Pct_Change']
    vwap = row['VWAP']
    bias = row['BIAS']
    
    is_breakout = (pct_change > 5.0) and (vol_ratio > 1.8) and (close > ma60)
    is_limit_up = pct_change > 9.0
    
    # 1. 趋势 (30分)
    trend_s = 0
    if is_golden_spider and close > ma60:
        trend_s = 30; breakdown.append("🕸️ [趋势] 困龙升天 (金蜘蛛) (+30)")
    elif close < ma60:
        trend_s += 0; breakdown.append("❌ [趋势] 股价<MA60 (0)")
    else:
        if ma60 >= prev_ma60: trend_s += 15; breakdown.append("✅ [趋势] 站稳MA60 (+15)")
        else:
            if is_breakout or is_limit_up: trend_s += 15; breakdown.append("🔥 [趋势] 强力扭转 (+15)")
            else: trend_s += 5; breakdown.append("⚖️ [趋势] MA60未平 (+5)")
            
    if is_golden_spider: trend_s += 15; breakdown.append("🕸️ [均线] 高度共振 (+15)")
    elif ma5 > ma10 > ma20: trend_s += 15; breakdown.append("✅ [均线] 多头排列 (+15)")
    elif ma5 > ma20 and ma10 > ma20: trend_s += 15; breakdown.append("✅ [均线] 向上发散 (+15)")
    elif close < ma20: trend_s += 0; breakdown.append("❌ [均线] 破位MA20 (0)")
    else: trend_s += 5; breakdown.append("⚖️ [均线] 杂乱 (+5)")
    score += trend_s

    # 2. 流动性 (25分)
    liq_s = 0
    if is_limit_up and vol_ratio < 1.0: liq_s += 25; breakdown.append("👑 [量能] 缩量板 (+25)")
    elif is_divergence: liq_s += 0; negatives.append("⚠️ 量价背离"); breakdown.append("⚠️ [量能] 背离 (0)")
    else:
        if 1.0 <= vol_ratio <= 3.0: 
            if has_pressure: liq_s += 5; breakdown.append("⚠️ [量能] 放量滞涨 (+5)")
            else: liq_s += 15; breakdown.append("✅ [量能] 活跃 (+15)")
        elif 0.8 <= vol_ratio < 1.0: liq_s += 10; breakdown.append("⚖️ [量能] 正常 (+10)")
        elif vol_ratio > 3.0: liq_s += 15; breakdown.append("🔥 [量能] 抢筹 (+15)")
        elif vol_ratio < 0.6: liq_s += 0; breakdown.append("❌ [量能] 僵尸 (0)")
        else: liq_s += 5; breakdown.append("⚠️ [量能] 交易冷清 (+5)")
    score += liq_s

    # 3. 结构 (25分)
    struc_s = 0
    if has_pressure: struc_s -= 15; negatives.append("☠️ 射击之星"); breakdown.append("☠️ [形态] 见顶 (-15)")
    
    dist_ma20 = (close - ma20) / ma20
    if is_golden_spider: struc_s += 15; breakdown.append("✅ [位置] 粘合启动 (+15)")
    elif abs(dist_ma20) < 0.03 and close > ma20: struc_s += 15; breakdown.append("✅ [位置] 回踩支撑 (+15)")
    elif bias > 15: struc_s -= 10; breakdown.append("⚠️ [位置] 超买 (-10)")
    else: struc_s += 5; breakdown.append("⚖️ [位置] 悬空 (+5)")
        
    if is_breakout or is_limit_up: struc_s += 10; breakdown.append("🔨 [筹码] 突围 (+10)")
    elif close >= view_high * 0.99: struc_s += 10; breakdown.append("✅ [筹码] 新高 (+10)")
    elif close > vwap: struc_s += 8; breakdown.append("✅ [筹码] 站上成本 (+8)")
    else: struc_s += 0; breakdown.append("❌ [筹码] 套牢区 (0)")
    score += struc_s

    # 4. 盈亏比 (20分)
    rr_s = 0
    if has_pressure: rr_s += 0; breakdown.append("⚠️ [赔率] 形态坏 (0)")
    elif rr_ratio == float('inf') or rr_ratio > 3.0: rr_s += 20; breakdown.append("✅ [赔率] 完美 (+20)")
    elif rr_ratio >= 1.5: rr_s += 15; breakdown.append("✅ [赔率] 合格 (+15)")
    else: rr_s += 0; breakdown.append("❌ [赔率] 亏本 (0)")
    score += rr_s
    
    if score >= 90: grade, g_color, concl = "S 级", "#d32f2f", "👑 核心资产，强推"
    elif score >= 75: grade, g_color, concl = "A 级", "#ef6c00", "🚀 趋势启动，买入"
    elif score >= 60: grade, g_color, concl = "B 级", "#f9a825", "😐 震荡，轻仓"
    else: grade, g_color, concl = "C 级 (垃圾)", "#455a64", "☠️ 破位，调出"
    
    return score, grade, g_color, breakdown, concl, negatives

def analyze_market_behavior(row, view_high, rr_ratio, low_60d, is_breakout, is_golden_spider, has_pressure, is_divergence):
    vol_ratio = row['Vol_Ratio']
    bias = row['BIAS'] 
    close = row['Close']
    vwap = row['VWAP'] 
    ma20 = row['MA20']
    ma60 = row['MA60']
    
    if is_divergence: vol_msg = f"⚠️ **[资金]** 量比 {vol_ratio:.2f}，高位缩量滞涨，量价背离！"
    elif has_pressure: vol_msg = f"⚠️ **[资金]** 冲高回落，主力出货嫌疑。"
    elif vol_ratio > 3.0: vol_msg = f"🔥 **[资金]** 量比 {vol_ratio:.2f}，主力扫货，攻击意愿极强。"
    elif vol_ratio > 2.0: vol_msg = f"🔥 **[资金]** 量比 {vol_ratio:.2f}，资金活跃，抢筹明显。"
    elif vol_ratio > 1.2: vol_msg = f"🚀 **[资金]** 量比 {vol_ratio:.2f}，温和放量攻击。"
    elif vol_ratio < 0.6: vol_msg = f"🧊 **[资金]** 量比 {vol_ratio:.2f}，流动性枯竭。"
    else: vol_msg = f"⚖️ **[资金]** 量比 {vol_ratio:.2f}，换手正常。"

    if has_pressure: trend_msg = f"☠️ **[形态]** 射击之星，短线见顶！"
    elif is_golden_spider: trend_msg = f"🕸️ **[趋势]** 金蜘蛛启动，起爆点！"
    elif is_breakout: trend_msg = f"🚀 **[趋势]** 长阳突破MA60，反转！"
    elif close < ma60: trend_msg = f"❌ **[趋势]** 熊市压制。"
    else: trend_msg = f"✅ **[趋势]** 多头保护。"

    if is_breakout or is_golden_spider: cost_msg = f"🔨 **[筹码]** 困龙升天，空间打开。"
    elif close > vwap: cost_msg = f"💰 **[筹码]** 获利盘主导。"
    else: cost_msg = f"⛰️ **[筹码]** 抛压沉重。"

    if has_pressure: rr_msg = "⚠️ **[赔率]** 形态走坏，不博弈。"
    elif rr_ratio == -1: rr_msg = "❌ **[赔率]** 已破位。"
    elif rr_ratio == float('inf'): rr_msg = "👑 **[赔率]** 空间无限。"
    elif rr_ratio >= 3.0: rr_msg = f"🎯 **[赔率]** {rr_ratio:.1f}:1 (极佳)。"
    elif rr_ratio >= 1.5: rr_msg = f"👌 **[赔率]** {rr_ratio:.1f}:1 (及格)。"
    else: rr_msg = f"🚫 **[赔率]** {rr_ratio:.1f}:1 (不及格)。"

    return f"{vol_msg}<br>{trend_msg}<br>{cost_msg}<br>{rr_msg}"

def auto_fix_code(code):
    code = code.strip()
    if "." in code: return code.upper()
    if code.startswith("6"): return code + ".SH"
    elif code.startswith("8") or code.startswith("4"): return code + ".BJ"
    else: return code + ".SZ"

# ==========================================
# 数据引擎
# ==========================================
@st.cache_data(ttl=3600) 
def get_real_data(token, stock_code, view_days):
    try:
        ts.set_token(token)
        pro = ts.pro_api()
        today = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=600)).strftime('%Y%m%d')
        df = pro.daily(ts_code=stock_code, start_date=start_date, end_date=today)
        if df.empty: return None, None, None, None, None, None, None, None, None, None, f"无数据"
        
        df = df.sort_values('trade_date').reset_index(drop=True)
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df = df.rename(columns={'trade_date':'Date','open':'Open','high':'High','low':'Low','close':'Close','vol':'Volume','amount':'Amount'})
        
        for ma in [5,10,20,60]: df[f'MA{ma}'] = df['Close'].rolling(ma).mean()
        df['BIAS'] = (df['Close'] - df['MA20']) / df['MA20'] * 100
        df['Prev_Close'] = df['Close'].shift(1)
        df['Pct_Change'] = (df['Close'] - df['Prev_Close']) / df['Prev_Close'] * 100
        df['Vol_MA5_Ref'] = df['Volume'].rolling(5).mean().shift(1)
        df['Vol_Ratio'] = (df['Volume'] / df['Vol_MA5_Ref']).fillna(1.0)

        df_view = df.tail(view_days).copy().reset_index(drop=True)
        df_view['Date_Str'] = df_view['Date'].dt.strftime('%Y-%m-%d')
        
        # 悬浮窗 (大字)
        df_view['hover_text'] = df_view.apply(lambda x: (
            f"<b>{x['Date_Str']}</b><br>"
            f"开: {x['Open']:.2f}  高: {x['High']:.2f}<br>"
            f"低: {x['Low']:.2f}  收: {x['Close']:.2f}<br>"
            f"量比: <b>{x['Vol_Ratio']:.2f}</b><br>"
            f"<b>乖离: {x['BIAS']:.2f}%</b>"
        ), axis=1)
        
        df_view['VWAP'] = (df_view['Amount'].cumsum() * 10) / df_view['Volume'].cumsum()
        low_60d = df.tail(60)['Low'].min()
        orig_idx = df[df['Date'] == df_view.iloc[-1]['Date']].index[0]
        prev_row = df.iloc[orig_idx - 1]
        
        last_ma = df.iloc[-1]
        ma_list = [last_ma['MA5'], last_ma['MA10'], last_ma['MA20'], last_ma['MA60']]
        ma_std = np.std(ma_list)
        ma_mean = np.mean(ma_list)
        is_golden_spider = (ma_std / ma_mean < 0.015) and (df.iloc[-1]['Close'] > max(ma_list))
        
        if is_golden_spider: smart_stop = ma_mean
        elif df.iloc[-1]['Close'] > df.iloc[-1]['MA60']: smart_stop = df.iloc[-1]['MA60']
        else: smart_stop = low_60d
        
        last_row = df.iloc[-1]
        upper_shadow = last_row['High'] - max(last_row['Close'], last_row['Open'])
        has_pressure = (upper_shadow > 1.5 * abs(last_row['Close'] - last_row['Open'])) and (upper_shadow / last_row['Close'] > 0.015)
        is_divergence = (last_row['Close'] > last_row['MA20']) and (last_row['Vol_Ratio'] < 0.7)

        return df_view, df_view.loc[df_view['Low'].idxmin()], df_view.loc[df_view['High'].idxmax()], df_view['Low'].min(), df_view['High'].max(), smart_stop, prev_row, is_golden_spider, has_pressure, is_divergence, None
    except Exception as e:
        return None, None, None, None, None, None, None, None, None, None, f"异常: {str(e)}"

# ==========================================
# 界面逻辑
# ==========================================
with st.sidebar:
    st.header("🗃️ 指挥中心")
    default_token = "" 
    ts_token = st.text_input("Tushare Token", value=default_token, type="password")
    
    st.markdown("---")
    st.subheader("👀 视野")
    period_options = {"短线(60)":60, "中线(90)":90, "长线(150)":150, "年线(250)":250}
    view_days = period_options[st.selectbox("周期", list(period_options.keys()), index=1)]

    st.markdown("---")
    st.subheader("📈 标的")
    with st.form("add", clear_on_submit=True):
        c1, c2 = st.columns([2,1])
        icode = c1.text_input("代码", placeholder="002230")
        iname = c2.text_input("名称", placeholder="讯飞")
        if st.form_submit_button("加自选", type="primary"):
            if icode and iname:
                fcode = auto_fix_code(icode)
                if fcode not in st.session_state.stock_list['code'].values:
                    st.session_state.stock_list = pd.concat([st.session_state.stock_list, pd.DataFrame([{"code":fcode,"name":iname}])], ignore_index=True)
                    st.rerun()
    
    current_sel = st.selectbox("我的持仓", [f"{r['code']} - {r['name']}" for i,r in st.session_state.stock_list.iterrows()])
    if current_sel: code, name = current_sel.split(" - ")

# --- 主逻辑 ---
if not ts_token:
    st.warning("请填入 Tushare Token")
elif current_sel:
    with st.spinner(f"正在全维扫描 {name}..."):
        df, min_p, max_p, view_min, view_max, smart_stop, prev_row, is_golden_spider, has_pressure, is_divergence, err = get_real_data(ts_token, code, view_days)
    
    if err:
        st.error(err)
    else:
        last = df.iloc[-1]
        chg = last['Close'] - prev_row['Close']
        pct = last['Pct_Change']
        
        UP, DOWN, FLAT = '#EB4D3D', '#3BB372', '#333333'
        color, sign = (UP, "+") if chg > 0 else ((DOWN, "") if chg < 0 else (FLAT, ""))
        
        is_breakout = (last['Pct_Change'] > 5.0) and (last['Vol_Ratio'] > 1.8) and (last['Close'] > last['MA60'])
        is_limit_up = last['Pct_Change'] > 9.0 
        
        raw_risk = last['Close'] - smart_stop
        calc_risk = max(raw_risk, last['Close'] * 0.015) 
        
        if is_golden_spider or is_breakout or is_limit_up: target_price = view_max
        elif last['Close'] < last['MA60']: target_price = last['MA60']
        elif last['Close'] < last['VWAP']: target_price = last['VWAP']
        else: target_price = view_max
            
        reward = target_price - last['Close']
        
        rr_ratio = 0
        rr_display = ""
        if last['Close'] < smart_stop:
            rr_display = "状态: 止损离场"; rr_color = "#888888"; rr_ratio = -1
        elif is_limit_up and last['Vol_Ratio'] < 1.0:
            rr_ratio = float('inf'); rr_display = "盈亏比: ∞ (锁仓)"; rr_color = UP
        elif is_breakout:
            rr_ratio = float('inf'); rr_display = "盈亏比: ∞ (突围)"; rr_color = UP
        elif reward <= 0 and last['Close'] > last['VWAP']:
            rr_ratio = float('inf'); rr_display = "状态: 创新高"; rr_color = "#ef6c00"
        else:
            rr_ratio = reward / calc_risk if calc_risk > 0 else 0
            rr_display = f"盈亏比: {rr_ratio:.2f} : 1"
            rr_color = "#2e7d32" if rr_ratio >= 2.5 else ("#f9a825" if rr_ratio >= 1.5 else "#c62828")

        tb_score, tb_grade, tb_color, tb_details, tb_conclusion, negatives = calculate_tb_alpha_score(last, prev_row, view_max, rr_ratio, is_golden_spider, has_pressure, is_divergence)
        analysis_html = analyze_market_behavior(last, view_max, rr_ratio, smart_stop, is_breakout, is_golden_spider, has_pressure, is_divergence)
        
        # 🟢 核心功能：一键保存记录 (单股查看时也保存)
        save_to_history(code, name, tb_score, tb_grade, tb_conclusion, last['Vol_Ratio'], rr_display)

        st.markdown(f"""
            <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:15px; border-bottom:1px solid #eee; padding-bottom:10px;">
                <div>
                    <span class="stock-header">{name}</span>
                    <span class="stock-price" style="color: {color};">{last['Close']:.2f}</span>
                    <span class="stock-pct" style="color: {color};">({sign}{pct:.2f}%)</span>
                    <span class="stock-meta">{last['Date_Str']}</span>
                </div>
                <div>
                    <span style="font-size:18px; font-weight:bold; color:{rr_color};">{rr_display}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # 顶部图例
        MA_C = {'MA5':'#FF69B4', 'MA10':'#FFD700', 'MA20':'#87CEFA', 'MA60':'#999999'}
        legend_items = []
        for ma, c in MA_C.items(): legend_items.append(f"<span style='color:{c}; font-weight:bold; font-size:18px; margin-right:20px;'>{ma}: {last[ma]:.2f}</span>")
        legend_items.append(f"<span style='color:#D32F2F; font-weight:bold; font-size:18px; margin-right:20px;'>成本: {last['VWAP']:.2f}</span>")
        legend_items.append(f"<span style='color:#888888; font-weight:bold; font-size:18px; border-bottom:1px dashed #888888;'>止损: {smart_stop:.2f}</span>")
        st.markdown(f"<div style='margin-bottom:10px; text-align:right;'>{''.join(legend_items)}</div>", unsafe_allow_html=True)

        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"""<div class="analysis-box"><div class="analysis-title">🔍 机器战术建议</div><div class="analysis-content">{analysis_html}</div></div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="score-card"><div class="score-val" style="color:{tb_color}">{tb_score}</div><div class="score-grade" style="background-color:{tb_color}">{tb_grade}</div><div class="score-conclusion">{tb_conclusion}</div>{''.join([f'<div class="score-neg">{neg}</div>' for neg in negatives])}</div>""", unsafe_allow_html=True)

        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.85, 0.15])
        fig.add_trace(go.Candlestick(x=df['Date_Str'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], increasing_line_color=UP, increasing_fillcolor=UP, decreasing_line_color=DOWN, decreasing_fillcolor=DOWN, name='K线', showlegend=False, text=df['hover_text'], hoverinfo='text'), row=1, col=1)
        for ma, c in MA_C.items():
            width = 2.5 if ma == 'MA20' else (2.0 if ma == 'MA60' else 1.0)
            fig.add_trace(go.Scatter(x=df['Date_Str'], y=df[ma], name=ma, line=dict(color=c, width=width, dash='dash' if ma=='MA60' else None), showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['Date_Str'], y=df['VWAP'], name='平均成本', line=dict(color='#D32F2F', width=1.5, dash='dot'), showlegend=False), row=1, col=1)
        
        if rr_ratio > 0 and rr_ratio != float('inf'):
            fig.add_trace(go.Scatter(x=[df['Date_Str'].iloc[0], df['Date_Str'].iloc[-1]], y=[target_price, target_price], name='Target', line=dict(color='#2e7d32', width=1, dash='dashdot'), showlegend=False), row=1, col=1)
            fig.add_annotation(x=df['Date_Str'].iloc[-1], y=target_price, text=f"压力:{target_price:.2f}", showarrow=False, xanchor="left", font=dict(color="#2e7d32"), row=1, col=1)

        fig.add_trace(go.Scatter(x=[df['Date_Str'].iloc[0], df['Date_Str'].iloc[-1]], y=[smart_stop, smart_stop], name='Stop', line=dict(color='#888888', width=1, dash='dash'), showlegend=False), row=1, col=1)
        fig.add_annotation(x=df['Date_Str'].iloc[-1], y=smart_stop, text=f"止损:{smart_stop:.2f}", showarrow=False, xanchor="left", font=dict(color="#888888"), row=1, col=1)

        vol_colors = [UP if o < c else DOWN for o, c in zip(df['Open'], df['Close'])]
        fig.add_trace(go.Bar(x=df['Date_Str'], y=df['Volume'], marker_color=vol_colors, hovertemplate='成交量: %{y:.2f}', showlegend=False), row=2, col=1)

        y_min = min(view_min, smart_stop) * 0.95; y_max = max(view_max, target_price) * 1.05
        fig.update_layout(template='plotly_white', height=800, margin=dict(l=10, r=10, t=80, b=10), xaxis_rangeslider_visible=False, hovermode='x unified', xaxis=dict(type='date', rangebreaks=[dict(bounds=["sat", "mon"])]), yaxis=dict(range=[y_min, y_max], fixedrange=False), hoverlabel=dict(font=dict(size=16)))
        axis_cfg = dict(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)', griddash='dash', showline=False)
        fig.update_xaxes(**axis_cfg, row=1, col=1, showticklabels=False); fig.update_xaxes(**axis_cfg, row=2, col=1, showticklabels=True, tickformat='%m-%d')
        fig.update_yaxes(**axis_cfg, row=1, col=1); fig.update_yaxes(**axis_cfg, row=2, col=1, showticklabels=False)
        
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        # 🟢 一键全仓体检
        if st.button("🚀 一键全仓深度体检", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            total_stocks = len(st.session_state.stock_list)
            
            for i, row in st.session_state.stock_list.iterrows():
                batch_code = row['code']
                batch_name = row['name']
                status_text.text(f"正在扫描: {batch_name} ({batch_code}) ...")
                
                try:
                    b_df, _, _, b_view_max, _, b_stop, b_prev, b_gold, b_press, b_div, _ = get_real_data(ts_token, batch_code, view_days)
                    if b_df is not None:
                        b_last = b_df.iloc[-1]
                        b_is_break = (b_last['Pct_Change'] > 5.0) and (b_last['Vol_Ratio'] > 1.8) and (b_last['Close'] > b_last['MA60'])
                        b_is_limit = b_last['Pct_Change'] > 9.0
                        
                        b_risk = max(b_last['Close'] - b_stop, b_last['Close']*0.015)
                        
                        if b_gold or b_is_break or b_is_limit: b_target = b_view_max
                        elif b_last['Close'] < b_last['MA60']: b_target = b_last['MA60']
                        elif b_last['Close'] < b_last['VWAP']: b_target = b_last['VWAP']
                        else: b_target = b_view_max
                        
                        b_reward = b_target - b_last['Close']
                        
                        b_rr_ratio = 0
                        b_rr_disp = ""
                        if b_last['Close'] < b_stop: b_rr_disp = "状态: 止损"; b_rr_ratio = -1
                        elif b_is_limit and b_last['Vol_Ratio'] < 1.0: b_rr_ratio = float('inf'); b_rr_disp = "∞ (锁仓)"
                        elif b_is_break: b_rr_ratio = float('inf'); b_rr_disp = "∞ (突围)"
                        elif b_reward <= 0 and b_last['Close'] > b_last['VWAP']: b_rr_ratio = float('inf'); b_rr_disp = "新高"
                        else:
                             b_rr_ratio = b_reward / b_risk if b_risk > 0 else 0
                             b_rr_disp = f"{b_rr_ratio:.2f} : 1"
                        
                        b_score, b_grade, _, _, b_concl, _ = calculate_tb_alpha_score(b_last, b_prev, b_view_max, b_rr_ratio, b_gold, b_press, b_div)
                        
                        save_to_history(batch_code, batch_name, b_score, b_grade, b_concl, b_last['Vol_Ratio'], b_rr_disp)
                except:
                    pass
                
                progress_bar.progress((i + 1) / total_stocks)
            
            status_text.text("✅ 全仓体检完成！")
            time.sleep(1)
            st.rerun()

        # 🟢 战术复盘档案库
        st.markdown("### 🏆 战术复盘档案库 (按得分排序)")
        if os.path.exists(HISTORY_FILE):
            df_hist = pd.read_csv(HISTORY_FILE)
            def color_grade(val):
                if 'S 级' in str(val): return 'color: #d32f2f; font-weight: bold'
                elif 'A 级' in str(val): return 'color: #ef6c00; font-weight: bold'
                elif 'B 级' in str(val): return 'color: #f9a825'
                return 'color: #666'

            st.dataframe(
                df_hist.style.map(color_grade, subset=['评级']),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "得分": st.column_config.NumberColumn(format="%d 分"),
                    "量比": st.column_config.NumberColumn(format="%.2f 倍"),
                }
            )
        else:
            st.info("暂无记录，请点击上方按钮进行体检。")

        with st.expander("📝 查看 TB-Alpha 评分明细", expanded=False):
            st.markdown("#### 评分细则")
            for item in tb_details: st.text(item)
else:
    st.info("准备就绪")