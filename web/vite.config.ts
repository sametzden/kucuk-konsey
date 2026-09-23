import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Kuzgunlar web/ klasörünün dışında (../kuzgunlar). Vite varsayılan olarak proje klasörü dışındaki
// dosyaları sunmaz; bir üst klasöre okuma izni veriyoruz.
export default defineConfig({
  plugins: [react()],
  server: { fs: { allow: ['..'] } },
})
