#include <DHT.h>
#include <SoftwareSerial.h>

// Sensör verisini terminale basalım mı?
// 1 = EVET (sürekli akar), 0 = HAYIR (sadece komut var)
#define ENABLE_SENSOR_STREAM 1

// ================= AUTO MODE AYARLARI =================
#define ENABLE_AUTO_DRIVE 1   // 0 = sadece karar yaz (motor sürme), 1 = motor sür

enum Mode { MANUAL, AUTO, PAUSE };
Mode mode = MANUAL;

const int  MIN_DIST_CM   = 20;   // Engel eşiği (cm)
const int  AUTO_TICK_MS  = 200;  // Auto karar periyodu (ms)
unsigned long lastAutoTick = 0;


/*
  PIN PLANI (GÜNCEL)
  ------------------

  DHT11 Isı & Nem Sensörü
    DATA -> D2

  Ultrasonik HC-SR04 (hareket / mesafe sensörü)
    TRIG -> D3
    ECHO -> D4
    VCC  -> 5V
    GND  -> GND

  4'lü Çizgi Sensörü
    S1   -> D5
    S2   -> D6
    S3   -> D7
    S4   -> D8
    VCC  -> 5V
    GND  -> GND

  Işık Sensörü (MH Sensor Series, 4 pin: AO, DO, GND, VCC)
    AO   -> A0
    DO   -> Kullanılmıyor
    VCC  -> 5V
    GND  -> GND

  MQ-9 Duman / Gaz Sensörü
    AO   -> A1
    VCC  -> 5V
    GND  -> GND

  ACS712 Akım Sensörü
    OUT  -> A2
    VCC  -> 5V
    GND  -> GND

  Bluetooth HC-05
    TX   -> D10  (Arduino RX)
    RX   -> D11  (Arduino TX) [gerekirse 1K dirençle]
    VCC  -> 5V
    GND  -> GND

  Röle + Buzzer
    Röle IN  -> D12
    Röle VCC -> 5V
    Röle GND -> GND

    Buzzer + -> Röle NO
    Buzzer - -> GND
    Röle COM -> 5V

  L298N Motor Sürücü
    IN1 -> D9   (Sağ motor)
    IN2 -> A3   (Sağ motor)
    IN3 -> A4   (Sol motor)
    IN4 -> A5   (Sol motor)

    OUT1-OUT2 -> Sağ motor uçları
    OUT3-OUT4 -> Sol motor uçları

    +12V -> Pil + (9-12V)
    GND  -> Pil GND
    Arduino GND -> Pil GND (ORTAK GND ŞART)
*/

// ================= DHT11 =================
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// ================= SENSOR PINLERI =================
const int TRIG_PIN   = 3;   // HC-SR04 TRIG
const int ECHO_PIN   = 4;   // HC-SR04 ECHO

const int S1_PIN     = 5;   // Çizgi sensörü
const int S2_PIN     = 6;
const int S3_PIN     = 7;
const int S4_PIN     = 8;

const int LIGHT_PIN  = A0;  // Işık sensörü AO
const int MQ9_PIN    = A1;  // Duman sensörü AO
const int ACS_PIN    = A2;  // ACS712 OUT

// ================= ROLE / DEBUG LED =================
const int ROLE_PIN   = 13;          // Röle
const int LED_DBG    = LED_BUILTIN; // D13 onboard LED

// ================= MOTOR PINLERI (L298N) =================
const int IN1 = 9;    // Sağ motor
const int IN2 = A3;   // Sağ motor
const int IN3 = A4;   // Sol motor
const int IN4 = A5;   // Sol motor

// ================= BLUETOOTH (HC-05) =================
const int BT_RX_PIN = 10; // Arduino RX  (HC-05 TX)
const int BT_TX_PIN = 11; // Arduino TX  (HC-05 RX)
SoftwareSerial BTSerial(BT_RX_PIN, BT_TX_PIN);

// ================= ACS712 ayarlari =================
const float ACS_OFFSET      = 2.5;
const float ACS_SENSITIVITY = 0.185;
const int   ACS_SAMPLES     = 30;

// ================= SENSOR PERIYODU =================
unsigned long lastSensorTime   = 0;
const unsigned long SENSOR_PERIOD = 1000;

