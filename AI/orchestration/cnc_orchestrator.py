#!/usr/bin/env python3
"""
CNC Cam Kesme Makinesi - AI Model Orchestrator

Bu script, Alibaba Cloud DashScope AI modellerini CNC makinesi projeleri için
özelleştirilmiş promptlar ile kullanır.

Kullanım:
    python cnc_orchestrator.py --task code           # Kod yazdır
    python cnc_orchestrator.py --task design         # Tasarım önerisi
    python cnc_orchestrator.py --task optimize       # Optimizasyon
    python cnc_orchestrator.py --task debug          # Hata ayıklama
    python cnc_orchestrator.py --task plc            # PLC/EtherCAT
    python cnc_orchestrator.py --task cam            # E-Cam profili
    python cnc_orchestrator.py --custom "Soru"       # Özel soru
"""

import asyncio
import aiohttp
import json
import argparse
import ssl
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


# =============================================================================
# PROJE BAĞLAMI - LiSEC GFB-60/30RE CNC Cam Kesme Makinesi
# =============================================================================

PROJECT_CONTEXT = """
PROJE: LiSEC GFB-60/30RE Cam Kesme Makinesi Revizyonu

TEKNİK ÖZELLİKLER:
- Maksimum Cam Boyutu: 6000 x 3000 mm
- Kesim Hızı: 0-80 m/dk
- Hassasiyet: ±0.05 mm (24-bit encoder)
- Eksen Sayısı: 5 (X, Y, Z, Alt, CNC/Rodaj)
- EtherCAT Cycle Time: 100 μs

KONTROL SİSTEMİ:
- CNC: Delta NC300 (EtherCAT Master, G-kod işleme)
- Servo Sürücü: Delta ASDA-A3-E (EtherCAT, 100μs cycle)
- HMI: Delta DOP-110CS (10.1" Touch)
- Uzak I/O: Delta R1-EC (EtherCAT Slave)

SERVO MOTORLAR:
- X Ekseni: ECMA-L11845 (4.5kW, Yüksek Atalet) - Portal hareketi
- Y Ekseni: ECMA-E11320 (2.0kW, Orta Atalet) - Kesim kafası köprü
- Z Ekseni: ECMA-C11010 (1.0kW, Frenli) - Kesim kafası iniş/kalkış
- Alt Eksen: ECMA-E11320 (2.0kW) - Lamine kesim E-Cam
- CNC Eksen: ECMA-E11315 (1.5kW, IP67) - Rodaj/Profil kesim

GÜVENLİK:
- STO (Safe Torque Off) sistemi
- Pilz PNOZ güvenlik rölesi
- Acil durdurma devresi
"""

# =============================================================================
# GÖREV TANIMLARI - Özelleştirilmiş Promptlar
# =============================================================================

