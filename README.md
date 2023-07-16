# MadnessDescent
This is an roguelite game about slowly descending into madness. In this game you need to pass through all 4 levels, and find out whether you are worthy of salvation.  

# Table of Contents
- [About](#about)
- [Getting Started](#getting_started)
- [Controls](#controls)

# About
The player takes control of the character that can steal weapons from enemies. After stealing a weapon the player can use it a limited number of times, after which you can steal another one. A level consists of a number of randomly generated rooms, which all need to be cleared of enemies to open the boss room. Leaving and re-entering a room respawns all unkilled enemies with full health. In the boss room, there is a unique boss that is dependent on the level. After the boss is defeated, an elevator that can take you further into this twisted world. At each elevator ride, you are offered a choice of 3 perks, which can help you. Also, this game includes a functional minimap and 2 endings, the better of which is achieved by no more than 30 damage.

# Getting Started

There are 2 ways to install our project:

## 1. Using a compiled standalone Windows application

Head to [this link](https://drive.google.com/file/d/1lDcoUUXR5T_G51LqupkCNVunzkQf5ItC/view?usp=sharing) and download the archive. This folder is a copy of dist from the repository
After downloading and un-zipping the folder, launch "Madness Descent.exe" and enjoy!

This method does not require Python to be installed, so you can play the game without complications

## 2. Manually launching the project using Python

Alternatively, you can launch the project using Python, if you want to modify the code:

### 2.1. Install Python
If Python is not already installed on your device, download and install it from the official [Python website](https://www.python.org/downloads).

You can check if pyhton is installed correctly by typing
```cmd
python --version
```
into the terminal. If it does not recognise Python, and you are sure you installed it, add it to PATH by following [this guide](https://www.educative.io/answers/how-to-add-python-to-path-variable-in-windows) 

### 2.2. Install pip
Pip is a package manager for Python packages. It allows you to install and manage additional packages that are not included with Python by default. To install Pip, follow the instructions below:
```bash
python -m ensurepip --upgrade
```

### 2.3. Install pygame
Pygame is a library this project is built on, so you need it to launch the project
```bash
pip install pygame
```

### 2.4. Get the source code and resources
Once you have the access to the code, to get it, use the following command:
```bash
git clone https://github.com/Tedor49/TowerDescent.git
```

### 2.5. Launch the project
Navigate to the repository folder and run
```cmd
python main.py
```

These steps will ensure that you have everything required to be able to install and use the game.

## Controls
W - jump / enter elevator

A - move left

D - mode right

Left Click - use weapon / press menu buttons

Left CLick / 1 2 3 number keys - select perk

F - discard weapon (only possible with perk)

F1 - reset health to full (cheat)
