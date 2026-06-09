#  Dự Báo Nồng Độ Bụi Mịn PM2.5 tại TP.HCM
### Tiền Xử Lý · Feature Engineering · Baseline Models

---

##  Tổng Quan Dự Án

| Hạng mục | Nội dung |
|---|---|
| **Bài toán** | Dự báo nồng độ PM2.5 tại TP.HCM theo giờ (nhìn trước 1h) |
| **Loại bài toán** | Supervised Learning — Time Series Regression |
| **Nguồn dữ liệu** | OpenAQ (5 trạm quan trắc) + Open-Meteo Archive API |
| **Phạm vi thời gian** | 2024 → nay (múi giờ Asia/Ho_Chi_Minh) |
| **Target variable** | `pm25` — nồng độ bụi mịn PM2.5 (µg/m³) |

---

##  Mục Tiêu

- Xây dựng pipeline tiền xử lý **chống data leakage** hoàn chỉnh cho chuỗi thời gian
- Chẩn đoán cơ chế khuyết thiếu (MCAR/MAR) và lựa chọn phương pháp imputation phù hợp
- Tạo feature set phong phú từ lag, rolling, cyclical encoding và weather interactions
- Huấn luyện và so sánh 3 baseline models: Linear Regression, Random Forest, XGBoost
- Đánh giá thống kê ý nghĩa của sự khác biệt giữa các models (Diebold-Mariano, Paired t-test)

## Cấu Trúc Dự Án
```text
KHÍ HẬU ĐỒ ÁN/
├── data/
│   ├── raw/                          # Dữ liệu thô (không được sửa)
│   │   ├── raw_openaq.csv
│   │   └── raw_openmeteo.csv
│   │
│   ├── processed/                    # Dữ liệu sau cleaning
│   │   ├── cleaned_final.csv         # Dataset sau merge & gap handling
|   |
│   │
│   └── clean_and_features/                     # Dữ liệu sau feature engineering
│       ├── train_features.csv
│       ├── val_features.csv
│       └── test_features.csv
│       ├── train_clean.csv
│       ├── val_clean.csv
│       └── test_clean.csv
├── dashboard/
|       ├──app.py
|
├── notebook/
│   ├── 01_data_collection_merge/
    |               ├──data_collection_openaq.ipynb
    |               ├──data_collection_openmeteo.ipynb
    |                
│   ├── 02_data_ingestion_and_cleaning.ipynb
│   ├── 03_eda.ipynb
│   ├── 04_feature_engineering_and_modeling.ipynb
│
├── src/                              
│   ├── __pycache__
│   ├── features.py
│   └── evaluation.py
|   └── config.py
│
│
├── README.md
├── CodeBook.md
├── requirements.txt
├── .dockerignore
├── Dockerfile
├── docker-compose.yml


```
---
##  Pipeline Tổng Thể
```text
Thu thập dữ liệu (OpenAQ + Open-Meteo)
↓
Làm sạch & kiểm tra giá trị hợp lệ (PM2.5 ∈ [0, 400] µg/m³)
↓
Merge PM2.5 + Khí tượng theo timestamp
↓
EDA sơ bộ: phân phối, missing values
↓
Chẩn đoán cơ chế khuyết thiếu (MCAR / MAR)
↓
Kiểm định tính dừng (ADF + KPSS)
↓
Gap Detection: loại bỏ đứt gãy > 7 ngày
↓
EDA chuyên sâu (ACF/PACF, Seasonal Decomposition, Correlation)
↓
SPLIT THEO THỜI GIAN (Train / Val / Test) ← TRƯỚC MỌI BƯỚC XỬ LÝ
↓
Imputation độc lập từng tập (interpolate + ffill)
↓
Validation Imputation (Synthetic Removal Test)
↓
Outlier Analysis: Flag (không xóa)
↓
Feature Engineering (Lag / Rolling / Diff / Cyclical / Interactions)
↓
Scaling (RobustScaler — fit trên Train, transform Val & Test)
↓
Chuẩn bị X, y
↓
Baseline Models: Linear Regression → Random Forest → XGBoost (CV)
↓
Residual Analysis
↓
So sánh tổng hợp + Statistical Tests
```
---

## Dữ Liệu Đầu Vào

### 1. PM2.5 (OpenAQ)
- **File:** `raw_openaq.csv`
- **Nội dung:** Đo lường PM2.5 theo giờ từ 5 trạm quan trắc tại TP.HCM
- **Xử lý:** Loại giá trị âm và > 400 µg/m³; chuyển UTC → Asia/Ho_Chi_Minh; gộp tất cả trạm (lấy trung bình theo giờ)

### 2. Khí Tượng (Open-Meteo Archive API)
-  **File:** `raw_openmeteo.csv`
- **Tọa độ:** 10.7769°N, 106.7009°E (TP.HCM)
- **Biến thu thập:**

