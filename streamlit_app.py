import streamlit as st
import pandas as pd
from rfm_analysis_utils import load_data, calculate_rfm, visualize_rfm_heatmap, compare_high_low_rfm

# データ読み込み
st.title("RFM分析結果の可視化")
data_dir = "/content/drive/MyDrive/マナビDX/PBL01/演習03（機械学習）/DXQuest_PBL01/Data/"
sales_data, item_data, category_data, test_data = load_data(data_dir)

# 発注データ（結果ファイル）を結合
results = pd.read_csv(data_dir + "ID100947_PBL01_ver30.csv", header=None)
test_data["発注量"] = results[1]

# 商品カテゴリIDが test_data に無ければ item_data を使って追加
if "商品カテゴリID" not in test_data.columns:
    test_data = test_data.merge(item_data[["商品ID", "商品カテゴリID"]], on="商品ID", how="left")

# 商品カテゴリIDが rfm_data に無ければ item_data を使って追加
if "商品カテゴリID" not in sales_data.columns:
    sales_data = sales_data.merge(item_data[["商品ID", "商品カテゴリID"]], on="商品ID", how="left")

# RFMスコアの計算
st.title("RFMスコア計算")
rfm_data = calculate_rfm(sales_data)

# デバッグ: RFMデータを確認
st.title("RFMスコアデータ:")
st.write(rfm_data.head())

# RFMスコアと発注データの結合
st.title("RFMスコアと発注データの結合")
rfm_analysis = test_data.merge(rfm_data, on=['店舗ID', '商品ID'], how='left')

# デバッグ: 結合後のデータを確認
st.title("結合後のデータ:")
st.write(rfm_analysis.head())

st.write(rfm_analysis.head())
# item_dataを使用して商品カテゴリIDを結合
rfm_analysis = rfm_analysis.merge(
    item_data[['商品ID', '商品カテゴリID']],
    on='商品ID',
    how='left')

rfm_analysis['商品カテゴリID'] = rfm_analysis['商品カテゴリID_x']
rfm_analysis = rfm_analysis.drop(columns=['商品カテゴリID_x', '商品カテゴリID_y'])
# category_dataを使用して商品カテゴリ名を結合
rfm_analysis = rfm_analysis.merge(
    category_data,
    on='商品カテゴリID',
    how='left'
)

# RFMスコア別カテゴリのヒートマップを表示
st.write("RFMスコア別カテゴリのヒートマップ")
fig_heatmap = visualize_rfm_heatmap(rfm_analysis, save_path=None)  # Matplotlibの図を作成
st.pyplot(fig_heatmap)  # Streamlitで図を描画

# 高スコア vs 低スコアの比較を表示
st.write("高RFMスコア商品 vs. 低RFMスコア商品の平均発注量")
rfm_analysis = rfm_analysis.dropna(subset=["RFMスコア"])
fig_comparison = compare_high_low_rfm(rfm_analysis)  # Matplotlibの図を作成
st.pyplot(fig_comparison)  # Streamlitで図を描画
