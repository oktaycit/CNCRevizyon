#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwen API Client - Lamine Cam Kesim Parametre Hesaplama
Lisec GFB-60/30RE-S Hibrit Sistem

Qwen API Dokümantasyonu: https://help.aliyun.com/zh/dashscope/
"""

import os
import json
import requests
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class LamineCamParametreleri:
    """Lamine cam girdi parametreleri"""
    ust_kalinlik: float  # mm
    film_kalinlik: float  # mm (PVB)
    alt_kalinlik: float  # mm
    cam_tipi: str  # 'PVB', 'EVA', 'SGP'
    cam_boyut_x: float  # mm
    cam_boyut_y: float  # mm


class QwenAPIClient:
    """
    Qwen API Client for Lamine Cutting Parameter Calculation
    
    ÖNEMLİ: API Key formatı "sk-" ile başlamalıdır.
    Örnek: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    
    API Endpoint: https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
    Model: qwen-turbo, qwen-plus, qwen-max
    """
    
    # Qwen API Endpoint
    API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    # Mevcut modeller
    MODELS = {
        'turbo': 'qwen-turbo',      # Hızlı, ekonomik
        'plus': 'qwen-plus',        # Dengeli
        'max': 'qwen-max',          # En yetenekli
        'max_long': 'qwen-max-longcontext'  # Uzun context
    }
    
    def __init__(self, api_key: Optional[str] = None, model: str = 'plus'):
        """
        Qwen API Client başlat
        
        Args:
            api_key: Qwen API key (sk-xxxxxxxx formatında olmalı)
                     Eğer None ise, QWEN_API_KEY environment variable'dan okunur
            model: Kullanılacak model ('turbo', 'plus', 'max', 'max_long')
        """
        # API key'i al
        self.api_key = api_key or os.getenv('QWEN_API_KEY')
        
        # API key doğrulama
        if not self.api_key:
            raise ValueError(
                "Qwen API key bulunamadı! Lütfen:\n"
                "1. api_key parametresi ile geçirin, VEYA\n"
                "2. QWEN_API_KEY environment variable'ı ayarlayın\n\n"
                "API key formatı: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n"
                "Key'i https://dashscope.console.aliyun.com/ adresinden alabilirsiniz."
            )
        
        # API key format kontrolü
        if not self.api_key.startswith('sk-'):
            raise ValueError(
                f"Geçersiz API key formatı! API key 'sk-' ile başlamalıdır.\n"
                f"Girilen key: '{self.api_key[:10]}...'\n"
                "Lütfen API key'inizi kontrol edin."
            )
        
        self.model = self.MODELS.get(model, self.MODELS['plus'])
        
        # Headers - ÖNEMLİ: Authorization formatı
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',  # "Bearer " ile başlamalı
            'Content-Type': 'application/json'
        }
    
    def _create_system_prompt(self) -> str:
        """Sistem prompt'u oluştur"""
        return """Sen bir cam işleme uzman sistemisin. 
Lamine cam kesim parametrelerini hesaplamak için görevlisin.

Görevin:
1. Kullanıcıdan gelen cam parametrelerini analiz et
2. Optimum kesim parametrelerini hesapla
3. JSON formatında sonuç döndür

DİKKAT: Sadece JSON formatında cevap ver, başka açıklama ekleme."""

    def _create_user_prompt(self, params: LamineCamParametreleri) -> str:
        """Kullanıcı prompt'u oluştur"""
        return f"""Lamine cam kesim parametrelerini hesapla:

Cam Özellikleri:
- Üst cam kalınlığı: {params.ust_kalinlik} mm
- PVB film kalınlığı: {params.film_kalinlik} mm
- Alt cam kalınlığı: {params.alt_kalinlik} mm
- Cam tipi: {params.cam_tipi}
- Cam boyutu: {params.cam_boyut_x} x {params.cam_boyut_y} mm

Beklenen JSON çıktısı formatı:
{{
    "isitma_suresi": 4.2,
    "isitma_sicaklik": 135,
    "ust_kesim_basinc": 3.5,
    "alt_kesim_basinc": 3.2,
    "ayirma_basinc": 2.8,
    "kirma_basinc": 4.0,
    "kesim_hizi": 1800,
    "ust_alt_offset_x": 0.02,
    "ust_alt_offset_y": -0.01
}}"""

    def calculate_parameters(self, params: LamineCamParametreleri, 
                            max_retries: int = 3) -> Dict:
        """
        Qwen API ile lamine kesim parametrelerini hesapla
        
        Args:
            params: Lamine cam parametreleri
            max_retries: Maksimum tekrar deneme sayısı
            
        Returns:
            API'den dönen parametre sözlüğü
            
        Raises:
            ValueError: API key hatalı ise
            requests.exceptions.RequestException: Network hatası
            json.JSONDecodeError: Geçersiz JSON cevabı
        """
        
        messages = [
            {"role": "system", "content": self._create_system_prompt()},
            {"role": "user", "content": self._create_user_prompt(params)}
        ]
        
        payload = {
            "model": self.model,
            "input": {
                "messages": messages
            },
            "parameters": {
                "temperature": 0.1,  # Düşük temperature - daha deterministik
                "max_tokens": 500,
                "result_format": "message"
            }
        }
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.API_URL,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
                
                # HTTP status code kontrolü
                if response.status_code == 401:
                    raise ValueError(
                        "HTTP 401: Yetkilendirme hatası!\n\n"
                        "Olası nedenler:\n"
                        "1. API key hatalı veya geçersiz\n"
                        "2. API key 'sk-' ile başlamıyor\n"
                        "3. API key'inizin yetkisi yok veya süresi dolmuş\n"
                        "4. Authorization header formatı hatalı (Bearer olmalı)\n\n"
                        f"Girilen API key: {self.api_key[:10]}...\n\n"
                        "Çözüm:\n"
                        "1. https://dashscope.console.aliyun.com/ adresinden yeni key alın\n"
                        "2. Key'in tam olarak kopyalandığından emin olun\n"
                        "3. Environment variable'ı kontrol edin: echo $QWEN_API_KEY"
                    )
                
                elif response.status_code == 400:
                    error_data = response.json()
                    raise ValueError(f"HTTP 400: Geçersiz istek - {error_data}")
                
                elif response.status_code == 429:
                    # Rate limit - bekle ve tekrar dene
                    import time
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Rate limit aşıldı, {wait_time}s bekleniyor...")
                    time.sleep(wait_time)
                    continue
                
                elif response.status_code >= 500:
                    # Server hatası - tekrar dene
                    import time
                    wait_time = 2 ** attempt
                    print(f"Server hatası ({response.status_code}), {wait_time}s bekleniyor...")
                    time.sleep(wait_time)
                    continue
                
                elif response.status_code != 200:
                    raise ValueError(f"HTTP {response.status_code}: {response.text}")
                
                # Başarılı cevap
                response_data = response.json()
                
                # Qwen API response parsing
                if 'output' in response_data and 'choices' in response_data['output']:
                    content = response_data['output']['choices'][0]['message']['content']
                elif 'output' in response_data and 'text' in response_data['output']:
                    content = response_data['output']['text']
                else:
                    raise ValueError(f"Beklenmeyen API response formatı: {response_data}")
                
                # JSON parse et
                return self._parse_json_response(content)
                
            except requests.exceptions.RequestException as e:
                last_error = e
                print(f"Network hatası ({attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)
                continue
        
        # Tüm denemeler başarısız
        if last_error:
            raise last_error
        raise ValueError("API çağrısı başarısız")
    
    def _parse_json_response(self, content: str) -> Dict:
        """
        API'den gelen JSON içeriğini parse et
        
        Args:
            content: API'den dönen içerik
            
        Returns:
            Parse edilmiş sözlük
        """
        # JSON code block içinde olabilir
        if '```json' in content:
            import re
            match = re.search(r'```json\s*(.+?)\s*```', content, re.DOTALL)
            if match:
                content = match.group(1)
        elif '```' in content:
            import re
            match = re.search(r'```\s*(.+?)\s*```', content, re.DOTALL)
            if match:
                content = match.group(1)
        
        return json.loads(content.strip())
    
    def test_connection(self) -> bool:
        """
        API bağlantısını test et
        
        Returns:
            True ise bağlantı başarılı
        """
        try:
            messages = [
                {"role": "user", "content": "Merhaba, sadece 'OK' yaz."}
            ]
            
            payload = {
                "model": self.model,
                "input": {"messages": messages},
                "parameters": {"max_tokens": 10}
            }
            
            response = requests.post(
                self.API_URL,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✓ API bağlantısı başarılı!")
                return True
            elif response.status_code == 401:
                print("✗ API key hatalı (401 Unauthorized)")
                return False
            else:
                print(f"✗ API hatası: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Bağlantı hatası: {e}")
            return False


def main():
    """Örnek kullanım"""
    
    # 1. API key'i environment variable'dan al
    # Önce shell'de export QWEN_API_KEY='sk-xxx' yapın
    
    # 2. Veya doğrudan geçirin (güvenli değil, sadece test için)
    # api_key = 'sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    
    print("=" * 60)
    print("Qwen API - Lamine Cam Kesim Parametre Hesaplama")
    print("=" * 60)
    
    # API client oluştur
    try:
        client = QwenAPIClient(model='plus')
    except ValueError as e:
        print(f"\n❌ HATA: {e}")
        return
    
    # Bağlantı testi
    print("\n🔍 API bağlantısı test ediliyor...")
    if not client.test_connection():
        print("\n❌ API bağlantısı başarısız! Lütfen API key'inizi kontrol edin.")
        return
    print("✓ Bağlantı başarılı!\n")
    
    # Örnek parametreler
    params = LamineCamParametreleri(
        ust_kalinlik=4,
        film_kalinlik=0.76,
        alt_kalinlik=4,
        cam_tipi='PVB',
        cam_boyut_x=2000,
        cam_boyut_y=1500
    )
    
    print(f"📊 Cam Özellikleri:")
    print(f"   - Üst: {params.ust_kalinlik}mm")
    print(f"   - Film: {params.film_kalinlik}mm ({params.cam_tipi})")
    print(f"   - Alt: {params.alt_kalinlik}mm")
    print(f"   - Boyut: {params.cam_boyut_x} x {params.cam_boyut_y}mm\n")
    
    # Parametre hesapla
    print("🔄 Parametreler hesaplanıyor...")
    try:
        result = client.calculate_parameters(params)
        
        print("\n✅ Sonuçlar:")
        print("-" * 40)
        for key, value in result.items():
            print(f"   {key}: {value}")
        print("-" * 40)
        
    except Exception as e:
        print(f"\n❌ Hata: {e}")


if __name__ == '__main__':
    main()