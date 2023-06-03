import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import base64
import datetime
import toml
import plotly.express as px
from scipy.stats import zscore

# Load the TOML file for theme configuration
config_data = toml.load('https://github.com/alanampalathara/trading/blob/main/config.toml')

# Apply theme settings if necessary
st.set_page_config(**config_data['theme'])


#def add_bg_from_local(image_file):
 #   with open(image_file, "rb") as image_file:
  #      encoded_string = base64.b64encode(image_file.read())
   # st.markdown(
  #  f"""
  #  <style>
  #  .stApp {{
   #     background-image: url(data:image/{"jpg"};base64,{encoded_string.decode()});
    #    background-size: 100% 100%;

   # }}
   # </style>
   # """,
   # unsafe_allow_html=True
  #  )
#add_bg_from_local('C:/Users/alant/Documents/Rainman/UI/background.jpg')  

def stock_compar(stock1, stock2, date, end, invest_amt, z_score):           
    try:
        # Downloading info about the two stocks
        stock_data1 = yf.download(stock1, start=date, end=end)
        stock_data2 = yf.download(stock2, start=date, end=end)
        # Finding average daily price of both stocks 
        stock1_mean = (stock_data1['High']+stock_data1['Low'])/2
        stock2_mean = (stock_data2['High']+stock_data2['Low'])/2
        # Converting to dataframe
        result = pd.merge(pd.DataFrame(stock1_mean), pd.DataFrame(stock2_mean), on = "Date")
        column_mapping = {'0_x':'Stock1 value', '0_y':'Stock2 value'}
        result = result.rename(columns=column_mapping)
        # Finding ratio between both stocks
        result["Ratio(Num/Denom)"] = result['Stock1 value']/result['Stock2 value']
        
        
        result['5_DMA'] = result["Ratio(Num/Denom)"].rolling(window=5).mean()
        result['20_DMA'] = result["Ratio(Num/Denom)"].rolling(window=20).mean()
        
        #result = result.dropna()
        result["std_20Day"] = result["Ratio(Num/Denom)"].rolling(window=20).std()
        result["Z_score(20DMA)"] = (result['5_DMA'] - result['20_DMA'])/result["std_20Day"]
        result["Signal"] = np.nan
        result["Quantity of stock1 bought"] = 0.0
        result["Quantity of stock1 sold"] = 0.0
        result["Quantity of stock2 bought"] = 0.0
        result["Quantity of stock2 sold"] = 0.0
        result["Val stock2 bought"] = 0.0
        result["Val stock2 sold"] = 0.0
        result["Val stock1 bought"] = 0.0
        result["Val stock1 sold"] = 0.0
        result["Total purchase"] = 0.0
        result["Total sales"] = 0.0
        result["Profit"] = 0.0
        result["Profit %"] = 0.0

        
        z_sign = [0]
        Num_count = 0.0
        Denom_count = 0.0
        tot_profit = 0.0
        tot_invest = 0.0
        curr_tot_invest = 0.0
        temp = invest_amt


        for index, row in result.iterrows():
            if row["Z_score(20DMA)"] >= z_score and z_sign[-1] != 1:
                z_sign.append(1)
                result.at[index, "Signal"] = 0.0
                Tot_stk_value = (row["Stock1 value"]*Num_count) + (row["Stock2 value"]*Denom_count)
                result.at[index, "Quantity of stock1 bought"] = 0.0
                result.at[index, "Quantity of stock1 sold"] = Num_count
                result.at[index, "Quantity of stock2 bought"] = (temp+Tot_stk_value)/row["Stock2 value"]
                result.at[index, "Quantity of stock2 sold"] = 0.0
                result.at[index, "Val stock2 bought"] = row["Quantity of stock2 bought"]*row["Stock2 value"]
                result.at[index, "Val stock2 sold"] = 0.0
                result.at[index, "Val stock1 bought"] = 0.0
                result.at[index, "Val stock1 sold"] = row["Stock1 value"]*Num_count
                result.at[index, "Total purchase"] = row["Val stock2 bought"]+row["Val stock1 bought"]
                result.at[index, "Total sales"] = row["Val stock2 sold"] + row["Val stock1 sold"]
                result.at[index, "Profit"] = row["Total sales"] - invest_amt + temp
                tot_profit += row["Profit"]
                tot_invest += row["Total purchase"]
                curr_tot_invest = tot_invest - row["Total purchase"]
                if(curr_tot_invest == 0):
                    result.at[index, "Profit %"] = 0.0
                else:
                    result.at[index, "Profit %"] = (tot_profit/curr_tot_invest)*100
                Tot_stk_value = row["Total purchase"]
                Num_count = 0
                Denom_count = row["Quantity of stock2 bought"]
                invest_amt = row["Total purchase"] 
                temp = 0
            elif row["Z_score(20DMA)"] <= -(z_score) and z_sign[-1] != -1:
                z_sign.append(-1)
                result.at[index, "Signal"] = 1.0
                Tot_stk_value = (row["Stock1 value"]*Num_count) + (row["Stock2 value"]*Denom_count)
                result.at[index, "Quantity of stock1 bought"] = (temp+Tot_stk_value)/row["Stock1 value"]
                result.at[index, "Quantity of stock1 sold"] = 0.0
                result.at[index, "Quantity of stock2 bought"] = 0.0
                result.at[index, "Quantity of stock2 sold"] = Denom_count
                result.at[index, "Val stock2 bought"] = 0.0
                result.at[index, "Val stock2 sold"] = row["Stock2 value"]*Denom_count
                result.at[index, "Val stock1 bought"] = row["Quantity of stock1 bought"]*row["Stock1 value"]
                result.at[index, "Val stock1 sold"] = 0.0
                result.at[index, "Total purchase"] = row["Val stock2 bought"]+row["Val stock1 bought"]
                result.at[index, "Total sales"] = row["Val stock2 sold"] + row["Val stock1 sold"]
                result.at[index, "Profit"] = row["Total sales"] - invest_amt + temp
                tot_profit += row["Profit"]
                tot_invest += row["Total purchase"]
                curr_tot_invest = tot_invest - row["Total purchase"]
                if(curr_tot_invest == 0):
                    result.at[index, "Profit %"] = 0.0
                else:
                    result.at[index, "Profit %"] = (tot_profit/curr_tot_invest)*100
                Tot_stk_value = row["Total purchase"]
                Num_count = row["Quantity of stock1 bought"]
                Denom_count = 0
                invest_amt = row["Total purchase"] 
                temp = 0
            else:
                z_sign.append(z_sign[-1])
                result.at[index, "Signal"] = 0.5

        
        result.insert(0, "Date",result.index)
        result['Date'] = result['Date'].map(lambda x: x.date())

        

        z_score_df = result[['Date','Z_score(20DMA)']]

        result['Signal'] = result['Signal'].replace({0.5:"NA", 1.0:"Sell Stock2 and buy Stock1", 0.0:"Sell Stock1 and buy Stock2"})
        # result.drop(result[result['Signal'] == "NA"].index, inplace = True)

        
        return result, z_score_df
    except Exception as e:
        print(f"Error occurred while fetching stock data: {e}")
        return None, None



