# Datasheet for PM2.5 TP.HCM Dataset

> Theo chuẩn Gebru et al., *"Datasheets for Datasets"*, Communications of the ACM, 2021.

---

## 1. Motivation

**For what purpose was the dataset created?**

Bộ dữ liệu được tạo ra để hỗ trợ nghiên cứu về **dự báo nồng độ bụi mịn PM2.5 theo giờ** tại Thành phố Hồ Chí Minh (TP.HCM). Đây là một *methodological dataset* — được thiết kế để cung cấp một bộ dữ liệu chuỗi thời gian đa nguồn đã qua tiền xử lý nghiêm ngặt, phục vụ cho phân tích thống kê, trực quan hóa, và huấn luyện các mô hình học máy cơ sở (Linear Regression, Random Forest, XGBoost). Bộ dữ liệu nhấn mạnh tính **tái lập (reproducibility)** và **chống rò rỉ dữ liệu (data leakage prevention)** thông qua pipeline tiền xử lý có hệ thống, được kiểm chứng theo khung đánh giá DMES (Dataset–Method–Experiment Standard).

**Who created the dataset and on behalf of which entity?**

Nhóm nghiên cứu sinh viên **DS108** (Lương Trần Kim Ngọc, Nguyễn Phương Nguyên), thuộc Ngành Khoa học Dữ liệu, Trường Đại học Công nghệ Thông tin, ĐHQG Thành phố Hồ Chí Minh, Việt Nam. Đây là sản phẩm của đồ án cuối kỳ môn " Tiền xử lý dữ liệu (DS108)".

**Who funded the creation of the dataset?**

Không có nguồn tài trợ bên ngoài. Công sức thu thập, xử lý và phân tích dữ liệu được thực hiện hoàn toàn bởi nhóm tác giả.

**Any other comments?**

Đây là một *methodological dataset* — tập trung vào chất lượng pipeline tiền xử lý và cấu trúc đặc trưng, không phải dữ liệu thương mại từ hệ thống quan trắc tư nhân. Dữ liệu không chứa thông tin cá nhân (PII) hay dữ liệu nhạy cảm về an ninh. Tất cả nguồn dữ liệu đều là nguồn mở (open data).

---

## 2. Composition

**What do the instances that comprise the dataset represent?**

Mỗi dòng là một **mốc đo lường 1 giờ** tại TP.HCM, bao gồm nồng độ PM2.5 trung bình theo giờ từ 5 trạm quan trắc và 5 biến khí tượng đi kèm, cùng các đặc trưng kỹ thuật được trích xuất (lag, rolling statistics, cyclical encoding, weather interactions).

**How many instances are there in total?**

- Dữ liệu thô sau merge: 12.912 quan sát theo giờ (19/11/2024 – 10/05/2026).
- Sau làm sạch (gap detection + loại đứt gãy >7 ngày): 11.555 quan sát hợp lệ.

- Sau phân chia theo thời gian (clean datasets):
  - Train: 4.551 mẫu (23/06/2025 – 31/12/2025)
  - Validation: 1.416 mẫu (01/01/2026 – 28/02/2026)
  - Test: 1.689 mẫu (01/03/2026 – 10/05/2026)
- Tổng sau split (không có missing): 7.656 mẫu.

- Sau bước feature engineering (feature datasets):
  - Train: 4.383 mẫu
  - Validation: 1.248 mẫu
  - Test: 1.521 mẫu
- Tổng: 7.152 mẫu.

Sự chênh lệch 504 mẫu xuất phát từ việc tạo các đặc trưng lag và rolling statistics. Các hàng đầu chuỗi thời gian không đủ dữ liệu lịch sử để tính toán đặc trưng được loại bỏ thông qua dropna().

Bộ dữ liệu đặc trưng (`*_features.csv`) bao gồm **31 biến đầu vào** được sử dụng cho huấn luyện mô hình. Biến mục tiêu `pm25` (đã scale) nằm riêng trong các file `*_clean.csv` và được ghép khi huấn luyện.

**Các nhóm đặc trưng bao gồm:** 5 biến khí tượng, 3 biến thời gian, 5 lag features, 5 rolling statistics, 2 difference features, 5 weather interaction features và 6 cyclical encoding features.