// --------------------------------------------------------------------
// ORTAK CIKTI FONKSIYONU
// --------------------------------------------------------------------
void sendLine(const String &s) {
  Serial.println(s);
  BTSerial.println(s);
}

// --------------------------------------------------------------------
// AKIM OKUMA (ACS712)
// --------------------------------------------------------------------
float readCurrentACS712(float *rawOut) {
  long total = 0;
  for (int i = 0; i < ACS_SAMPLES; i++) {
    total += analogRead(ACS_PIN);
    delayMicroseconds(200);
  }

  float avg = (float)total / ACS_SAMPLES;
  if (rawOut != NULL) {
    *rawOut = avg;
  }

  float voltage = avg * (5.0 / 1023.0);
  float diff    = voltage - ACS_OFFSET;
  float current = diff / ACS_SENSITIVITY;
  if (current < 0) current = -current;

  return current;
}

// --------------------------------------------------------------------
// ULTRASONIK MESAFE OKUMA (HC-SR04) [cm olarak]
// --------------------------------------------------------------------
long readDistanceCm() {
  // TRIG'e kısa bir puls verelim
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // ECHO'dan süreyi ölç
  long duration = pulseIn(ECHO_PIN, HIGH, 30000UL); // 30ms timeout

  if (duration == 0) {
    return -1; // ölçüm yok
  }

  long distance = duration * 0.034 / 2; // ses hızı yaklaşık 0.034 cm/us
  return distance;
}
// --------------------------------------------------------------------
// AUTO MODE TICK (Karar motoru)
// --------------------------------------------------------------------
void autoTick() {
  long d = readDistanceCm();

  if (d < 0) {
    sendLine("AUTO: NO_DISTANCE -> STOP");
#if ENABLE_AUTO_DRIVE
    stopMotors();
#endif
    return;
  }

  if (d > MIN_DIST_CM + 15) {
    sendLine("AUTO: FORWARD dist=" + String(d));
#if ENABLE_AUTO_DRIVE
    forward();
#endif
  } else if (d >= MIN_DIST_CM) {
    sendLine("AUTO: CAUTION dist=" + String(d) + " -> FORWARD");
#if ENABLE_AUTO_DRIVE
    forward();
#endif
  } else {
    sendLine("AUTO: AVOID dist=" + String(d) + " -> STOP/BACK/TURN_RIGHT");
#if ENABLE_AUTO_DRIVE
    stopMotors();
    delay(80);
    backward();
    delay(300);
    stopMotors();
    delay(80);
    turnRight();
    delay(450);   // 90 dereceyi sonra kalibre edeceğiz
    stopMotors();
#endif
  }
}
// --------------------------------------------------------------------
// MOTOR FONKSIYONLARI
// --------------------------------------------------------------------
void stopMotors() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