st.markdown(f'<h1 style="color:#212121;background-color: rgba(255, 255, 255, 0.3);font-size:40px;border-radius:3%;">{"ALGORITHMIC TRADING PLATFORM"}</h1>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Profitable stocks", "Z graph"])

with tab1:
    # To enter the stock codes and other information
    st.sidebar.write("Not sure about the stock code? [Click here](https://finance.yahoo.com/q?s=gg)")
    stock1 = st.sidebar.text_input("stock1", "Enter stock1")
    stock2 = st.sidebar.text_input("stock2", "Enter stock2")

    today = datetime.date.today()
    before = today - datetime.timedelta(days=700)
    start_date = st.sidebar.date_input('Start date', before)
    end_date = st.sidebar.date_input('End date', today)

    invest_amt = st.sidebar.text_input("Invest amount", "Enter the invest amount in rupees")  
    graph_df = pd.DataFrame()
    if st.button("Find"):
        invest_amt = float(invest_amt) 
        df, graph_df = stock_compar(stock1, stock2, start_date, end_date, invest_amt, z_score = 1.25)
        # df = df.drop(['Ratio(Num/Denom)', '5_DMA', '20_DMA', 'std_20Day', 'Z_score(20DMA)'], axis=1)
        # CSS to inject contained in a string
        hide_table_row_index = """
                    <style>
                    thead tr th:first-child {display:none}
                    tbody th {display:none}
                    </style>
                    """

        # Inject CSS with Markdown
        st.markdown(hide_table_row_index, unsafe_allow_html=True)

        # Display a static table
        st.table(df)

with tab2:
    if len(graph_df) != 0:
        fig = px.line(graph_df, x="Date", y="Z_score(20DMA)")
        fig.add_shape(type="line", x0=min(graph_df["Date"]), y0=-1.25,x1=max(graph_df["Date"]), y1=-1.25)
        fig.add_shape(type="line",x0=min(graph_df["Date"]), y0=1.25,x1=max(graph_df["Date"]), y1=1.25)
        fig.update_layout(legend_title="legend", font=dict(family="Arial", size=13, color="green"))
        fig.update_layout(yaxis=dict(tickformat='.2f', dtick=0.25))
        fig.update_layout(title = "ASIAN PAINTS vs AKZO")
        st.plotly_chart(fig)

 

