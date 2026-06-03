import numpy as np
import pandas as pd


def create_features(df):
    """
    Tạo toàn bộ features từ một DataFrame đã có cột 'pm25_raw'.
    """
    df = df.copy()
    raw = df['pm25_raw']

    if not pd.api.types.is_datetime64_any_dtype(df['time']):
        df['time'] = pd.to_datetime(df['time'])

    # Lag features
    for lag in [1, 3, 6, 24, 168]:
        df[f'pm25_lag_{lag}'] = raw.shift(lag)

    # Rolling statistics (dùng shift(1) để tránh target leakage)
    rolled_24 = raw.shift(1).rolling(24)
    rolled_168 = raw.shift(1).rolling(168)
    df['pm25_roll_mean_24'] = rolled_24.mean()
    df['pm25_volatility_24'] = rolled_24.std()
    df['pm25_roll_max_24'] = rolled_24.max()
    df['pm25_roll_min_24'] = rolled_24.min()
    df['pm25_roll_mean_168'] = rolled_168.mean()

    # Diff features
    df['pm25_diff_1'] = raw.shift(1).diff(1)
    df['pm25_diff_24'] = raw.shift(1).diff(24)

    # Rain features
    df['precipitation_log'] = np.log1p(df['precipitation'])
    df['is_rain'] = (df['precipitation'] > 0).astype(int)

    # Cyclical encoding — lấy trực tiếp từ time, không dùng cột hour/month/dayofweek
    df['hour_sin'] = np.sin(2 * np.pi * df['time'].dt.hour / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['time'].dt.hour / 24)
    df['month_sin'] = np.sin(2 * np.pi * df['time'].dt.month / 12)
    df['month_cos'] = np.cos(2 * np.pi * df['time'].dt.month / 12)
    df['dow_sin'] = np.sin(2 * np.pi * df['time'].dt.dayofweek / 7)
    df['dow_cos'] = np.cos(2 * np.pi * df['time'].dt.dayofweek / 7)

    # Weather interactions
    df['temp_humidity'] = df['temperature'] * df['humidity']

    # Weather diff
    df['temp_diff_1'] = df['temperature'].shift(1).diff(1).fillna(0)
    df['humidity_diff_1'] = df['humidity'].shift(1).diff(1).fillna(0)

    return df