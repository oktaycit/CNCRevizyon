#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Herofis Integration Connector
Cam Sipariş Yönetimi Entegrasyonu

Herofis ERP'den CSV export ile sipariş alımı ve
Glass Cutting Program'a dönüştürme.

Desteklenen Herofis CSV Formatları:
1. Standart Sipariş CSV (SiparişNo, Müşteri, En, Boy, Kalınlık, CamTipi, Adet)
2. PenCAD Export (Quote No, Glass Dimensions, Edge Processing)
3. CamCAD Online Export (Production Order Format)

Usage:
    connector = HerofisConnector()
    orders = connector.import_csv("siparisler.csv")
    # orders -> GlassOrder objects ready for optimization
"""

import os
import csv
import json
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HerofisConnector")


# Herofis CSV Column Mappings (Turkish/English)
HEROFIS_COLUMN_MAPPINGS = {
    # Turkish column names
    "siparis_no": ["siparis_no", "sipariş_no", "siparisno", "order_id", "order_no", "no"],
    "musteri": ["musteri", "müşteri", "customer", "client", "cari"],
    "en": ["en", "width", "genislik", "genişlik", "w", "boyut_en"],
    "boy": ["boy", "height", "yukseklik", "yükseklik", "h", "boyut_boy", "uzunluk"],
    "kalınlık": ["kalınlık", "kalınlik", "thickness", "thick", "mm", "kalinlik_mm"],
    "cam_tipi": ["cam_tipi", "cam tipi", "glass_type", "camtipi", "tip", "tur", "tür"],
    "adet": ["adet", "quantity", "qty", "miktar", "adet_sayisi", "sayi", "sayı"],
    "öncelik": ["öncelik", "oncelik", "priority", "aciliyet", "urgent"],
    "notlar": ["notlar", "notes", "açıklama", "aciklama", "remark", "description"],
    "poz_no": ["poz_no", "poz", "poz numarası", "position", "poz_no", "ref"],
    "kenar": ["kenar", "edge", "kenar_islem", "edge_processing", "processing"],
    "fatura_no": ["fatura_no", "fatura", "invoice", "inv_no"],
    "tarih": ["tarih", "date", "order_date", "created_at"],
    "film_tipi": ["film_tipi", "film type", "interlayer", "pvb", "eva", "sgp"],
    "film_kalınlık": ["film_kalınlık", "film thickness", "film_mm", "ara_tabaka"],
}

# Glass type mappings (Turkish to system)
GLASS_TYPE_MAPPINGS = {
    "float": ["float", "flo", "normal", "standart", "düz", "duz", "plain"],
    "laminated": ["lamine", "laminated", "lam", "laminli", "lamine cam", "compound"],
    "tempered": ["temperli", "tempered", "temp", "hardened", "ısıl işlemli", "isil islemli"],
    "low_e": ["low-e", "low e", "lowe", "low_e", "düşük e", "enerji"],
    "reflective": ["reflective", "reflektif", "mirror", "ayna", "refle"],
    "tinted": ["tinted", "renkli", "colored", "bronz", "grey", "gri"],
}

# Film type mappings
FILM_TYPE_MAPPINGS = {
    "PVB": ["pvb", "pvb 0.38", "pvb 0.76", "pvb 1.52"],
    "EVA": ["eva", "eva 0.5", "eva 0.76"],
    "SGP": ["sgp", "sentrygard", "sgp 1.52", "sgp 2.28"],
}

# Priority mappings
PRIORITY_MAPPINGS = {
    1: ["acil", "urgent", "yüksek", "yuksek", "high", "1", "önel", "aciliyet"],
    2: ["normal", "standart", "orta", "medium", "2", "standart"],
    3: ["düşük", "dusuk", "low", "gecikmeli", "3", "sonra"],
}


@dataclass
class HerofisOrder:
    """Raw Herofis order from CSV"""
    siparis_no: str
    musteri: str = ""
    en: float = 0.0
    boy: float = 0.0
    kalınlık: float = 4.0
    cam_tipi: str = "float"
    adet: int = 1
    öncelik: int = 2
    notlar: str = ""
    poz_no: str = ""
    kenar: str = ""
    fatura_no: str = ""
    tarih: str = ""
    film_tipi: str = ""
    film_kalınlık: float = 0.0
    raw_data: Dict = field(default_factory=dict)


@dataclass
class ImportResult:
    """Result of CSV import operation"""
    success: bool
    orders: List[HerofisOrder]
    total_rows: int
    imported_rows: int
    skipped_rows: int
    errors: List[str]
    warnings: List[str]
    source_file: str
    import_time: str


class HerofisConnector:
    """
    Herofis ERP Integration Connector
    
    Features:
    - CSV import with flexible column mapping
    - Auto-detect column names (Turkish/English)
    - Glass type normalization
    - Convert to GlassOrder format
    - Import history tracking
    """
    
    def __init__(self, 
                 data_dir: Optional[str] = None,
                 custom_mappings: Optional[Dict] = None):
        """
        Initialize Herofis connector
        
        Args:
            data_dir: Directory for imported files
            custom_mappings: Custom column mappings
        """
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / "data" / "herofis"
        self.import_dir = self.data_dir / "imports"
        self.history_file = self.data_dir / "import_history.json"
        
        # Create directories
        self.import_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Custom mappings
        self.column_mappings = custom_mappings or HEROFIS_COLUMN_MAPPINGS
        
        # Import history
        self.history: List[Dict] = self._load_history()
        
        logger.info(f"HerofisConnector initialized. Data dir: {self.data_dir}")
    
    def _load_history(self) -> List[Dict]:
        """Load import history"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_history(self):
        """Save import history"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
    
    def import_csv(self, 
                   file_path: str,
                   encoding: str = 'utf-8',
                   delimiter: str = ',',
                   skip_header: bool = True) -> ImportResult:
        """
        Import orders from Herofis CSV file
        
        Args:
            file_path: Path to CSV file
            encoding: File encoding (utf-8, windows-1254, iso-8859-9)
            delimiter: CSV delimiter (comma, semicolon, tab)
            skip_header: Skip first row as header
            
        Returns:
            ImportResult with imported orders
        """
        errors = []
        warnings = []
        orders = []
        total_rows = 0
        imported_rows = 0
        skipped_rows = 0
        
        # Detect encoding if not specified
        if encoding == 'auto':
            encoding = self._detect_encoding(file_path)
        
        # Detect delimiter if not specified
        if delimiter == 'auto':
            delimiter = self._detect_delimiter(file_path, encoding)
        
        try:
            with open(file_path, 'r', encoding=encoding, newline='') as f:
                reader = csv.reader(f, delimiter=delimiter)
                rows = list(reader)
                
                if not rows:
                    return ImportResult(
                        success=False,
                        orders=[],
                        total_rows=0,
                        imported_rows=0,
                        skipped_rows=0,
                        errors=["Empty CSV file"],
                        warnings=[],
                        source_file=file_path,
                        import_time=datetime.now().isoformat()
                    )
                
                # Parse header
                header = rows[0] if skip_header else None
                column_map = self._map_columns(header) if header else None
                
                total_rows = len(rows) - 1 if skip_header else len(rows)
                
                # Parse data rows
                start_idx = 1 if skip_header else 0
                
                for idx, row in enumerate(rows[start_idx:], start=start_idx):
                    try:
                        order = self._parse_row(row, column_map, header, idx)
                        if order:
                            orders.append(order)
                            imported_rows += 1
                        else:
                            skipped_rows += 1
                    except Exception as e:
                        errors.append(f"Row {idx}: {str(e)}")
                        skipped_rows += 1
            
            # Save import history
            self._add_to_history(file_path, imported_rows, skipped_rows, errors)
            
            # Copy file to import archive
            self._archive_file(file_path)
            
            logger.info(f"Imported {imported_rows} orders from {file_path}")
            
            return ImportResult(
                success=imported_rows > 0,
                orders=orders,
                total_rows=total_rows,
                imported_rows=imported_rows,
                skipped_rows=skipped_rows,
                errors=errors,
                warnings=warnings,
                source_file=file_path,
                import_time=datetime.now().isoformat()
            )
            
        except FileNotFoundError:
            return ImportResult(
                success=False,
                orders=[],
                total_rows=0,
                imported_rows=0,
                skipped_rows=0,
                errors=["File not found"],
                warnings=[],
                source_file=file_path,
                import_time=datetime.now().isoformat()
            )
        except Exception as e:
            return ImportResult(
                success=False,
                orders=[],
                total_rows=0,
                imported_rows=0,
                skipped_rows=0,
                errors=[f"Import error: {str(e)}"],
                warnings=[],
                source_file=file_path,
                import_time=datetime.now().isoformat()
            )
    
    def _detect_encoding(self, file_path: str) -> str:
        """Detect file encoding"""
        # Try common Turkish encodings
        encodings = ['utf-8', 'windows-1254', 'iso-8859-9', 'utf-8-sig']
        
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc) as f:
                    f.read(1000)  # Read first 1000 chars
                return enc
            except UnicodeDecodeError:
                continue
        
        return 'utf-8'  # Default fallback
    
    def _detect_delimiter(self, file_path: str, encoding: str) -> str:
        """Detect CSV delimiter"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                first_line = f.readline()
                
                # Count delimiter candidates
                comma_count = first_line.count(',')
                semicolon_count = first_line.count(';')
                tab_count = first_line.count('\t')
                
                if semicolon_count > comma_count and semicolon_count > tab_count:
                    return ';'
                elif tab_count > comma_count:
                    return '\t'
                else:
                    return ','
        except:
            return ','
    
    def _map_columns(self, header: List[str]) -> Dict[str, int]:
        """Map header columns to standard names"""
        mapping = {}
        
        for idx, col in enumerate(header):
            col_clean = col.strip().lower()
            
            # Find matching standard column
            for standard_name, aliases in self.column_mappings.items():
                if col_clean in aliases:
                    mapping[standard_name] = idx
                    break
        
        return mapping
    
    def _parse_row(self, 
                   row: List[str],
                   column_map: Optional[Dict[str, int]],
                   header: Optional[List[str]],
                   row_idx: int) -> Optional[HerofisOrder]:
        """Parse a CSV row into HerofisOrder"""
        
        # If no column map, try to guess structure
        if not column_map:
            # Try to detect by position (common format)
            # Format: SiparişNo, En, Boy, Kalınlık, Adet, CamTipi
            if len(row) >= 5:
                siparis_no = row[0].strip()
                en = self._parse_float(row[1])
                boy = self._parse_float(row[2])
                kalınlık = self._parse_float(row[3]) if len(row) > 3 else 4
                adet = self._parse_int(row[4]) if len(row) > 4 else 1
                cam_tipi = row[5].strip() if len(row) > 5 else "float"
                
                return HerofisOrder(
                    siparis_no=siparis_no,
                    en=en,
                    boy=boy,
                    kalınlık=kalınlık,
                    cam_tipi=self._normalize_glass_type(cam_tipi),
                    adet=adet
                )
            return None
        
        # Use column mapping
        try:
            siparis_no = self._get_column_value(row, column_map, "siparis_no", f"ORD-{row_idx}")
            musteri = self._get_column_value(row, column_map, "musteri", "")
            en = self._parse_float(self._get_column_value(row, column_map, "en", "0"))
            boy = self._parse_float(self._get_column_value(row, column_map, "boy", "0"))
            kalınlık = self._parse_float(self._get_column_value(row, column_map, "kalınlık", "4"))
            cam_tipi_raw = self._get_column_value(row, column_map, "cam_tipi", "float")
            adet = self._parse_int(self._get_column_value(row, column_map, "adet", "1"))
            öncelik_raw = self._get_column_value(row, column_map, "öncelik", "2")
            notlar = self._get_column_value(row, column_map, "notlar", "")
            poz_no = self._get_column_value(row, column_map, "poz_no", "")
            kenar = self._get_column_value(row, column_map, "kenar", "")
            fatura_no = self._get_column_value(row, column_map, "fatura_no", "")
            tarih = self._get_column_value(row, column_map, "tarih", "")
            film_tipi_raw = self._get_column_value(row, column_map, "film_tipi", "")
            film_kalınlık = self._parse_float(self._get_column_value(row, column_map, "film_kalınlık", "0"))
            
            # Validate dimensions
            if en <= 0 or boy <= 0:
                logger.warning(f"Row {row_idx}: Invalid dimensions {en}x{boy}")
                return None
            
            return HerofisOrder(
                siparis_no=siparis_no,
                musteri=musteri,
                en=en,
                boy=boy,
                kalınlık=kalınlık,
                cam_tipi=self._normalize_glass_type(cam_tipi_raw),
                adet=max(1, adet),
                öncelik=self._normalize_priority(öncelik_raw),
                notlar=notlar,
                poz_no=poz_no,
                kenar=kenar,
                fatura_no=fatura_no,
                tarih=tarih,
                film_tipi=self._normalize_film_type(film_tipi_raw),
                film_kalınlık=film_kalınlık,
                raw_data=dict(zip(header, row)) if header else {}
            )
        except Exception as e:
            logger.error(f"Row {row_idx}: Parse error - {e}")
            return None
    
    def _get_column_value(self, 
                          row: List[str],
                          column_map: Dict[str, int],
                          key: str,
                          default: str) -> str:
        """Get value from row using column mapping"""
        idx = column_map.get(key)
        if idx is not None and idx < len(row):
            return row[idx].strip()
        return default
    
    def _parse_float(self, value: str) -> float:
        """Parse float from string (handles Turkish format)"""
        try:
            # Replace Turkish decimal separator
            value = value.replace(',', '.').strip()
            # Remove non-numeric chars except dot
            value = re.sub(r'[^\d.]', '', value)
            return float(value) if value else 0.0
        except ValueError:
            return 0.0
    
    def _parse_int(self, value: str) -> int:
        """Parse int from string"""
        try:
            value = re.sub(r'[^\d]', '', value.strip())
            return int(value) if value else 0
        except ValueError:
            return 0
    
    def _normalize_glass_type(self, value: str) -> str:
        """Normalize glass type to standard values"""
        value_lower = value.lower().strip()
        
        for standard_type, aliases in GLASS_TYPE_MAPPINGS.items():
            if value_lower in aliases:
                return standard_type
        
        # Default to float if unknown
        return "float"
    
    def _normalize_priority(self, value: str) -> int:
        """Normalize priority to 1-3"""
        value_lower = value.lower().strip()
        
        for priority, aliases in PRIORITY_MAPPINGS.items():
            if value_lower in aliases:
                return priority
        
        # Try parsing as number
        try:
            num = int(value_lower)
            return max(1, min(3, num))
        except ValueError:
            return 2  # Default normal
    
    def _normalize_film_type(self, value: str) -> str:
        """Normalize film type to standard values"""
        value_lower = value.lower().strip()
        
        for standard_type, aliases in FILM_TYPE_MAPPINGS.items():
            if value_lower in aliases:
                return standard_type
        
        return value if value else ""
    
    def _add_to_history(self, file_path: str, imported: int, skipped: int, errors: List[str]):
        """Add import to history"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "source_file": file_path,
            "imported_count": imported,
            "skipped_count": skipped,
            "errors": errors[:5] if errors else [],  # Keep first 5 errors
            "success_rate": f"{imported}/{imported+skipped}"
        }
        
        self.history.append(entry)
        
        # Keep last 50 entries
        if len(self.history) > 50:
            self.history = self.history[-50:]
        
        self._save_history()
    
    def _archive_file(self, file_path: str):
        """Archive imported file"""
        try:
            import shutil
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = Path(file_path).stem
            archive_path = self.import_dir / f"{filename}_{timestamp}.csv"
            shutil.copy2(file_path, archive_path)
            logger.info(f"Archived to {archive_path}")
        except Exception as e:
            logger.warning(f"Could not archive file: {e}")
    
    def convert_to_glass_orders(self, 
                                 herofis_orders: List[HerofisOrder],
                                 rotate_allowed_default: bool = True) -> List[Dict]:
        """
        Convert HerofisOrder to GlassOrder format for optimization
        
        Args:
            herofis_orders: List of HerofisOrder objects
            rotate_allowed_default: Default rotation permission
            
        Returns:
            List of GlassOrder-compatible dicts
        """
        glass_orders = []
        
        for order in herofis_orders:
            # Create glass order dict
            glass_order = {
                "order_id": order.siparis_no,
                "width": order.en,
                "height": order.boy,
                "quantity": order.adet,
                "thickness": order.kalınlık,
                "glass_type": order.cam_tipi,
                "priority": order.öncelik,
                "rotate_allowed": rotate_allowed_default,
                "customer": order.musteri,
                "notes": order.notlar,
                "poz_no": order.poz_no,
                "edge_processing": order.kenar,
                "invoice_no": order.fatura_no,
                "order_date": order.tarih,
            }
            
            # Add laminated glass specific fields
            if order.cam_tipi == "laminated" and order.film_tipi:
                glass_order["film_type"] = order.film_tipi
                glass_order["film_thickness"] = order.film_kalınlık or 0.76
            
            glass_orders.append(glass_order)
        
        return glass_orders
    
    def get_import_history(self, limit: int = 20) -> List[Dict]:
        """Get import history"""
        return self.history[-limit:] if self.history else []
    
    def clear_history(self):
        """Clear import history"""
        self.history = []
        self._save_history()
    
    def save_orders_json(self, 
                         orders: List[HerofisOrder],
                         output_path: Optional[str] = None,
                         include_sheet_info: bool = True) -> str:
        """
        Save orders to JSON format compatible with GlassCuttingOrchestrator
        
        Args:
            orders: List of HerofisOrder
            output_path: Output file path
            include_sheet_info: Include sheet dimensions
            
        Returns:
            Path to saved JSON file
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.data_dir / f"herofis_orders_{timestamp}.json")
        
        # Convert to GlassOrder format
        glass_orders = self.convert_to_glass_orders(orders)
        
        output_data = {
            "orders": glass_orders,
            "source": "herofis",
            "import_time": datetime.now().isoformat(),
        }
        
        if include_sheet_info:
            output_data["sheet"] = {
                "width": 6000,
                "height": 3000,
            }
        
        output_data["metadata"] = {
            "source_file": orders[0].raw_data.get("_source", "unknown") if orders else "unknown",
            "total_orders": len(orders),
            "converter": "HerofisConnector v1.0"
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(orders)} orders to {output_path}")
        return output_path
    
    def create_sample_csv(self, output_path: Optional[str] = None) -> str:
        """
        Create a sample Herofis CSV file for testing
        
        Returns:
            Path to sample CSV
        """
        if not output_path:
            output_path = str(self.data_dir / "sample_herofis_import.csv")
        
        # Sample data with Turkish headers
        headers = ["Sipariş_No", "Müşteri", "En", "Boy", "Kalınlık", "Cam_Tipi", "Adet", "Öncelik", "Notlar"]
        
        sample_orders = [
            ["HERO-001", "ABC Cam", "500", "400", "4", "Float", "10", "Normal", "Pencere camları"],
            ["HERO-002", "XYZ Dekorasyon", "800", "600", "6", "Float", "5", "Acil", "Büyük panel"],
            ["HERO-003", "Mekan Cam", "300", "200", "4", "Float", "20", "Normal", "Vitrin"],
            ["HERO-004", "Pencere Ltd", "1200", "800", "8", "Lamine", "3", "Acil", "Giriş kapısı"],
            ["HERO-005", "Ayna Sanayi", "450", "350", "5", "Float", "15", "Düşük", "Standart"],
        ]
        
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(headers)
            writer.writerows(sample_orders)
        
        logger.info(f"Created sample CSV at {output_path}")
        return output_path


