import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
# data1 = pd.read_csv(r"Enterprise_Sales_Dirty.csv")
# data1.to_excel(r"Enterprise_Sales_Dirty.xlsx",index=False)
data = pd.read_excel(r"Dataset\Sales Dataset.xlsx")

# # ==========================================================================
# #                         2. Data Cleaning
# # ==========================================================================
# # print(data.head(10))
# # ======================================
# # 2.1. Remove duplicates
# # ======================================
data.drop_duplicates(inplace=True)
# # print(f"Rows after removing exact duplicates: {len(data)}")

# # Order_ID check
# # print(f"Duplicate Order IDs: {data.duplicated(subset=['Order_ID']).sum()}")

data.drop_duplicates(subset=['Order_ID'], keep='first', inplace=True)
# # print(f"Final rows: {len(data)}")
# # ======================================
# # 2.2. Handle missing values
# # ======================================
# # print(data.info())

# # Generate missing unique IDs   
# # print(data['Order_ID'].unique())
mask = data['Order_ID'].isnull()
data.loc[mask, 'Order_ID'] = ['ORD-' + str(i).zfill(4) 
                               for i in range(1001, 1001 + mask.sum())]
# # ===========================================================================
# #                       Date column
# # ===========================================================================


def parse_date(val):
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m-%d-%Y",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%d %b %Y",
        "%d %B %Y"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(str(val).strip(), fmt)
        except:
            continue
    return None

# Step 1 — Parse karo
data['Date'] = data['Date'].apply(parse_date)

# Step 2 — ZAROOR datetime convert karo ← yahi missing tha
data['Date'] = pd.to_datetime(data['Date'], errors='coerce')

# Step 3 — Verify dtype
# print(f"Dtype: {data['Date'].dtype}")       # datetime64[ns]
# print(f"NaT count: {data['Date'].isna().sum()}")  # 0

# Step 4 — Quarter fix
data['Quarter'] = "Q" + data['Date'].dt.quarter.astype('Int64').astype(str)
data.loc[data['Date'].isna(), 'Quarter'] = 'Unknown'

# # # Step 5 — Verify
# # print(data['Quarter'].value_counts())
# # print(data[['Date', 'Month', 'Quarter']].head(30))

# # print(data["Date"].dtype)
# # print(data["Date"].head(30).tolist())
# # ===========================================================================


data["City"] = data.groupby("Region")["City"].transform(lambda x: x.fillna(x.mode()[0]))
# # customer segment formate
# # # Overall mode se bharo
data['Customer_Segment'] = data['Customer_Segment'].fillna(data['Customer_Segment'].mode()[0])
data['Customer_Segment'] = data['Customer_Segment'].replace({
    'government': 'Government',
    'GOVERNMENT': 'Government',
    'Goverment': 'Government',
    'Govt': 'Government',

    'enterprise': 'Enterprise',
    'ENTERPRISE': 'Enterprise',
    'Enterprize': 'Enterprise',
    'Enterp.': 'Enterprise',

    'retail': 'Retail',
    'RETAIL': 'Retail',
    'Retial': 'Retail',
    'Retl': 'Retail',

    'SMb': 'SMB',
    'smb': 'SMB',
    'Smb': 'SMB',
    'S.M.B': 'SMB'
})
data['Region'] = data['Region'].replace({
    'Est': 'East',
    'EAST': 'East',
    'east': 'East',
    'East ': 'East',

    'Wst': 'West',
    'WEST': 'West',
    'west': 'West',
    ' West': 'West',

    'NORTH': 'North',
    'Nrth': 'North',
    'north': 'North',
    'North ': 'North',

    'south': 'South',
    'Soth': 'South',
    'SOUTH': 'South',
    'South ': 'South',
    
    'Centre': 'Central',
    'CENTRAL': 'Central',
    'central': 'Central',
})
# print("REGION values:")
# print(data['Region'].value_counts())
# print(data['Region'].unique())

# print(data.Customer_Segment.unique())