| Biến | Mô tả | Đơn vị |
|---|---|---|
| `temperature_2m` | Nhiệt độ tại độ cao 2m | °C |
| `relative_humidity_2m` | Độ ẩm tương đối | % |
| `wind_speed_10m` | Tốc độ gió tại 10m | km/h |
| `surface_pressure` | Áp suất bề mặt | hPa |
| `precipitation` | Lượng mưa | mm |

---

## Chiến Lược Split Dữ Liệu

| Tập | Khoảng thời gian | Mục đích |
|---|---|---|
| **Train** |  2025-06-23 → 2025-12-31 | Huấn luyện models + fit scalers |
| **Validation** | 2026-01-01 → 2026-02-28 | Early stopping, hyperparameter tuning |
| **Test** |  2026-03-01 → 2026-05-10 | Đánh giá cuối cùng (không dùng trong quá trình train) |

> **Nguyên tắc quan trọng:** Split thực hiện **trước** imputation, scaling và feature engineering. Scaler/Imputer chỉ được `fit` trên tập Train, sau đó `transform` Val và Test.

---

## Feature Engineering

| Nhóm Feature | Các features | Ghi chú |
|---|---|---|
| **Lag** | `pm25_lag_1/3/6/24/168` | Tính từ `pm25_raw` (chưa scale) |
| **Rolling** | `roll_mean/std/max/min_24`, `roll_mean_168`, `volatility_24` | `shift(1)` để tránh target leakage |
| **Diff** | `pm25_diff_1`, `pm25_diff_24` | Justify bởi Stationarity test |
| **Cyclical** | `hour_sin/cos`, `month_sin/cos`, `dow_sin/cos` | Giữ tính liên tục chu kỳ |
| **Weather** | `precipitation_log`, `is_rain`, `temp_humidity`, `wind_press_ratio` | Phi tuyến hóa |
| **Weather Diff** | `temp_diff_1`, `humidity_diff_1` | Tốc độ thay đổi |

---

## Baseline Models & Kết Quả

### Metrics đánh giá

| Metric | Ý nghĩa |
|---|---|
| **MAE** | Mean Absolute Error — sai số tuyệt đối trung bình (µg/m³) |
| **RMSE** | Root Mean Squared Error — phạt nặng hơn với sai số lớn |
| **R²** | Coefficient of determination — tỷ lệ phương sai được giải thích |
| **MAPE (%)** | Mean Absolute Percentage Error |
| **Within±5 (%)** | % dự báo nằm trong ±5 µg/m³ so với thực tế |
| **Within±10 (%)** | % dự báo nằm trong ±10 µg/m³ so với thực tế |

### Models

| Model | Ưu điểm | Lưu ý |
|---|---|---|
| **Linear Regression** | Đơn giản, interpretable, baseline nhanh | Hệ số không ổn định do đa cộng tuyến cao (VIF > 10 ở lag features) |
| **Random Forest** | Phi tuyến, robust với multicollinearity, feature importance tự nhiên | 200 trees, max_depth=12 |
| **XGBoost** | Tốt nhất trong 3 models; có early stopping; 5-fold TimeSeriesSplit CV | 500 estimators, early_stopping_rounds=50 |

---

## Cấu Hình Toàn Cục (CONFIG)

```python
CONFIG = {
    'gap_threshold_days':      7,     # Đứt gãy > 7 ngày → loại bỏ
    'interpolate_limit_hours': 3,     # Nội suy tối đa 3h liên tiếp
    'ffill_limit_hours':       3,     # Forward-fill tối đa 3h
    'train_ratio':  0.80,
    'val_ratio':    0.10,
    'test_ratio':   0.10,
    'iqr_multiplier': 1.5,            # Ngưỡng IQR cho outlier flag
    'random_state': 42,
    'target': 'pm25'
}
```

---

## Thư Viện Sử Dụng

pandas, numpy, requests, joblib, matplotlib, seaborn, missingno
scipy, statsmodels, sklearn, xgboost

Cài đặt:
```bash
pip install pandas numpy requests joblib matplotlib seaborn missingno \
            scipy statsmodels scikit-learn xgboost
```

---

## Lưu Ý Quan Trọng

1. **Data Leakage:** Tất cả lag/rolling features tính từ `pm25_raw` (giá trị gốc), không từ `pm25` đã scale. Scaler chỉ `fit` trên Train.
2. **Outlier Strategy:** Không xóa outlier PM2.5 vì chúng là real pollution events (đốt rác, traffic đêm). Chỉ flag bằng `pm25_outlier_iqr`. Dùng `RobustScaler` để giảm ảnh hưởng.
3. **Multicollinearity:** VIF cao ở lag features là bình thường cho time series. Không ảnh hưởng RF/XGBoost; cần thận trọng khi interpret hệ số Linear Regression.
4. **Missing Data:** Cơ chế khuyết thiếu là **MAR** (Missing At Random) — xác nhận qua Point-Biserial correlation. Dùng `interpolate(method='time', limit=3)` cho PM2.5 và `ffill(limit=3)` cho khí tượng.
