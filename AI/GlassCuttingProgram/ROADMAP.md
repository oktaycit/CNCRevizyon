# Glass Cutting Program - Roadmap 2026

## ✅ Tamamlanan (v1.0)

- [x] Rectangular nesting (Guillotine)
- [x] Path optimization (TSP 2-opt)
- [x] G-Code generation (NC300)
- [x] Lamine glass E-Cam profiles
- [x] Shape cutting (circle, polygon, arc)
- [x] Web interface (6 pages)
- [x] AI orchestration (6 models)
- [x] Offline mode
- [x] Settings management

---

## 🎯 Phase 2: Advanced Features (v2.0)

### 1. DXF/DWG Import (Öncelik: Yüksek)
**Hedef:** AutoCAD DXF dosyalarından şekil import

**Tasks:**
- [ ] DXF parser (ezdxf library)
- [ ] Entity support: LINE, ARC, CIRCLE, POLYLINE
- [ ] Layer filtering
- [ ] Scale & units conversion
- [ ] Preview before import
- [ ] Auto-nesting from DXF

**AI Models:**
- qwen3-coder-plus: DXF parser code
- qwen3-coder-next: Entity conversion
- glm-4.7: Validation

**Tahmini:** 3-4 gün

---

### 2. Vision System Integration (Öncelik: Yüksek)
**Hedef:** Gerçek kusur tespiti

**Tasks:**
- [ ] Camera calibration
- [ ] Image preprocessing (OpenCV)
- [ ] Defect detection CNN
- [ ] Defect classification
- [ ] Defect map generation
- [ ] Auto-avoidance in nesting

**AI Models:**
- qwen3-max: CNN architecture
- qwen3-coder-plus: OpenCV integration
- kimi-k2.5: Documentation

**Hardware:**
- Industrial camera (Basler/Keyence)
- Lighting system
- Trigger sensor

**Tahmini:** 7-10 gün

---

### 3. Database Integration (Öncelik: Orta)
**Hedef:** SQLite ile data persistence

**Tasks:**
- [ ] SQLite schema design
- [ ] Orders table
- [ ] Cutting history table
- [ ] Defects table
- [ ] Users table
- [ ] ORM (SQLAlchemy)
- [ ] Migration scripts

**AI Models:**
- qwen3-coder-plus: Database schema
- qwen3.5-plus: CRUD operations

**Tahmini:** 2-3 gün

---

### 4. User Authentication (Öncelik: Orta)
**Hedef:** Multi-user support

**Tasks:**
- [ ] Login/Register pages
- [ ] JWT token auth
- [ ] Role-based access (Admin, Operator, Viewer)
- [ ] Password hashing (bcrypt)
- [ ] Session management
- [ ] Password reset

**AI Models:**
- qwen3-coder-plus: Auth implementation
- glm-4.7: Security review

**Tahmini:** 2-3 gün

---

### 5. Reports & Analytics (Öncelik: Düşük)
**Hedef:** Cutting history & reports

**Tasks:**
- [ ] Daily/Weekly/Monthly reports
- [ ] Utilization charts
- [ ] Waste analysis
- [ ] PDF export
- [ ] Excel export
- [ ] Print support

**AI Models:**
- qwen3-coder-plus: Report generation
- kimi-k2.5: Report templates

**Tahmini:** 3-4 gün

---

## 🚀 Phase 3: Optimization (v3.0)

### 6. Batch Processing (Çoklu Levha)
**Hedef:** Multiple sheets optimization

**Tasks:**
- [ ] Multi-sheet nesting
- [ ] Remnant management
- [ ] Sheet merging
- [ ] Priority-based cutting
- [ ] Queue management

**Tahmini:** 4-5 gün

---

### 7. Real-time WebSocket (Öncelik: Orta)
**Hedef:** Live machine status

**Tasks:**
- [ ] WebSocket server (Flask-SocketIO)
- [ ] Position streaming
- [ ] Progress updates
- [ ] Alarm notifications
- [ ] Client reconnection

**Tahmini:** 2-3 gün

---

### 8. Mobile Responsive (Öncelik: Düşük)
**Hedef:** Mobile-friendly UI

**Tasks:**
- [ ] Responsive CSS grid
- [ ] Touch-friendly controls
- [ ] Mobile navigation
- [ ] PWA support
- [ ] Offline caching

**Tahmini:** 3-4 gün

---

## 🔮 Phase 4: Advanced AI (v4.0)

### 9. Machine Learning Optimization
**Hedef:** Learning from historical data

**Tasks:**
- [ ] Collect cutting data
- [ ] Feature engineering
- [ ] Train utilization predictor
- [ ] Optimize cutting parameters
- [ ] Defect prediction

**AI Models:**
- All 6 models for different tasks

**Tahmini:** 10-14 gün

---

### 10. Digital Twin
**Hedef:** Virtual machine simulation

**Tasks:**
- [ ] 3D visualization (Three.js)
- [ ] Kinematics simulation
- [ ] Collision detection
- [ ] Cycle time estimation
- [ ] What-if analysis

**Tahmini:** 7-10 gün

---

## 📊 Öncelik Matrisi

| Özellik | Impact | Effort | Priority |
|---------|--------|--------|----------|
| DXF Import | High | Medium | P0 |
| Vision System | High | High | P0 |
| Database | Medium | Low | P1 |
| Auth System | Medium | Low | P1 |
| Reports | Low | Medium | P2 |
| Batch Processing | High | Medium | P1 |
| WebSocket | Medium | Low | P2 |
| Mobile UI | Low | Medium | P3 |

---

## 🎯 Kısa Vadeli Hedefler (2 hafta)

1. **DXF Import** - En çok talep edilen özellik
2. **Database** - Data persistence için gerekli
3. **Reports** - Management reporting için

---

## 📈 Metrikler

| Metrik | Şimdi | Hedef |
|--------|-------|-------|
| Utilization | %50-95% | %98% |
| Max Parts | 100+ | 500+ |
| Shapes | 4 types | 20+ types |
| API Latency | 2-5s | <1s |
| Page Load | 1-2s | <0.5s |

---

**Son Güncelleme:** 2026-04-11
**Versiyon:** 1.0
**Sonraki Milestone:** v2.0 (2026-04-25)