import subprocess
import webbrowser
import time
import os

# Caminho para o diretório do projeto
project_dir = os.path.dirname(os.path.abspath(__file__))

# Caminho para o venv (um nível acima)
venv_dir = os.path.dirname(project_dir)

# Comando para iniciar o servidor
command = [
    os.path.join(venv_dir, '.venv', 'bin', 'uvicorn'),
    'api.index:app',
    '--host', '0.0.0.0',
    '--port', '8000'
]

# Iniciar o servidor em background
process = subprocess.Popen(command, cwd=project_dir)

# Aguardar um pouco para o servidor iniciar
time.sleep(2)

# Abrir o navegador
webbrowser.open('http://localhost:8000')

# Manter o script rodando
try:
    process.wait()
except KeyboardInterrupt:
    process.terminate()