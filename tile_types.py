from typing import Tuple

import numpy as np  # type: ignore

# Структурный тип графики плитки совместимый с Console.tiles_rgb
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint.
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors. 3 бита, тк rgb
        ("bg", "3B"),
    ]
)
# ch - герой в формате int, мы переведем его из int в unicode
# fg (foreground) - цвет переднего плана
# bg (bachground) - цвет заднего плана

# Структура для плитки (данные определены и не меняются) 
tile_dt = np.dtype(
    [
        ("walkable", np.bool),  # True если по плитке можно пройти.
        ("transparent", np.bool),  # True если эта плитка не блокирует FOV (поле зрения).
        ("dark", graphic_dt),  # графика для случаев, когда плитка не в FOV.
        ("light", graphic_dt),  # графика для случаев, когда плитка в FOV. 
    ]
)


def new_tile( # def new_tile определяет тип плитки (walkable, transparent, dark)
    *,  
    #Использует ключевые слова, поэтому порядок, в котором идут параметры, не важен.
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    """Вспомогательная функция для определения типа каждой конкретной плитки """
    
    return np.array((walkable, transparent, dark, light), dtype=tile_dt) 

# SHROUD отображает неисследованные, невидимые плитки
# SHROUD используется для отрисовки черной плитки
SHROUD = np.array((ord(" "), (255, 255, 255), (26,1,52)), dtype=graphic_dt)


floor = new_tile(
    walkable=True, 
    transparent=True, 
    dark=(ord(" "), (255, 255, 255), (110,4,161)), 
    light=(ord(" "), (255, 255, 255), (219,149,5)), 
)
wall = new_tile(
    walkable=False, 
    transparent=False,
    dark=(ord(" "), (255, 255, 255), (87, 3, 128)),
    light=(ord(" "), (255, 255, 255), (161,110,4)),
)

down_stairs = new_tile(
   walkable=True,
   transparent=True,
   dark=(ord(">"), (0, 0, 100), (50, 50, 150)),
   light=(ord(">"), (255, 255, 255), (200, 180, 50)),
)