**Does the dataset contain all possible instances or is it a sample?**

Đây là **toàn bộ** dữ liệu có sẵn từ 5 trạm quan trắc ổn định trong giai đoạn nghiên cứu (11/2024 – 05/2026), sau khi áp dụng các bước làm sạch và loại bỏ các khoảng đứt gãy lớn. Không phải mẫu chọn lọc.

**What data does each instance consist of?**

Mỗi mẫu bao gồm:
- **Biến mục tiêu:** `pm25` — nồng độ PM2.5 đã qua nội suy và chuẩn hóa (µg/m³, RobustScaler).
- **Khí tượng:** Nhiệt độ (°C), độ ẩm (%), tốc độ gió (km/h), áp suất (hPa), lượng mưa (mm).
- **Thời gian:** Giờ, tháng, thứ trong tuần (dạng số nguyên + sin/cos cyclical encoding).
- **PM2.5 gốc & flags:** `pm25_raw` (chưa scale), `pm25_interpolated` (bool), `pm25_outlier_iqr` (0/1), `n_obs` (số trạm đo trong giờ).
- **Lag features:** `pm25_lag_1`, `pm25_lag_3`, `pm25_lag_6`, `pm25_lag_24`, `pm25_lag_168`.
- **Rolling statistics:** Trung bình, độ lệch chuẩn, max, min trên cửa sổ 24h và 168h.
- **Difference features:** `pm25_diff_1`, `pm25_diff_24`.
- **Weather interactions:** `precipitation_log`, `is_rain`, `temp_humidity`, `temp_diff_1`, `humidity_diff_1`.

**Is there a label or target associated with each instance?**

Có. Mỗi mẫu có **1 biến mục tiêu** (`pm25`) là nồng độ PM2.5 theo giờ (µg/m³). Không có nhãn phân loại hay nhãn bất thường — đây là bài toán **hồi quy chuỗi thời gian** (time series regression).

**Is any information missing from individual instances?**

- Dữ liệu thô ban đầu: tỷ lệ khuyết thiếu PM2.5 là **10,51%** (1.357/12.912 quan sát), tập trung thành các khoảng đứt gãy lớn (tháng 1/2025, 2/2025, 6/2025).
- Sau xử lý: các khoảng đứt gãy >7 ngày bị **loại bỏ hoàn toàn** (40,3% tổng quan sát ban đầu).
- Các khoảng trống ngắn (≤3 giờ) được nội suy tuyến tính; các khoảng >3 giờ còn sót lại bị loại bỏ sau dropna.
- Các cột lag và rolling có giá trị NaN ở các hàng đầu (do `shift`), được loại bỏ sau khi tạo đặc trưng.
- Kết quả cuối cùng: **không còn giá trị missing** trong các file CSV cuối cùng (`train_features.csv`, `val_features.csv`, `test_features.csv`).

**Are relationships between individual instances made explicit?**

Có, thông qua:
- Cột `time` (timestamp liên tục 1 giờ, múi giờ Asia/Ho_Chi_Minh).
- Các lag features (`pm25_lag_1` đến `pm25_lag_168`).
- Các rolling window features (trên cửa sổ 24h và 168h).
- Các difference features (thay đổi so với 1h và 24h trước).

**Are there recommended data splits?**

Có. Phân chia **theo thời gian (chronological split)** để tránh data leakage:
- Train: 23/06/2025 – 31/12/2025 (4.551 mẫu trong clean dataset; 4.383 mẫu trong feature dataset)
- Validation: 01/01/2026 – 28/02/2026 (1.416 mẫu trong clean dataset; 1.248 mẫu trong feature dataset)
- Test: 01/03/2026 – 10/05/2026 (1.689 mẫu trong clean dataset; 1.521 mẫu trong feature dataset)

Tất cả các bước chuẩn hóa (RobustScaler, IQR outlier thresholds) đều được **fit trên Train** và **transform trên Val/Test** để đảm bảo không có rò rỉ dữ liệu.

**Are there any errors, sources of noise, or redundancies in the dataset?**

