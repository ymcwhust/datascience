import altair as alt
import pandas as pd
import numpy as np
import streamlit as st
from vega_datasets import data as vega_data
alt.data_transformers.disable_max_rows()



def draw_pie_chart(data, country_name):
    # 筛选指定国家的数据
    country_data = data[(data['country'] == country_name) & (data['year'] == 2021)]
    # 计算各个行业的GVA总和
    total_gva = country_data[['manufacturing_gva','agr_hunt_forest_fish_gva','construction_gva',
                              'mining_manufacturing_utilities_gva', 'transport_storage_comm_gva',
                              'wholesale_retail_trade_gva', 'other_activities_gva']].sum().sum()
    
    # 生成饼状图的数据
    pie_data = pd.DataFrame({
        'Industry': ['Manufacturing', 'Agriculture, Hunting, Forestry, Fishing', 'Construction', 
                     'Mining, Manufacturing, Utilities', 'Transport, Storage, Communication', 
                     'Wholesale, Retail Trade', 'Other Activities'],
        'GVA': [
            country_data['manufacturing_gva'].iloc[0],
            country_data['agr_hunt_forest_fish_gva'].iloc[0],
            country_data['construction_gva'].iloc[0],
            country_data['mining_manufacturing_utilities_gva'].iloc[0],
            country_data['transport_storage_comm_gva'].iloc[0],
            country_data['wholesale_retail_trade_gva'].iloc[0],
            country_data['other_activities_gva'].iloc[0]
        ]
    })
    
    # 计算每个行业GVA的百分比
    pie_data['Percentage'] = pie_data['GVA'] / total_gva
    
    # 绘制饼状图
    base = alt.Chart(pie_data).encode(
        theta=alt.Theta(field="Percentage", type="quantitative"),
        color=alt.Color(field="Industry", type="nominal", scale=alt.Scale(scheme='category20c')),
        tooltip=[alt.Tooltip('Industry'), alt.Tooltip('GVA:Q', format='~e')]
    ).properties(
        title=f'{country_name}'
    )

    pie_chart = base.mark_arc(outerRadius=100)
    text = base.mark_text(radius=110, size=10).encode(
        text=alt.Text('Percentage:Q', format='.1%'),
        theta=alt.Theta(field='Percentage', type='quantitative', stack=True)
    )

    return (pie_chart + text).properties(width=250,height=250,title=f"{country_name} 2021")

data = pd.read_csv('./Global Economy Indicators.csv')

# data.info()
data.columns = data.columns.str.strip()
rename_rules = {
    'CountryID': 'country_id',  # 国家的唯一标识符
    'Country': 'country',  # 国家名称
    'Year': 'year',  # 年份
    'AMA exchange rate': 'ama_exchange_rate',  # AMA汇率
    'IMF based exchange rate': 'imf_exchange_rate',  # 基于IMF的汇率
    'Population': 'population',  # 人口数量
    'Currency': 'currency',  # 使用的货币
    'Per capita GNI': 'per_capita_gni',  # 人均国民总收入
    'Agriculture, hunting, forestry, fishing (ISIC A-B)': 'agr_hunt_forest_fish_gva',  # 农业、狩猎、林业、渔业产值
    'Changes in inventories': 'changes_in_inventories',  # 存货变动
    'Construction (ISIC F)': 'construction_gva',  # 建筑业产值
    'Exports of goods and services': 'exports',  # 商品和服务出口总额
    'Final consumption expenditure': 'final_consumption_expenditure',  # 最终消费支出
    'General government final consumption expenditure': 'gov_final_consumption_expenditure',  # 政府最终消费支出
    'Gross capital formation': 'gross_capital_formation',  # 固定资本形成总额
    'Gross fixed capital formation (including Acquisitions less disposals of valuables)': 'gross_fixed_capital_formation',  # 固定资本形成净额
    'Household consumption expenditure (including Non-profit institutions serving households)': 'household_consumption_expenditure',  # 家庭消费支出
    'Imports of goods and services': 'imports',  # 商品和服务进口总额
    'Manufacturing (ISIC D)': 'manufacturing_gva',  # 制造业产值
    'Mining, Manufacturing, Utilities (ISIC C-E)': 'mining_manufacturing_utilities_gva',  # 采矿业、制造业和公共事业产值
    'Other Activities (ISIC J-P)': 'other_activities_gva',  # 其他活动产值
    'Total Value Added': 'total_value_added',  # 总增加值
    'Transport, storage and communication (ISIC I)': 'transport_storage_comm_gva',  # 运输、仓储和通信业产值
    'Wholesale, retail trade, restaurants and hotels (ISIC G-H)': 'wholesale_retail_trade_gva',  # 批发和零售贸易、餐饮和酒店业产值
    'Gross National Income(GNI) in USD': 'gni_usd',  # 以美元计的国民总收入
    'Gross Domestic Product (GDP)': 'gdp'  # 国内生产总值
}

df = data.rename(columns=rename_rules)
df = df.fillna(0)
df['country'] = df['country'].str.strip()

st.title('Global Economy Data Analysis')

