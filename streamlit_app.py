import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import plotly.express as px


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
        column_mapping = {'0_x':f'{stock1} value', '0_y':f'{stock2} value'}
        result = result.rename(columns=column_mapping)
        # Finding ratio between both stocks
        if(stock1_mean[0]>=stock2_mean[0]):
            result[f"Ratio({stock1}/{stock2})"] = result[f'{stock1} value']/result[f'{stock2} value']
            result['5_DMA'] = result[f"Ratio({stock1}/{stock2})"].rolling(window=5).mean()
            result['20_DMA'] = result[f"Ratio({stock1}/{stock2})"].rolling(window=20).mean()
            result["std_20Day"] = result[f"Ratio({stock1}/{stock2})"].rolling(window=20).std()
        else:
            result[f"Ratio({stock2}/{stock1})"] = result[f'{stock2} value']/result[f'{stock1} value']
            result['5_DMA'] = result[f"Ratio({stock2}/{stock1})"].rolling(window=5).mean()
            result['20_DMA'] = result[f"Ratio({stock2}/{stock1})"].rolling(window=20).mean()
            result["std_20Day"] = result[f"Ratio({stock2}/{stock1})"].rolling(window=20).std()

        result["Z_score(20DMA)"] = (result['5_DMA'] - result['20_DMA'])/result["std_20Day"]             
        result["Signal"] = np.nan
        result[f"Quantity of {stock1} bought"] = 0.0
        result[f"Quantity of {stock1} sold"] = 0.0
        result[f"Quantity of {stock2} bought"] = 0.0
        result[f"Quantity of {stock2} sold"] = 0.0
        result[f"Val {stock2} bought"] = 0.0
        result[f"Val {stock2} sold"] = 0.0
        result[f"Val {stock1} bought"] = 0.0
        result[f"Val {stock1} sold"] = 0.0
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

        if(stock1_mean[0]>=stock2_mean[0]):
            for index, row in result.iterrows():
                if row["Z_score(20DMA)"] >= z_score and z_sign[-1] != 1:
                    z_sign.append(1)
                    result.at[index, "Signal"] = 0.0
                    Tot_stk_value = (row[f"{stock1} value"]*Num_count) + (row[f"{stock2} value"]*Denom_count)
                    result.at[index, f"Quantity of {stock1} bought"] = 0.0
                    result.at[index, f"Quantity of {stock1} sold"] = Num_count
                    result.at[index, f"Quantity of {stock2} bought"] = (temp+Tot_stk_value)/row[f"{stock2} value"]
                    result.at[index, f"Quantity of {stock2} sold"] = 0.0
                    result.at[index, f"Val {stock2} bought"] = row[f"Quantity of {stock2} bought"]*row[f"{stock2} value"]
                    result.at[index, f"Val {stock2} sold"] = 0.0
                    result.at[index, f"Val {stock1} bought"] = 0.0
                    result.at[index, f"Val {stock1} sold"] = row[f"{stock1} value"]*Num_count
                    result.at[index, "Total purchase"] = row[f"Val {stock2} bought"]+row[f"Val {stock1} bought"]
                    result.at[index, "Total sales"] = row[f"Val {stock2} sold"] + row[f"Val {stock1} sold"]
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
                    Denom_count = row[f"Quantity of {stock2} bought"]
                    invest_amt = row["Total purchase"] 
                    temp = 0
                elif row["Z_score(20DMA)"] <= -(z_score) and z_sign[-1] != -1:
                    z_sign.append(-1)
                    result.at[index, "Signal"] = 1.0
                    Tot_stk_value = (row[f"{stock1} value"]*Num_count) + (row[f"{stock2} value"]*Denom_count)
                    result.at[index, f"Quantity of {stock1} bought"] = (temp+Tot_stk_value)/row[f"{stock1} value"]
                    result.at[index, f"Quantity of {stock1} sold"] = 0.0
                    result.at[index, f"Quantity of {stock2} bought"] = 0.0
                    result.at[index, f"Quantity of {stock2} sold"] = Denom_count
                    result.at[index, f"Val {stock2} bought"] = 0.0
                    result.at[index, f"Val {stock2} sold"] = row[f"{stock2} value"]*Denom_count
                    result.at[index, f"Val {stock1} bought"] = row[f"Quantity of {stock1} bought"]*row[f"{stock1} value"]
                    result.at[index, f"Val {stock1} sold"] = 0.0
                    result.at[index, "Total purchase"] = row[f"Val {stock2} bought"]+row[f"Val {stock1} bought"]
                    result.at[index, "Total sales"] = row[f"Val {stock2} sold"] + row[f"Val {stock1} sold"]
                    result.at[index, "Profit"] = row["Total sales"] - invest_amt + temp
                    tot_profit += row["Profit"]
                    tot_invest += row["Total purchase"]
                    curr_tot_invest = tot_invest - row["Total purchase"]
                    if(curr_tot_invest == 0):
                        result.at[index, "Profit %"] = 0.0
                    else:
                        result.at[index, "Profit %"] = (tot_profit/curr_tot_invest)*100
                    Tot_stk_value = row["Total purchase"]
                    Num_count = row[f"Quantity of {stock1} bought"]
                    Denom_count = 0
                    invest_amt = row["Total purchase"] 
                    temp = 0
                else:
                    z_sign.append(z_sign[-1])
                    result.at[index, "Signal"] = 0.5
            result['Signal'] = result['Signal'].replace({0.5:"NA", 1.0:f"Sell {stock2} and buy {stock1}", 0.0:f"Sell {stock1} and buy {stock2}"})
        else:
            for index, row in result.iterrows():
                if row["Z_score(20DMA)"] >= z_score and z_sign[-1] != 1:
                    z_sign.append(1)
                    result.at[index, "Signal"] = 0.0
                    Tot_stk_value = (row[f"{stock2} value"]*Num_count) + (row[f"{stock1} value"]*Denom_count)
                    result.at[index, f"Quantity of {stock2} bought"] = 0.0
                    result.at[index, f"Quantity of {stock2} sold"] = Num_count
                    result.at[index, f"Quantity of {stock1} bought"] = (temp+Tot_stk_value)/row[f"{stock1} value"]
                    result.at[index, f"Quantity of {stock1} sold"] = 0.0
                    result.at[index, f"Val {stock1} bought"] = row[f"Quantity of {stock1} bought"]*row[f"{stock1} value"]
                    result.at[index, f"Val {stock1} sold"] = 0.0
                    result.at[index, f"Val {stock2} bought"] = 0.0
                    result.at[index, f"Val {stock2} sold"] = row[f"{stock2} value"]*Num_count
                    result.at[index, "Total purchase"] = row[f"Val {stock1} bought"]+row[f"Val {stock2} bought"]
                    result.at[index, "Total sales"] = row[f"Val {stock1} sold"] + row[f"Val {stock2} sold"]
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
                    Denom_count = row[f"Quantity of {stock1} bought"]
                    invest_amt = row["Total purchase"] 
                    temp = 0
                elif row["Z_score(20DMA)"] <= -(z_score) and z_sign[-1] != -1:
                    z_sign.append(-1)
                    result.at[index, "Signal"] = 1.0
                    Tot_stk_value = (row[f"{stock2} value"]*Num_count) + (row[f"{stock1} value"]*Denom_count)
                    result.at[index, f"Quantity of {stock2} bought"] = (temp+Tot_stk_value)/row[f"{stock2} value"]
                    result.at[index, f"Quantity of {stock2} sold"] = 0.0
                    result.at[index, f"Quantity of {stock1} bought"] = 0.0
                    result.at[index, f"Quantity of {stock1} sold"] = Denom_count
                    result.at[index, f"Val {stock1} bought"] = 0.0
                    result.at[index, f"Val {stock1} sold"] = row[f"{stock1} value"]*Denom_count
                    result.at[index, f"Val {stock2} bought"] = row[f"Quantity of {stock2} bought"]*row[f"{stock2} value"]
                    result.at[index, f"Val {stock2} sold"] = 0.0
                    result.at[index, "Total purchase"] = row[f"Val {stock1} bought"]+row[f"Val {stock2} bought"]
                    result.at[index, "Total sales"] = row[f"Val {stock1} sold"] + row[f"Val {stock2} sold"]
                    result.at[index, "Profit"] = row["Total sales"] - invest_amt + temp
                    tot_profit += row["Profit"]
                    tot_invest += row["Total purchase"]
                    curr_tot_invest = tot_invest - row["Total purchase"]
                    if(curr_tot_invest == 0):
                        result.at[index, "Profit %"] = 0.0
                    else:
                        result.at[index, "Profit %"] = (tot_profit/curr_tot_invest)*100
                    Tot_stk_value = row["Total purchase"]
                    Num_count = row[f"Quantity of {stock2} bought"]
                    Denom_count = 0
                    invest_amt = row["Total purchase"] 
                    temp = 0
                else:
                    z_sign.append(z_sign[-1])
                    result.at[index, "Signal"] = 0.5
            result['Signal'] = result['Signal'].replace({0.5:"NA", 1.0:f"Sell {stock1} and buy {stock2}", 0.0:f"Sell {stock2} and buy {stock1}"})


        
        result.insert(0, "Date",result.index)
        result['Date'] = result['Date'].map(lambda x: x.date())

        

        clean_df = result.copy()

        clean_df.drop(clean_df[clean_df['Signal'] == "NA"].index, inplace = True)

        
        return result, clean_df
    except Exception as e:
        print(f"Error occurred while fetching stock data: {e}")
        return pd.DataFrame(), pd.DataFrame()