TASK_PROMPTS = {
    "code": {
        "name": "Kod Yazma",
        "description": "Python, FreeCAD, NC programı kodları yazdırır",
        "system_prompt": """Sen endüstriyel CNC otomasyon sistemleri konusunda uzman bir yazılım mühendisisin.
LiSEC GFB-60/30RE cam kesme makinesi üzerinde çalışıyoruz.

YANIT PRENSİPLERİ:
1. Kod her zaman çalıştırılabilir ve test edilmiş olmalı
2. Endüstriyel güvenlik standartlarına uygun olmalı (STO, acil durdurma)
3. EtherCAT 100μs cycle time'a uygun olmalı
4. Hata yönetimi eksiksiz olmalı
5. Türkçe yorum satırları ekle

KULLANILAN TEKNOLOJİLER:
- Delta NC300 CNC (G-kod, PLC)
- Delta ASDA-A3-E EtherCAT servo
- Python 3.10+
- FreeCAD Assembly4""",
        "user_prompt_template": """Aşağıdaki görevi yerine getir:

{task}

PROJE BAĞLAMI:
{context}"""
    },
    
    "design": {
        "name": "Tasarım Önerisi",
        "description": "Mekanik tasarım ve CAD önerileri",
        "system_prompt": """Sen endüstriyel makine tasarımı konusunda uzman bir makine mühendisisin.
FreeCAD ve Assembly4 konusunda derin bilgiye sahipsin.

TASARIM PRENSİPLERİ:
1. Modüler tasarım (kolay bakım için)
2. Profil alüminyum gövde (80x80 veya 120x120)
3. HIWIN lineer kılavuz sistemleri (HGH25/HGH30)
4. Motor seçiminde güvenlik faktörü 1.5
5. Kablolama kanalları ve kablo tankı tasarımı

DİKKAT EDİLECEKLER:
- Kesim kafası ağırlığı: ~15kg
- Portal hızı: 80m/dk maksimum
- Titreşim analizi önemli
- Termal genleşme hesaba katılmalı""",
        "user_prompt_template": """Aşağıdaki tasarım sorununu çöz:

{task}

MEVCUT SİSTEM:
{context}"""
    },
    
    "optimize": {
        "name": "Optimizasyon",
        "description": "Kesim yolu, hız ve verimlilik optimizasyonu",
        "system_prompt": """Sen üretim optimizasyonu ve yapay zeka tabanlı algoritma uzmanısın.
Cam kesme endüstrisinde 20 yıllık deneyimin var.

OPTİMİZASYON HEDEFLERİ:
1. Minimum fire (cam israfı)
2. Minimum kesim süresi
3. Maksimum kesim kalitesi
4. Enerji verimliliği
5. Takım ömrü uzatma

KULLANILABİLECEK ALGORİTMALAR:
- Genetic Algorithm (GA)
- Particle Swarm Optimization (PSO)
- Simulated Annealing
- Dynamic Programming
- Bin Packing Problem çözümleri""",
        "user_prompt_template": """Aşağıdaki optimizasyon problemini çöz:

{task}

MAKİNE KISITLARI:
{context}"""
    },
    
    "debug": {
        "name": "Hata Ayıklama",
        "description": "Sistem hatalarını analiz et ve çözüm öner",
        "system_prompt": """Sen endüstriyel otomasyon sistemleri hata ayıklama uzmanısın.
Delta Electronics ürünleri konusunda sertifikalı teknisyensin.

HATA AYIKLAMA METODOLOJİSİ:
1. Hata kodunu analiz et
2. EtherCAT network durumunu kontrol et
3. Servo parametrelerini incele
4. I/O durumlarını kontrol et
5. Mekanik bağları gözden geçir

OLASI HATA NEDENLERİ:
- EtherCAT通信 hatası (Al, Err LED)
- Servo alarm (hata kodları)
- Limit switch tetikleme
- STO aktif
- Encoder zayıf sinyal
- Kablo hasarı""",
        "user_prompt_template": """Aşağıdaki hatayı analiz et ve çözüm öner:

{task}

SİSTEM DURUMU:
{context}"""
    },
    
    "plc": {
        "name": "PLC/EtherCAT",
        "description": "Delta NC300 PLC ve EtherCAT konfigürasyonu",
        "system_prompt": """Sen Delta Electronics PLC ve EtherCAT network uzmanısın.
NC300, ASDA-A3-E ve R1-EC sistemlerinde sertifikalisin.

ETHERCAT CONFIGURATION:
- Cycle Time: 100μs
- Sync Mode: DC (Distributed Clock)
- PDO mapping doğru yapılandırılmalı
- CoE (CAN over EtherCAT) kullanılıyor

NC300 PLC:
- Ladder ve Structured Text destekleniyor
- High-speed interrupt handling
- E-Cam table yönetimi
- G-kod interpreter entegrasyonu

GÜVENLİK:
- STO devresi öncelikli
- Emergency stop Category 0
- Guard lock monitoring""",
        "user_prompt_template": """Aşağıdaki PLC/EtherCAT görevini yerine getir:

{task}

MEVCUT NETWORK:
{context}"""
    },
    
    "cam": {
        "name": "E-Cam Profili",
        "description": "Lamine kesim için elektronik kam profili tasarımı",
        "system_prompt": """Sen E-Cam (Elektronik Kam) profil tasarımı uzmanısın.
Lamine cam kesme uygulamalarında derin bilgiye sahipsin.

E-CAM TASARIM PRENSİPLERİ:
1. Ana eksen (X) ile kesim ekseni senkronizasyonu
2. Hız profili: trapezoidal veya S-kurve
3. Cam kalınlığına göre penetrasyon derinliği
4. Lamine PVB tabakası için özel profil
5. Dönüş noktasında yumuşak geçiş

PROFİL PARAMETRELERİ:
- Cam kalınlığı: 2-25mm
- Kesim hızı: 0-80 m/dk
- Penetrasyon: cam kalınlığı + 0.5mm
- Return speed: maksimum hızlı""",
        "user_prompt_template": """Aşağıdaki E-Cam profilini tasarla:

{task}

KESİM PARAMETRELERİ:
{context}"""
    },
    
    "gcode": {
        "name": "G-Kod Programı",
        "description": "Delta NC300 için G-kod programı oluştur",
        "system_prompt": """Sen CNC G-kod programlama uzmanısın.
Delta NC300 kontrolöründe 15 yıllık deneyimin var.

G-KOD STANDARTLARI:
- ISO 6983 uyumlu
- Delta özel kodları (G10, G28, G30)
- Döngüler (G81-G89)
- Telafi (G41, G42, G40)
- Koordinat sistemleri (G54-G59)

NC300 ÖZEL KODLARI:
- G10: Veri seti
- G28: Referans dönüş
- G30: 2. referans dönüş
- G92: Koordinat sistemi preset
- M kodları: Makine özel fonksiyonları""",
        "user_prompt_template": """Aşağıdaki parça için G-kod programı yaz:

{task}

PARÇA ÖZELLİKLERİ:
{context}"""
    },
    
    "safety": {
        "name": "Güvenlik Sistemi",
        "description": "STO ve makine güvenliği analizi",
        "system_prompt": """Sen makine güvenliği ve fonksiyonel güvenlik uzmanısın.
ISO 13849-1 ve IEC 62061 sertifikalı mühendisisin.

GÜVENLİK STANDARTLARI:
- ISO 13849-1: PL d/e seviyesi
- IEC 62061: SIL 2/3
- ISO 14119: Koruyucu cihazlar
- ISO 13850: Acil durdurma

STO (Safe Torque Off):
- Category 0 duruş
- Pilz PNOZ güvenlik rölesi
- Dual-channel tasarım
- EDM (External Device Monitoring)""",
        "user_prompt_template": """Aşağıdaki güvenlik analizini yap:

{task}

MEVCUT GÜVENLİK SİSTEMİ:
{context}"""
    }
}


