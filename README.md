# Metaphorce Web Scraping

Este proyecto contiene scripts para hacer web scraping de ofertas de trabajo de LinkedIn, Indeed y Computrabajo.

## Setup

1. Clona el repositorio en tu máquina local.
2. Crea un archivo `.env` en el directorio raíz del proyecto con las siguientes variables:
```properties
  APP_ID=tu_app_id
  EMAIL=tu_correo
  PASSWORD=tu_contraseña
```

Reemplaza `tu_app_id`, `tu_correo` y `tu_contraseña` con tus datos reales.

3. Instala las bibliotecas requeridas ejecutando el siguiente comando en tu terminal:
```bash
  pip install -r requirements.txt
```


## Ejecución de los Scripts
Cada script se puede ejecutar con dos argumentos opcionales: `keywords` y `job_location`.

Por ejemplo, para ejecutar el scraper de Indeed, usa el siguiente comando:
```bash
  python indeed.py --keywords "Software Engineer" --location "New York"
```
Replace "Software Engineer" and "New York" with your desired job title and location.

Puedes ejecutar los scripts de LinkedIn y Computrabajo de manera similar:
```bash
  python linkedin.py --keywords "Data Scientist" --location "San Francisco"
  python computrabajo.py --keywords "Frontend Developer" --location "Los Angeles"
```

Esto generara archivos `.csv` en la ruta de ejecución, y, en la raíz de tu OneDrive, en una carpeta llamada `Scraping`, que tendrá toda la información solicitada.