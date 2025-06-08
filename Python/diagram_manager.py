#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from pathlib import Path
import xml.etree.ElementTree as ET
import uuid
from class_data import ClassData



class DiagramManager:
    """Клас для роботи з діаграмами drawio через XML."""

    def __init__(self, logger : logging.Logger):
        self.root = None
        self.diagram_element = None
        self.mxgraph_model = None
        self.filepath = None
        self.logger = logger

        self.class_style_identifier = "childLayout=stackLayout"
        
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
        self.max_height_on_line = 0

        self.auto_resize = True

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
        self.root_obj = ET.SubElement(self.mxgraph_model, "root")
        
        # Додаємо базові елементи (0 та 1)
        cell_0 = ET.SubElement(self.root_obj, "mxCell", id="0")
        cell_1 = ET.SubElement(self.root_obj, "mxCell", id="1", parent="0")

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
                self.logger.info(f"Відкриваємо існуючу діаграму: {filepath}")
                
                # Читаємо існуючий файл
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Парсимо XML
                self.root = ET.fromstring(content)
                self.diagram_element = self.root.find('diagram')
                
                if self.diagram_element is not None:
                    self.mxgraph_model = self.diagram_element.find('mxGraphModel')
                    if self.mxgraph_model is None:
                        self.logger.error("Не знайдено mxGraphModel у діаграмі")
                        return False
                    self.root_obj = self.mxgraph_model.find('root')
                    if self.root_obj is None:
                        self.logger.error("Не знайдено кореневий об'єкт у моделі")
                        return False
                else:
                    self.logger.error("Не знайдено елемент diagram")
                    return False
                
            else:
                self.logger.info(f"Створюємо нову діаграму: {filepath}")
                self._create_empty_diagram()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Помилка при відкритті/створенні діаграми: {e}")
            return False

    def save_diagram(self):
        """
        Зберігає діаграму у файл.
        
        Returns:
            bool: True, якщо діаграма успішно збережена, інакше False.
        """
        try:
            if self.root is None:
                self.logger.error("Діаграма не ініціалізована")
                return False
            
            # Створюємо директорію, якщо вона не існує
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
            
            # Записуємо файл
            tree = ET.ElementTree(self.root)
            ET.indent(tree, space="  ", level=0)
            tree.write(self.filepath, encoding='utf-8', xml_declaration=True)
            
            self.logger.info(f"Діаграму збережено: {self.filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Помилка при збереженні діаграми: {e}")
            return False

    def _add_user_object(self, tooltip="", cell_id=None, value="", style="", geometry=None, parent="1", vertex="1", source=None, target=None, edge=None):
        userObject = ET.SubElement(self.root_obj, 'UserObject', {'id': cell_id, 'label': value, 'tooltip': tooltip})
        self._add_cell_to_model(root_obj=userObject, cell_id=None, value=None, style=style, geometry=geometry, parent=parent, vertex=vertex, source=source, target=target, edge=edge)
        return userObject

    def _add_cell_to_model(self, root_obj=None, cell_id=None, value="", style="", geometry=None, parent="1", vertex="1", source=None, target=None, edge=None):
        """Додає нову клітинку до моделі діаграми."""
        if root_obj is None:
            root_obj = self.root_obj
        # Створюємо нову клітinку
        cell = ET.SubElement(root_obj, "mxCell")
        if cell_id is not None:
            cell.set("id", cell_id)
        if value is not None:
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


    def create_class(self, classData: ClassData, width, height) -> ET.Element:
        """Створює контейнер класу."""
        class_id = self._generate_id()

        full_name = classData.get_class_full_name()
        
        geometry = {
            'x': self.current_x,
            'y': self.current_y,
            'width': width,
            'height': height
        }
        
        user_object = self._add_user_object(
            cell_id=class_id,
            value=full_name,
            tooltip=classData.class_tooltip,
            style=self.class_style,
            geometry=geometry
        )
        
        # Зсуваємо позицію для наступного елементу
        self.current_x += width + 50
        self.max_height_on_line = max(self.max_height_on_line, height)

        if self.current_x > 1200:
            self.current_x = 50
            self.current_y += self.max_height_on_line + 50
            self.max_height_on_line = 0
        
        return user_object

    def create_class_item(self, value, tooltip, parent_id, y=40, width=300, height=205) -> ET.Element:
        """Створює елемент класу."""
        item_id = self._generate_id()
        
        geometry = {
            'x': 0,
            'y': y,  # Зсув вниз від заголовка контейнера
            'width': width,
            'height': height
        }
        
        user_object = self._add_user_object(
            cell_id=item_id,
            value=value,
            tooltip=tooltip,
            style=self.item_style,
            geometry=geometry,
            parent=parent_id
        )
        
        return user_object

    def create_class_separator(self, parent_id, y=0, width=300) -> ET.Element:
        """Створює розділювач класу."""
        separator_id = self._generate_id()
        
        geometry = {
            'x': 0,
            'y': y,
            'width': width,
            'height': 2
        }
        
        cell = self._add_cell_to_model(
            cell_id=separator_id,
            value="",
            style=self.horizontal_line_style,
            geometry=geometry,
            parent=parent_id
        )
        
        return cell
    
    def set_data_in_class(self, classData: ClassData):
        """Встановлює дані у клас."""

        fields_width, fields_height = classData.get_size_of_fields()
        methods_width, methods_height = classData.get_size_of_methods()

        class_width = max(fields_width, methods_width)
        class_width = max(class_width, ClassData.get_size_of_string(classData.get_class_full_name())[0])
        class_height = 40 + fields_height + methods_height
        if classData.fields is not None and classData.methods is not None:
            class_height += 2

        find_class = classData.class_user_object
        y = 40
        if find_class is None:
            find_class = self.create_class(classData, class_width, class_height)
            classData.class_id = find_class.attrib['id']
            classData.class_user_object = find_class
            if classData.fields is not None:
                classData.first_child = self.create_class_item(classData.fields, classData.fields_tooltip, classData.class_id, y, class_width, fields_height)
                y += fields_height
                if classData.methods is not None:
                    classData.separator_child = self.create_class_separator(classData.class_id, y, class_width)
            if classData.methods is not None:
                classData.second_child = self.create_class_item(classData.methods, classData.methods_tooltip, classData.class_id, y, class_width, methods_height)
            return find_class
        else:
            if classData.fields is not None and classData.methods is not None:
                if classData.first_child is not None and classData.second_child is not None:
                    classData.first_child.set('label', classData.fields)
                    classData.first_child.set('tooltip', classData.fields_tooltip)
                    classData.second_child.set('label', classData.methods)
                    classData.second_child.set('tooltip', classData.methods_tooltip)
                elif classData.first_child is not None:
                    classData.first_child.set('label', classData.fields)
                    classData.first_child.set('tooltip', classData.fields_tooltip)
                    y += fields_height
                    classData.separator_child = self.create_class_separator(classData.class_id, y, class_width)
                    y += 2
                    classData.second_child = self.create_class_item(classData.methods, classData.methods_tooltip, classData.class_id, y, class_width, methods_height)
                else:
                    classData.first_child = self.create_class_item(classData.fields, classData.fields_tooltip, classData.class_id, y, class_width, fields_height)
                    y += fields_height
                    classData.separator_child = self.create_class_separator(classData.class_id, y, class_width)
                    y += 2
                    classData.second_child = self.create_class_item(classData.methods, classData.methods_tooltip, classData.class_id, y, class_width, methods_height)

            elif classData.fields is not None or classData.methods is not None:
                val = classData.fields
                tooltip = classData.fields_tooltip
                if val is None:
                    val = classData.methods
                    tooltip = classData.methods_tooltip
                if classData.first_child is not None and classData.second_child is not None:
                    classData.first_child.set('label', val)
                    classData.first_child.set('tooltip', tooltip)
                    self.remove_cell(classData.separator_child)
                    self.remove_cell(classData.second_child)
                    classData.separator_child = None
                    classData.second_child = None
                elif classData.first_child is not None:
                    classData.first_child.set('label', val)
                    classData.first_child.set('tooltip', tooltip)
                elif classData.first_child is None:
                    classData.first_child = self.create_class_item(val, tooltip, classData.class_id, y, class_width, fields_height)
            else:
                if classData.second_child is not None:
                    self.remove_cell(classData.second_child)
                if classData.separator_child is not None:
                    self.remove_cell(classData.separator_child)
                if classData.first_child is not None:
                    self.remove_cell(classData.first_child)
                classData.first_child = None
                classData.separator_child = None
                classData.second_child = None

        if self.auto_resize:
            self.set_geometry(find_class, width=class_width, height=class_height)
            tmpY = 40
            if classData.first_child is not None:
                tmp_height = fields_height
                if tmp_height == 0:
                    tmp_height = methods_height
                self.set_geometry(classData.first_child, width=class_width, height=tmp_height)
                tmpY += tmp_height
            if classData.separator_child is not None:
                self.set_geometry(classData.separator_child, y_value=tmpY, width=class_width)
                tmpY += 2

            if classData.second_child is not None:
                self.set_geometry(classData.second_child, y_value=tmpY, width=class_width, height=methods_height)

        return find_class
    
    def set_geometry(self, cell : ET.Element, x_value : int | None = None, y_value : int | None = None, width : int | None = None, height : int | None = None):
        
        mxGeometry = cell.find('mxGeometry')
        if mxGeometry is None:
            cell = cell.find('mxCell')
            if cell is None:
                return
            mxGeometry = cell.find('mxGeometry')
            if mxGeometry is None:
                return
        
        if x_value is not None:
            mxGeometry.set('x', str(x_value))
        if y_value is not None:
            mxGeometry.set('y', str(y_value))
        if width is not None:
            mxGeometry.set('width', str(width))
        if height is not None:
            mxGeometry.set('height', str(height))

    
    def set_association(self, sourceClassData: ClassData, targetClassData: ClassData):
        """ <mxCell id="jwncBWTa32pbU5dlyMau-578999791956" value="" style="curved=1;endArrow=classic;html=1;rounded=0;" edge="1" parent="1" source="308272553998" target="230583623881">
                <mxGeometry width="50" height="50" relative="1" as="geometry">
                    <mxPoint as="sourcePoint" />
                    <mxPoint as="targetPoint" />
                </mxGeometry>
            </mxCell>"""
        """Встановлює асоціацію між класами."""


        source_cell = sourceClassData.class_user_object
        target_cell = targetClassData.class_user_object
        
        arrow = self.find_arrow(sourceClassData, targetClassData)
        arrow2 = self.find_arrow(targetClassData, sourceClassData)
        if arrow is None and arrow2 is not None:
            if arrow2.get('style') != self.double_association_style:
                arrow2.set('style', self.double_association_style)
                log = f'!Тепер двостороння асоціація: {sourceClassData.name} <-> {targetClassData.name}'
                print(log)
                self.logger.info(log)
            return
        if arrow is not None:
            return
        
        if source_cell is not None and target_cell is not None:
            log = f'!Створення асоціації: {sourceClassData.name} -> {targetClassData.name}'
            print(log)
            self.logger.info(log)
            association_id = self._generate_id()
            association_cell = self._add_cell_to_model(
                cell_id=association_id,
                value="",
                style=self.association_style,
                parent="1",
                source=sourceClassData.class_id,
                target=targetClassData.class_id,
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
            self.logger.info("Стрілка наслідування між класами вже існує: " + base_classData.name + " -> " + classData.name)
            return
        
        class_cell = classData.class_user_object
        base_class_cell = base_classData.class_user_object
        

        if class_cell is not None and base_class_cell is not None:
            self.logger.info(f"Створення стрілки наслідування: {base_classData.name} -> {classData.name}")

            extends_id = self._generate_id()
            extends_cell = self._add_cell_to_model(
                cell_id=extends_id,
                value="Extends",
                style=self.extends_style,
                parent="1",
                source=base_classData.class_id,
                target=classData.class_id,
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
            self.logger.error("Не знайдено класу target: " + classData.name)
            self.logger.error("Не знайдено класу source: " + base_classData.name)

    def find_arrow(self, sourceClassData: ClassData, targetClassData: ClassData):
        """Знаходить стрілку між класами."""

        source_cell = sourceClassData.class_user_object
        target_cell = targetClassData.class_user_object

        if source_cell is None or target_cell is None:
            self.logger.error("Не знайдено класу source: " + sourceClassData.name)
            self.logger.error("Не знайдено класу target: " + targetClassData.name)
            return None

        for cell in self.root_obj.findall('mxCell'):
            if 'source' in cell.attrib and 'target' in cell.attrib and cell.attrib['source'] == source_cell.attrib['id'] and cell.attrib['target'] == target_cell.attrib['id']:
                return cell
        return None

    def cleanup_classes(self, class_data_list : list[ClassData]):
        """Видаляє класи, які більше не існують у коді."""
        
        classes_to_delete = []
        for userObj in self.root_obj.findall('UserObject'):
            cell = userObj.find('mxCell')
            if cell is not None and 'style' in cell.attrib and self.class_style_identifier in cell.attrib['style']:
                classes_to_delete.append(userObj)

        for class_data in class_data_list:
            for cell in classes_to_delete:
                if class_data.get_class_full_name() == cell.get('label'):
                    classes_to_delete.remove(cell)

        for cell in classes_to_delete:
            print(f"!Видаляємо клас: {cell.get('label')}")
            self.remove_class_and_children(cell.get('id'))
    
    def remove_class_and_children(self, classId : str):
        """Видаляє клас та його дітей, а також стрілки, які на нього вказують."""

        userObjects = self.root_obj.findall('UserObject')
        for userObject in userObjects:
            if userObject.get('id') == classId:
                self.remove_cell(userObject)
                continue
            cell = userObject.find(f'mxCell[@parent="{classId}"]')
            if cell is not None:
                self.remove_cell(userObject)
                continue
        
        cells = self.root_obj.findall('mxCell')
        for cell in cells:
            if cell.get('source') == classId or cell.get('target') == classId or cell.get('parent') == classId:
                self.remove_cell(cell)
                continue


    def cleanup_associations(self, class_data_list : list[ClassData]):
        """Видаляє асоціації, які більше не існують у коді."""
        all_associations = []
        
        # Шукаємо всі двосторонні асоціації
        for cell in self.root_obj.findall('mxCell'):
            style = cell.get('style')
            if style == self.double_association_style or style == self.association_style:
                all_associations.append(cell)

        # Перевіряємо, чи асоціація ще актуальна
        for association in all_associations:
            source_cell = self.find_user_object({'id': association.get('source')})
            target_cell = self.find_user_object({'id': association.get('target')})
            if source_cell is None or target_cell is None:
                log = f"!Асоціація не має діаграмного елементу: {association.get('source')} -> {association.get('target')}"
                print(log)
                self.logger.error(log)
                self.remove_cell(association)
                continue

            source_class_data = self.find_class_data_by_user_object(source_cell, class_data_list)
            target_class_data = self.find_class_data_by_user_object(target_cell, class_data_list)

            if source_class_data is None or target_class_data is None:
                log = f"!Асоціація не має класу: {association.get('source')} -> {association.get('target')}"
                print(log)
                self.logger.error(log)
                self.remove_cell(association)
                continue

            # Перевіряю, чи асоціація ще двостороння
            find1 = source_class_data in target_class_data.associations
            find2 = target_class_data in source_class_data.associations
            if find1 is False and find2 is False:
                self.remove_cell(association)
                log = f"!Видаляєм асоціацію: {source_class_data.name} -> {target_class_data.name}"
                print(log)
                self.logger.error(log)
            elif find1 is False:
                if association.get('style') == self.double_association_style:
                    association.set('style', self.association_style)
                    log = f"!Змінюємо на односторонню асоціацію: {source_class_data.name} -> {target_class_data.name}"
                    print(log)
                    self.logger.error(log)
            elif find2 is False:
                association.set('style', self.association_style)
                association.set('source', target_cell.get('id'))
                association.set('target', source_cell.get('id'))
                
                log = f"!Змінюємо на односторонню асоціацію: {target_class_data.name} -> {source_class_data.name}"
                print(log)
                self.logger.error(log)

    def cleanup_extends(self, class_data_list : list[ClassData]):
        """Видаляє наслідування, які більше не існують у коді."""
        
        extends_to_delete = []
        for cell in self.root_obj.findall('mxCell'):
            if 'style' in cell.attrib and self.extends_style in cell.attrib['style']:
                extends_to_delete.append(cell)
        
        for cell in extends_to_delete:
            source_cell = self.find_user_object({'id': cell.get('source')})
            target_cell = self.find_user_object({'id': cell.get('target')})
            if source_cell is None or target_cell is None:
                log = f"!Наслідування не має діаграмного елементу: {cell.get('source')} -> {cell.get('target')}"
                print(log)
                self.logger.error(log)
                self.remove_cell(cell)
                continue

            base_class_data = self.find_class_data_by_user_object(target_cell, class_data_list)
            class_data = self.find_class_data_by_user_object(source_cell, class_data_list)
            if base_class_data is None or class_data is None:
                log = f"!Наслідування не має класу: {cell.get('source')} -> {cell.get('target')}"
                print(log)
                self.logger.error(log)
                self.remove_cell(cell)
                continue

            if class_data.base_class != base_class_data.name:
                log = f"!Не вірний батьківський клас: {class_data.base_class} -> {class_data.name}"
                print(log)
                self.logger.error(log)
                self.remove_cell(cell)
                continue

    def find_class_data_by_user_object(self, userObject : ET.Element, class_data_list : list[ClassData]):
        class_name = userObject.get('label')
        for class_data in class_data_list:
            if class_data.get_class_full_name() == class_name:
                return class_data
        return None

    # Знаходить елемент за атрибутами та значеннями
    def find_user_object(self, attributes : dict[str, str]):
        """Знаходить елемент за атрибутом та значенням."""

        for userObject in self.root_obj.findall('UserObject'):
            is_match = True
            for attr, value in attributes.items():
                if userObject.get(attr) != value:
                    is_match = False
                    break
            if is_match:
                return userObject
        return None

    def remove_cell(self, cell):
        """Видаляє комірку з моделі."""
        if cell in self.root_obj:
            self.root_obj.remove(cell)

    def megrate_to_user_object(self):
        """Переводить діаграму в об'єкт для користувача."""

        def copy_children(from_cell : ET.Element, to_cell : ET.Element):
            for child in from_cell:
                newChild = ET.SubElement(to_cell, child.tag, child.attrib)
                copy_children(child, newChild)

        cells = self.root_obj.findall('mxCell')
        for cell in cells:
            if not 'value' in cell.attrib or cell.attrib['value'] == "":
                continue
            if not 'style' in cell.attrib or ('endArrow' or 'startArrow') in cell.attrib['style']:
                continue
            self.logger.info(f"Міграція елементу: {cell.get('value')}")
            
            userObject = ET.SubElement(self.root_obj, 'UserObject', {'id': cell.get('id'), 'label': cell.get('value')})
            userObject.set('tooltip', 'Test tooltip')
            
            newSubCell = ET.SubElement(userObject, 'mxCell', cell.attrib)
            newSubCell.attrib.pop('value')
            newSubCell.attrib.pop('id')

            copy_children(cell, newSubCell)

        for cell in cells:
            if not 'value' in cell.attrib or cell.attrib['value'] == "":
                continue
            if not 'style' in cell.attrib or ('endArrow' or 'startArrow') in cell.attrib['style']:
                continue
            self.root_obj.remove(cell)

