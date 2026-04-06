# Yapay Zeka Destekli Kesim Optimizasyonu
## Lisec GFB 60-30 Cam Kesme Makinesi

## 1. Genel Bakış

Bu modül, cam levhalarından en az fire ile maksimum parça çıkarmak için yapay zeka algoritmaları kullanır.

### 1.1 Optimizasyon Hedefleri
- **Fire Oranı:** %5'in altında
- **Kesim Süresi:** Minimum
- **Kalite:** Çatlak/kırık olmadan
- **Maliyet:** Minimum hammadde kullanımı

## 2. Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Cutting Optimizer                         │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │  Input      │  │  Nesting    │  │  Path Optimization      │ │
│  │  Processor  │──►  Engine     │──►  (TSP/Genetic Algo)     │ │
│  │             │  │  (2D Bin    │  │                         │ │
│  │ - Order     │  │   Packing)  │  │ - Minimum travel        │ │
│  │ - Dimensions│  │             │  │ - Collision avoidance   │ │
│  │ - Quality   │  │             │  │ - Tool wear balance     │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│         │                │                      │               │
│         ▼                ▼                      ▼               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Machine Learning Model                     │   │
│  │                                                         │   │
│  │  - Historical cutting data                              │   │
│  │  - Defect prediction                                    │   │
│  │  - Optimal cutting parameters                           │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## 3. 2D Nesting (Yerleştirme) Algoritması

### 3.1 Algoritma Seçenekleri

#### A) Genetic Algorithm (GA)
```python
from deap import base, creator, tools, algorithms
import numpy as np

class GeneticNesting:
    def __init__(self, sheet_width, sheet_height):
        self.sheet_w = sheet_width
        self.sheet_h = sheet_height
        self.creator = creator
        
    def create_fitness(self):
        creator.create("FitnessMax", base.Fitness, weights=(1.0, -1.0))  # (utilization, cuts)
        creator.create("Individual", list, fitness=creator.FitnessMax)
        
    def evaluate(self, individual):
        """
        Fitness değerlendirme:
        - Material utilization (maximize)
        - Number of cuts (minimize)
        """
        utilization = self.calculate_utilization(individual)
        num_cuts = len(individual)
        return utilization, num_cuts
    
    def optimize(self, parts, population_size=100, generations=50):
        toolbox = base.Toolbox()
        # Individual creation
        toolbox.register("individual", self.create_individual, parts)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", self.evaluate)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
        toolbox.register("select", tools.selTournament, tournsize=3)
        
        population = toolbox.population(n=population_size)
        algorithms.eaSimple(population, toolbox, 
                           cxpb=0.7, mutpb=0.2, 
                           ngen=generations, verbose=True)
        
        return tools.selBest(population, 1)[0]
```

#### B) Guillotine Split Algorithm
```python
class GuillotinePacker:
    """Guillotine kesim için optimal yerleştirme"""
    
    def __init__(self, width, height):
        self.sheet_width = width
        self.sheet_height = height
        self.free_rectangles = [(0, 0, width, height)]  # (x, y, w, h)
        self.placed_parts = []
        
    def insert(self, part_width, part_height, rotation=False):
        """Parçayı yerleştirmeye çalış"""
        best_rect = None
        best_score = float('inf')
        
        for i, (x, y, rw, rh) in enumerate(self.free_rectangles):
            # Normal yerleştirme
            if part_width <= rw and part_height <= rh:
                score = self._score_placement(rw, rh, part_width, part_height)
                if score < best_score:
                    best_score = score
                    best_rect = (i, False)
            
            # Rotasyonlu yerleştirme
            if rotation and part_height <= rw and part_width <= rh:
                score = self._score_placement(rw, rh, part_height, part_width)
                if score < best_score:
                    best_score = score
                    best_rect = (i, True)
        
        if best_rect is None:
            return None  # Yerleştirilemedi
        
        rect_idx, rotated = best_rect
        x, y, rw, rh = self.free_rectangles[rect_idx]
        
        # Parçayı yerleştir
        if rotated:
            self.placed_parts.append((x, y, part_height, part_width, True))
            # Kalan alanları güncelle
            self._split_rectangle(rect_idx, part_height, part_width, rotated)
        else:
            self.placed_parts.append((x, y, part_width, part_height, False))
            self._split_rectangle(rect_idx, part_width, part_height, rotated)
            
        return (x, y)
    
    def _split_rectangle(self, rect_idx, pw, ph, rotated):
        """Yerleştirilen dikdörtgeni böl"""
        x, y, rw, rh = self.free_rectangles[rect_idx]
        self.free_rectangles.pop(rect_idx)
        
        # Guillotine split - horizontal veya vertical
        if rw - pw > rh - ph:  # Vertical split daha iyi
            if pw < rw:
                self.free_rectangles.append((x + pw, y, rw - pw, rh))
            if ph < rh:
                self.free_rectangles.append((x, y + ph, pw, rh - ph))
        else:  # Horizontal split daha iyi
            if ph < rh:
                self.free_rectangles.append((x, y + ph, rw, rh - ph))
            if pw < rw:
                self.free_rectangles.append((x + pw, y, rw - pw, ph))
```

