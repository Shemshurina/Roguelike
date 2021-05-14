# этот файл отвечает за отрисовку карты и объектов
# и реакцию на действия (input) игрока
# в том числе файл нужен, чтобы разгрузить main

from __future__ import annotations 
from typing import TYPE_CHECKING 


from tcod.console import Console
from tcod.map import compute_fov

import exceptions
from message_log import MessageLog
import render_functions

if TYPE_CHECKING: 
    from entity import Actor 
    from game_map import GameMap, GameWorld


class Engine:
    game_map: GameMap 
    game_world: GameWorld

    def __init__(self, player: Actor): 
        self.message_log = MessageLog()
        self.mouse_location = (0, 0) # здесь ханится информация о местонахождении мыши
        self.player = player

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}: 
            if entity.ai:
                try:
                    entity.ai.perform()
                except exceptions.Impossible:
                    pass  # Игнорирует исключения, возникающие из-за невозможных действий AI.

    def update_fov(self) -> None:
        """Пересчитывает видимую область на основе местонахождения героя."""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8, # радиус отвечает за то, насколько обширным будет поле зрения
        )
        # Если плитка - "visible", она должны быть добавлена к "explored".
        self.game_map.explored |= self.game_map.visible # добавляет увиденные плитки к исследованным
        #(любая плитка, которая была увидена, автоматически считается исследованной)

    def render(self, console: Console) -> None:
        self.game_map.render(console)

        self.message_log.render(console=console, x=21, y=47, width=45, height=7)

        render_functions.render_bar(   
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20,
        )

        render_functions.render_spaceship_level(
            console=console,
            dungeon_level=self.game_world.current_floor,
            location=(0, 49),
        )

        render_functions.render_names_at_mouse_location(
            console=console, x=21, y=46, engine=self
        )
        render_functions.render_help(
            console=console, location=(68, 47)
        )

# render управляет отрисовкой экрана, объектов, шкалы
