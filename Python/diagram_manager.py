#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from pathlib import Path
import xml.etree.ElementTree as ET
import uuid

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="uml_generator.log"
)
logger = logging.getLogger("diagram_manager")

class ClassData:
    def __init__(self, name, fields, methods, base_class, associations):
        self.name = name
        self.fields = fields
        self.methods = methods
        self.base_class = base_class
        self.associations = associations

class DiagramManager:
    """Клас для роботи з діаграмами drawio через XML."""

    def __init__(self):
        self.root = None
        self.diagram_element = None
        self.mxgraph_model = None
        self.filepath = None
        
        # Стилі для елементів діаграми (з прикладу drawpyo)
        self.class_style = "swimlane;whiteSpace=wrap;rounded=0;dashed=0;fontStyle=1;childLayout=stackLayout;startSize=40;horizontalStack=0;horizontal=1;resizeParent=1;resizeParentMax=0;resizeLast=0;collapsible=1;marginButtom=0;html=1;align=center;verticalAlign=top;marginBottom=0;"
        self.horizontal_line_style = "line;whiteSpace=wrap;rounded=0;fillColor=none;strokeColor=inherit;dashed=0;strokeWidth=1;align=left;verticalAlign=middle;spacingTop=-1;spacingLeft=3;spacingRight=3;rotatable=0;labelPosition=right;points=[];portConstraint=eastwest;"
        self.item_style = "text;whiteSpace=wrap;rounded=0;fillColor=none;strokeColor=none;dashed=0;align=left;verticalAlign=top;spacingLeft=4;spacingRight=4;overflow=hidden;rotatable=0;points=[[0,0.5],[1,0.5]];portConstraint=eastwest;html=1;"
        self.association_style = "curved=1;endArrow=classic;html=1;rounded=0;"
        self.double_association_style = "curved=1;startArrow=classic;endArrow=classic;html=1;rounded=0;"
        self.extends_style = "endArrow=block;endSize=16;endFill=0;html=1;rounded=0;"

        # Лічильники для позиціонування
        self.current_x = 50
        self.current_y = 50

    def _generate_id(self):
        """Генерує унікальний ID для елементів діаграми."""
        return str(uuid.uuid4().int)[:12]  # Використовуємо числовий ID як в drawpyo

    def _create_empty_diagram(self):
        """Створює пусту структуру діаграми."""
        # Корневий елемент (як в прикладі drawpyo)
        self.root = ET.Element("mxfile")
        self.root.set("host", "Python Script")
        self.root.set("modified", "2025-05-25T16:04:28")
        self.root.set("agent", "Python 3.x, Custom XML")
        self.root.set("version", "21.6.5")
        self.root.set("type", "device")
        
        # Діаграма
        self.diagram_element = ET.SubElement(self.root, "diagram")
        self.diagram_element.set("name", "Page-1")
        self.diagram_element.set("id", self._generate_id())
        
        # Створюємо mxGraphModel (як в прикладі)
        self.mxgraph_model = ET.SubElement(self.diagram_element, "mxGraphModel")
        self.mxgraph_model.set("dx", "2037")
        self.mxgraph_model.set("dy", "830")
        self.mxgraph_model.set("grid", "1")
        self.mxgraph_model.set("gridSize", "10")
        self.mxgraph_model.set("guides", "1")
        self.mxgraph_model.set("toolTips", "1")
        self.mxgraph_model.set("connect", "1")
        self.mxgraph_model.set("arrows", "1")
        self.mxgraph_model.set("fold", "1")
        self.mxgraph_model.set("page", "1")
        self.mxgraph_model.set("pageScale", "1")
        self.mxgraph_model.set("pageWidth", "850")
        self.mxgraph_model.set("pageHeight", "1100")
        self.mxgraph_model.set("math", "0")
        self.mxgraph_model.set("shadow", "0")
        
        # Кореневий об'єкт
        root_obj = ET.SubElement(self.mxgraph_model, "root")
        
        # Додаємо базові елементи (0 та 1)
        cell_0 = ET.SubElement(root_obj, "mxCell", id="0")
        cell_1 = ET.SubElement(root_obj, "mxCell", id="1", parent="0")

    def open_diagram_or_create(self, filepath):
        """
        Відкриває існуючу діаграму або створює нову, якщо файл не існує.
        
        Args:
            filepath (str): Шлях до файлу діаграми.
            
        Returns:
            bool: True, якщо діаграма успішно відкрита або створена, інакше False.
        """
        try:
            if not os.path.isabs(filepath):
                current_dir = os.path.dirname(os.path.abspath(__file__))
                self.filepath = os.path.join(current_dir, filepath)
            else:
                self.filepath = filepath
            
            path = Path(self.filepath)
            
            if path.exists():
                logger.info(f"Відкриваємо існуючу діаграму: {filepath}")
                
                # Читаємо існуючий файл
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Парсимо XML
                self.root = ET.fromstring(content)
                self.diagram_element = self.root.find('diagram')
                
                if self.diagram_element is not None:
                    self.mxgraph_model = self.diagram_element.find('mxGraphModel')
                    if self.mxgraph_model is None:
                        logger.error("Не знайдено mxGraphModel у діаграмі")
                        return False
                else:
                    logger.error("Не знайдено елемент diagram")
                    return False
                
            else:
                logger.info(f"Створюємо нову діаграму: {filepath}")
                self._create_empty_diagram()
            
            return True
            
        except Exception as e:
            logger.error(f"Помилка при відкритті/створенні діаграми: {e}")
            return False

    def save_diagram(self):
        """
        Зберігає діаграму у файл.
        
        Returns:
            bool: True, якщо діаграма успішно збережена, інакше False.
        """
        try:
            if self.root is None:
                logger.error("Діаграма не ініціалізована")
                return False
            
            # Створюємо директорію, якщо вона не існує
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            
            # Записуємо файл
            tree = ET.ElementTree(self.root)
            ET.indent(tree, space="  ", level=0)
            tree.write(self.filepath, encoding='utf-8', xml_declaration=True)
            
            logger.info(f"Діаграму збережено: {self.filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Помилка при збереженні діаграми: {e}")
            return False

    def _add_cell_to_model(self, cell_id, value="", style="", geometry=None, parent="1", vertex="1", source=None, target=None, edge=None):
        """Додає нову клітинку до моделі діаграми."""
        root_obj = self.mxgraph_model.find('root')
        if root_obj is None:
            logger.error("Не знайдено кореневий об'єкт у моделі")
            return None
        
        # Створюємо нову клітinку
        cell = ET.SubElement(root_obj, "mxCell")
        cell.set("id", cell_id)
        cell.set("value", value)
        cell.set("style", style)
        cell.set("vertex", vertex)
        cell.set("parent", parent)
        if source is not None:
            cell.set("source", source)
        if target is not None:
            cell.set("target", target)
        if edge is not None:
            cell.set("edge", edge)

        # Додаємо геометрію, якщо вказана
        if geometry:
            geom = ET.SubElement(cell, "mxGeometry")
            geom.set("x", str(geometry.get('x', 0)))
            geom.set("y", str(geometry.get('y', 0)))
            geom.set("width", str(geometry.get('width', 100)))
            geom.set("height", str(geometry.get('height', 50)))
            geom.set("as", "geometry")
        
        return cell
    
    def get_class_full_name(self, name, base_name=None):
        full_name = name
        if base_name is not None:
            full_name = name + "<div>&lt;&lt;" + base_name + "&gt;&gt;</div>"
        return full_name

    def create_class(self, name, base_name=None):
        """Створює контейнер класу."""
        class_id = self._generate_id()

        full_name = self.get_class_full_name(name, base_name)
        
        geometry = {
            'x': self.current_x,
            'y': self.current_y,
            'width': 120,
            'height': 202
        }
        
        cell = self._add_cell_to_model(
            cell_id=class_id,
            value=full_name,
            style=self.class_style,
            geometry=geometry
        )
        
        # Зсуваємо позицію для наступного елементу
        self.current_x += 200
        if self.current_x > 800:
            self.current_x = 50
            self.current_y += 250
        
        return {'id': class_id, 'cell': cell}

    def create_class_item(self, value, parent_id, y=40):
        """Створює елемент класу."""
        item_id = self._generate_id()
        
        geometry = {
            'x': 0,
            'y': y,  # Зсув вниз від заголовка контейнера
            'width': 120,
            'height': 80
        }
        
        cell = self._add_cell_to_model(
            cell_id=item_id,
            value=value,
            style=self.item_style,
            geometry=geometry,
            parent=parent_id
        )
        
        return {'id': item_id, 'cell': cell}

    def create_class_separator(self, parent_id, y=0):
        """Створює розділювач класу."""
        separator_id = self._generate_id()
        
        geometry = {
            'x': 0,
            'y': y,
            'width': 120,
            'height': 2
        }
        
        cell = self._add_cell_to_model(
            cell_id=separator_id,
            value="",
            style=self.horizontal_line_style,
            geometry=geometry,
            parent=parent_id
        )
        
        return {'id': separator_id, 'cell': cell}
    
    def set_data_in_class(self, classData: ClassData):
        """Встановлює дані у клас."""

        find_class = self.find_class(classData.name, classData.base_class)
        if find_class is None:
            classUML = self.create_class(classData.name, classData.base_class)
            if classData.fields is not None:
                self.create_class_item(classData.fields, classUML['id'])
                if classData.methods is not None:
                    self.create_class_separator(classUML['id'], 120)
            if classData.methods is not None:
                self.create_class_item(classData.methods, classUML['id'], 120)
            return self.find_class(classData.name, classData.base_class)
        else:
            items = self.find_class_items(find_class.attrib['id'])
            if classData.fields is not None and classData.methods is not None:
                if len(items) == 3:
                    items[0].set('value', classData.fields)
                    items[2].set('value', classData.methods)
                elif len(items) == 1:
                    items[0].set('value', classData.fields)
                    self.create_class_separator(find_class.attrib['id'], 120)
                    self.create_class_item(classData.methods, find_class.attrib['id'])
                elif len(items) == 0:
                    self.create_class_item(classData.fields, find_class.attrib['id'])
                    self.create_class_separator(find_class.attrib['id'], 120)
                    self.create_class_item(classData.methods, find_class.attrib['id'], 120)
                else:
                    logger.error("Не вірний формат діаграми. Клас: " + classData.name)
            elif classData.fields is not None or classData.methods is not None:
                val = classData.fields
                if val is None:
                    val = classData.methods
                root_obj = self.mxgraph_model.find('root')
                if root_obj is None:
                    logger.error("Не знайдено кореневий об'єкт у моделі")
                    return None
        
                if len(items) == 1:
                    items[0].set('value', val)
                elif len(items) == 0:
                    self.create_class_item(val, find_class.attrib['id'])
                elif len(items) == 3:
                    items[0].set('value', val)
                    root_obj.remove(items[1])
                    root_obj.remove(items[2])
                else:
                    logger.error("Не вірний формат діаграми. Клас: " + classData.name)
        return find_class


    def find_class(self, className, baseClassName):
        """Знаходить клас за ім'ям."""
        root_obj = self.mxgraph_model.find('root')
        if root_obj is None:
            logger.error("Не знайдено кореневий об'єкт у моделі")
            return None
        full_name = self.get_class_full_name(className, baseClassName)
        
        for cell in root_obj.findall('mxCell'):
            if cell.get('value') == full_name:
                return cell
        
        return None
    def find_class_items(self, parent_id):
        root_obj = self.mxgraph_model.find('root')
        if root_obj is None:
            logger.error("Не знайдено кореневий об'єкт у моделі")
            return None
        
        items = []
        for cell in root_obj.findall('mxCell'):
            if cell.get('parent') == parent_id:
                items.append(cell)

        return items
        
    def set_position_for_class(self, classData: ClassData, x, y):
        """Встановлює позицію для класу."""
        class_cell = self.find_class(classData.name, classData.base_class)
        if class_cell is not None:
            class_cell.set('x', str(x))
            class_cell.set('y', str(y))
    
    def set_association(self, sourceClassData: ClassData, targetClassData: ClassData):
        """ <mxCell id="jwncBWTa32pbU5dlyMau-578999791956" value="" style="curved=1;endArrow=classic;html=1;rounded=0;" edge="1" parent="1" source="308272553998" target="230583623881">
                <mxGeometry width="50" height="50" relative="1" as="geometry">
                    <mxPoint as="sourcePoint" />
                    <mxPoint as="targetPoint" />
                </mxGeometry>
            </mxCell>"""
        """Встановлює асоціацію між класами."""


        source_cell = self.find_class(sourceClassData.name, sourceClassData.base_class)
        target_cell = self.find_class(targetClassData.name, targetClassData.base_class)
        
        arrow = self.find_arrow(sourceClassData, targetClassData)
        arrow2 = self.find_arrow(targetClassData, sourceClassData)
        if arrow is None and arrow2 is not None:
            arrow2.set('style', self.double_association_style)
            print(f'Двостороння асоціація: {sourceClassData.name} -> {targetClassData.name}')
            return
        if arrow is not None:
            logger.error("Стрілка між класами вже існує: " + sourceClassData.name + " -> " + targetClassData.name)
            return
        
        if source_cell is not None and target_cell is not None:
            association_id = self._generate_id()
            association_cell = self._add_cell_to_model(
                cell_id=association_id,
                value="",
                style=self.association_style,
                parent="1",
                source=source_cell.attrib['id'],
                target=target_cell.attrib['id'],
                edge="1"
            )
            # MxGeometry
            mxGeometry = ET.SubElement(association_cell, "mxGeometry")
            mxGeometry.set("width", "50")
            mxGeometry.set("height", "50")
            mxGeometry.set("relative", "1")
            mxGeometry.set("as", "geometry")
            mxPoint = ET.SubElement(mxGeometry, "mxPoint")
            mxPoint.set("as", "sourcePoint")
            mxPoint = ET.SubElement(mxGeometry, "mxPoint")
            mxPoint.set("as", "targetPoint")
        else:
            logger.error("Не знайдено класу: " + sourceClassData.name)
            logger.error("Не знайдено класу: " + targetClassData.name)

    def set_extends(self, classData: ClassData, base_classData: ClassData):
        """Встановлює наслідування між класами."""
        """
        <mxCell id="yXxLP0Zb9wQtJZGc93Rl-249139961430" value="Extends" style="endArrow=block;endSize=16;endFill=0;html=1;rounded=0;" edge="1" parent="1" source="249139961429" target="242186206191">
          <mxGeometry width="160" relative="1" as="geometry">
            <mxPoint as="sourcePoint" />
            <mxPoint as="targetPoint" />
          </mxGeometry>
        </mxCell>
        """
        
        arrow = self.find_arrow(base_classData, classData)
        if arrow is not None:
            logger.error("Стрілка між класами вже існує: " + base_classData.name + " -> " + classData.name)
            return
        
        class_cell = self.find_class(classData.name, classData.base_class)
        base_class_cell = self.find_class(base_classData.name, base_classData.base_class)
        

        if class_cell is not None and base_class_cell is not None:
            extends_id = self._generate_id()
            extends_cell = self._add_cell_to_model(
                cell_id=extends_id,
                value="Extends",
                style=self.extends_style,
                parent="1",
                source=base_class_cell.attrib['id'],
                target=class_cell.attrib['id'],
                edge="1"
            )
            # MxGeometry
            mxGeometry = ET.SubElement(extends_cell, "mxGeometry")
            mxGeometry.set("width", "160")
            mxGeometry.set("relative", "1")
            mxGeometry.set("as", "geometry")
            mxPoint = ET.SubElement(mxGeometry, "mxPoint")
            mxPoint.set("as", "sourcePoint")
            mxPoint = ET.SubElement(mxGeometry, "mxPoint")
            mxPoint.set("as", "targetPoint")
        else:
            logger.error("Не знайдено класу: " + classData.name)
            logger.error("Не знайдено класу: " + base_classData.name)

    def find_arrow(self, sourceClassData: ClassData, targetClassData: ClassData):

        source_cell = self.find_class(sourceClassData.name, sourceClassData.base_class)
        target_cell = self.find_class(targetClassData.name, targetClassData.base_class)

        if source_cell is None or target_cell is None:
            logger.error("Не знайдено класу: " + sourceClassData.name)
            logger.error("Не знайдено класу: " + targetClassData.name)
            return None

        """Знаходить стрілку між класами."""
        root_obj = self.mxgraph_model.find('root')
        if root_obj is None:
            logger.error("Не знайдено кореневий об'єкт у моделі")
            return None
        for cell in root_obj.findall('mxCell'):
            if 'source' in cell.attrib and 'target' in cell.attrib and cell.attrib['source'] == source_cell.attrib['id'] and cell.attrib['target'] == target_cell.attrib['id']:
                return cell
        return None

    def create_class_test(self):
        """Створює тестовий клас з елементами."""

        classData = ClassData("ExtendedContainer", "+ elements[]: ElementClass", 
                              "+ test1: int<br/>+ test2: int<br/>+ test3: int<br/>+ test4: int<br/>+ test5: int<br/>+ test6: int<br/>+ test7: int<br/>+ test8: int<br/>+ test9: int<br/>+ test10: int<br/>+ test11: int<br/>+ test12: int<br/>+ test13: int<br/>+ test14: int<br/>+ test15: int<br/>+ test16: int<br/>+ test17: int<br/>+ test18: int<br/>+ test19: int<br/>+ test20: int<br/>", "Container", None)
        self.set_data_in_class(classData)

        classData2 = ClassData("Container", "Hello3", "+ Qweqr()", None, None)
        self.set_data_in_class(classData2)

        classData3 = ClassData("ElementClass", "+ arr: qwe", "+ Qweqr()", None, None)
        self.set_data_in_class(classData3)

        #self.set_association(classData.name, classData2.name)
        self.set_extends(classData2, classData)
        self.set_association(classData3, classData)

        logger.info("Створено тестовий клас з елементами")

    def cleanup_classes(self, class_data_list : list[ClassData]):
        """Видаляє класи, які більше не існують у коді."""

    def cleanup_associations(self, class_data_list : list[ClassData]):
        """Видаляє асоціації, які більше не існують у коді."""
        all_associations = []
        root_obj = self.mxgraph_model.find('root')
        if root_obj is None:
            logger.error("Не знайдено кореневий об'єкт у моделі")
            return None
        
        # Шукаємо всі двосторонні асоціації
        for cell in root_obj.findall('mxCell'):
            style = cell.get('style')
            if style == self.double_association_style or style == self.association_style:
                all_associations.append(cell)

        # Перевіряємо, чи асоціація ще актуальна
        for association in all_associations:
            source_cell = self.find_cell({'id': association.get('source')})
            target_cell = self.find_cell({'id': association.get('target')})
            if source_cell is None or target_cell is None:
                print(f"!Асоціація не має діаграмного елементу: {association.get('source')} -> {association.get('target')}")
                root_obj.remove(association)
                continue

            source_class_data = self.find_class_data_by_cell(source_cell, class_data_list)
            target_class_data = self.find_class_data_by_cell(target_cell, class_data_list)

            if source_class_data is None or target_class_data is None:
                print(f"!Асоціація не має класу: {association.get('source')} -> {association.get('target')}")
                root_obj.remove(association)
                continue

            # Перевіряю, чи асоціація ще двостороння
            find1 = source_class_data in target_class_data.associations
            find2 = target_class_data in source_class_data.associations
            if find1 is False and find2 is False:
                root_obj.remove(association)
                print(f"!Видаляєм асоціацію: {source_class_data.name} -> {target_class_data.name}")
            elif find1 is False:
                if association.get('style') == self.double_association_style:
                    association.set('style', self.association_style)
                    print(f"!Змінюємо на односторонню асоціацію: {source_class_data.name} -> {target_class_data.name}")
            elif find2 is False:
                association.set('style', self.association_style)
                association.set('source', target_cell.get('id'))
                association.set('target', source_cell.get('id'))
                print(f"!Змінюємо на односторонню асоціацію: {target_class_data.name} -> {source_class_data.name}")

    def find_class_data_by_cell(self, cell, class_data_list : list[ClassData]):
        class_name = cell.get('value')
        for class_data in class_data_list:
            if self.get_class_full_name(class_data.name, class_data.base_class) == class_name:
                return class_data
        return None

    # Знаходить елемент за атрибутами та значеннями
    def find_cell(self, attributes : dict[str, str]):
        """Знаходить елемент за атрибутом та значенням."""
        root_obj = self.mxgraph_model.find('root')
        if root_obj is None:
            logger.error("Не знайдено кореневий об'єкт у моделі")
            return None
        for cell in root_obj.findall('mxCell'):
            is_match = True
            for attr, value in attributes.items():
                if cell.get(attr) != value:
                    is_match = False
                    break
            if is_match:
                return cell
        return None

# Ініціалізація менеджера діаграм
manager = DiagramManager()

if __name__ == "__main__":
    # Завантаження або створення діаграми
    test_file = "test_diagram.drawio"
    if not manager.open_diagram_or_create(test_file):
        print("Failed to open or create diagram")
        exit(1)

    manager.create_class_test()

    if manager.save_diagram():
        print(f"Diagram saved successfully to {test_file}")
    else:
        print("Failed to save diagram")