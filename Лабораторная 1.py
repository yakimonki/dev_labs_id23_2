#!/usr/bin/env python
# coding: utf-8

# In[13]:


from tkinter import *
import math

# Размеры окна и радиус окружности
size = 600
radius = 200

# Создание главного окна
root=Tk()
root.title("Движущаяся точка по окружности")
canvas = Canvas(root, width=size, height=size, bg='white')
canvas.pack()

# Создание окружности
main_circle = canvas.create_oval(300 - 200, 300 - 200, 300 + 200, 300 + 200, fill='pink', outline='white')
# Создание точки
mini_circle = canvas.create_oval(295, 95, 305, 105, fill='blue')

# Переменные для управления движением
direction = 0  # Начальное направление
speed = 5      # Скорость движения 

def moveBall():
    global direction
    # Вычисление координат точки на окружности
    x_direction = 300 + math.cos(math.radians(direction)) * radius
    y_direction = 300 + math.sin(math.radians(direction)) * radius
    # Перемещение точки
    canvas.coords(mini_circle, x_direction - 5, y_direction - 5, x_direction + 5, y_direction + 5)
    # Увеличение угла направления для движения по часовой стрелке
    direction += speed
    # Обеспечение кругового движения
    if direction >= 360:
        direction -= 360
    # Запланировать следующий вызов функции через 50 миллисекунд
    root.after(50, moveBall)

# Запуск движения точки
moveBall()

# Запуск главного цикла
root.mainloop()


# In[ ]:





# In[ ]:




