# Dynamic Page Title System

Sistem title halaman dinamis telah diimplementasikan untuk seluruh aplikasi.

## Cara Kerja

1. **Otomatis**: Title akan berubah secara otomatis berdasarkan route yang aktif
2. **Format**: `[Page Title] - NexClaim`
3. **Fallback**: Jika tidak ada title, akan menggunakan "NexClaim"

## Konfigurasi Route

Setiap route sudah dikonfigurasi dengan meta title:

```javascript
{
  path: '/dashboard',
  component: Dashboard,
  meta: { title: 'Dashboard' }
}
```

## Penggunaan Manual (Opsional)

Jika perlu mengubah title secara dinamis dalam komponen:

```javascript
import { usePageTitle } from '@/composables/usePageTitle'

export default {
  setup() {
    const { setTitle } = usePageTitle()
    
    // Ubah title secara manual
    setTitle('Custom Title')
    
    return { setTitle }
  }
}
```

## File yang Dimodifikasi

- `src/composables/usePageTitle.js` - Composable untuk mengelola title
- `src/App.vue` - Integrasi composable
- `src/router.js` - Penambahan meta title untuk setiap route