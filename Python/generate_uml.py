#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
import argparse
import glob

# Додаємо шлях до директорії з diagram_manager.py
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "UML_scripts"))

# Імпортуємо класи з diagram_manager.py
from diagram_manager import DiagramManager, ClassData

def parse_xml_to_class_data(xml_path) -> list[ClassData]:
    """Парсить XML файл з описом класів і повертає список об'єктів ClassData."""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        class_data_list = []
        
        # Проходимо по всім класам у XML
        for class_elem in root.findall('.//Class'):
            name = class_elem.get('n').replace("<", "&lt;").replace(">", "&gt;")
            base_class =  class_elem.get('b')
            
            # Збираємо поля
            fields_elem = class_elem.find('Fields')
            fields_text = ""
            if fields_elem is not None:
                field_items = fields_elem.findall('Field')
                if field_items:
                    fields_text = "<br/>".join([field.get('v').replace("<", "&lt;").replace(">", "&gt;") for field in field_items if field.get('v')])
            
            # Збираємо методи
            methods_elem = class_elem.find('Methods')
            methods_text = ""
            if methods_elem is not None:
                method_items = methods_elem.findall('Method')
                if method_items:
                    methods_text = "<br/>".join([method.get('v').replace("<", "&lt;").replace(">", "&gt;") for method in method_items if method.get('v')])
            
            if fields_text == "":
                fields_text = None
            if methods_text == "":
                methods_text = None
            
            # Створюємо об'єкт ClassData з порожнім списком асоціацій
            class_data = ClassData(name, fields_text, methods_text, base_class, [])
            class_data_list.append(class_data)
        
        return class_data_list
    
    except Exception as e:
        print(f"Помилка при парсингу XML: {e}")
        return []

def find_class_data_by_name(class_data_list, name):
    """Знаходить об'єкт ClassData за іменем класу."""
    for class_data in class_data_list:
        if class_data.name == name:
            return class_data
    return None

def find_associations(class_data_list):
    """Знаходить асоціації між класами на основі типів полів."""
    
    def process_type(type_str, source_class, depth=0):
        """Рекурсивно обробляє тип та його дженерік-параметри.
        
        Args:
            type_str: Рядок з типом для аналізу
            source_class: Вихідний клас, який містить поле цього типу
            depth: Поточна глибина рекурсії для відступів у виведенні
        """
        # Обробляємо базовий тип
        clean_type = type_str.split("(")[0].split("[")[0].strip()
        target_class = find_class_data_by_name(class_data_list, clean_type)
        if target_class and target_class != source_class:
            # Перевіряємо, чи вже існує така асоціація в списку асоціацій вихідного класу
            if target_class not in source_class.associations:
                source_class.associations.append(target_class)
                indent = "  " * depth
                print(f"{indent}Додано асоціацію: {source_class.name} -> {target_class.name} (з {type_str})")
        
        # Якщо є дженерік-параметри, обробляємо їх
        if "&lt;" in type_str and "&gt;" in type_str:
            # Отримуємо текст між &lt; та &gt;
            generic_params_text = type_str.split("&lt;", 1)[1].split("&gt;", 1)[0]
            # Розбиваємо параметри за комами, враховуючи вкладені дженеріки
            generic_params = []
            current_param = ""
            nested_level = 0
            
            for char in generic_params_text:
                if char == ',' and nested_level == 0:
                    generic_params.append(current_param.strip())
                    current_param = ""
                else:
                    if char == '&lt;':
                        nested_level += 1
                    elif char == '&gt;':
                        nested_level -= 1
                    current_param += char
            
            if current_param:  # Додаємо останній параметр
                generic_params.append(current_param.strip())
            
            # Рекурсивно обробляємо кожен параметр
            for param in generic_params:
                process_type(param, source_class, depth + 1)
    
    # Головний цикл для обробки всіх класів
    for source_class in class_data_list:
        
        if not source_class.fields:
            continue
        
        # Розбиваємо поля на рядки
        field_lines = source_class.fields.split("<br/>")
        
        for field_line in field_lines:
            # Шукаємо тип поля (після двокрапки)
            if ":" in field_line:
                field_parts = field_line.split(":", 1)
                field_type = field_parts[1].strip()
                
                # Обробляємо тип поля та його дженерік-параметри
                process_type(field_type, source_class)
    

