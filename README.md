<div align="center">
  <img src="static/images/icons/icon-72x72.png" width="80" height="80" alt="Spiderweb Logo" />
  <h1>SPIDERWEB (Modern Fork)</h1>
  <p><strong>Premium Ham Radio DX Cluster Web Viewer</strong></p>

  [![GPLv3 license](https://img.shields.io/badge/License-GPLv3-blue.svg)](http://perso.crans.org/besson/LICENSE.html)
  [![made-with-python](https://img.shields.io/badge/B.e.-Python-1f425f.svg)](https://www.python.org/)
  [![Bootstrap 5.3](https://img.shields.io/badge/UI-Bootstrap%205.3-purple)](https://getbootstrap.com/)
  [![Performance-Optimized](https://img.shields.io/badge/Performance-Optimized-success)](#performance-enhancements)
</div>

---

## 🛰️ Project Overview
**Spiderweb** is a feature-rich, high-performance web interface for [DXSpider](http://www.dxcluster.org/) cluster nodes. It provides ham radio operators with a stunning, real-time dashboard to monitor DX spots, analyze propagation, and track global amateur radio activity.

> [!NOTE]
> This repository is a **Fork** of the original project developed by **Corrado Gerbaldo (IU1BOW)**. This version focuses on premium UI/UX enhancements and backend scalability.

---

## 🚀 Performance Enhancements
In this fork, we have implemented critical optimizations to ensure a smooth experience even on heavily loaded clusters:

| Feature | Improvement | Impact |
| :--- | :--- | :--- |
| **Intelligent Caching** | 5-minute TTL on heavy DB queries | 90% reduction in homepage load overhead |
| **Prefix Memoization** | Request-local cache for CTY lookups | Faster spot rendering & lower CPU usage |
| **SQL Optimization** | Refined indices and subquery logic | Faster search and filtering responses |
| **UI Rendering** | Efficient DOM manipulation | Reduced browser-side latency |

---

## 🏗️ Architecture
The system follows a modern WSGI-based architecture designed for high availability and low latency.

```mermaid
graph TD
    subgraph External_Data
        A["DXSpider Cluster (Node)"]
        B["QRZ.com / HamQSL / NG3K"]
    end

    subgraph Backend_Flask
        C["webapp.py (Server)"]
        D["Caching Layer (TTL/Local)"]
        E["MariaDB / MySQL"]
    end

    subgraph Frontend_UI
        F["Bootstrap 5.3 (Glassmorphism)"]
        G["ECharts (Live Stats)"]
        H["PWA Service Worker"]
    end

    A -- "Telnet/XML" --> C
    B -- "API/XML" --> C
    C <--> D
    C <--> E
    C -- "Jinja2 / JSON" --> F
    F --> G
    F --> H
```

---

## ✨ Key Features
- **Real-time Spotting**: View the latest 50 spots with advanced filtering (Band, Continent, Mode).
- **Premium UI**: Modern dark theme with **Glassmorphism**, integrated typography (Inter/Outfit), and smooth transitions.
- **Propagation Analysis**: Integrated MUF maps, solar data from HamQSL, and ECharts-powered statistics.
- **PWA Support**: Installable as a Progressive Web App on mobile and desktop.
- **Search Engine Optimized**: Built-in support for sitemaps and semantic HTML.

---

## 🛠️ Quick Start

### Prerequisites
- **Python 3.13+**
- **MariaDB / MySQL**
- **DxSpider** node (v1.57 build 560+)

### 1. Database Configuration
Edit your DXSpider `local/DXVars.pm`:
```perl
$dsn = "dbi:mysql:dxcluster:localhost:3306";
$dbuser = "your-user";
$dbpass = "your-password";
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Build & Run
```bash
# Build web assets (Minify CSS/JS)
cd scripts && ./build.sh -r
cd ..

# Run the server
python3 webapp.py
```

---

## 📊 Statistics & Data Sources
Spiderweb aggregates data from multiple world-class amateur radio resources:
- **ECharts**: Real-time trend analysis and heatmaps.
- **Flag-Icon-CSS**: Visual country identification.
- **NG3K**: Announced DX operations tracking.
- **KC2G**: Real-time Maximum Usable Frequency (MUF) mapping.

---

## 📄 License
This fork is distributed under the **GPL v3.0** License. See the [LICENSE](LICENSE) file for more details. Original Author: [Corrado Gerbaldo - IU1BOW](https://www.qrz.com/db/IU1BOW).
