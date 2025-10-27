#!/bin/bash

echo "================================================"
echo "AI Agents Lab Setup Script (Linux)"
echo "================================================"
echo ""

# Install Azure CLI
echo "Instalando Azure CLI..."
echo "------------------------------------------------"
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

echo ""
echo "Verificando instalación do Azure CLI..."
if command -v az &> /dev/null; then
    echo "✓ Azure CLI está instalado"
    az version
else
    echo "⚠ Azure CLI no encontrado en PATH. Por favor, instálelo manualmente o reinicie el terminal."
fi

echo ""
echo "------------------------------------------------"

# Check if Python is installed
echo "Verificando instalación do Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    echo "✓ Python3 encontrado: $(python3 --version)"
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    echo "✓ Python encontrado: $(python --version)"
else
    echo "✗ Python no encontrado. Por favor, instálelo manualmente o reinicie el terminal."
    exit 1
fi

echo ""
echo "------------------------------------------------"

# Install Python dependencies
echo "Instalando dependencias de Python..."
echo ""

if [ -f "requirements.txt" ]; then
    echo "Instalando desde requirements.txt..."
    $PYTHON_CMD -m pip install --upgrade pip
    $PYTHON_CMD -m pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✓ Todas las dependencias de Python instaladas correctamente!"
    else
        echo ""
        echo "✗ Fallo al instalar algunas dependencias. Por favor, compruebe los mensajes de error anteriores."
        exit 1
    fi
else
    echo "✗ requirements.txt no encontrado en el directorio actual."
    exit 1
fi

echo ""
echo "================================================"
echo "Setup Completado!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Ejecutar 'az login' para autenticarse con Azure"
echo "2. Configurar el archivo .env "
echo "3. Empezar a trabajar en los laboratorios!"
echo ""

