// GlassCutting - Simulation Module
// G-kod görselleştirme ve simülasyon

class GlassCuttingSimulation {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.reset();
  }

  reset() {
    this.position = { x: 0, y: 0, z: 50 };
    this.path = [];
    this.isRunning = false;
    this.isPaused = false;
    this.speed = 1;
    this.glassSize = { width: 3000, height: 2000 };
    this.scale = 1;
    this.offset = { x: 20, y: 20 };
  }

  setGlassSize(width, height) {
    this.glassSize = { width, height };
    this.calculateScale();
  }

  setSpeed(speed) {
    this.speed = speed;
  }

  calculateScale() {
    const availableWidth = this.canvas.width - 40;
    const availableHeight = this.canvas.height - 40;
    
    const scaleX = availableWidth / this.glassSize.width;
    const scaleY = availableHeight / this.glassSize.height;
    
    this.scale = Math.min(scaleX, scaleY);
  }

  toCanvasCoords(x, y) {
    return {
      x: this.offset.x + x * this.scale,
      y: this.canvas.height - this.offset.y - y * this.scale
    };
  }

  draw() {
    this.clear();
    this.drawGrid();
    this.drawGlassArea();
    this.drawPath();
    this.drawPosition();
    this.drawAxes();
  }

  clear() {
    this.ctx.fillStyle = '#1a1a2e';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
  }

  drawGrid() {
    const ctx = this.ctx;
    const gridSize = 50;
    
    ctx.strokeStyle = '#2a2a4e';
    ctx.lineWidth = 1;
    
    for (let x = 0; x < this.canvas.width; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, this.canvas.height);
      ctx.stroke();
    }
    
    for (let y = 0; y < this.canvas.height; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(this.canvas.width, y);
      ctx.stroke();
    }
  }

  drawGlassArea() {
    const ctx = this.ctx;
    const pos = this.toCanvasCoords(0, 0);
    const width = this.glassSize.width * this.scale;
    const height = this.glassSize.height * this.scale;
    
    // Cam alanı
    ctx.strokeStyle = '#4CAF50';
    ctx.lineWidth = 2;
    ctx.strokeRect(pos.x, pos.y - height, width, height);
    
    // Arka plan
    ctx.fillStyle = 'rgba(76, 175, 80, 0.1)';
    ctx.fillRect(pos.x, pos.y - height, width, height);
  }

  drawPath() {
    if (this.path.length < 2) return;
    
    const ctx = this.ctx;
    ctx.strokeStyle = '#ffe66d';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    
    ctx.beginPath();
    const start = this.toCanvasCoords(this.path[0].x, this.path[0].y);
    ctx.moveTo(start.x, start.y);
    
    for (let i = 1; i < this.path.length; i++) {
      const pos = this.toCanvasCoords(this.path[i].x, this.path[i].y);
      ctx.lineTo(pos.x, pos.y);
    }
    
    ctx.stroke();
  }

  drawPosition() {
    const ctx = this.ctx;
    const pos = this.toCanvasCoords(this.position.x, this.position.y);
    
    // Kesim kafası
    ctx.fillStyle = '#ff6b6b';
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, 8, 0, Math.PI * 2);
    ctx.fill();
    
    // Dış halka
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 2;
    ctx.stroke();
    
    // Gölge efekti
    ctx.fillStyle = 'rgba(255, 107, 107, 0.3)';
    ctx.beginPath();
    ctx.arc(pos.x, pos.y, 12, 0, Math.PI * 2);
    ctx.fill();
  }

  drawAxes() {
    const ctx = this.ctx;
    const origin = this.toCanvasCoords(0, 0);
    
    // X ekseni
    ctx.strokeStyle = '#ff6b6b';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(origin.x - 10, origin.y);
    ctx.lineTo(this.canvas.width - 20, origin.y);
    ctx.stroke();
    
    // X oku
    this.drawArrowhead(this.canvas.width - 20, origin.y, 0);
    
    // Y ekseni
    ctx.strokeStyle = '#4ecdc4';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(origin.x, origin.y + 10);
    ctx.lineTo(origin.x, 20);
    ctx.stroke();
    
    // Y oku
    this.drawArrowhead(origin.x, 20, Math.PI);
    
    // Etiketler
    ctx.fillStyle = '#ff6b6b';
    ctx.font = 'bold 14px Arial';
    ctx.fillText('X', this.canvas.width - 35, origin.y - 5);
    
    ctx.fillStyle = '#4ecdc4';
    ctx.fillText('Y', origin.x + 10, 35);
    
    // Başlangıç noktası
    ctx.fillStyle = '#ffe66d';
    ctx.beginPath();
    ctx.arc(origin.x, origin.y, 5, 0, Math.PI * 2);
    ctx.fill();
  }

  drawArrowhead(x, y, angle) {
    const ctx = this.ctx;
    const size = 8;
    
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);
    
    ctx.beginPath();
    ctx.moveTo(-size, -size/2);
    ctx.lineTo(0, 0);
    ctx.lineTo(-size, size/2);
    ctx.fillStyle = ctx.strokeStyle;
    ctx.fill();
    
    ctx.restore();
  }

  parseGCode(gcode) {
    const lines = gcode.split('\n');
    const movements = [];
    let currentPos = { x: 0, y: 0, z: 50 };
    let feedRate = 1000;
    let absoluteMode = true;
    
    lines.forEach(line => {
      line = line.trim();
      if (!line || line.startsWith(';') || line.startsWith('(')) return;
      
      const parts = line.toUpperCase().split(/\s+/);
      let command = null;
      let newPos = { ...currentPos };
      let newFeed = feedRate;
      
      parts.forEach(part => {
        const code = part.substring(0, 2);
        const value = parseFloat(part.substring(2));
        
        if (code === 'G') {
          command = value;
        } else if (code === 'X') {
          newPos.x = absoluteMode ? value : currentPos.x + value;
        } else if (code === 'Y') {
          newPos.y = absoluteMode ? value : currentPos.y + value;
        } else if (code === 'Z') {
          newPos.z = absoluteMode ? value : currentPos.z + value;
        } else if (code === 'F') {
          newFeed = value;
        } else if (code === 'G90') {
          absoluteMode = true;
        } else if (code === 'G91') {
          absoluteMode = false;
        }
      });
      
      if (command === 0 || command === 1) {
        movements.push({
          type: command === 0 ? 'rapid' : 'cut',
          from: { ...currentPos },
          to: { ...newPos },
          feedRate: command === 0 ? 5000 : newFeed
        });
        currentPos = newPos;
        feedRate = newFeed;
      }
    });
    
    return movements;
  }

  simulate(movements, callback) {
    this.isRunning = true;
    this.isPaused = false;
    this.path = [];
    
    let moveIndex = 0;
    let progress = 0;
    
    const animate = () => {
      if (!this.isRunning) return;
      
      if (this.isPaused) {
        requestAnimationFrame(animate);
        return;
      }
      
      if (moveIndex >= movements.length) {
        this.isRunning = false;
        if (callback) callback('complete');
        return;
      }
      
      const move = movements[moveIndex];
      const speedFactor = this.speed * 0.01;
      const step = move.feedRate * speedFactor / 60;
      const distance = Math.sqrt(
        Math.pow(move.to.x - move.from.x, 2) + 
        Math.pow(move.to.y - move.from.y, 2)
      );
      
      if (progress >= distance) {
        this.position = { ...move.to };
        this.path.push({ ...move.to });
        moveIndex++;
        progress = 0;
      } else {
        const ratio = progress / distance;
        this.position.x = move.from.x + (move.to.x - move.from.x) * ratio;
        this.position.y = move.from.y + (move.to.y - move.from.y) * ratio;
        progress += step;
      }
      
      this.draw();
      
      if (callback) {
        callback('progress', {
          currentMove: moveIndex,
          totalMoves: movements.length,
          position: { ...this.position },
          progress: progress / distance
        });
      }
      
      requestAnimationFrame(animate);
    };
    
    animate();
  }

  start(gcode) {
    const movements = this.parseGCode(gcode);
    this.simulate(movements);
    return movements;
  }

  pause() {
    this.isPaused = !this.isPaused;
    return this.isPaused;
  }

  stop() {
    this.isRunning = false;
    this.isPaused = false;
    this.position = { x: 0, y: 0, z: 50 };
    this.path = [];
    this.draw();
  }

  getPosition() {
    return { ...this.position };
  }

  getPath() {
    return [...this.path];
  }

  getTotalDistance() {
    let distance = 0;
    for (let i = 1; i < this.path.length; i++) {
      distance += Math.sqrt(
        Math.pow(this.path[i].x - this.path[i-1].x, 2) + 
        Math.pow(this.path[i].y - this.path[i-1].y, 2)
      );
    }
    return distance;
  }
}

// Export for use in popup
if (typeof module !== 'undefined' && module.exports) {
  module.exports = GlassCuttingSimulation;
}