### 3.2 Neural Network Tabanlı Yaklaşım
```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class NestingNetwork(nn.Module):
    """
    Parça yerleşimini tahmin eden sinir ağı
    Input: Parts list + Sheet dimensions
    Output: Placement positions
    """
    
    def __init__(self, num_parts=50, part_feat_dim=4):
        super().__init__()
        self.part_encoder = nn.Sequential(
            nn.Linear(part_feat_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
        )
        
        self.sheet_encoder = nn.Sequential(
            nn.Linear(2, 32),  # width, height
            nn.ReLU(),
            nn.Linear(32, 64),
            nn.ReLU(),
        )
        
        self.attention = nn.MultiheadAttention(embed_dim=128, num_heads=4)
        
        self.decoder = nn.Sequential(
            nn.Linear(128 + 64, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 4),  # x, y, rotation, confidence
        )
        
    def forward(self, parts, sheet_dims):
        # parts: [batch, num_parts, 4] (w, h, priority, type)
        # sheet: [batch, 2]
        
        part_emb = self.part_encoder(parts)  # [B, N, 128]
        sheet_emb = self.sheet_encoder(sheet_dims)  # [B, 64]
        
        # Attention
        part_emb = part_emb.permute(1, 0, 2)  # [N, B, 128]
        attn_out, _ = self.attention(part_emb, part_emb, part_emb)
        attn_out = attn_out.permute(1, 0, 2)  # [B, N, 128]
        
        # Combine with sheet info
        sheet_expanded = sheet_emb.unsqueeze(1).expand(-1, parts.size(1), -1)
        combined = torch.cat([attn_out, sheet_expanded], dim=-1)
        
        output = self.decoder(combined)  # [B, N, 4]
        return output
```

## 4. Kesim Yolu Optimizasyonu (TSP)

### 4.1 Traveling Salesman Problem Çözümü
```python
from scipy.spatial import distance
import numpy as np

class CuttingPathOptimizer:
    """Kesim kafası hareket yolunu optimize eder"""
    
    def __init__(self, cuts):
        """
        cuts: [(x1, y1, x2, y2), ...] kesim segmentleri
        """
        self.cuts = cuts
        self.n = len(cuts)
        
    def optimize_nearest_neighbor(self):
        """En yakın komşu algoritması"""
        unvisited = set(range(self.n))
        path = []
        current = 0
        path.append(current)
        unvisited.remove(current)
        
        while unvisited:
            current_pos = self._get_end_point(current)
            nearest = min(unvisited, 
                         key=lambda i: distance.euclidean(
                             current_pos, 
                             self._get_start_point(i)))
            path.append(nearest)
            unvisited.remove(nearest)
            current = nearest
            
        return path
    
    def optimize_2opt(self, max_iterations=1000):
        """2-opt local search optimizasyonu"""
        path = self.optimize_nearest_neighbor()
        improved = True
        iterations = 0
        
        while improved and iterations < max_iterations:
            improved = False
            for i in range(1, len(path) - 1):
                for j in range(i + 1, len(path)):
                    new_path = path[:i] + path[i:j+1][::-1] + path[j+1:]
                    if self._path_length(new_path) < self._path_length(path):
                        path = new_path
                        improved = True
                        break
                if improved:
                    break
            iterations += 1
            
        return path
    
    def _get_start_point(self, idx):
        x1, y1, x2, y2 = self.cuts[idx]
        return (x1, y1)
    
    def _get_end_point(self, idx):
        x1, y1, x2, y2 = self.cuts[idx]
        return (x2, y2)
    
    def _path_length(self, path):
        total = 0
        for i in range(len(path) - 1):
            end = self._get_end_point(path[i])
            start = self._get_start_point(path[i + 1])
            total += distance.euclidean(end, start)
        return total
```

