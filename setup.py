#!/usr/bin/env python3
"""Скрипт для автоматической настройки проекта."""

import os
import sys
from pathlib import Path

def create_directories():
    """Создать необходимые директории."""
    directories = [
        'config',
        'api',
        'models',
        'data',
        'analyzer',
        'storage',
        'cli',
        'tests',
        'data_samples',
        'output',
        'docs'
    ]
    
    print("📁 Создание директорий...")
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  ✓ {directory}/")

def create_init_files():
    """Создать __init__.py файлы."""
    modules = ['config', 'api', 'models', 'data', 'analyzer', 'storage', 'cli', 'tests']
    
    print("\n📝 Создание __init__.py файлов...")
    for module in modules:
        init_file = Path(module) / '__init__.py'
        if not init_file.exists():
            init_file.touch()
            print(f"  ✓ {init_file}")

def check_files():
    """Проверить наличие основных файлов."""
    required_files = [
        'requirements.txt',
        '.env.example',
        '.gitignore',
        'README.md',
        'run.py'
    ]
    
    print("\n✅ Проверка основных файлов...")
    missing_files = []
    for file in required_files:
        if Path(file).exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - ОТСУТСТВУЕТ")
            missing_files.append(file)
    
    return missing_files

def print_next_steps(missing_files):
    """Вывести следующие шаги."""
    print("\n" + "="*60)
    print("🎉 СТРУКТУРА ПРОЕКТА СОЗДАНА!")
    print("="*60)
    
    if missing_files:
        print("\n⚠️  Необходимо добавить следующие файлы:")
        for file in missing_files:
            print(f"  - {file}")
    
    print("\n🚀 СЛЕДУЮЩИЕ ШАГИ:")
    print("\n1. Установите зависимости:")
    print("   pip install -r requirements.txt")
    
    print("\n2. Настройте конфигурацию:")
    print("   cp .env.example .env")
    print("   # Отредактируйте .env и добавьте ваш WB_API_KEY")
    
    print("\n3. Запустите проект:")
    print("   python run.py")
    
    print("\n4. Запустите тесты:")
    print("   python -m pytest tests/")
    
    print("\n📚 Документация:")
    print("   - docs/QUICK_START.md")
    print("   - docs/FORMULAS.md")
    print("   - docs/API.md")
    print("   - README.md")
    print("\n" + "="*60)

def main():
    """Главная функция."""
    print("\n🔧 WB API Formuli Python - Setup")
    print("="*60)
    
    try:
        create_directories()
        create_init_files()
        missing_files = check_files()
        print_next_steps(missing_files)
        
        return 0
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())