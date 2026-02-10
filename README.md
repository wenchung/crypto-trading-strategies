# Speed Camera Warning App 🚗📷

[![Android](https://img.shields.io/badge/Android-7.0%2B-green.svg)](https://developer.android.com)
[![Kotlin](https://img.shields.io/badge/Kotlin-1.9.21-blue.svg)](https://kotlinlang.org)
[![License](https://img.shields.io/badge/License-AGPLv3%20%2F%20Commercial-blue.svg)](LICENSE.txt)

Android 測速照相警示 App - 使用政府開放資料 API 即時提醒駕駛接近測速照相機位置

## ✨ 功能特色

- 🗺️ **即時位置追蹤** - 使用 GPS 持續監控你的位置和速度
- 📍 **測速照相點資料** - 從政府開放平台自動同步全台測速照相點
- 🔔 **距離警示** - 接近測速照相時分級提醒（500m/300m/100m）
- 🔊 **語音播報** - TTS 語音提醒，專心開車免看手機
- 🏃 **背景執行** - 前景服務確保 App 在背景持續運作
- 💾 **離線功能** - 本地資料庫儲存，無網路也可運作
- ⚡ **效能優化** - 智慧定位更新頻率，節省電量

## 📱 系統需求

- Android 7.0 (API 24) 或更高版本
- GPS 定位功能
- 網路連線（首次同步資料時）
- 儲存空間約 50MB

## 🏗️ 技術架構

### 核心技術棧

- **Language**: Kotlin
- **Architecture**: MVVM (Model-View-ViewModel)
- **Dependency Injection**: Hilt
- **Database**: Room
- **Network**: Retrofit + OkHttp
- **Async**: Kotlin Coroutines + Flow
- **Location**: Google Play Services Location API
- **Background**: Foreground Service + WorkManager

### 主要依賴

```gradle
// Android Core
androidx.core:core-ktx:1.12.0
androidx.appcompat:appcompat:1.6.1
androidx.lifecycle:lifecycle-runtime-ktx:2.7.0

// UI
androidx.constraintlayout:constraintlayout:2.1.4
com.google.android.material:material:1.11.0

// Dependency Injection
com.google.dagger:hilt-android:2.48

// Database
androidx.room:room-runtime:2.6.1
androidx.room:room-ktx:2.6.1

// Network
com.squareup.retrofit2:retrofit:2.9.0
com.squareup.retrofit2:converter-gson:2.9.0

// Location
com.google.android.gms:play-services-location:21.1.0

// Background Tasks
androidx.work:work-runtime-ktx:2.9.0
```

## 📂 專案結構

```
app/src/main/java/com/example/speedcamerawarning/
├── SpeedCameraApp.kt                 # Application 類別
├── data/                              # 資料層
│   ├── local/
│   │   ├── database/
│   │   │   └── AppDatabase.kt        # Room 資料庫
│   │   ├── dao/
│   │   │   └── SpeedCameraDao.kt     # 資料存取物件
│   │   └── entity/
│   │       └── SpeedCameraEntity.kt  # 資料庫實體
│   ├── remote/
│   │   ├── api/
│   │   │   └── DataGovApi.kt         # API 介面定義
│   │   └── model/
│   │       └── SpeedCameraResponse.kt # API 回應模型
│   └── repository/
│       └── SpeedCameraRepository.kt  # 資料倉庫
├── domain/                            # 領域層
│   └── model/
│       └── SpeedCamera.kt            # 領域模型
├── presentation/                      # 呈現層
│   └── main/
│       ├── MainActivity.kt           # 主要 Activity
│       └── MainViewModel.kt          # ViewModel
├── service/                           # 服務層
│   ├── LocationTrackingService.kt    # 位置追蹤前景服務
│   └── NotificationHelper.kt         # 通知輔助類別
└── util/                              # 工具類別
    ├── Constants.kt                  # 常數定義
    ├── DistanceCalculator.kt         # 距離計算
    ├── LocationHelper.kt             # 位置輔助工具
    └── PermissionHelper.kt           # 權限處理
```

## 🚀 快速開始

### 前置需求

1. [Android Studio](https://developer.android.com/studio) (最新穩定版)
2. Android SDK 34
3. Gradle 8.2+

### 安裝步驟

1. **Clone 專案**

```bash
git clone https://github.com/wenchung/SpeedCameraWarning.git
cd SpeedCameraWarning
```

2. **用 Android Studio 開啟**

```
File → Open → 選擇專案資料夾
```

3. **Gradle 同步**

等待 Android Studio 自動同步依賴（或點擊 "Sync Now"）

4. **連接裝置**

- 實體裝置：啟用 USB 偵錯
- 或使用 Android 模擬器 (API 24+)

5. **執行 App**

點擊綠色播放按鈕或按 `Shift + F10`

### 詳細執行指南

完整的執行說明請參考 [RUN_INSTRUCTIONS.md](RUN_INSTRUCTIONS.md)

## 🎯 使用方式

### 首次使用

1. **授予權限**
   - 位置權限：選擇「一律允許」
   - 通知權限：允許
   - 前景服務權限：允許 (Android 14+)

2. **同步資料**
   - 點擊「同步測速照相資料」按鈕
   - 等待資料下載完成（約 5-10 秒）

3. **開始監控**
   - 點擊「開始監控」按鈕
   - 通知欄會顯示前景服務運作中

### 日常使用

- App 在背景持續監控位置
- 接近測速照相時自動提醒
- 可隨時停止監控以節省電力

### 警示級別

| 距離 | 警示類型 | 說明 |
|------|---------|------|
| 500m | 提醒通知 | 前方有測速照相 |
| 300m | 重要提醒 | 注意速限 |
| 100m | 警告 | 立即檢查速度 |

## 📊 資料來源

本 App 使用以下政府開放資料：

- **資料集**: 固定式測速照相設備設置點一覽表
- **提供機關**: 中華民國交通部
- **資料格式**: JSON
- **更新頻率**: 不定期更新

資料欄位包含：
- 縣市別、鄉鎮、村里
- 設置地點、速限
- 經緯度座標
- 設置方向

## 🔒 隱私權政策

- ✅ 位置資料僅用於本地計算距離
- ✅ 不會上傳或儲存軌跡記錄
- ✅ 不會收集個人識別資訊
- ✅ 測速照相資料來自公開政府資料

## 🛠️ 開發指南

### 建置 Debug APK

```bash
./gradlew assembleDebug
# 輸出: app/build/outputs/apk/debug/app-debug.apk
```

### 建置 Release APK

```bash
./gradlew assembleRelease
# 輸出: app/build/outputs/apk/release/app-release.apk
```

### 執行測試

```bash
# 單元測試
./gradlew test

# 整合測試
./gradlew connectedAndroidTest
```

### 程式碼品質

```bash
# Lint 檢查
./gradlew lint

# 查看報告
open app/build/reports/lint-results.html
```

## 🐛 已知問題

- [ ] 部分地區測速照相點資料可能不完整
- [ ] 模擬器上語音播報可能無效
- [ ] 長時間使用會增加電量消耗

## 🗺️ 未來規劃

- [ ] 整合 Google Maps 顯示測速照相位置
- [ ] 新增使用者自訂警示距離
- [ ] 支援區間測速提醒
- [ ] 新增駕駛統計與歷史記錄
- [ ] 多語系支援（英文）
- [ ] Wear OS 支援

## 🤝 貢獻指南

歡迎提交 Issue 或 Pull Request！

1. Fork 本專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. Commit 你的變更 (`git commit -m 'Add some AmazingFeature'`)
4. Push 到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權條款

本專案採用 **雙重授權（Dual License）**：

### 🆓 AGPLv3 授權
適用於：
- ✅ 開源專案（GPL 相容授權）
- ✅ 個人使用
- ✅ 教育用途

詳見 [LICENSE.txt](LICENSE.txt) 或 https://www.gnu.org/licenses/agpl-3.0.html

### 💼 商業授權
適用於：
- 🏢 專有/閉源軟體
- 🚫 無法遵守 AGPLv3 開源要求
- 📦 作為商業產品的一部分分發

**商業授權諮詢**: cwthome@gmail.com

---

**選擇指南**：
- 如果你的專案是開源的或個人使用 → 使用 AGPLv3
- 如果你要開發閉源商業產品 → 需要商業授權

## 👨‍💻 作者

**Chiu Wen Chung**
- Email: cwthome@gmail.com
- GitHub: [@wenchung](https://github.com/wenchung)

## 🙏 致謝

- 感謝交通部提供開放資料
- 感謝 Android 開源社群的貢獻

## 📞 聯絡方式

如有問題或建議，歡迎：
- 開啟 [GitHub Issue](https://github.com/wenchung/SpeedCameraWarning/issues)
- Email: cwthome@gmail.com

---

⚠️ **免責聲明**: 本 App 僅供參考，駕駛時仍應遵守交通規則，注意路況標示。開發者不對使用本 App 導致的任何後果負責。

🚗 **安全駕駛，一路平安！**