### 4.2 Genetik Algoritma ile TSP
```python
class TSPGenetic:
    """TSP için genetik algoritma"""
    
    def __init__(self, distance_matrix, population_size=100):
        self.dist_matrix = distance_matrix
        self.pop_size = population_size
        self.n_cities = len(distance_matrix)
        
    def evolve(self, generations=200):
        population = self._init_population()
        
        for gen in range(generations):
            # Fitness evaluation
            fitness = [self._fitness(ind) for ind in population]
            
            # Selection
            parents = self._tournament_select(population, fitness, k=5)
            
            # Crossover (OX1)
            offspring = []
            for i in range(0, len(parents), 2):
                child1, child2 = self._ox1_crossover(parents[i], parents[i+1])
                offspring.extend([child1, child2])
            
            # Mutation
            for ind in offspring:
                if np.random.random() < 0.1:  # 10% mutation rate
                    self._swap_mutation(ind)
            
            # Replacement
            population = self._survivor_selection(population, offspring, fitness)
            
        # Return best
        best = min(population, key=lambda ind: self._fitness(ind))
        return best
    
    def _ox1_crossover(self, p1, p2):
        """Order Crossover 1"""
        size = len(p1)
        pt1, pt2 = sorted(np.random.choice(size, 2, replace=False))
        
        child1 = [None] * size
        child2 = [None] * size
        
        # Copy segment
        child1[pt1:pt2+1] = p1[pt1:pt2+1]
        child2[pt1:pt2+1] = p2[pt1:pt2+1]
        
        # Fill remaining
        def fill_child(child, parent):
            idx = 0
            for gene in parent:
                if gene not in child:
                    while child[idx] is not None:
                        idx += 1
                    child[idx] = gene
        
        fill_child(child1, p2)
        fill_child(child2, p1)
        
        return child1, child2
```

## 5. Defect Detection (Kusur Tespiti)

### 5.1 Computer Vision ile Cam Kusurları
```python
import cv2
import numpy as np
from tensorflow import keras

class GlassDefectDetector:
    """Cam kusurlarını tespit eden CNN modeli"""
    
    def __init__(self, model_path='models/defect_detector.h5'):
        self.model = keras.models.load_model(model_path)
        self.classes = ['clean', 'scratch', 'bubble', 'crack', 'inclusion']
        
    def preprocess(self, image):
        """Görüntüyü ön işle"""
        img = cv2.resize(image, (224, 224))
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)
        return img
    
    def detect(self, image):
        """Kusur tespiti"""
        preprocessed = self.preprocess(image)
        predictions = self.model.predict(preprocessed)
        
        class_idx = np.argmax(predictions[0])
        confidence = predictions[0][class_idx]
        
        return {
            'class': self.classes[class_idx],
            'confidence': float(confidence),
            'all_scores': dict(zip(self.classes, predictions[0].tolist()))
        }
    
    def detect_with_location(self, image, grid_size=10):
        """Görüntüyü grid'e bölüp her bölgeyi kontrol et"""
        h, w = image.shape[:2]
        grid_h, grid_w = h // grid_size, w // grid_size
        
        defects = []
        for i in range(grid_size):
            for j in range(grid_size):
                x, y = j * grid_w, i * grid_h
                patch = image[y:y+grid_h, x:x+grid_w]
                result = self.detect(patch)
                
                if result['class'] != 'clean' and result['confidence'] > 0.7:
                    defects.append({
                        'x': x + grid_w // 2,
                        'y': y + grid_h // 2,
                        **result
                    })
        
        return defects
```