@dataclass
class ModelConfig:
    """Model yapılandırma sınıfı"""
    model_id: str
    api_key: str
    api_endpoint: str = "https://coding-intl.dashscope.aliyuncs.com/v1"
    temperature: float = 0.7
    max_tokens: int = 4096
    system_prompt: str = ""


@dataclass
class ModelResponse:
    """Model yanıt sınıfı"""
    model_id: str
    content: str
    status: str
    latency_ms: float
    error: Optional[str] = None
    timestamp: str = ""
    tokens_used: int = 0
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class DashScopeClient:
    """DashScope API istemcisi"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate(
        self, 
        messages: List[Dict], 
        session: aiohttp.ClientSession
    ) -> ModelResponse:
        """Model yanıtı üret"""
        start_time = datetime.now()
        
        payload = {
            "model": self.config.model_id,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
        
        try:
            # SSL sertifika doğrulamasını gevşet (macOS için)
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as secure_session:
                async with secure_session.post(
                    f"{self.config.api_endpoint}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    latency = (datetime.now() - start_time).total_seconds() * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                        usage = data.get("usage", {})
                        return ModelResponse(
                            model_id=self.config.model_id,
                            content=content,
                            status="success",
                            latency_ms=latency,
                            tokens_used=usage.get("total_tokens", 0)
                        )
                    else:
                        error_text = await response.text()
                        return ModelResponse(
                            model_id=self.config.model_id,
                            content="",
                            status="error",
                            latency_ms=latency,
                            error=f"HTTP {response.status}: {error_text}"
                        )
        except asyncio.TimeoutError:
            return ModelResponse(
                model_id=self.config.model_id,
                content="",
                status="timeout",
                latency_ms=(datetime.now() - start_time).total_seconds() * 1000,
                error="Request timeout (120s)"
            )
        except Exception as e:
            return ModelResponse(
                model_id=self.config.model_id,
                content="",
                status="error",
                latency_ms=(datetime.now() - start_time).total_seconds() * 1000,
                error=str(e)
            )


class CNCAIOrchestrator:
    """CNC Projesi için AI Orkestratör"""
    
    def __init__(self, configs: List[ModelConfig]):
        self.configs = configs
        self.clients = [DashScopeClient(config) for config in configs]
        self.project_context = PROJECT_CONTEXT
    
    def _create_messages(
        self, 
        task_config: Dict, 
        user_task: str
    ) -> List[Dict]:
        """API için mesaj formatı oluştur"""
        messages = []
        
        # System prompt
        system_prompt = task_config["system_prompt"]
        messages.append({"role": "system", "content": system_prompt})
        
        # User prompt with context
        user_prompt = task_config["user_prompt_template"].format(
            task=user_task,
            context=self.project_context
        )
        messages.append({"role": "user", "content": user_prompt})
        
        return messages
    
    async def run_task(
        self,
        task_type: str,
        user_task: str,
        model_indices: Optional[List[int]] = None
    ) -> List[ModelResponse]:
        """Belirli bir görev tipini çalıştır"""
        if task_type not in TASK_PROMPTS:
            raise ValueError(f"Bilinmeyen görev tipi: {task_type}")
        
        task_config = TASK_PROMPTS[task_type]
        messages = self._create_messages(task_config, user_task)
        
        if model_indices is None:
            model_indices = list(range(len(self.clients)))
        
        selected_clients = [self.clients[i] for i in model_indices]
        
        async with aiohttp.ClientSession() as session:
            tasks = [client.generate(messages, session) for client in selected_clients]
            responses = await asyncio.gather(*tasks)
            return list(responses)
    
    async def run_parallel(
        self,
        task_type: str,
        user_task: str,
        model_indices: Optional[List[int]] = None
    ) -> List[ModelResponse]:
        """Paralel çalıştırma - tüm modeller aynı görevi yapar"""
        return await self.run_task(task_type, user_task, model_indices)
    
    async def run_specialized(
        self,
        task_type: str,
        user_task: str
    ) -> Dict[str, ModelResponse]:
        """
        Uzmanlaşmış çalıştırma - her model kendi uzmanlık alanında çalışır
        
        Model atamaları:
        - qwen3.5-plus: Genel görevler
        - qwen3-coder-plus: Kod yazma
        - qwen3-max: Karmaşık analiz
        """
        results = {}
        
        # Görev tipine göre model ataması
        model_assignments = {
            "code": [2],  # qwen3-coder-plus
            "design": [0, 2],  # qwen3.5-plus + coder
            "optimize": [0, 2],  # qwen3.5-plus + coder
            "debug": [0, 1],  # qwen3.5-plus + max
            "plc": [2],  # qwen3-coder-plus
            "cam": [0, 2],  # qwen3.5-plus + coder
            "gcode": [2],  # qwen3-coder-plus
            "safety": [1],  # qwen3-max
        }
        
        indices = model_assignments.get(task_type, [0])
        responses = await self.run_task(task_type, user_task, indices)
        
        for response in responses:
            results[response.model_id] = response
        
        return results
    
    async def run_comparison(
        self,
        task_type: str,
        user_task: str
    ) -> str:
        """Modeller arası karşılaştırma tablosu oluştur"""
        responses = await self.run_task(task_type, user_task)
        
        lines = [
            f"## {TASK_PROMPTS[task_type]['name']} - Model Karşılaştırması\n",
            f"**Görev:** {user_task[:100]}...\n",
            "| Model | Durum | Latency | Token | Yanıt (Özet) |",
            "|-------|-------|---------|-------|--------------|"
        ]
        
        for r in responses:
            status_emoji = "✅" if r.status == "success" else "❌"
            preview = r.content[:80].replace("\n", " ") + "..." if r.content else r.error
            lines.append(
                f"| {r.model_id} | {status_emoji} | {r.latency_ms:.0f}ms | {r.tokens_used} | {preview} |"
            )
        
        return "\n".join(lines)
    
    async def run_best_answer(
        self,
        task_type: str,
        user_task: str
    ) -> ModelResponse:
        """En iyi yanıtı seç (hız + kalite skoru)"""
        responses = await self.run_task(task_type, user_task)
        
        successful = [r for r in responses if r.status == "success"]
        if not successful:
            return responses[0] if responses else None
        
        # Skor hesaplama: token sayısı / latency (kalite/hız oranı)
        def score(r: ModelResponse) -> float:
            # Daha uzun yanıt genellikle daha detaylı (ama çok uzun değil)
            length_score = min(len(r.content) / 1000, 10)
            # Hız skoru (ters orantılı)
            speed_score = 10000 / max(r.latency_ms, 100)
            return length_score * speed_score
        
        best = max(successful, key=score)
        return best


def load_config(config_path: str) -> List[ModelConfig]:
    """Yapılandırma dosyasından yükle"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    api_key = config.get("api_key", "")
    api_endpoint = config.get("api_endpoint", "https://coding-intl.dashscope.aliyuncs.com/v1")
    
    configs = []
    for model in config.get("models", []):
        configs.append(ModelConfig(
            model_id=model.get("model_id", "qwen3.5-plus"),
            api_key=model.get("api_key", api_key),
            api_endpoint=model.get("api_endpoint", api_endpoint),
            temperature=model.get("temperature", 0.7),
            max_tokens=model.get("max_tokens", 4096),
            system_prompt=model.get("system_prompt", "")
        ))
    
    return configs


