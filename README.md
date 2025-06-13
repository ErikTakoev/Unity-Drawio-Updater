# Unity Drawio Updater

🇺🇸 [English](README.md) | 🇺🇦 [Українська](README_UA.md)

![](Readme/Diagram.png)

A convenient tool for automatically creating and updating UML diagrams based on your Unity code. Generates up-to-date class diagrams with complete representation of relationships between your project components, preserving your layout, styles, and arrow configurations.

## Video Presentation

[![Watch the video](https://img.youtube.com/vi/Rfj9ufq07pU/0.jpg)](https://www.youtube.com/watch?v=Rfj9ufq07pU)

## Features

- **Automatic UML diagram creation**: Generate class diagrams based on your Unity project code
- **Layout preservation**: Update existing diagrams without losing element positioning
- **Relationship analysis**: Automatic detection of inheritance and associations between classes
- **Contextual tooltips**: Automatically add tooltips with context for classes, methods, and fields
- **Git integration**: Option to automatically update diagrams after commits
- **Customization**: Flexible parameters to control the diagram generation process

## Installation

1. Add [Unity-AI-Context](https://github.com/ErikTakoev/Unity-AI-Context?tab=readme-ov-file#via-package-manager) to your Unity project via Package Manager.
2. Configure [Unity-AI-Context](https://github.com/ErikTakoev/Unity-AI-Context?tab=readme-ov-file#creating-settings)
3. Add this package to your Unity project via Package Manager
4. Ensure you have Python 3.x installed
5. Create settings through the "Expecto/Drawio Diagram/Create Settings" menu

## Usage

1. Configure parameters through the "Expecto/Drawio Diagram/Open Settings" menu
2. Specify the Python path and output directory for diagrams
3. Generate diagrams through the "Expecto/Drawio Diagram/Generate Drawio Diagram" menu
4. Optional: add a Git hook for automatic diagram updates after commits

## Configuration

- **Python Path**: Path to the Python executable or simply "python" if available in PATH
- **Output Directory**: Directory for saving generated drawio files
- **Cleanup Classes**: Automatically remove classes that no longer exist in the codebase
- **Cleanup Arrows**: Automatically remove arrows for non-existing relationships

## Requirements

- Unity 2019.1 or newer
- Python 3.x
- Draw.io (for viewing generated diagrams)

## Support me and the project!

![](Readme/HelpPlz.jpg)

## Author

[Erik Takoev](https://github.com/ErikTakoev/)