def main():
    """Test Herofis connector"""
    print("=" * 60)
    print("Herofis Connector Test")
    print("=" * 60)
    
    connector = HerofisConnector()
    
    # Create sample CSV
    sample_path = connector.create_sample_csv()
    print(f"\nSample CSV created: {sample_path}")
    
    # Import sample with auto delimiter detection
    result = connector.import_csv(sample_path, encoding='utf-8', delimiter='auto')
    
    print(f"\nImport Result:")
    print(f"  Success: {result.success}")
    print(f"  Total rows: {result.total_rows}")
    print(f"  Imported: {result.imported_rows}")
    print(f"  Skipped: {result.skipped_rows}")
    print(f"  Errors: {result.errors}")
    
    if result.orders:
        print(f"\nImported Orders:")
        for order in result.orders[:3]:
            print(f"  {order.siparis_no}: {order.en}x{order.boy}mm, {order.kalınlık}mm, {order.cam_tipi}, {order.adet} pcs")
        
        # Convert to GlassOrder format
        glass_orders = connector.convert_to_glass_orders(result.orders)
        print(f"\nConverted to GlassOrder format: {len(glass_orders)} orders")
        
        # Save as JSON
        json_path = connector.save_orders_json(result.orders)
        print(f"Saved JSON: {json_path}")
    
    print("\n" + "=" * 60)
    print("Test completed!")


if __name__ == "__main__":
    main()