- **Khoảng đứt gãy lớn:** Các khoảng >7 ngày không có dữ liệu (tập trung vào tháng 1, 2, 6/2025) đã được loại bỏ hoàn toàn.
- **Giá trị sentinel:** Các giá trị -999, -999.0 từ OpenAQ đã được loại bỏ như giá trị không hợp lệ.
- **Giá trị ngoại phạm:** PM2.5 âm hoặc >400 µg/m³ được xử lý như missing values.
- **Đa cộng tuyến:** Tương correlation cao giữa `temperature` và `humidity` (r = -0.83) được ghi nhận nhưng không loại bỏ — mô hình cây (XGBoost, Random Forest) có khả năng xử lý đa cộng tuyến.
- **Tỷ lệ mưa cao:** Phân phối lượng mưa lệch phải mạnh → dùng `log1p` transform (`precipitation_log`).

**Is the dataset self-contained, or does it link to external resources?**

**Bán tự chứa.** Dữ liệu khí tượng được thu thập từ Open-Meteo Historical API và đã được tích hợp sẵn vào dataset. Người dùng không cần gọi lại API để tái tạo kết quả. Tuy nhiên, dữ liệu gốc thô (`raw_openaq.csv`, `raw_openmeteo.csv`) được giữ lại trong `data/raw/` để đảm bảo tính minh bạch và khả năng tái lập.

**Does the dataset contain data that might be considered confidential?**

Không. Dữ liệu PM2.5 đến từ nền tảng OpenAQ (dữ liệu mở công khai), dữ liệu khí tượng từ Open-Meteo (API miễn phí). Không chứa thông tin cá nhân, vị trí nhạy cảm, hay dữ liệu thương mại độc quyền.

**Does the dataset contain data that might be offensive, insulting, threatening, or cause anxiety?**

Không.

**Does the dataset relate to people?**

Gián tiếp — dữ liệu đo lường chất lượng không khí có tác động trực tiếp đến sức khỏe cộng đồng, nhưng không chứa thông tin định danh cá nhân hay dữ liệu về con người.

**Any other comments?**