void forward() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void backward() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void turnLeft() {
  // Sağ motor ileri, sol motor geri
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void turnRight() {
  // Sağ motor geri, sol motor ileri
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

// --------------------------------------------------------------------
// ALARM (RÖLE + BUZZER)
// --------------------------------------------------------------------
void alarmOn() {
  digitalWrite(ROLE_PIN, HIGH);
}

void alarmOff() {
  digitalWrite(ROLE_PIN, LOW);
}

// --------------------------------------------------------------------
// KOMUT ISLEME (Hem BT, hem PC buraya düşer)
// --------------------------------------------------------------------
void handleCommand(char c) {
  // Enter / newline vs. gelirse ignore
  if (c == '\r' || c == '\n') return;

  String info = "Komut alindi: ";
  info += c;
  sendLine(info);
    // ====== MODE KOMUTLARI ======
  if (c == 'A' || c == 'a') {
    mode = AUTO;
    sendLine("MODE -> AUTO");
    return;
  }
  if (c == 'M' || c == 'm') {
    mode = MANUAL;
    sendLine("MODE -> MANUAL");
    return;
  }
  if (c == 'P' || c == 'p') {
    mode = PAUSE;
    stopMotors();
    sendLine("MODE -> PAUSE (STOP)");
    return;
  }


  // Debug LED ping
  //digitalWrite(LED_DBG, HIGH);
  //delay(50);
  //digitalWrite(LED_DBG, LOW);

  switch (c) {
    case 'F':
    case 'f':
      forward();
      break;

    case 'B':
    case 'b':
      backward();
      break;

    case 'R':
    case 'r':
      turnLeft();
      break;

    case 'L':
    case 'l':
      turnRight();
      break;

    case 'S':
    case 's':
      stopMotors();
      break;

    case 'Q':
    case 'q':
      alarmOn();
      break;

    case 'H':
    case 'h':
      alarmOff();
      break;

    default:
      sendLine("Bilinmeyen komut.");
      break;
  }
}

// --------------------------------------------------------------------
// SENSORLERI OKU VE YOLLA
// --------------------------------------------------------------------
void readAndSendSensors() {
#if ENABLE_SENSOR_STREAM
  // DHT11
  float temperature = dht.readTemperature();
  float humidity    = dht.readHumidity();
  if (isnan(temperature)) temperature = -1;
  if (isnan(humidity))    humidity = -1;

  // Işık
  int lightRaw = analogRead(LIGHT_PIN);

  // Duman / Gaz (MQ-9)
  int mq9Raw   = analogRead(MQ9_PIN);

  // Ultrasonik mesafe
  long distance = readDistanceCm();

  // Çizgi sensörleri
  int s1 = digitalRead(S1_PIN);
  int s2 = digitalRead(S2_PIN);
  int s3 = digitalRead(S3_PIN);
  int s4 = digitalRead(S4_PIN);

  // Akım
  float acsRaw;
  float current = readCurrentACS712(&acsRaw);

  sendLine("===== SENSOR VERILERI =====");
  sendLine("Sicaklik   : " + String(temperature, 1) + " C");
  sendLine("Nem        : " + String(humidity, 1)    + " %");
  sendLine("Isik (A0)  : " + String(lightRaw));
  sendLine("Gaz (MQ9)  : " + String(mq9Raw));

  if (distance >= 0) {
    sendLine("Mesafe     : " + String(distance) + " cm");
  } else {
    sendLine("Mesafe     : OLÇÜM YOK");
  }

  String lineStr = "Cizgi      : S1=" + String(s1) +
                   " S2=" + String(s2) +
                   " S3=" + String(s3) +
                   " S4=" + String(s4);
  sendLine(lineStr);

  sendLine("ACS RAW    : " + String(acsRaw, 1));
  sendLine("Akim       : " + String(current, 3) + " A");
  sendLine("----------------------------");
  sendLine("");
#endif
}

// --------------------------------------------------------------------
// SETUP
// --------------------------------------------------------------------
void setup() {
  pinMode(LED_DBG, OUTPUT);
  digitalWrite(LED_DBG, LOW);

  Serial.begin(9600);
  BTSerial.begin(9600);
  dht.begin();

  // Ultrasonik
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // Çizgi sensörleri
  pinMode(S1_PIN, INPUT);
  pinMode(S2_PIN, INPUT);
  pinMode(S3_PIN, INPUT);
  pinMode(S4_PIN, INPUT);

  // Röle
  pinMode(ROLE_PIN, OUTPUT);
  alarmOff();

  // Motor pinleri
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  stopMotors();

  delay(1000);
  sendLine("FINAL ARABA SISTEMI BASLADI (YENI PIN PLANI)");
  sendLine("Komutlar (PC veya Bluetooth):");
  sendLine("F,B,L,R,S  -> Hareket");
  sendLine("H          -> Alarm ON");
  sendLine("Q          -> Alarm OFF");
  sendLine("---------------------------------------------");
}

// --------------------------------------------------------------------
// LOOP
// --------------------------------------------------------------------
void loop() {
  unsigned long now = millis();

  // 1) Sensör verileri
  if (ENABLE_SENSOR_STREAM) {
    if (now - lastSensorTime >= SENSOR_PERIOD) {
      readAndSendSensors();
      lastSensorTime = now;
    }
  }

  // 2) Bluetooth'tan gelen komutlar
  if (BTSerial.available()) {
    char c = BTSerial.read();
    handleCommand(c);
  }

  // 3) PC (USB - Tera Term) üzerinden gelen komutlar
  if (Serial.available()) {
    char c = Serial.read();
    handleCommand(c);
  }
    // 4) AUTO MODE çalıştırma
  if (mode == AUTO) {
    unsigned long now2 = millis();
    if (now2 - lastAutoTick >= AUTO_TICK_MS) {
      autoTick();
      lastAutoTick = now2;
    }
  } else if (mode == PAUSE) {
    // Güvenlik: sürekli stop
    stopMotors();
  }

}