st.subheader('Dataset')
st.write('The "Global Economy Indicators.csv" dataset consists of 10,512 records, encompassing detailed economic indicators of countries worldwide from 1970 to 2021. This dataset includes 26 fields, each representing a specific economic indicator, such as country ID, year, exchange rates, population, and the output value of various economic activities.')

description = df.describe()
st.dataframe(description)

world_geojson = vega_data.world_110m.url
countries = alt.topo_feature(world_geojson, 'countries')

st.subheader('Annual Global GDP Map')
st.write('You can select different years through a slider, and the map updates to display the global GDP distribution for that year.')
year = st.slider('Select Year for Global GDP Data', min_value=df['year'].min(), max_value=df['year'].max(), step=1)

df['country_id'] = df['country_id'].astype(str)
df['year'] = df['year'].astype(int)

# 使用滑动条的值来筛选数据
df_filtered = df[df['year'] == year]


# 创建地图
map_base = alt.Chart(countries).mark_geoshape(
    fill='lightgray',
    stroke='white'
).project(type='equalEarth')

map_colored = alt.Chart(countries).mark_geoshape().encode(
    color=alt.condition(
        alt.datum.gdp != 0, 
        alt.Color('gdp:Q', scale=alt.Scale(scheme="blueorange"), title="GDP"),
        alt.value('lightgray')
    ),
    tooltip=[alt.Tooltip('gdp:Q', format='~e')]
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(df_filtered, 'country_id', ['gdp', 'year'])
).project(type='equalEarth')

map_chart = alt.layer(map_base, map_colored).properties(
    width=800,
    height=400,
    title='Global GDP Map by Year'
)
# 在 Streamlit 中显示地图


df_years = df[df['year'].isin([1970,2000, 2021])]

# 对这些年份的GDP数据进行排序，以便图表显示时从高到低排列
df_top_countries = df_years.groupby('year').apply(lambda x: x.nlargest(12, 'gdp')).reset_index(drop=True)

# 创建条形图
rank_chart = alt.Chart(df_top_countries).mark_bar().encode(
    x=alt.X('gdp:Q', title='GDP in Scientific Notation'),
    y=alt.Y('country:N', sort='-x'),  # 根据GDP排序国家
    color='year:N',  # 颜色按年份区分
    tooltip=['country', 'year', 'gdp']  # 鼠标悬停时显示的信息
).properties(
    width=800,
    height=400,
    title='Worldwide Countries\' GDP in 1970, 2000 and 2021'
)


# 筛选出美国、中国、和日本的数据
countries_of_interest = ['United States', 'China', 'Japan']
df_selected_countries = df[df['country'].isin(countries_of_interest)]

# 宏观经济指标分析 - GDP趋势折线图
# 设置图表的宽度和高度

gdp_trend = alt.Chart(df_selected_countries).mark_line(point=True).encode(
    x='year:O',
    y=alt.Y('mean(gdp):Q', title='Average GDP'),
    color='country:N',
    tooltip=['year:O', 'country:N','mean(gdp):Q']
).properties(
    width=800,
    height=400,
    title='GDP Trend Over Years for Selected Countries'
)

manufacturing_gva_trend = alt.Chart(df_selected_countries).mark_line(point=True).encode(
    x='year:O',
    y=alt.Y('mean(manufacturing_gva):Q'),
    color='country:N',
    tooltip=['year:O', 'country:N','mean(manufacturing_gva):Q']
).properties(
    width=800,
    height=400,
    title='Manufacturing GVA Trend Over Years for Selected Countries'
)

population_consumption = alt.Chart(df_selected_countries).mark_point().encode(
    x=alt.X('population:Q'),
    y=alt.Y('household_consumption_expenditure:Q'),
    color='country:N',
).properties(
    width=800,
    height=400,
    title='Population vs. Household Consumption Expenditure for Selected Countries'
)

industry_contribution = alt.Chart(df_selected_countries).transform_fold(
    fold=['manufacturing_gva','agr_hunt_forest_fish_gva','construction_gva','mining_manufacturing_utilities_gva',
          'transport_storage_comm_gva','wholesale_retail_trade_gva', 'other_activities_gva'],
    as_=['Industry', 'GVA']
).mark_bar().encode(
    x='sum(GVA):Q',
    y='country:N',
    color=alt.Color('Industry:N', scale=alt.Scale(scheme='category20c')),
).properties(
    width=900,
    height=350,
    title='Contribution of Different Industries to GDP for Selected Countries'
)

df_selected_countries['trade_balance'] = df_selected_countries['exports'] - df_selected_countries['imports']
countries = df_selected_countries['country'].unique()