def get_default_configs() -> List[ModelConfig]:
    """Varsayılan model yapılandırmaları"""
    api_key = "sk-sp-1dfff295506a4cbba9c3745dd54e5796"
    
    return [
        ModelConfig(
            model_id="qwen3.5-plus",
            api_key=api_key,
            temperature=0.7,
            max_tokens=4096,
            system_prompt="Sen endüstriyel otomasyon uzmanı bir AI asistansısın."
        ),
        ModelConfig(
            model_id="qwen3-max-2026-01-23",
            api_key=api_key,
            temperature=0.7,
            max_tokens=4096,
            system_prompt="Sen karmaşık teknik analizler yapan kıdem bir mühendissin."
        ),
        ModelConfig(
            model_id="qwen3-coder-plus",
            api_key=api_key,
            temperature=0.3,
            max_tokens=8192,
            system_prompt="Sen endüstriyel otomasyon ve CNC sistemleri konusunda uzman bir yazılım mühendisisin."
        )
    ]


async def main_async():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(
        description="CNC Cam Kesme Makinesi - AI Orkestratör",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
GÖREV TİPLERİ:
  code      - Python/FreeCAD/NC kod yazma
  design    - Mekanik tasarım önerileri
  optimize  - Kesim optimizasyonu
  debug     - Hata ayıklama
  plc       - PLC/EtherCAT konfigürasyonu
  cam       - E-Cam profili tasarımı
  gcode     - G-kod programı
  safety    - Güvenlik sistemi analizi

ÖRNEKLER:
  python cnc_orchestrator.py --task code --custom "FreeCAD için motor montaj scripti yaz"
  python cnc_orchestrator.py --task plc --custom "EtherCAT PDO mapping ayarları"
  python cnc_orchestrator.py --task optimize --custom "Cam kesim yerleşimi optimizasyonu"
  python cnc_orchestrator.py --task compare --custom "Servo motor titreşim analizi"
        """
    )
    
    parser.add_argument(
        "--task", "-t",
        type=str,
        choices=["code", "design", "optimize", "debug", "plc", "cam", "gcode", "safety", "compare"],
        default=None,
        help="Görev tipi"
    )
    parser.add_argument(
        "--custom", "-c",
        type=str,
        help="Özel görev tanımı"
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Yapılandırma dosyası"
    )
    parser.add_argument(
        "--models",
        type=str,
        help="Model seçimi (virgülle ayrılmış)"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["parallel", "specialized", "best", "compare"],
        default="specialized",
        help="Çalışma modu"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Çıktı dosyası"
    )
    parser.add_argument(
        "--list-tasks",
        action="store_true",
        help="Görev tiplerini listele"
    )
    
    args = parser.parse_args()
    
    # Görev tiplerini listele
    if args.list_tasks:
        print("\n=== CNC AI Orkestratör - Görev Tipleri ===\n")
        for key, task in TASK_PROMPTS.items():
            print(f"  {key:12} - {task['description']}")
        print()
        return
    
    # Yapılandırma yükle
    if args.config:
        configs = load_config(args.config)
    else:
        configs = get_default_configs()
    
    orchestrator = CNCAIOrchestrator(configs)
    
    # Özel görev veya demo
    if args.custom:
        user_task = args.custom
    else:
        # Demo görevler
        demo_tasks = {
            "code": "X ekseni için limit switch kontrolü yapan Python fonksiyonu yaz",
            "design": "Kesim kafası için motor montaj brakti tasarımı öner",
            "optimize": "6000x3000mm camdan 500x400mm parçalar için optimal yerleşim",
            "debug": "X ekseni servo alarmı: Err 13.1 (Position deviation too large)",
            "plc": "R1-EC0902D input modülü için EtherCAT PDO mapping",
            "cam": "12mm lamine cam için E-Cam profili oluştur",
            "gcode": "500x400x12mm cam için dikdörtgen kesim programı",
            "safety": "STO devresi için ISO 13849-1 PL d analizi"
        }
        user_task = demo_tasks.get(args.task, "Görev tanımlanmadı")
        print(f"Demo görev kullanılıyor: {user_task}\n")
    
    # Model filtreleme
    model_indices = None
    if args.models:
        selected = [m.strip() for m in args.models.split(",")]
        model_indices = []
        for i, c in enumerate(configs):
            if c.model_id in selected:
                model_indices.append(i)
    
    print(f"\n{'='*60}")
    print(f"GÖREV: {TASK_PROMPTS[args.task]['name']}")
    print(f"{'='*60}")
    print(f"Soru: {user_task}\n")
    
    result = None
    
    if args.mode == "parallel":
        responses = await orchestrator.run_parallel(args.task, user_task, model_indices)
        for r in responses:
            print(f"\n{'-'*50}")
            print(f"Model: {r.model_id}")
            print(f"Durum: {r.status} | Latency: {r.latency_ms:.0f}ms | Token: {r.tokens_used}")
            if r.status == "success":
                print(f"\n{r.content[:1000]}...")
            else:
                print(f"Hata: {r.error}")
        result = {"responses": [asdict(r) for r in responses]}
    
    elif args.mode == "specialized":
        results = await orchestrator.run_specialized(args.task, user_task)
        for model_id, r in results.items():
            print(f"\n{'-'*50}")
            print(f"Model: {r.model_id}")
            print(f"Durum: {r.status} | Latency: {r.latency_ms:.0f}ms")
            if r.status == "success":
                print(f"\n{r.content}")
            else:
                print(f"Hata: {r.error}")
        result = {"responses": {k: asdict(v) for k, v in results.items()}}
    
    elif args.mode == "best":
        best = await orchestrator.run_best_answer(args.task, user_task)
        print(f"\nSeçilen Model: {best.model_id}")
        print(f"Latency: {best.latency_ms:.0f}ms\n")
        print(best.content)
        result = {"best": asdict(best)}
    
    elif args.mode == "compare":
        comparison = await orchestrator.run_comparison(args.task, user_task)
        print(comparison)
        result = {"comparison": comparison}
    
    # Dosyaya kaydet
    if args.output and result:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nSonuçlar kaydedildi: {args.output}")


def main():
    """Ana giriş noktası"""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()