### 5.2 Kusur Haritası Oluşturma
```python
def create_defect_map(defects, sheet_width, sheet_height):
    """
    Kusur haritası oluştur
    Kesim planlamasında kusurlu bölgelerden kaçınmak için kullanılır
    """
    defect_map = np.zeros((sheet_height, sheet_width), dtype=np.float32)
    
    for defect in defects:
        x, y = int(defect['x']), int(defect['y'])
        
        # Kusur tipine göre ağırlık
        severity = {
            'scratch': 0.3,
            'bubble': 0.5,
            'crack': 1.0,
            'inclusion': 0.7
        }.get(defect['class'], 0.5)
        
        # Gaussian blur ile etki alanı oluştur
        sigma = 50 * severity
        for dy in range(-int(3*sigma), int(3*sigma)+1):
            for dx in range(-int(3*sigma), int(3*sigma)+1):
                nx, ny = x + dx, y + dy
                if 0 <= nx < sheet_width and 0 <= ny < sheet_height:
                    dist = np.sqrt(dx**2 + dy**2)
                    defect_map[ny, nx] += severity * np.exp(-dist**2 / (2*sigma**2))
    
    # Normalize
    defect_map = np.clip(defect_map, 0, 1)
    
    return defect_map

def optimize_cutting_around_defects(cuts, defect_map, margin=50):
    """
    Kesim yollarını kusurlardan uzaklaştır
    """
    optimized_cuts = []
    
    for cut in cuts:
        x1, y1, x2, y2 = cut
        
        # Kesim boyuncakusur kontrolü
        num_points = int(np.sqrt((x2-x1)**2 + (y2-y1)**2))
        x_vals = np.linspace(x1, x2, num_points)
        y_vals = np.linspace(y1, y2, num_points)
        
        max_defect = 0
        for x, y in zip(x_vals, y_vals):
            if 0 <= int(y) < defect_map.shape[0] and 0 <= int(x) < defect_map.shape[1]:
                max_defect = max(max_defect, defect_map[int(y), int(x)])
        
        if max_defect > 0.5:
            # Bu kesim kusurlu bölgeden geçiyor, alternatif ara
            # (Basit offset örneği)
            offset = margin * (1 - max_defect)
            # Normal vektör hesapla
            dx, dy = x2 - x1, y2 - y1
            length = np.sqrt(dx**2 + dy**2)
            nx, ny = -dy / length, dx / length  # Normal
            
            optimized_cuts.append((
                x1 + nx * offset, y1 + ny * offset,
                x2 + nx * offset, y2 + ny * offset
            ))
        else:
            optimized_cuts.append(cut)
    
    return optimized_cuts
```

## 6. Python Modül Kurulumu

### 6.1 requirements.txt
```
numpy>=1.21.0
scipy>=1.7.0
scikit-learn>=1.0.0
torch>=1.9.0
tensorflow>=2.6.0
opencv-python>=4.5.0
deap>=1.3.0
matplotlib>=3.4.0
pandas>=1.3.0
```

