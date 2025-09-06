# Sistema de Precios de Supermercados

Sistema automatizado para extraer y mostrar precios de productos en supermercados colombianos (Éxito, Jumbo, Carulla) integrado con Unity.

## 🚀 Características

- **Web Scraping**: Extracción automática de precios desde las páginas web de los supermercados
- **Integración Unity**: Componente de Unity que consume los datos automáticamente
- **Actualización en tiempo real**: Los precios se actualizan desde GitHub
- **Fallback integrado**: Datos por defecto si no se puede acceder a la fuente

## 📁 Estructura del proyecto

```
precios-supermercados/
├── scraper_precios.py      # Script Python para extraer precios
├── ActualizarPrecios.cs    # Componente Unity
├── precios.json           # Datos de precios generados
└── README.md              # Este archivo
```

## 🐍 Requisitos Python

```bash
pip install requests beautifulsoup4 selenium
```

También necesitas [ChromeDriver](https://chromedriver.chromium.org/) instalado.

## 💻 Uso

### 1. Extraer precios (Python)
```bash
python scraper_precios.py
```

### 2. Subir a GitHub
```bash
git add precios.json
git commit -m "Actualizar precios"
git push
```

### 3. En Unity
1. Arrastra `ActualizarPrecios.cs` a un GameObject
2. Configura tu nombre de usuario de GitHub en el Inspector
3. Asigna el prefab del panel de precios
4. Los precios se cargarán automáticamente

## 🔧 Configuración Unity

```csharp
// En el Inspector del componente ActualizarPrecios:
Github Usuario: "tu_usuario"
Repositorio: "precios-supermercados" 
Branch: "main"
Archivo: "precios.json"
```

## 📊 Formato de datos JSON

```json
{
  "metadata": {
    "fecha_actualizacion": "2025-01-06T10:30:00",
    "version": "1.0",
    "descripcion": "Precios de supermercados colombianos"
  },
  "entries": [
    {
      "producto": "aceite de oliva sublime 500ml",
      "precios": {
        "exito": 12500,
        "jumbo": 11800,
        "carulla": 13200
      }
    }
  ]
}
```

## 🏷️ Tags Unity requeridas

Asegúrate de que tus productos en Unity tengan:
- **Tag**: `Product`
- **Componente Text**: Con el nombre del producto (debe coincidir con el JSON)
- **Componente Button**: Se agregará automáticamente si no existe

## 🎮 Estructura del prefab del panel

Tu prefab de panel debe tener esta jerarquía:
```
Panel_Supermercados/
├── exito/
│   └── PrecioTextSupermercado (Text)
├── jumbo/
│   └── PrecioTextSupermercado (Text)
└── carulla/
    └── PrecioTextSupermercado (Text)
```

## ⚠️ Solución de problemas

### Error 404 - Archivo no encontrado
- Verifica que el repositorio sea público
- Confirma que `precios.json` esté en la raíz del repositorio
- Revisa tu nombre de usuario en la configuración de Unity

### Error 410 - Recurso eliminado
- La URL puede estar incorrecta
- Verifica el formato: `https://raw.githubusercontent.com/usuario/repo/main/archivo.json`

### No se encuentra el producto
- Los nombres deben coincidir exactamente (no sensible a mayúsculas)
- Revisa que el texto del botón corresponda al nombre en el JSON

### Precios no se muestran
- Verifica la estructura del prefab del panel
- Asegúrate de que los GameObjects se llamen exactamente: `exito`, `jumbo`, `carulla`
- Los textos deben llamarse: `PrecioTextSupermercado`

## 🔄 Automatización

### GitHub Actions (opcional)
Puedes automatizar la actualización de precios creando `.github/workflows/update-prices.yml`:

```yaml
name: Actualizar Precios
on:
  schedule:
    - cron: '0 6 * * *'  # Todos los días a las 6 AM
  workflow_dispatch:

jobs:
  update-prices:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        pip install requests beautifulsoup4 selenium
        sudo apt-get install chromium-browser
    - name: Run scraper
      run: python scraper_precios.py
    - name: Commit changes
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add precios.json
        git commit -m "Actualizar precios automáticamente" || exit 0
        git push
```

## 🛠️ Personalización

### Agregar más productos
En `scraper_precios.py`, agrega productos al diccionario `PRODUCTOS`:

```python
PRODUCTOS = {
    "aceite de oliva sublime 500ml": {
        "exito": "url_exito",
        "jumbo": "url_jumbo", 
        "carulla": "url_carulla"
    },
    "arroz diana 500g": {
        "exito": "url_exito_arroz",
        "jumbo": "url_jumbo_arroz",
        "carulla": "url_carulla_arroz"
    }
    # Agregar más productos aquí...
}
```

### Modificar supermercados
Para agregar más supermercados, actualiza:
1. El diccionario `PRODUCTOS` en Python
2. Los `SELECTORES` CSS en Python  
3. La clase `Precios` en Unity
4. Los métodos de actualización en Unity

## 📈 Mejoras futuras

- [ ] Interfaz web para gestionar productos
- [ ] Base de datos para histórico de precios
- [ ] Notificaciones de ofertas
- [ ] Comparación de precios por categorías
- [ ] API REST para terceros
- [ ] Soporte para más supermercados

## 🤝 Contribuir

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE.md](LICENSE.md) para detalles.

## 🆘 Soporte

Si tienes problemas:
1. Revisa la sección de "Solución de problemas" arriba
2. Verifica los logs de Unity Console
3. Comprueba que Chrome y ChromeDriver estén actualizados
4. Abre un issue en GitHub con detalles del error

---

**Nota**: Este proyecto es solo para fines educativos. Respeta los términos de uso de los sitios web de los supermercados y las políticas de scraping.
