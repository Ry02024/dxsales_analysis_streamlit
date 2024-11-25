import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib

def load_data(data_dir):
    sales_data = pd.read_csv(data_dir + "sales_history.csv")
    item_data = pd.read_csv(data_dir + "item_categories.csv")
    category_data = pd.read_csv(data_dir + "category_names.csv")
    test_data = pd.read_csv(data_dir + "test.csv")

    return sales_data, item_data, category_data, test_data

# 可視化のための処理
def process_data(sales_history_df, item_categories_df, category_names_df):
    print("可視化のための処理を開始します...")
    join_data_df = pd.merge(sales_history_df, item_categories_df, on='商品ID', how='left')
    join_data_df = pd.merge(join_data_df, category_names_df, on='商品カテゴリID', how='left')
    join_data_df = join_data_df.drop_duplicates()

    print("データの前処理が完了しました。")
    return join_data_df
    
def calculate_rfm(sales_data):
    sales_data["購入日"] = pd.to_datetime(sales_data["日付"])
    reference_date = sales_data["購入日"].max()
    
    rfm = sales_data.groupby(["店舗ID", "商品ID"]).agg({
        "購入日": lambda x: (reference_date - x.max()).days,
        "売上個数": "count",
        "商品価格": "sum"
    }).reset_index()

    rfm.rename(columns={"購入日": "Recency", "売上個数": "Frequency", "商品価格": "Monetary"}, inplace=True)

    rfm["Rスコア"] = pd.qcut(rfm["Recency"], 4, labels=[4, 3, 2, 1])
    rfm["Fスコア"] = pd.qcut(rfm["Frequency"], 4, labels=[1, 2, 3, 4])
    rfm["Mスコア"] = pd.qcut(rfm["Monetary"], 4, labels=[1, 2, 3, 4])
    rfm["RFMスコア"] = rfm["Rスコア"].astype(str) + rfm["Fスコア"].astype(str) + rfm["Mスコア"].astype(str)
    
    return rfm

def visualize_rfm_heatmap(rfm_analysis_data, save_path=None):
    rfm_pivot = rfm_analysis_data.pivot_table(
        index="商品カテゴリ名", columns="RFMスコア", values="発注量", fill_value=0
    )

    plt.figure(figsize=(20, 8))
    sns.heatmap(rfm_pivot, cmap="YlGnBu", annot=True, fmt=".0f")
    plt.title("RFMスコア別商品カテゴリの発注量分布")
    plt.xlabel("RFMスコア")
    plt.ylabel("商品カテゴリ名")
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()

def compare_high_low_rfm(rfm_analysis):
    high_rfm = rfm_analysis[rfm_analysis["RFMスコア"].str.startswith("4")]
    low_rfm = rfm_analysis[rfm_analysis["RFMスコア"].str.startswith("1")]

    high_avg = high_rfm["発注量"].mean()
    low_avg = low_rfm["発注量"].mean()

    fig, ax = plt.subplots()
    ax.bar(["高RFMスコア商品", "低RFMスコア商品"], [high_avg, low_avg], color=["blue", "red"])
    ax.set_ylabel("平均発注量")
    ax.set_title("高RFMスコア商品 vs. 低RFMスコア商品の平均発注量")
    plt.tight_layout()
    return fig