Dataset đã trải qua pipeline kiểm định nghiêm ngặt: chẩn đoán cơ chế khuyết thiếu (MCAR/MAR qua Little's MCAR test và phân tích phân phối có điều kiện), kiểm tra nội suy giả lập (Synthetic Removal Test, MAE ≈ 3.76 µg/m³), và đánh giá theo khung DMES (Completeness, Accuracy, Consistency, Timeliness).

---

## 3. Collection Process

**How was the data associated with each instance acquired?**

- **Dữ liệu PM2.5:** Từ nền tảng OpenAQ (https://docs.openaq.org) thông qua API v3. Quy trình: xác định 11 sensors thuộc 11 locations trong bán kính 25 km quanh trung tâm TP.HCM (10.7769°N, 106.7009°E) → trích xuất chuỗi dữ liệu theo giờ → sau hợp nhất và làm sạch, chỉ giữ lại 5 sensors cung cấp dữ liệu ổn định và có ý nghĩa thống kê trong giai đoạn nghiên cứu.
- **Dữ liệu khí tượng:** Từ Open-Meteo Historical Archive API (https://open-meteo.com/en/docs/historical-weather-api), tọa độ trung tâm TP.HCM, độ phân giải giờ, múi giờ Asia/Ho_Chi_Minh. 5 biến cốt lõi: nhiệt độ 2m, độ ẩm tương đối 2m, tốc độ gió 10m, áp suất bề mặt, lượng mưa.

**What mechanisms or procedures were used to collect the data?**

- **OpenAQ:** API call tự động qua endpoint `/v3/locations`, `/v3/locations/{id}/sensors`, `/v3/sensors/{id}/hours`. Retry logic với exponential backoff (max 5 lần). Rate limiting: 1 giây giữa các request. Thu thập theo tháng (batching).
- **Open-Meteo:** Archive API với tọa độ cố định (10.7769°N, 106.7009°E), tham số: `temperature_2m`, `relative_humidity_2m`, `wind_speed_10m`, `surface_pressure`, `precipitation`. Tần suất 1 giờ, múi giờ Asia/Ho_Chi_Minh.
- **Validation sau fetch:** Kiểm tra số dòng, null, range nhiệt độ (hợp lý cho TP.HCM), range độ ẩm ([0, 100]%).

**If the dataset is a sample from a larger set, what was the sampling strategy?**

Không áp dụng — đây là toàn bộ dữ liệu có sẵn từ 5 trạm quan trắc ổn định trong giai đoạn 11/2024 – 05/2026. Tuy nhiên, chỉ 5/11 sensors ban đầu được giữ lại sau bước làm sạch do các sensors còn lại không cung cấp dữ liệu ổn định.

**Who was involved in the data collection process?**

- **Nhóm DS108 (Lương Trần Kim Ngọc, Nguyễn Phương Nguyên):** Thiết kế pipeline thu thập tự động, xử lý đa nguồn, tiền xử lý, feature engineering, đánh giá mô hình.
- **Nguồn dữ liệu bên thứ ba:** OpenAQ (cộng đồng quan trắc không khí toàn cầu) và Open-Meteo (dựa trên ERA5 của ECMWF).

**Over what timeframe was the data collected?**

- **Thu thập:** Giai đoạn 11/2024 – 05/2026.
- **Dữ liệu thô cuối cùng:** 19/11/2024 – 10/05/2026 (12.912 quan sát theo giờ).
- **Dữ liệu hợp lệ sau làm sạch:** 19/11/2024 – 10/05/2026 (11.555 quan sát).
- **Dữ liệu sau phân chia:** 23/06/2025 – 10/05/2026 (7.656 mẫu).
- **Dữ liệu sau feature engineering (feature datasets):** 23/06/2025 – 10/05/2026 (7.152 mẫu). Chênh lệch 504 mẫu xuất phát từ việc loại bỏ các hàng đầu chuỗi thời gian không đủ lịch sử để tính toán các đặc trưng lag và rolling statistics.

**Were any ethical review processes conducted?**

Không cần thiết. Dữ liệu công khai từ nền tảng mở, không chứa PII, không liên quan đến con người.

**Does the dataset relate to people?**

Gián tiếp — dữ liệu đo lường chất lượng không khí có ý nghĩa sức khỏe cộng đồng, nhưng không chứa thông tin định danh cá nhân hay dữ liệu về cá nhân cụ thể.

**Did you collect the data from the individuals in question directly, or obtain it via third parties or other sources?**

Thu thập qua bên thứ ba: OpenAQ Community (mạng lưới trạm quan trắc mặt đất toàn cầu) và Open-Meteo (dựa trên ERA5 ECMWF).

**Were the individuals in question notified about the data collection?**

Không áp dụng — đây là dữ liệu quan trắc môi trường công khai, không thu thập từ cá nhân.

**Did the individuals in question consent to the collection and use of their data?**

Không áp dụng.

**If consent was obtained, were the consenting individuals provided with a mechanism to revoke their consent in the future or for certain uses?**

Không áp dụng.

**Has an analysis of the potential impact of the dataset and its use on data subjects been conducted?**

Không có data subjects. Tuy nhiên, nhóm khuyến nghị người dùng không nên áp dụng trực tiếp kết quả dự báo vào hệ thống cảnh báo sức khỏe cộng đồng mà không có chuyên gia môi trường và y tế công cộng xem xét. Ngưỡng WHO (15 µg/m³ trung bình 24h, 5 µg/m³ trung bình năm) được cung cấp làm tham chiếu trong Codebook.

**Any other comments?**

Không.

---

## 4. Preprocessing / Cleaning / Labeling

**Was any preprocessing/cleaning/labeling of the data done?**

Có, pipeline gồm 6 giai đoạn chính:

| Giai đoạn | Mô tả |
|-----------|-------|
| 1. Chuẩn hóa thời gian & đơn vị | Chuyển múi giờ UTC → Asia/Ho_Chi_Minh (UTC+7), loại bỏ tzinfo, chuyển kiểu datetime64[ns]. OpenAQ đã có sẵn đơn vị µg/m³; Open-Meteo trả về đơn vị chuẩn (°C, %, km/h, hPa, mm) — không cần chuyển đổi. |
| 2. Phát hiện & xử lý đứt gãy | Gap detection với ngưỡng `gap_threshold_days=7`. Các khoảng >7 ngày bị loại bỏ hoàn toàn (40,3% tổng quan sát ban đầu). Lý do: bảo toàn cấu trúc thời gian, tránh sai lệch nội suy trên khoảng trống lớn. |
| 3. Chẩn đoán & xử lý missing values | Phân tích cơ chế khuyết thiếu (MCAR/MAR) qua Little's MCAR test (p-value > 0.05) và phân phối có điều kiện. Kết luận: chủ yếu thuộc MCAR hoặc MAR. PM2.5: nội suy tuyến tính theo thời gian, giới hạn 3 giờ liên tiếp. Khí tượng: forward-fill, giới hạn 3 giờ. Biến cờ `pm25_interpolated` đánh dấu các quan sát đã nội suy. |
| 4. Phát hiện & quản lý ngoại lai | Phát hiện bằng IQR (Q1 - 1.5×IQR đến Q3 + 1.5×IQR, fit trên Train). **Không loại bỏ** — tạo biến cờ `pm25_outlier_iqr` (0/1) và sử dụng RobustScaler để giảm tác động của ngoại lai trong chuẩn hóa. Lý do: bảo toàn thông tin về các đợt ô nhiễm cực đoan. |
| 5. Chuẩn hóa & phân chia | RobustScaler fit trên Train, transform Val/Test. Phân chia chronological (Split → Impute → Scale) để ngăn chặn data leakage. |
| 6. Tạo đặc trưng & loại bỏ NaN | Tạo lag features, rolling statistics, difference features, weather interaction features và cyclical encoding. Các hàng đầu chuỗi thời gian không đủ dữ liệu lịch sử để tính toán đặc trưng được loại bỏ bằng dropna(), làm giảm số lượng mẫu từ 7.656 xuống 7.152. |
**Was the "raw data" saved in addition to the preprocessed/cleaned/labeled data?**

Có. Cấu trúc thư mục phân cấp:
- `data/raw/`: Dữ liệu thô gốc từ OpenAQ (`raw_openaq.csv`) và Open-Meteo (`raw_openmeteo.csv`), không chỉnh sửa.
- `data/processed/`: Dữ liệu sau merge, làm sạch, xử lý đứt gãy và missing (`cleaned_final.csv`).
- `data/clean_and_features/`: Dữ liệu cuối cùng sau feature engineering và chuẩn hóa, đã phân chia (`train_features.csv`, `val_features.csv`, `test_features.csv`, `train_clean.csv`, `val_clean.csv`, `test_clean.csv`).

**Is the software used to preprocess/clean/label the instances available?**

Có, toàn bộ mã nguồn được đặt trong thư mục `src/` và notebooks tại `notebook/`:
- `src/config.py`: Cấu hình pipeline (ngưỡng gap, giới hạn nội suy, tỷ lệ phân chia, IQR multiplier, random state).
- `src/data_loader.py`: Loader cho dashboard, đọc `cleaned_final.csv`.
- `src/features.py`: Hàm `create_features()` tạo toàn bộ feature set (lag, rolling, cyclical, weather interactions).
- `src/evaluation.py`: Đánh giá mô hình (MAE, RMSE, R², MAPE, Diebold-Mariano test, Paired t-test).
- `notebooks/`: 5 notebooks theo trình tự pipeline (thu thập, làm sạch, EDA, feature engineering & modeling).

Pipeline được viết bằng Python 3.14, sử dụng Pandas, NumPy, PyWavelets, Scikit-learn, XGBoost. Tính tái lập được đảm bảo qua:
- OOP modular design.
- Git version control.
- `requirements.txt` đầy đủ.
- Kiểm định DMES (Completeness, Accuracy, Consistency, Timeliness).

**Any other comments?**

Pipeline đảm bảo **zero data leakage** thông qua:
- Phân chia **trước** khi xử lý (Split → Impute → Scale).
- Tất cả rolling windows dùng `center=False`, lag chỉ nhìn về quá khứ (`shift>0`).
- RobustScaler chỉ fit trên Train, transform Val/Test.
- Không dùng back-fill trong weather merge.
- Biến `pm25_interpolated` và `pm25_outlier_iqr` là flag chỉ để audit, không được dùng làm feature huấn luyện trực tiếp (nhưng không bị loại bỏ để đảm bảo tính minh bạch).

Kiểm định chất lượng: Synthetic Removal Test (MAE ≈ 3.76 µg/m³, R² = 0.9143), ADF/KPSS stationarity test, ACF/PACF analysis, Pearson correlation matrix, Little's MCAR test.

---

## 5. Uses

**Has the dataset been used for any tasks already?**

Dataset đã được sử dụng nội bộ cho:
- Đánh giá tác động của kỹ thuật đặc trưng (lag, rolling, cyclical encoding, weather interactions) đến khả năng dự báo PM2.5.
- So sánh 3 mô hình cơ sở: Linear Regression, Random Forest, XGBoost. Kết quả: XGBoost đạt hiệu năng tốt nhất (xác nhận qua Diebold-Mariano test, p-value < 0.05, và Paired t-test, α = 0.05).
- Kiểm định pipeline tiền xử lý với DMES framework (Completeness, Accuracy, Consistency, Timeliness).
- Phân tích chuỗi thời gian: ACF/PACF, decomposition, stationarity test (ADF/KPSS).

**Is there a repository that links to any or all papers or systems that use the dataset?**

Repository GitHub chính thức của dự án (private trong giai đoạn đồ án, dự kiến public sau khi hoàn thiện báo cáo). Cấu trúc repository bao gồm: `data/`, `src/`, `notebooks/`, `dashboard/`, `README.md`, `Codebook.md`.

**What (other) tasks could the dataset be used for?**

- Dự báo ngắn hạn nồng độ PM2.5 (short-term load forecasting, STLF) với các mô hình học sâu (LSTM, GRU, Transformer).
- Phân loại mức độ ô nhiễm (ví dụ: WHO 24h guideline > 15 µg/m³, QCVN 05:2023 > 75 µg/m³).
- Phát hiện bất thường không giám sát (unsupervised anomaly detection) cho các đợt ô nhiễm cực đoan.
- Phân tích tác động của khí tượng đến chất lượng không khí đô thị.
- Nghiên cứu về tính mùa vụ và chu kỳ ô nhiễm không khí tại TP.HCM.
- So sánh các chiến lược tiền xử lý chuỗi thời gian (imputation, outlier handling, scaling).
- Đánh giá khả năng tổng quát hóa của mô hình sang các thành phố khác trong khu vực Đông Nam Á.

**Is there anything about the composition that might impact future uses?**

- **Phụ thuộc hạ tầng OpenAQ:** Chất lượng dữ liệu phụ thuộc vào hệ thống vận hành của OpenAQ, tiềm ẩn rủi ro mất dữ liệu cục bộ không thể khắc phục.
- **Phạm vi biến số:** Chỉ có 5 biến khí tượng, chưa tích hợp các yếu tố như mật độ giao thông, hoạt động công nghiệp thời gian thực, hay dữ liệu vệ tinh — có thể hạn chế khả năng giải thích các biến động cực đoan.
- **Một trạm trung tâm:** Tọa độ cố định (10.7769°N, 106.7009°E) — không phản ánh sự khác biệt không gian trong TP.HCM.
- **Chu kỳ ngắn:** Giai đoạn ~17 tháng — có thể chưa đủ để nắm bắt tính mùa vụ dài hạn (nhiều năm).

**Are there tasks for which the dataset should not be used?**

- **Không nên** dùng để ra quyết định chính sách công sức khỏe hay cảnh báo công cộng mà không có chuyên gia y tế và môi trường xem xét.
- **Không nên** dùng trực tiếp làm hệ thống dự báo thời gian thực (real-time) mà không kiểm tra độ trễ và độ ổn định của nguồn dữ liệu.
- **Không nên** dùng cho dự báo dài hạn (nhiều ngày/tuần) do tính tự tương quan của chuỗi giảm mạnh sau 24–48h.
- **Không nên** dùng cho phân tích không gian (spatial analysis) do chỉ có một tọa độ trung tâm TP.HCM.

**Any other comments?**

Không.

---

## 6. Distribution

**Will the dataset be distributed to third parties outside of the entity on behalf of which the dataset was created?**

Có. Dataset hiện đã được công khai trên Kaggle và có thể tiếp tục được phân phối thông qua:
- Kaggle Dataset Repository.
- GitHub repository (public).

**How will the dataset be distributed?**

Dạng CSV (`cleaned_final.csv`, `train_features.csv`, `val_features.csv`, `test_features.csv`) kèm theo:
- File datasheet này (`DATASHEET.md`).
- Codebook (`Codebook.md`) mô tả chi tiết từng cột.
- Pipeline source code (`src/`, `notebooks/`).
- `requirements.txt` và `README.md`.

**When will the dataset be distributed?**

Dataset đã được phát hành công khai trên Kaggle. Các phiên bản mới có thể tiếp tục được cập nhật trong tương lai khi dữ liệu hoặc pipeline được mở rộng.

**Will the dataset be distributed under a copyright or other IP license, and/or under applicable terms of use (ToU)?**

- **Dữ liệu gốc OpenAQ:** CC BY 4.0 (theo điều khoản sử dụng của OpenAQ).
- **Dữ liệu khí tượng Open-Meteo:** Miễn phí cho mục đích phi thương mại (theo điều khoản Open-Meteo).
- **Đặc trưng kỹ thuật, pipeline, mã nguồn:** MIT License (do nhóm DS108 tạo ra).

**Have any third parties imposed IP-based or other restrictions on the data associated with the instances?**

Không. Cả hai nguồn đều là dữ liệu mở với điều khoản sử dụng cho phép nghiên cứu học thuật.

**Do any export controls or other regulatory restrictions apply to the dataset or to individual instances?**

Không. Dữ liệu không chứa thông tin quốc phòng, an ninh, hay xuất khẩu bị hạn chế.

**Any other comments?**

The dataset is publicly available on Kaggle:

https://www.kaggle.com/datasets/kiwi171106/d-liu-kh-tng-v-pm2-5-ti-tp-hcm

Phiên bản Kaggle bao gồm:
- train_clean.csv
- val_clean.csv
- test_clean.csv
- train_features.csv
- val_features.csv
- test_features.csv
- DATASHEET.md
- Codebook.md
- README.md

---

## 7. Maintenance

**Who is supporting/hosting/maintaining the dataset?**

Nhóm nghiên cứu DS108, Trường ĐH Công nghệ Thông tin, ĐHQG-HCM.

**How can the owner/curator/manager of the dataset be contacted?**

- Email: [địa chỉ email nhóm].
- GitHub Issues trên repository chính thức.

**Is there an erratum?**

Chưa có. Mọi lỗi phát hiện sẽ được ghi nhận trong file `CHANGELOG.md` và thông báo qua GitHub Issues.

**Will the dataset be updated?**

Không có kế hoạch cập nhật định kỳ. Tuy nhiên, có thể mở rộng thêm:
- Dữ liệu năm 2026+ nếu nguồn OpenAQ/Open-Meteo tiếp tục cung cấp.
- Thêm các trạm quan trắc khác trong TP.HCM để tăng độ phủ không gian.
- Tích hợp thêm biến khí tượng (điểm sương, bức xạ mặt trời, hướng gió) hoặc yếu tố động (mật độ giao thông, hoạt động công nghiệp).

**If the dataset relates to people, are there applicable limits on the retention of the data associated with the instances?**

Không áp dụng — dataset không chứa thông tin cá nhân.

**Will older versions of the dataset continue to be supported/hosted/maintained?**

Có, thông qua Git tags và releases trên GitHub. Mỗi phiên bản dataset sẽ kèm theo changelog rõ ràng và commit hash tương ứng.

**If others want to extend/augment/build on/contribute to the dataset, is there a mechanism for them to do so?**

Có. Cộng đồng có thể:
- Fork repository và tạo Pull Request.
- Đề xuất thêm đặc trưng mới, cải tiến pipeline qua GitHub Issues.
- Sử dụng pipeline OOP hiện có để tích hợp dữ liệu từ thành phố khác (chỉ cần map cột timestamp và biến khí tượng theo schema trong `Codebook.md`).
- Báo cáo lỗi hoặc đề xuất cải thiện chất lượng dữ liệu.

**Any other comments?**

Nhóm hoan nghênh mọi phản hồi về chất lượng tiền xử lý, đặc trưng kỹ thuật, và kết quả đánh giá mô hình — đặc biệt từ cộng đồng nghiên cứu về khoa học dữ liệu môi trường và dự báo chất lượng không khí.

---

*Datasheet này được soạn thảo theo khuyến nghị của Gebru et al., "Datasheets for Datasets", Communications of the ACM, 2021.*
