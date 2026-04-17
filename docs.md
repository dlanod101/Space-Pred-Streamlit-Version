# 📡 Telecom Event Prediction API

This API provides machine learning–based predictions for telecom network events using a pre-trained PyTorch model.

It supports:

* Segment-based prediction (time window)
* Moment-based prediction (single time point)

---

## 🔗 Base URL

```
http://localhost:8000
```

(Replace with your deployed URL when live)

---

## 🧠 Model Info

* Model: `LightweightTelecomNet`
* Framework: `PyTorch`
* Device: Auto-detects (`CPU` or `CUDA`)
* Classes:

  * `0 → Normal`
  * `1 → Scintillation`
  * `2 → Congestion`
  * `3 → Rain Fade`

---

## 📦 Response Schema

```json
{
  "predicted_event": "string",
  "predicted_vulnerability": 0.0
}
```

---

# 🚀 Endpoints

---

## 1️⃣ Predict Segment

### 🔹 Endpoint

```
GET /predict_segment
```

### 🔹 Description

Predicts a telecom event over a **time segment** (multiple 10-minute intervals).

---

### 🔹 Query Parameters

| Parameter                     | Type | Default | Description                    |
| ----------------------------- | ---- | ------- | ------------------------------ |
| `sample_idx`                  | int  | 200     | Index of the sample in dataset |
| `start_time_idx`              | int  | 0       | Start time index (0–143)       |
| `duration_in_10min_intervals` | int  | 1       | Number of intervals (1–144)    |

---

### 🔹 Example Request

```
GET /predict_segment?sample_idx=10&start_time_idx=5&duration_in_10min_intervals=3
```

---

### 🔹 Example Response

```json
{
  "predicted_event": "Congestion",
  "predicted_vulnerability": 0.73
}
```

---

### ⚠️ Notes

* Each interval = **10 minutes**
* Max duration = **24 hours (144 intervals)**
* Uses temporal + spatial + operator data

---

## 2️⃣ Predict Moment

### 🔹 Endpoint

```
GET /predict_moment
```

### 🔹 Description

Predicts a telecom event for a **single moment in time**.

---

### 🔹 Query Parameters

| Parameter    | Type | Default | Description         |
| ------------ | ---- | ------- | ------------------- |
| `sample_idx` | int  | 200     | Index of the sample |
| `moment_idx` | int  | 0       | Time index (0–143)  |

---

### 🔹 Example Request

```
GET /predict_moment?sample_idx=10&moment_idx=20
```

---

### 🔹 Example Response

```json
{
  "predicted_event": "Rain Fade",
  "predicted_vulnerability": 0.41
}
```

---

## ⚙️ Data Handling

* Data is loaded from:

```
data/synthetic_data.pt
```

* Supported formats:

  * List of dictionaries
  * Dictionary of lists
  * Tuple-based dataset

---

## ❌ Error Responses

### Model Not Loaded

```json
{
  "predicted_event": "Model not loaded",
  "predicted_vulnerability": 0.0
}
```

---

### Runtime Error

```json
{
  "predicted_event": "Error: <error_message>",
  "predicted_vulnerability": 0.0
}
```

---

## 🧪 Local Testing

Run server:

```bash
uvicorn main:app --reload
```

Interactive docs:

```
http://localhost:8000/docs
```

---

## 🧩 Integration Tips

* Use `/predict_segment` for:

  * Trend analysis
  * Network monitoring dashboards

* Use `/predict_moment` for:

  * Real-time alerts
  * Instant anomaly detection

---

## 🔐 Dependencies

* FastAPI
* PyTorch
* Uvicorn

Install:

```bash
pip install fastapi uvicorn torch
```

---

## 📌 Summary

| Feature                  | Endpoint           |
| ------------------------ | ------------------ |
| Segment Prediction       | `/predict_segment` |
| Single Moment Prediction | `/predict_moment`  |