def create_uml_diagram(class_data_list : list[ClassData], output_path, cleanup_classes, cleanup_arrows):
    """Створює UML діаграму на основі списку об'єктів ClassData."""
    try:
        # Ініціалізуємо менеджер діаграм
        manager = DiagramManager()
        
        # Відкриваємо існуючу діаграму або створюємо нову
        if not manager.open_diagram_or_create(output_path):
            print(f"Не вдалося відкрити або створити діаграму: {output_path}")
            return False
        
        manager.megrate_to_user_object()
        
        # Спочатку знаходимо всі асоціації між класами
        find_associations(class_data_list)
        
        # Додаємо класи до діаграми
        for class_data in class_data_list:
            manager.set_data_in_class(class_data)
        
        # Додаємо зв'язки наслідування між класами
        for class_data in class_data_list:
            if class_data.base_class:
                base_class_data = find_class_data_by_name(class_data_list, class_data.base_class)
                if base_class_data:
                    manager.set_extends(base_class_data, class_data)
        
        # Додаємо асоціації між класами
        for class_data in class_data_list:
            for target_class in class_data.associations:
                manager.set_association(class_data, target_class)
                print(f"Додано асоціацію: {class_data.name} -> {target_class.name}")

        if cleanup_classes:
            manager.cleanup_classes(class_data_list)
        if cleanup_arrows:
            manager.cleanup_associations(class_data_list)
            manager.cleanup_extends(class_data_list)
        
        # Зберігаємо діаграму
        if manager.save_diagram():
            print(f"Діаграма успішно збережена: {output_path}")
            return True
        else:
            print(f"Не вдалося зберегти діаграму: {output_path}")
            return False
    
    except Exception as e:
        print(f"Помилка при створенні UML діаграми: {e}")
        return False

def parse_arguments():
    """Парсинг аргументів командного рядка."""
    parser = argparse.ArgumentParser(description='Створення UML діаграм з XML файлів')
    parser.add_argument('--input', '-i', required=True, help='Папка з XML файлами')
    parser.add_argument('--output', '-o', required=True, help='Папка для збереження UML діаграм')
    parser.add_argument('--cleanup-classes', action='store_true', help='Автоматично видаляє класи, які більше не існують у коді')
    parser.add_argument('--cleanup-arrows', action='store_true', help='Автоматично видаляє стрілки, які більше не існують у коді')
    return parser.parse_args()

def main():
    # Парсимо аргументи командного рядка
    args = parse_arguments()
    
    # Перевіряємо існування вхідної папки
    if not os.path.exists(args.input):
        print(f"Помилка: Вхідна папка '{args.input}' не існує.")
        return
    
    # Створюємо вихідну папку, якщо вона не існує
    os.makedirs(args.output, exist_ok=True)
    
    # Знаходимо всі XML файли у вхідній папці
    xml_files = glob.glob(os.path.join(args.input, "*.xml"))
    
    if not xml_files:
        print(f"У папці '{args.input}' не знайдено XML файлів.")
        return
    
    print(f"Знайдено {len(xml_files)} XML файлів.")
    
    # Обробляємо кожен XML файл
    for xml_path in xml_files:
        # Отримуємо ім'я файлу без шляху та розширення
        file_name = os.path.basename(xml_path)
        file_name_without_ext = os.path.splitext(file_name)[0]
        
        # Шлях до вихідного файлу drawio
        output_path = os.path.join(args.output, f"{file_name_without_ext}.drawio")
        
        print(f"\nОбробка файлу: {file_name}")
        
        # Парсимо XML і отримуємо список об'єктів ClassData
        class_data_list = parse_xml_to_class_data(xml_path)
        
        if not class_data_list:
            print(f"Не вдалося отримати дані про класи з файлу {file_name}.")
            continue
        
        print(f"Знайдено {len(class_data_list)} класів у файлі {file_name}.")
        
        # Створюємо UML діаграму
        create_uml_diagram(class_data_list, output_path, args.cleanup_classes, args.cleanup_arrows)

if __name__ == "__main__":
    main()