data["Sales_Channel"] = data["Sales_Channel"].fillna(
    data["Sales_Channel"].mode()[0]
)
data['Sales_Channel'] = data['Sales_Channel'].replace({
    'DISTRIBUTOR': 'Distributor',
    'distributor': 'Distributor',
    'Distributer': 'Distributor',
    'Dist.': 'Distributor',

    'online': 'Online',
    'Onlne': 'Online',
    'On-line': 'Online',
    'ONLINE': 'Online',

    'retail store': 'Retail Store',
    'RETAIL': 'Retail Store',
    'Retal Store': 'Retail Store',
    'RetailStore': 'Retail Store',
    'Retail store': 'Retail Store',

    'Direct sales': 'Direct Sales',
    'Direct Sles': 'Direct Sales',
    'DirectSales': 'Direct Sales',
    'direct sales': 'Direct Sales'
})
# print(data.Sales_Channel.unique())

data.loc[data['Discount_Pct'] > 100 ,"Discount_Pct"] = np.nan
data['Discount_Pct'] = data['Discount_Pct'].fillna(0)
# print(data.Discount_Pct.max())
# print(data[data.Discount_Pct > 100])

data['Pipeline_Stage'] = data['Pipeline_Stage'].fillna('Unknown')
# Median better hai — outliers se safe
data['Days_to_Close'] = data['Days_to_Close'].fillna(
    data['Days_to_Close'].median()
)


# # print(data.isnull().sum())
# # print(data.isnull().sum() / len(data) * 100)
# # ===========================================================================
# #                           Revenue Column fix
# # ===========================================================================
# # Step 1 — Currency symbols hataو aur numeric banao
data['Revenue_PKR'] = data['Revenue_PKR'].astype(str)
data['Revenue_PKR'] = data['Revenue_PKR'].str.replace('PKR', '', regex=False)
data['Revenue_PKR'] = data['Revenue_PKR'].str.replace('$', '', regex=False)
data['Revenue_PKR'] = data['Revenue_PKR'].str.strip()
data['Revenue_PKR'] = pd.to_numeric(data['Revenue_PKR'], errors='coerce')

# Step 2 — Negative values fix karo
data['Revenue_PKR'] = data['Revenue_PKR'].abs()

# Step 3 — Outliers check karo
Q1 = data['Revenue_PKR'].quantile(0.25)
Q3 = data['Revenue_PKR'].quantile(0.75)
IQR = Q3 - Q1
upper_limit = Q3 + 1.5 * IQR
# print(upper_limit)
data['Revenue_PKR'] = data['Revenue_PKR'].clip(upper=upper_limit)

# Unique values dekho har column mein

# # print("\nSALES_CHANNEL values:")
# # print(data['Sales_Channel'].value_counts())

# # print("\nCUSTOMER_SEGMENT values:")
# # print(data['Customer_Segment'].value_counts())

# # print("\nPIPELINE_STAGE values:")
# # print(data['Pipeline_Stage'].value_counts())

# # =======================================================================
# #                       Quantity column
# # =======================================================================
# # print("Quantity")
data['Quantity'] = data["Quantity"].abs()
# # print(data["Quantity"].describe())
# # print(f"Negative Value :  {(data["Quantity"] < 0).sum()}")
# # print(f"Zero Value :  {(data["Quantity"] == 0).sum()}")
# # print(data[data["Quantity"]>0])
# # =======================================================================
# #                       Discount_Pct column
# # =======================================================================
# # print("Discunt_Pct")
# # print(data["Discount_Pct"].describe())
# # print(f"Negative Value : {(data["Discount_Pct"]<0).sum()}")
# # print(f"Greater than 100 Value : {(data["Discount_Pct"]>100).sum()}")
# # =======================================================================
# #                       Gross Margin Pct column
# # =======================================================================
# # print(data["Gross_Margin_Pct"])
data["Gross_Margin_Pct"] =data["Gross_Margin_Pct"].clip(lower=0,upper=100)
# # print(data["Gross_Margin_Pct"].describe())
# # print(f"Greater than 100 : {(data["Gross_Margin_Pct"]>100).sum()}")
# # print(f"Less than 0 : {(data["Gross_Margin_Pct"]<0).sum()}")
# # =======================================================================
# #                       Unit price column
# # =======================================================================
# # print("Unit_Price_PKR")
data['Unit_Price_PKR'] = data.groupby('Product_Name')['Unit_Price_PKR'].transform(lambda x: x.replace(0, x[x > 0].median()))
# )
# # print(f"Zero prices remaining: {(data['Unit_Price_PKR'] == 0).sum()}")  # 0 hona chahiye

