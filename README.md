# Speed Camera Warning App 🚗📷

[![Android](https://img.shields.io/badge/Android-7.0%2B-green.svg)](https://developer.android.com)
[![Kotlin](https://img.shields.io/badge/Kotlin-1.9.21-blue.svg)](https://kotlinlang.org)
[![License](https://img.shields.io/badge/License-AGPLv3%20%2F%20Commercial-blue.svg)](LICENSE.txt)

Android 測速照相警示 App - 使用政府開放資料 API 即時提醒駕駛接近測速照相機位置

## ✨ 功能特色

- 🗺️ **即時位置追蹤** - 使用 GPS 持續監測你的位置和速度
- 📍 **測速照相黑資料** - 整合政府開放平台自動同步全台測速照相黑
- 🔔 **距離警示** - 接近測速照相時分級提醒（500m/300m/100m）
- 🔊 **語音播報** - TTS 語音提醒，專心開車免看手機
- 🏃 **背景執行** - 前景服務保持 App 在背景持續運作
- 💾 **離線功能** - 本地資料庫儲存，無網路也可運作
- ⚡ **效能優化** - 智慧定位頻率保存，簡省電量

## 📑 系統需求

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

## 📂 合規結構

```
app/src/main/java/com/example/speedcamerawarning/
├── SpeedCameraApp.kt                    # Application 類別
├── data/                                # 資料層
│   ├── local/
│   │   ├── database/
│   │   │   └── AppDatabase.kt           # Room 資料庫
│   │   ├── dao/
│   │   │   └── SpeedCameraDao.kt       # 資料存取物件
│   │   └── entity/
│   │       └── SpeedCameraEntity.kt    # 資料庫實體
│   ├── remote/
│   │   ├── api/
│   │   │   └── DataGovApi.kt           # API 介面定義
│   │   └── model/
│   │       └── SpeedCameraResponse.kt  # API 回應模型
│   └── repository/
│       └── SpeedCameraRepository.kt    # 資料倉庫
├── domain/                              # 業務邏輯層
│   ├── model/
│   │   └── SpeedCamera.kt              # 領域模型
│   └── usecase/
│       ├── GetSpeedCamerasUseCase.kt   # 取得測速相機
│       └── SyncDataUseCase.kt          # 同步資料
├── presentation/                        # 展示層
│   ├── main/
│   │   ├── MainActivity.kt             # 主畫面
│   │   └── MainViewModel.kt            # 主畫面 ViewModel
│   └── service/
│       └── LocationTrackingService.kt  # 位置追蹤服務
└── di/                                  # 依賴注入
    ├── AppModule.kt
    ├── DatabaseModule.kt
    └── NetworkModule.kt
```

## 🚀 快速開始

### 前置需求

- Android Studio Hedgehog | 2023.1.1 或更新版本
- JDK 17 或更高版本
- Android SDK API 34

### 安裝步驟

1. **Clone 專案**
```bash
git clone https://github.com/wenchung/crypto-trading-strategies.git
cd crypto-trading-strategies
```

2. **開啟專案**
   - 使用 Android Studio 開啟專案資料夾
   - 等待 Gradle 同步完成

3. **設定 API Key**（如需要）
   - 複製 `local.properties.template` 為 `local.properties`
   - 填入必要的 API 金鑰

4. **執行應用程式**
   - 連接 Android 裝置或啟動模擬器
   - 點擊 Run 按鈕

## 📱 使用說明

1. **首次啟動**
   - 授予定位權限
   - 授予通知權限
   - 等待測速照相資料同步完成

2. **開始追蹤**
   - 點擊「開始追蹤」按鈕
   - App 會在背景持續監測你的位置
   - 接近測速照相時會自動提醒

3. **設定調整**
   - 調整警示距離
   - 開啟/關閉語音播報
   - 設定更新頻率

## 🗺️ 資料來源

測速照相資料來自：
- **政府資料開放平臺** - [固定式測速照相機座標資料](https://data.gov.tw/)
- 資料更新頻率：每日自動同步

## 📄 授權條款

本專案採用雙重授權模式：

### 開源使用 (AGPL v3)
- 個人使用、學習、研究
- 需遵守 AGPL v3 條款
- 修改後的程式碼必須開源

### 商業授權
- 商業應用、企業內部使用
- 不需開源修改的程式碼
- 請聯繫作者獲取商業授權

詳見 [LICENSE.txt](LICENSE.txt)

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

### 貢獻指南

1. Fork 此專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## ⚠️ 免責聲明

- 本 App 僅供輔助駕駛參考使用
- 駕駛人仍需遵守交通規則，注意路況
- 測速照相位置可能有誤差或延遲更新
- 使用本 App 不代表可以超速或違規
- 作者不對使用本 App 造成的任何後果負責

## 📧 聯絡方式

- **作者**: Chiu Wen Chung
- **Email**: cwthome@gmail.com
- **GitHub**: [@wenchung](https://github.com/wenchung)

## 💖 支持此專案

如果這個專案對你有幫助，歡迎透過 GitHub Sponsors 支持開發工作！

[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-red?logo=github&style=for-the-badge)](https://github.com/sponsors/wenchung)

### 贊助方案

#### ☕ 咖啡贊助者 - $5/月
- 在 README 中列出你的名字
- 專案更新通知
- 感謝你的支持！

#### 🌟 銅級贊助者 - $10/月
- 所有咖啡贊助者的權益
- 在專案網站上展示你的頭像
- 優先處理 Issue 回報

#### 🚀 銀級贊助者 - $25/月
- 所有銅級贊助者的權益
- 在 README 中展示你的 Logo（附連結）
- 每月專案進度報告
- 功能建議優先考慮

#### 💎 金級贊助者 - $50/月
- 所有銀級贊助者的權益
- 專屬技術諮詢（每月 1 小時）
- 客製化功能開發討論
- 特別感謝區展示

#### 🏢 企業贊助 - $100+/月
- 所有金級贊助者的權益
- 商業授權諮詢
- 企業級技術支援
- 專案合作機會
- 在所有文件中展示企業 Logo

### 目前贊助者

感謝以下贊助者的支持：

<!-- sponsors -->
_暫無贊助者，成為第一位支持者吧！_
<!-- sponsors -->

你的支持將用於：
- ⚡ 持續開發和維護
- 🐛 Bug 修復和效能優化
- 📚 文件和教學改進
- 🔐 安全性更新
- 🎨 UI/UX 改進

## 🙏 致謝

- 政府資料開放平臺提供測速照相資料
- Android 開發社群的各項開源專案
- 所有貢獻者和使用者

---

Made with ❤️ in Taiwan 🇹🇼
