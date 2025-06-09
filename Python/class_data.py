#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import typing


class ClassData:
    def __init__(self, name : str, base_class : str | None, class_tooltip : str):
        self.name : str = name
        self.base_class : str | None = base_class

        self.class_tooltip : str = class_tooltip
        self.fields_tooltip : str = ""
        self.methods_tooltip : str = ""

        self.fields : str | None = None
        self.methods : str | None = None

        self.associations : list["ClassData"] = []
        

        self.class_user_object: ET.Element = None
        self.class_id: str = None
        self.first_child: ET.Element | None = None
        self.separator_child: ET.Element | None = None
        self.second_child: ET.Element | None = None

    def append_field(self, field : str, tooltip : str | None):
        field = field.replace("<", "&lt;").replace(">", "&gt;")
        if tooltip is not None:
            tooltip = tooltip.replace("<", "&lt;").replace(">", "&gt;")
            
            # - damage: float
            short_field = field.split(":")[0]
            short_field = short_field.split(" ")[1]


            if self.fields_tooltip == "":
                self.fields_tooltip = short_field + ": " + tooltip
            else:
                self.fields_tooltip += "<br/>" + short_field + ": " + tooltip
        
        if self.fields is None:
            self.fields = field
        else:
            self.fields += "<br/>" + field

    def append_method(self, method : str, tooltip : str | None):
        method = method.replace("<", "&lt;").replace(">", "&gt;")
        
        if tooltip is not None:
            tooltip = tooltip.replace("<", "&lt;").replace(">", "&gt;")

            # + Enter(): void
            short_method = method.split("(")[0]
            short_method = short_method.split(" ")[1]

            if self.methods_tooltip == "":
                self.methods_tooltip = short_method + "(...): " + tooltip
            else:
                self.methods_tooltip += "<br/>" + short_method + "(...): " + tooltip
        
        if self.methods is None:
            self.methods = method
        else:
            self.methods += "<br/>" + method

    def get_size_of_fields(self) -> tuple[int, int]: 
        return ClassData.get_size_of_string(self.fields)
    
    def get_size_of_methods(self) -> tuple[int, int]: 
        return ClassData.get_size_of_string(self.methods)
    
    def get_size_of_string(string: str | None) -> tuple[int, int]:
        if string is None:
            return 0, 0
        strings = string.replace("&lt;", "<").replace("&gt;", ">").split("<br/>")
        width, height = 50, 20
        for s in strings:
            tmpWidth = 50 + len(s) * 5.3
            if tmpWidth > 450:
                tmpWidth = tmpWidth * 0.66
                height += 14
            width = max(width, tmpWidth)
            height += 14
        width = int(width)
        height = int(height)
        return width, height

    def get_parent(self, class_data_list : typing.List["ClassData"]) -> typing.Union["ClassData", None]:
        for class_data in class_data_list:
            if class_data.name == self.base_class:
                return class_data
        return None

    def get_class_full_name(self):
        full_name = self.name.replace("<", "&lt;").replace(">", "&gt;")
        if self.base_class is not None:
            full_name = full_name + "<br/>&lt;&lt;" + self.base_class + "&gt;&gt;"
        return full_name
    
    def load_data_from_diagram(self, root_obj : ET.Element):
        self.class_user_object = root_obj.find(f'UserObject[@label="{self.get_class_full_name()}"]')
        if self.class_user_object is None:
            return
        
        self.class_id = self.class_user_object.get('id')

        userObjects = root_obj.findall(f'.//UserObject')
        is_first = True
        for userObject in userObjects:
            cell = userObject.find(f'mxCell[@parent="{self.class_id}"]')
            if cell is None:
                continue
            if is_first:
                self.first_child = userObject
                is_first = False
            else:
                self.second_child = userObject

        self.separator_child = root_obj.find(f'mxCell[@parent="{self.class_id}"]')
