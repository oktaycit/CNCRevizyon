// Basit PNG ikon oluşturucu - Canvas API kullanır
// Bu dosyayı tarayıcıda açarak ikonları oluşturabilirsiniz

const fs = require('fs');
const path = require('path');

// Not: Gerçek PNG oluşturmak için canvas npm paketi gerekli
// npm install canvas
// Veya generate-icons.html dosyasını tarayıcıda açın

console.log('GlassCutting İkon Oluşturucu');
console.log('============================');
console.log('');
console.log('İkonları oluşturmak için iki seçenek:');
console.log('');
console.log('1. Tarayıcı yöntemi (önerilen):');
console.log('   - icons/generate-icons.html dosyasını Chrome\'da açın');
console.log('   - İkonlar otomatik olarak indirilecek');
console.log('');
console.log('2. Node.js yöntemi:');
console.log('   - npm install canvas');
console.log('   - node generate-icons-node.js');
console.log('');

// Basit placeholder ikonlar oluştur (eğer canvas yoksa)
const sizes = [16, 48, 128];

sizes.forEach(size => {
  const iconPath = path.join(__dirname, `icon${size}.png`);
  
  if (!fs.existsSync(iconPath)) {
    console.log(`⚠️  icon${size}.png bulunamadı`);
    console.log(`   Lütfen generate-icons.html dosyasını tarayıcıda açın`);
  } else {
    console.log(`✓ icon${size}.png mevcut`);
  }
});

console.log('');
console.log('Chrome\'a yüklemek için:');
console.log('1. chrome://extensions/ sayfasına gidin');
console.log('2. "Geliştirici modu"nu açın');
console.log('3. "Paketlenmemiş öğe yükle"ye tıklayın');
console.log('4. GlassCutting klasörünü seçin');