st.markdown(f'<h1 style="color:#212121;font-size:40px;border-radius:3%;">{"ALGORITHMIC TRADING PLATFORM"}</h1>', unsafe_allow_html=True)


tab1, tab2, tab3 = st.tabs(["Full table","Transaction dates", "Z graph"])

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
    
    df = pd.DataFrame()
    cleaned_df = pd.DataFrame()
    
    st.markdown('<p style="font-family:Arial; font-size: 12px;">*To access sidebar, click the arrow located in the top left corner. Fill in the stock details in the fields given in the sidebar and click Find.</p>',unsafe_allow_html=True)
    if st.sidebar.button("Find"):
        invest_amt = float(invest_amt) 
        df, cleaned_df = stock_compar(stock1, stock2, start_date, end_date, invest_amt, z_score = 1.25)
        if df.empty:
            st.write("Please check the entered details and try again")
        else:
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

            #To convert the dataframe to CSV and add download button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download table in csv format",csv,f"{stock1}_vs_{stock2}.csv","text/csv",key='download-csv')


            # Display a static table
            st.table(df)
        
            
        
with tab2:
    # To show clean table
    if cleaned_df.empty:
        st.write("No data to display.")
    else:
        st.table(cleaned_df)
        
with tab3:
    # To display the graph    
    if df.empty:
        st.write("No graph to display.")
    else:
        fig = px.line(df, x="Date", y="Z_score(20DMA)")
        fig.add_shape(type="line", x0=min(df["Date"]), y0=-1.25,x1=max(df["Date"]), y1=-1.25)
        fig.add_shape(type="line",x0=min(df["Date"]), y0=1.25,x1=max(df["Date"]), y1=1.25)
        fig.update_layout(legend_title="legend", font=dict(family="Arial", size=13, color="green"))
        fig.update_layout(yaxis=dict(tickformat='.2f', dtick=0.25))
        fig.update_layout(title = f"{stock1} vs {stock2}")
        st.plotly_chart(fig)

 
