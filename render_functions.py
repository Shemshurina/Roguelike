# отвечает за шкалу здоровья
from __future__ import annotations

from typing import Tuple, TYPE_CHECKING

import color

if TYPE_CHECKING:
    from tcod import Console
    from engine import Engine
    from game_map import GameMap

def get_names_at_location(x: int, y: int, game_map: GameMap) -> str:
   if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
       return ""

   names = ", ".join(
       entity.name for entity in game_map.entities if entity.x == x and entity.y == y
   )

   return names.capitalize()
# get_names_at_location возвращает имена объектов (с большой буквы) 


def render_bar(   #шкала здоровья
    console: Console, current_value: int, maximum_value: int, total_width: int
) -> None:
    bar_width = int(float(current_value) / maximum_value * total_width)

    console.draw_rect(x=0, y=47, width=20, height=1, ch=1, bg=color.bar_empty) #рисует красную полосу

    if bar_width > 0:
        console.draw_rect(
            x=0, y=47, width=bar_width, height=1, ch=1, bg=color.bar_filled #рисует зеленую поверх красной
        )

    console.print(
        x=1, y=47, string=f"HP: {current_value}/{maximum_value}", fg=color.bar_text
    )

def render_spaceship_level(
    console: Console, dungeon_level: int, location: Tuple[int, int]
 ) -> None:
    """
    Отображает на каком этаже персонаж.
    """
    x, y = location

    console.print(x=x, y=y, string=f"Floor: {dungeon_level}")

def render_names_at_mouse_location(
   console: Console, x: int, y: int, engine: Engine
) -> None:
   mouse_x, mouse_y = engine.mouse_location

   names_at_mouse_location = get_names_at_location(
       x=mouse_x, y=mouse_y, game_map=engine.game_map
   )

   console.print(x=x, y=y, string=names_at_mouse_location)

def render_help(
    console: Console, location: Tuple[int, int]
 ) -> None:

    x, y = location

    console.print(x=x, y=y, string=f"Hints:", fg=color.help_mes)
    console.print(x=x, y=y+1, string=f"- Use TAB to see the controls", fg=color.help_mes)
    console.print(x=x, y=y+2, string=f"- You can hit a monster just", fg=color.help_mes)
    console.print(x=x, y=y+3, string=f"by walking at it", fg=color.help_mes)