# # =======================================================================
# #                              Verify
# =======================================================================
print(f"Discount :         -Min : {data["Discount_Pct"].min()}     -Max : {data["Discount_Pct"].max()}")
print(f"Quantity :         -Min : {data["Quantity"].min()}         -Max : {data["Quantity"].max()}")
print(f"Gross_Margin_Pct : -Min : {data["Gross_Margin_Pct"].min()} -Max : {data["Gross_Margin_Pct"].max()}")
print(f"Unit_Price_PKR :   -Min : {data["Unit_Price_PKR"].min()}   -Max : {data["Unit_Price_PKR"].max()}")

# # print(data.info())
# # print(data.isnull().sum())
# # print(data.duplicated().sum())
# # print(len(data))
# # print(len(data.columns))

print("=" * 45)
print("      DATA CLEANING SUMMARY REPORT")
print("=" * 45)

print(f"Original Rows        : 1030")
print(f"Final Rows           : {len(data)}")
print(f"Rows Removed         : {1030 - len(data)}")
print("-" * 45)
print(f"Duplicates Removed   : ~30")
print(f"NaN Values Fixed     : Order_ID, City,")
print(f"                       Segment, Channel,")
print(f"                       Discount, Pipeline,")
print(f"                       Days_to_Close")
print(f"Text Fixed           : Region, Channel,")
print(f"                       Segment, Names")
print(f"Date Formats Fixed   : 7 formats → 1")
print(f"Negative Values Fixed: Quantity, Revenue")
print(f"Invalid Values Fixed : Discount > 100%")
print(f"                       Margin > 100%")
print(f"Zero Prices Fixed    : Product median")
print(f"Currency Symbols     : PKR $  removed")
print("=" * 45)
print("  Dataset is ready for Power BI! ✅")
print("=" * 45)

# # data.to_excel(r"Dataset\Sales Dataset.xlsx",index=False)

# =========================================================================
#                        Exploratory Data Analysis (EDA)
# =========================================================================
def Basic_Overview():
    # Shape
    print(f"Total Rows : {data.shape[0]}")
    print(f"Total Column : {data.shape[1]}")
    print(f"Total Column : {data.shape}")
    # Data type
    print(data.dtypes)
# Basic_Overview()
# =========================================================================
def Statistic():
    print(data.describe())
# Statistic()
# =========================================================================
def category():
    column = ["Region","City","Product_Category","Product_Name","Sales_Channel","Pipeline_Stage"]
    for col in column:
        print(f"{col} : {data[col].value_counts()}")
        print(f"Unique Column : {data[col].unique()}")
# category()
# =========================================================================
def visual():
    fig, axes = plt.subplots(2 ,3 ,figsize=(16,8))
    fig.suptitle("EDA- Data Overview" , fontsize = 20)
    
    # Revenue Distribution
    axes[0,0].hist(data["Revenue_PKR"], bins=10, color="green" , edgecolor="black",density=True)
    axes[0,0].set_title("Revenue Distribution")
    axes[0,0].set_xlabel("Revenue_PKR")
    
    # order by Region
    region = data["Region"].value_counts()
    axes[0,1].bar(region.index,region.values , color = "coral")
    axes[0,1].set_title("Order by Region")
    
    # order by Pduduct category
    Product = data["Product_Category"].value_counts()
    axes[0,2].barh(Product.index,Product.values , color = "Blue")
    axes[0,2].set_title("Order by Product_Category")

    # order by Sales channel
    Sales = data["Sales_Channel"].value_counts()
    axes[1,0].pie(Sales.values, labels = Sales.index ,autopct='%1.1f%%')
    axes[1,0].set_title("Order by Sales_Channel")
    
    # 5. Customer Segment
    seg_counts = data['Customer_Segment'].value_counts()
    axes[1,1].bar(seg_counts.index, seg_counts.values, color='mediumpurple')
    axes[1,1].set_title('Customer Segments')
    
    # order by Pipeline stage
    pipe = data["Pipeline_Stage"].value_counts()
    axes[1,2].bar(pipe.index,pipe.values , color = "coral")
    axes[1,2].set_title("Order by Pipeline Stage")
    axes[1,2].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.legend()
    plt.show() 
visual()
# print(data["Customer_ID"].nunique())