# 对每个国家创建图表
charts = []
for country in countries:
    country_data = df_selected_countries[df_selected_countries['country'] == country]
    
    # 出口趋势图
    export_chart = alt.Chart(country_data).mark_line().encode(
        x='year:T',
        y=alt.Y('exports:Q', title=f'Exports Value(green)'),
        color=alt.value('green')  # 绿色表示出口
    ).properties(
        width=300,
        height=300,
        title=f'{country} Yearly Exports Trend'
    )
    
    # 进口趋势图
    import_chart = alt.Chart(country_data).mark_line().encode(
        x='year:T',
        y=alt.Y('imports:Q', title=f'Imports Value(Red)'),
        color=alt.value('red')  # 红色表示进口
    ).properties(
        width=300,
        height=300,
        title=f'{country} Yearly Imports Trend'
    )
    
    # 贸易平衡图
    trade_balance_chart = alt.Chart(country_data).mark_bar().encode(
        x='year:T',
        y=alt.Y('trade_balance:Q', title=f'{country} Trade Balance'),
        color=alt.condition(
            alt.datum.trade_balance > 0,
            alt.value('green'),  # 正数表示顺差，绿色
            alt.value('red')  # 负数表示逆差，红色
        )
    ).properties(
        width=300,
        height=300,
        title=f'{country} Yearly Trade Balance'
    )
    
    # 将三个图表合并为一个
    combined_chart = alt.hconcat(export_chart+import_chart, trade_balance_chart).resolve_scale(x='shared').properties(
        title=f'{country} Trade Analysis'
    )
    
    charts.append(combined_chart)


gdp_gni_correlation = alt.Chart(df_selected_countries).mark_circle().encode(
    x='per_capita_gni:Q',
    y='gdp:Q',
    size='population:Q',
    color='country:N',
).properties(
    width=800,
    height=400,
    title='Correlation between GDP and Per Capita GNI for Selected Countries'
)



st.altair_chart(map_chart)

st.subheader('Historical Global GDP Ranking Change Bar Chart')
st.altair_chart(rank_chart)
st.write('These changes reflect the shifting balance of global economic power, the rise of emerging market economies, and the adjustment of the relative positions of traditional economic powerhouses. These data emphasize how globalization has reshaped the economic map and revealed how some countries have expanded their influence through economic strategies and global trade networks. ')

st.subheader('Selected Country Economic Indicator Trend Analysis Line Chart')
st.altair_chart(gdp_trend)
st.write('The first line chart displays the GDP trend of the United States, China, and Japan from 1970 to 2020. The chart clearly shows the steady growth of the US GDP, maintaining its position as a world economic powerhouse. Since the 1990s, China\'s GDP growth rate has accelerated, especially after entering the 21st century, surpassing Japan in growth rate and rapidly catching up with the US, demonstrating its rise as an emerging economic superpower. After Japan\'s \"Lost Decade\" in the 1990s, its GDP growth slowed, contrasting with China and the US.')

st.altair_chart(manufacturing_gva_trend)
st.write('The second chart shows the trend of manufacturing GVA for these three countries. The manufacturing GVA of the US and China continued to grow, with China showing explosive growth since 2000, possibly due to its vigorous development of the manufacturing sector and export-oriented economic strategies. Meanwhile, Japan\'s manufacturing GVA changes were relatively stable, not showing the same growth momentum as China.')

st.subheader('Selected Country Industry Contribution Ratio Chart')
st.altair_chart(industry_contribution)

us_pie = draw_pie_chart(df_selected_countries, 'United States')
china_pie = draw_pie_chart(df_selected_countries, 'China')
japan_pie = draw_pie_chart(df_selected_countries, 'Japan')

pie_chart = alt.hconcat(us_pie, china_pie, japan_pie)
st.altair_chart(pie_chart)
st.write('These data show that while all three countries emphasize the importance of manufacturing in the economy, they also have their focus, reflecting different economic structures and stages of development. The economic structures of the US and China are more concentrated, especially in manufacturing, while Japan\'s economic structure is more diversified.')

st.subheader('Export and Import Trend Line Chart and Trade Balance Chart')
description = ['**China**: The speed of growth in both exports and imports was rapid, especially the remarkable growth in exports, resulting in China maintaining a significant trade surplus in most years, marking its status as a global manufacturing hub.',
               '**Japan**: Compared to China, Japan\'s export and import growth was relatively stable, maintaining a trade surplus for many years. However, in the early 21st century, as import growth accelerated, Japan\'s trade surplus diminished.',
               '**United States**: Although both exports and imports have grown, the growth rate of imports has been higher than that of exports, leading to a long-term trade deficit for the US. Particularly in recent years, an increased deficit may indicate a growing reliance on foreign products and services.']
for index,chart in enumerate(charts):
    st.altair_chart(chart)
    st.write(description[index])

st.subheader('Population vs. Household Consumption Relationship Scatter Plot')
st.altair_chart(population_consumption)
st.write('This graph reveals that the relationship between population size and household consumption expenditure is not simply linear. Although the US does not have the largest population size, its consumption expenditure is the highest, which may relate to the domestic consumption culture, credit systems, and personal wealth distribution.')
st.write('On the other hand, despite having a huge population base, China still has a lot of growth potential in household consumption.')

st.subheader('GDP and Per Capita GNI Relationship Scatter Plot')
st.altair_chart(gdp_gni_correlation)
st.write('The US and Japan points show some degree of positive correlation, indicating that as the GDP grows, the per capita GNI also increases accordingly.')
st.write('In contrast, the growth in China\'s GDP has not brought the same level of growth in per capita GNI, which may suggest that the dividend of China\'s GDP growth has not fully translated into an increase in per capita wealth.')
