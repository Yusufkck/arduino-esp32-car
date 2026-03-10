from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

# Arabaya gidecek son komut
# F = ileri, S = dur, B = geri, R = sağ, L = sol,
# Q = buzzer sustur, H = buzzer çalıştır, N = komut yok
# A = auto mode, M = manual mode, P = pause/stop

LAST_COMMAND = "S"   # Başlangıçta araba dursun

lock = threading.Lock()

VALID_COMMANDS = ["F", "S", "B", "R", "L", "Q", "H", "N", "A", "M", "P"]



@app.route("/telemetry", methods=["POST"])
def telemetry():
    """
    ESP32 buraya sensör verisini POST ile gönderiyor.
    Body: {"raw":"TEMP=23.4;HUM=40;LIGHT=300;GAS=150;DIST=20;CURR=0.1"}
    """
    data = request.get_json()
    if not data or "raw" not in data:
        return jsonify({"error": "raw field yok"}), 400

    raw = data["raw"]
    print("\n[GELEN TELEMETRI RAW]:", raw)

    # İstersen ileride parsed ile otomatik karar motoru yazarsın:
    parsed = {}
    try:
        parts = raw.split(";")
        for p in parts:
            if "=" in p:
                k, v = p.split("=")
                parsed[k] = float(v)
        print("[AYRISTIRILMIS VERI]:", parsed)
    except Exception as e:
        print("[Parse hatasi]:", e)

    # Şimdilik sadece logluyoruz
    return jsonify({"status": "ok"})


@app.route("/command", methods=["GET"])
def command():
    """
    ESP32, son komutu buradan çeker.

    ÖNEMLİ:
    - ESP32 şu formatı bekliyor: {"cmd":"F"}
    - O yüzden JSON dönüyoruz.
    """
    with lock:
        cmd_to_send = LAST_COMMAND

    print("[ESP32 komut istedi] → GÖNDERİLEN cmd:", cmd_to_send)

    # ESP32'nin parse ettiği format: {"cmd":"F"}
    return jsonify({"cmd": cmd_to_send})


@app.route("/set_command", methods=["GET"])
def set_command():
    """
    İstersen URL ile de komut verebilirsin:
    Örnek: http://PC_IP:8000/set_command?cmd=F
    """
    global LAST_COMMAND

    cmd = request.args.get("cmd", "")
    cmd = cmd.strip().upper()

    if cmd not in VALID_COMMANDS:
        print("[GEÇERSİZ KOMUT ISTEGI - HTTP]:", repr(cmd))
        return jsonify({"error": "gecersiz komut", "valid": VALID_COMMANDS}), 400

    with lock:
        LAST_COMMAND = cmd

    print("[MANUEL KOMUT AYARLANDI - HTTP] →", LAST_COMMAND)
    return jsonify({"status": "ok", "cmd": LAST_COMMAND})


def console_command_loop():
    """
    Bu fonksiyon AYRI BİR THREAD içinde çalışıyor.
    Terminalden komut yazmana izin veriyor.
    """
    global LAST_COMMAND

    print("\n[KLAVYE KONTROL HAZIR]")
    print("Geçerli komutlar:", VALID_COMMANDS)
    print("Örnek: F (ileri), S (dur), B (geri), R (sağ), L (sol), Q (buzzer off), H (buzzer on), N (komut yok)\n")

    while True:
        try:
            user_input = input("Komut gir (F/S/B/R/L/Q/H/N): ")
        except EOFError:
            print("\n[KLAVYE OKUMA BITTI]")
            break

        cmd = user_input.strip().upper()

        if cmd == "":
            continue

        if cmd not in VALID_COMMANDS:
            print("[HATA] Geçersiz komut girdin:", repr(cmd))
            print("Geçerli komutlar:", VALID_COMMANDS)
            continue

        with lock:
            LAST_COMMAND = cmd

        print("[MANUEL KOMUT AYARLANDI - KLAVYE] →", LAST_COMMAND)


if __name__ == "__main__":
    print("[SERVER] Flask + Console Bridge baslatiliyor...")

    # Klavyeden komut okuyacak thread
    t = threading.Thread(target=console_command_loop)
    t.daemon = True
    t.start()

    print("[SERVER] Flask dinlemede: 0.0.0.0:8000")
    # Windows'ta en stabil ayar: debug=False, use_reloader kullanmıyoruz
    app.run(host="0.0.0.0", port=8000, debug=False)



