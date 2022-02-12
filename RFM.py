import numpy as np
import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.5f' % x)

df_=pd.read_excel(r"E:\CAGLAR\datasets\online_retail_II.xlsx")
df=df_.copy()

## DATA PREPROCESSING

df.head()
df.shape
df.describe().T

#Remove missing values
df.isnull().sum()
df.dropna(inplace=True)
df.isnull().sum()

# How many unique products are in the dataset?
df["Description"].nunique()

# How many of each product are there?
df["Description"].value_counts().head()

# 5 Most ordered products
df.groupby("Description").agg({"Quantity": "sum"}).head().sort_values("Quantity", ascending=False)

# The 'C' in the invoices shows the canceled transactions. Remove the canceled transactions from the dataset.
df = df[~df["Invoice"].str.contains("C", na=False )]

# Total Price
df = df[(df['Quantity'] > 0)]
df = df[(df['Price'] > 0)]
df["TotalPrice"]= df["Quantity"]* df["Price"]
df.head()
## CALCULATION of RFM METRICS

df["InvoiceDate"].max()


today_date = dt.datetime(2010, 12, 11)


rfm = df.groupby('Customer ID').agg({'InvoiceDate': lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     'Invoice': lambda Invoice: Invoice.nunique(),
                                     'TotalPrice': lambda TotalPrice: TotalPrice.sum()})

rfm.head()

rfm.columns = ['recency', 'frequency', 'monetary']

## CALCULATION OF RFM SCORES

rfm["recency_score"] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])


rfm["frequency_score"] = pd.qcut(rfm['frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

# 1 1,1,2,3,3,3,3,3,

rfm["monetary_score"] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))

rfm.head()

rfm.describe().T

rfm[rfm["RFM_SCORE"] == "55"].head()

rfm[rfm["RFM_SCORE"] == "11"].head()

## CREATING & ANALYSING RFM SEGMENTS
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)

rfm.head()

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(["mean", "count"])

rfm[rfm["segment"] == "need_attention"].head()

# Choose 3 segment

#cant_loose
#need_attention
#at_Risk

rfm[rfm["segment"] == "cant_loose"].head()
rfm[rfm["segment"] == "need_attention"].head()
rfm[rfm["segment"] == "at_Risk"].head()


new_df=pd.DataFrame()

# What percentage of customers belong to the need_attention segment.

new_df["need_attention_ıd"] = rfm[rfm["segment"]== "need_attention"].index

new_df.head()

rfm.reset_index(inplace=True)
new_df.nunique() * 100 / rfm["Customer ID"].nunique()  #---> %4.8



new_df.to_excel("need_attention_ıd.xlsx")
