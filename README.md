# Details

```text
  █     █░ ▄▄▄     ▄▄▄█████▓  ██████  ▒█████   ███▄    █
▓█░ █ ░█░▒████▄   ▓  ██▒ ▓▒▒██    ▒ ▒██▒  ██▒ ██ ▀█   █
▒█░ █ ░█ ▒██  ▀█▄ ▒ ▓██░ ▒░░ ▓██▄   ▒██░  ██▒▓██  ▀█ ██▒
░█░ █ ░█ ░██▄▄▄▄██░ ▓██▓ ░   ▒   ██▒▒██   ██░▓██▒  ▐▌██▒
░░██▒██▓ ▒▓█   ▓██  ▒██▒ ░ ▒██████▒▒░ ████▓▒░▒██░   ▓██░
░ ▓░▒ ▒  ░▒▒   ▓▒█  ▒ ░░   ▒ ▒▓▒ ▒ ░░ ▒░▒░▒░ ░ ▒░   ▒ ▒
  ▒ ░ ░  ░ ░   ▒▒     ░    ░ ░▒  ░ ░  ░ ▒ ▒░ ░ ░░   ░ ▒░
  ░   ░    ░   ▒    ░      ░  ░  ░  ░ ░ ░ ▒     ░   ░ ░
    ░          ░                 ░      ░ ░           ░
v 0.1.0
```

[Español](#español) | [English](#english)

---

## Español

Herramienta OSINT + AI (Watson).

> [!NOTE]
> La integración y las funcionalidades de Inteligencia Artificial (IA) se encuentran actualmente en construcción.

### Configuración inicial

1. **Crear archivo de entorno (.env):**
   Para que la herramienta funcione correctamente, necesita un archivo de variables de entorno `.env` con tus credenciales.
   Utiliza la plantilla proporcionada (`.env.test` o `.env.example`) como base:
   
   Copia el archivo de plantilla a un nuevo archivo llamado `.env` en la raíz del proyecto:
   ```bash
   cp .env.example .env
   ```
   *(Nota: Si tu plantilla se llama `.env.test`, utiliza `cp .env.test .env`)*

2. Abre el archivo `.env` recién creado y reemplaza los valores por tus credenciales reales (como `BASE_URL` o `API_TOKEN`).

### Uso

Puedes ejecutar la herramienta de dos formas: en modo interactivo o mediante parámetros en la terminal.

#### Menú Interactivo
Si ejecutas el script sin argumentos, se abrirá un menú interactivo:
```bash
python main_watson.py
```

#### Línea de comandos (CLI)
También puedes realizar consultas directas:
```bash
python main_watson.py --email <correo>
python main_watson.py --ip <direccion_ip>
python main_watson.py --username <usuario>
python main_watson.py --domain <dominio>
```
*(Opcional: puedes añadir el parámetro `--raw` al comando para ver la respuesta completa en crudo del servidor, o usar `--Docs` para ver la ayuda de la herramienta).*

### Gestión de Resultados

Cuando realizas una investigación, la herramienta obtiene los datos, los limpia y los guarda.

- **Carpeta `Results/`:** Automáticamente, la herramienta guardará un archivo JSON con los datos limpios dentro de la carpeta `Results/` (por ejemplo, `Results/resultado_email_usuario_at_correo.com.json`). Si esta carpeta no existe, el programa la creará de manera automática.
- **Privacidad y Control de Versiones:** La carpeta `Results/` está configurada en el archivo `.gitignore`. Esto significa que **ninguno de los resultados JSON que se generen se subirán a tu repositorio**. De esta forma, la información y los datos obtenidos en tus investigaciones se mantendrán completamente privados y guardados de forma local en tu máquina.

---

## English

OSINT + AI Tool (Watson).

> [!NOTE]
> The Artificial Intelligence (AI) integration and features are currently under construction.

### Initial Setup

1. **Create an environment file (.env):**
   For the tool to work properly, it requires an environment variables file `.env` with your credentials.
   Use the provided template (`.env.test` or `.env.example`) as a base:
   
   Copy the template file to a new file named `.env` in the root of the project:
   ```bash
   cp .env.example .env
   ```
   *(Note: If your template is named `.env.test`, use `cp .env.test .env`)*

2. Open the newly created `.env` file and replace the placeholder values with your real credentials (such as `BASE_URL` or `API_TOKEN`).

### Usage

You can run the tool in two ways: in interactive mode or via terminal parameters.

#### Interactive Menu
If you run the script without any arguments, an interactive menu will open:
```bash
python main_watson.py
```

#### Command Line (CLI)
You can also make direct queries:
```bash
python main_watson.py --email <email>
python main_watson.py --ip <ip_address>
python main_watson.py --username <username>
python main_watson.py --domain <domain>
```
*(Optional: you can append the `--raw` parameter to the command to view the complete raw response from the server, or use `--Docs` to see the tool's help).*

### Results Management

When you perform an investigation, the tool fetches the data, cleans it, and saves it.

- **`Results/` Folder:** The tool will automatically save a JSON file with the cleaned data inside the `Results/` folder (e.g., `Results/resultado_email_user_at_email.com.json`). If this folder does not exist, the program will create it automatically.
- **Privacy and Version Control:** The `Results/` folder is configured in the `.gitignore` file. This means that **none of the generated JSON results will be uploaded to your repository**. This way, the information and data obtained in your investigations will remain completely private and stored locally on your machine.