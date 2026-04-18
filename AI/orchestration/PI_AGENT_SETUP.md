# Raspberry Pi Agent Kurulumu

Bu kurulum kullanıcı seviyesinde çalışır; `sudo` gerekmeden `systemd --user`
ile ajan döngüsü başlatılabilir.

## 1. Sanal ortam

```bash
cd ~/Projeler/CNCRevizyon
source .venv/bin/activate
```

## 2. Ortam değişkeni dosyası

```bash
mkdir -p ~/.config/cnc-pi-agent
cat > ~/.config/cnc-pi-agent/env <<'EOF'
DASHSCOPE_API_KEY=buraya_key
PI_AGENT_INTERVAL=20
AI_ORCHESTRATOR_CONFIG=/home/oktay/Projeler/CNCRevizyon/AI/orchestration/orchestrator_config.json
EOF
```

`DASHSCOPE_API_KEY` varsa ajan, config dosyasındaki anahtarı bununla ezer.

## 3. User service kurulumu

```bash
mkdir -p ~/.config/systemd/user
cp ~/Projeler/CNCRevizyon/AI/orchestration/systemd-user/cnc-pi-agent.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now cnc-pi-agent.service
loginctl enable-linger "$USER"
```

## 4. Durum komutları

```bash
systemctl --user status cnc-pi-agent.service
journalctl --user -u cnc-pi-agent.service -n 100 --no-pager
```

## 5. Hedef gönderme

```bash
cd ~/Projeler/CNCRevizyon
source .venv/bin/activate
python AI/orchestration/pi_agent_submit.py \
  --title "EtherCAT risk analizi" \
  --prompt "NC300 ve EtherCAT tarafı için kısa risk analizi yap." \
  --task-type review \
  --mode aggregate
```

Simülatör testi için:

```bash
python AI/orchestration/pi_agent_submit.py \
  --title "Simülatör sağlık kontrolü" \
  --prompt "NC300 simülatörünü test et" \
  --goal-type simulator_check
```

## 6. Çıktılar

- Kuyruk: `AI/orchestration/runtime/goals.json`
- Sonuçlar: `AI/orchestration/runtime/results/*.json`