### 6.2 Ana Optimizer Sınıfı
```python
# optimizer.py
from typing import List, Dict, Tuple
import numpy as np

class GlassCuttingOptimizer:
    """
    Ana optimizasyon sınıfı
    Tüm optimizasyon adımlarını yönetir
    """
    
    def __init__(self, sheet_width: int, sheet_height: int):
        self.sheet_w = sheet_width
        self.sheet_h = sheet_height
        self.defect_detector = GlassDefectDetector()
        self.path_optimizer = None
        
    def optimize(self, 
                 orders: List[Dict],
                 defects: List[Dict] = None) -> Dict:
        """
        Tam optimizasyon pipeline'ı
        
        Args:
            orders: Sipariş listesi [{width, height, quantity, priority}, ...]
            defects: Kusur bilgileri (opsiyonel)
            
        Returns:
            Optimizasyon sonucu {
                'placed_parts': [...],
                'cutting_path': [...],
                'utilization': 0.95,
                'waste': 0.05
            }
        """
        # 1. Kusur haritası oluştur
        if defects:
            defect_map = create_defect_map(defects, self.sheet_w, self.sheet_h)
        else:
            defect_map = None
        
        # 2. Nesting optimizasyonu
        packer = GuillotinePacker(self.sheet_w, self.sheet_h)
        placed_parts = self._nest_parts(orders, packer, defect_map)
        
        # 3. Kesim yolu optimizasyonu
        cuts = [(p[0], p[1], p[0]+p[2], p[1]+p[3]) for p in placed_parts]
        self.path_optimizer = CuttingPathOptimizer(cuts)
        optimal_path = self.path_optimizer.optimize_2opt()
        
        # 4. İstatistikler
        total_area = self.sheet_w * self.sheet_h
        used_area = sum(p[2] * p[3] for p in placed_parts)
        utilization = used_area / total_area
        
        return {
            'placed_parts': placed_parts,
            'cutting_path': optimal_path,
            'utilization': utilization,
            'waste': 1 - utilization,
            'num_cuts': len(optimal_path)
        }
    
    def _nest_parts(self, orders, packer, defect_map=None):
        """Parçaları yerleştir"""
        placed = []
        
        # Priority'ye göre sırala
        sorted_orders = sorted(orders, key=lambda x: x.get('priority', 0), reverse=True)
        
        for order in sorted_orders:
            for _ in range(order['quantity']):
                result = packer.insert(order['width'], order['height'], rotation=True)
                if result:
                    placed.append((result[0], result[1], order['width'], order['height']))
        
        return placed
    
    def export_gcode(self, result: Dict, output_file: str):
        """G-kod dosyası oluştur"""
        with open(output_file, 'w') as f:
            f.write("; Lisec GFB 60-30 Cam Kesme\n")
            f.write("; Generated by AI Optimizer\n\n")
            f.write("G21 ; Metric\n")
            f.write("G90 ; Absolute positioning\n\n")
            
            path = result['cutting_path']
            placed = result['placed_parts']
            
            for i, idx in enumerate(path):
                x1, y1, x2, y2 = placed[idx][0], placed[idx][1], \
                                 placed[idx][0]+placed[idx][2], placed[idx][1]+placed[idx][3]
                
                # Hızlı hareket başlangıca
                f.write(f"G00 X{x1} Y{y1}\n")
                # Kesim hareketi
                f.write(f"G01 X{x2} Y{y2} F1000\n")
                
            f.write("\nG00 X0 Y0 ; Home\n")
            f.write("M30 ; End program\n")
```

## 7. Kullanım Örneği

```python
# main.py
from optimizer import GlassCuttingOptimizer
import cv2

# 1. Optimizer oluştur (6000x3000 mm sheet)
optimizer = GlassCuttingOptimizer(6000, 3000)

# 2. Siparişler
orders = [
    {'width': 500, 'height': 400, 'quantity': 10, 'priority': 1},
    {'width': 300, 'height': 200, 'quantity': 20, 'priority': 2},
    {'width': 800, 'height': 600, 'quantity': 5, 'priority': 1},
]

# 3. Opsiyonel: Kusur tespiti
image = cv2.imread('glass_sheet.jpg')
defects = optimizer.defect_detector.detect_with_location(image)

# 4. Optimizasyon çalıştır
result = optimizer.optimize(orders, defects)

print(f"Utilization: {result['utilization']*100:.1f}%")
print(f"Waste: {result['waste']*100:.1f}%")
print(f"Number of cuts: {result['num_cuts']}")

# 5. G-kod export
optimizer.export_gcode(result, 'output.nc')
```

## 8. Performans Metrikleri

| Metrik | Hedef | Açıklama |
|--------|-------|----------|
| Utilization | >95% | Levha kullanım oranı |
| Optimization Time | <30s | Optimizasyon süresi |
| Path Length | Minimum | Toplam kesim yolu |
| Defect Avoidance | >90% | Kusurlardan kaçınma |

## 9. Dosya Yapısı

```
AI/
├── Optimization/
│   ├── optimizer.py          # Ana optimizasyon sınıfı
│   ├── nesting.py            # 2D yerleştirme algoritmaları
│   ├── path_planning.py      # Kesim yolu optimizasyonu
│   └── requirements.txt      # Python bağımlılıkları
├── Vision/
│   ├── defect_detector.py    # Kusur tespiti CNN
│   ├── preprocessing.py      # Görüntü ön işleme
│   └── models/               # Eğitilmiş modeller
└── Tests/
    ├── test_nesting.py
    ├── test_path.py
    └── test_vision.py