from flask import Flask, render_template, request, jsonify, Response, send_file
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import xgboost as xgb
import plotly.express as px

TIME_SERIES_MODEL = 'model/amp_cosumption_prediction_model.json'

app = Flask(__name__)

def create_time_series_features(df):
    """
    Creates time series based feature based on datetime index
    """
    df = df.copy()
    df['PowerStatusCode'] = df.PowerStatusCode
    df['date'] = df.index
    df['WeekNumber'] = df['date'].dt.isocalendar().week
    df['hour'] = df.index.hour
    df['dayofweek'] = df.index.dayofweek
    df['year'] = df.index.year
    df['dayofyear'] = df.index.dayofyear
    df['quarter'] = df.index.quarter
    df['dayofmonth'] = df['date'].dt.day
    df['date_offset'] = (df.date.dt.month*100 + df.date.dt.day - 320)%1300
    df['season'] = pd.cut(df['date_offset'], [-1, 300, 602, 900, 1301],
                         labels=['Spring', 'Summer', 'Fall', 'Winter'])
    return df

@app.route("/")
def index():
    color_pal = sns.color_palette()
    df = pd.read_excel('data.xlsx')
    df = df.set_index('time')
    df.index = pd.to_datetime(df.index)
    df['PowerStatusCode'] = 0
    df['PowerStatusCode'].loc[df['PowerStatus']=='On']=1
    features_xgb_reg_hour = ['WeekNumber','hour', 'dayofweek',
       'dayofyear','PowerStatusCode']
    features_xgb_reg_hour.insert(len(features_xgb_reg_hour),'isFuture')
    xgb_reg = xgb.XGBRegressor()
    xgb_reg.load_model(TIME_SERIES_MODEL)
    future = pd.date_range('2023-11-21', '2023-12-25', freq='1h')
    future_df = pd.DataFrame(index=future)
    future_df['PowerStatusCode'] = 0
    future_df['isFuture']=True
    df['isFuture']=False
    future_df = create_time_series_features(future_df)
    df = create_time_series_features(df)
    future_df = pd.get_dummies(future_df)
    future_df.WeekNumber = future_df.WeekNumber.astype(int)
    df_off_status = df[df['PowerStatusCode']==0]
    df_off_final = pd.concat([df_off_status[features_xgb_reg_hour], future_df[features_xgb_reg_hour]])
    future_df_with_features = df_off_final.query('isFuture').copy()
    future_df_with_features['predictions'] = xgb_reg.predict(future_df_with_features[['WeekNumber', 'hour', 'dayofweek', 'dayofyear', 'PowerStatusCode']])
    fig, ax = plt.subplots(figsize=(30, 10))
    df_off_status['TotalCurrentAmperage'].plot(ax=ax)
    np.exp(future_df_with_features['predictions']).plot(ax=ax, color=color_pal[4], lw=1, ms=1)
    plt.legend(['Past Actual Values From Dataset', 'Future Predicted Data'])
    plt.title("Next Month Future Predictions For Off Power Status")
    fig.savefig('static/monthly_off_status_prediction_plot.png')
    future_df['PowerStatusCode'] = 1
    future_df['isFuture']=True
    df['isFuture']=False
    future_df = create_time_series_features(future_df)
    df = create_time_series_features(df)
    future_df = pd.get_dummies(future_df)
    future_df.WeekNumber = future_df.WeekNumber.astype(int)
    df_on_status = df[df['PowerStatusCode']==1]
    df_on_final = pd.concat([df_on_status[features_xgb_reg_hour], future_df[features_xgb_reg_hour]])
    future_df_with_features = df_on_final.query('isFuture').copy()
    future_df_with_features['predictions'] = xgb_reg.predict(future_df_with_features[['WeekNumber', 'hour', 'dayofweek', 'dayofyear', 'PowerStatusCode']])
    fig, ax = plt.subplots(figsize=(30, 10))
    df_on_status['TotalCurrentAmperage'].plot(ax=ax)
    np.exp(future_df_with_features['predictions']).plot(ax=ax, color=color_pal[4], lw=1, ms=1)
    plt.legend(['Past Actual Values From Dataset', 'Future Predicted Data'])
    plt.title("Next Month Future Predictions For On Power Status")
    fig.savefig('static/monthly_on_status_prediction_plot.png')
    return render_template('index.html')

@app.route("/get_generated_plot", methods=["POST","GET"])
def get_generated_plot():
    if request.method == 'POST':
        color_pal = sns.color_palette()
        xgb_reg = xgb.XGBRegressor()
        xgb_reg.load_model(TIME_SERIES_MODEL)
        from_date = request.form['from_date']
        to_date = request.form['to_date']
        power_status = request.form['power_status']
        future = pd.date_range(str(from_date), str(to_date), freq='1h')
        future_df = pd.DataFrame(index=future)
        future_df['PowerStatusCode'] = int(power_status)
        future_df['isFuture']=True
        future_df = create_time_series_features(future_df)
        future_df = pd.get_dummies(future_df)
        future_df.WeekNumber = future_df.WeekNumber.astype(int)
        if future_df['PowerStatusCode'].unique() == 1:
            future_df['PowerStatus'] = "ON"
        if future_df['PowerStatusCode'].unique() == 0:
            future_df['PowerStatus'] = "OFF"
        generate_future_df = future_df[['WeekNumber','hour', 'dayofweek','dayofyear','PowerStatus','PowerStatusCode','isFuture']]
        future_df_with_features = generate_future_df.query('isFuture').copy()
        future_df_with_features['predictions'] = xgb_reg.predict(future_df_with_features[['WeekNumber', 'hour', 'dayofweek', 'dayofyear', 'PowerStatusCode']])
        future_df_with_features['reverse_transformed_predictions'] = np.exp(future_df_with_features['predictions'])
        generated_plot = px.line(
            future_df_with_features, 
            y = "reverse_transformed_predictions", color = "PowerStatus",
            labels={
                            "reverse_transformed_predictions": "Predicted Total Amperage",
                            "Rolling_forward_early_withdrwal_rate": "Early Withdrwal Rate",
                            "color": "PowerStatus"
                        },title="Predicted Total Amperage Usage of Machine between " + str(from_date)+ " to " + str(to_date) + " for " + str(future_df['PowerStatus'].unique()[0]) + " Power Status of Machine" )
        generated_plot.update_traces(mode='markers+lines',marker=dict(
            size=10),
        line=dict(
            width=3
        ))
        plot= generated_plot.to_html(full_html=False, include_plotlyjs=False)
        content = {'plot':plot}
        return render_template('generated_plot.html',content=content)

