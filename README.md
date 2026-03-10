# IoT-Based Predictive Maintenance System for Smart Cars

![Project Status](https://img.shields.io/badge/Status-Completed-success)
![Hardware](https://img.shields.io/badge/Hardware-Arduino%20%7C%20ESP32-blue)
![Software](https://img.shields.io/badge/Software-C++%20%7C%20Python-yellow)

> Merhaba normalde hep türkçe çalışıyorum ama bu projeyi yabancılar da inceleyebilsin ve aynı zamanda uluslararası dursun diye README'yi ingilizce hazırlamak istedim. Sırf ingilizce yazdım diye çekinmeyin, kodlar veya proje hakkında bir sorunuz olursa bana rahatça türkçe ulaşabilirsiniz. :)

## 📌 Project Overview
[cite_start]This project introduces an IoT-based Predictive Maintenance System designed for electric vehicles and autonomous mobile robots (AGVs)[cite: 14, 23]. [cite_start]Traditional reactive or preventive maintenance methods often lead to unexpected system failures, safety risks (such as battery leaks or cable fires), and a lack of historical data for root-cause analysis[cite: 16, 17, 18, 19, 20]. 

[cite_start]Our system solves these "blind flight" issues by continuously monitoring the vehicle's health using various sensors and utilizing Deep Learning (Autoencoders) to predict anomalies before mechanical or electrical failures occur[cite: 21, 299, 302].

## 📸 Project Visuals
*(Note: Ensure your image paths are correct in the repository)*
## 📸 Project Visuals
*(Note: Ensure your image paths are correct in the repository)*

![Görsel 1](<fotoğraflar/WhatsApp Image 2026-03-10 at 14.32.43.jpeg>)
![Görsel 2](<fotoğraflar/WhatsApp Image 2026-03-10 at 14.32.56.jpeg>)
![Görsel 3](<fotoğraflar/WhatsApp Image 2026-03-10 at 14.33.13.jpeg>)
![Görsel 4](<fotoğraflar/WhatsApp Image 2026-03-10 at 14.36.20.jpeg>)
![Görsel 5](<fotoğraflar/WhatsApp Image 2026-03-10 at 14.36.21.jpeg>)

## 🚀 Key Features
* [cite_start]**Predictive Maintenance (Early Warning):** Real-time monitoring of motor current and temperature to prevent part degradation[cite: 24, 25].
* [cite_start]**Operator & Fire Safety:** Millisecond-level detection of toxic gases and smoke caused by electrical arcs or battery leaks[cite: 26].
* [cite_start]**Wireless Telemetry:** Remote data monitoring from hazardous environments via Wi-Fi and Bluetooth[cite: 29, 60].
* [cite_start]**Machine Learning Anomaly Detection:** Utilizes an off-line trained Deep Learning Autoencoder model to learn normal sensor patterns and flag unusual spikes (e.g., sudden current draw or overheating)[cite: 298, 299, 304, 307].
* [cite_start]**Cloud Dashboard:** Real-time data visualization and logging using the ThingSpeak platform[cite: 170, 171].

## 🛠️ Hardware Components
* [cite_start]**Microcontrollers:** Arduino Uno R3 (Main sensor processing) & ESP32 (Wi-Fi/Cloud Telemetry)[cite: 65, 70, 71, 72].
* [cite_start]**Current Sensor:** ACS712 (30A Module) - Monitors motor load and mechanical jamming[cite: 85, 88].
* [cite_start]**Temperature & Humidity Sensor:** DHT11 - Monitors thermal stability[cite: 89, 91].
* [cite_start]**Gas & Smoke Sensor:** MQ-9 - Detects flammable gases and CO[cite: 92, 94].
* [cite_start]**Distance Sensor:** HC-SR04 Ultrasonic - Collision avoidance and spatial awareness[cite: 95, 97].
* [cite_start]**Actuators:** L298N Motor Driver, DC Motors (with reducers), 5V Relay, and Buzzer[cite: 98, 149, 153, 157, 160].

## 💻 Software & Technologies
* [cite_start]**C++ / Arduino IDE:** For sensor data acquisition and hardware control[cite: 103, 104].
* [cite_start]**Python (TensorFlow / Keras):** Used for training the Autoencoder model for anomaly detection[cite: 315].
* [cite_start]**ThingSpeak:** Cloud database and real-time dashboard UI[cite: 170, 269].

## 📊 How It Works
1.  [cite_start]**Data Acquisition:** Sensors collect environmental and operational data (current, temp, gas, distance)[cite: 343].
2.  [cite_start]**Processing & Transmission:** Arduino processes the raw data (using smoothing algorithms) and sends it to the ESP32[cite: 70, 80, 111].
3.  [cite_start]**Cloud Logging:** ESP32 pushes the data to the ThingSpeak cloud database in real-time[cite: 83, 270].
4.  **Anomaly Detection:** A Python script evaluates the incoming data against the pre-trained Autoencoder model. [cite_start]If the reconstruction error exceeds the threshold, an alert is triggered[cite: 307, 321, 323, 324].
5.  [cite_start]**Feedback:** The user receives automatic warnings via email (ThingSpeak React) or terminal alerts[cite: 345, 346, 347].

## 👥 Team
* [cite_start]Dilay Göbel, Yusuf Küçük, Dilara Yaman, Abdullah Özdin, Nisa Nur Ceran [cite: 2, 3, 4, 5, 6]
* [cite_start]Esra Ersoy, Bengisu Özkaya, Elif Refika Maraş, Meryem Doğan, Gülseren İnce [cite: 7, 8, 9, 10, 11]
