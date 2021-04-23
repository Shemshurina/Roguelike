# этот файл отвечает за отрисовку карты и объектов
# и реакцию на действия (input) игрока
# в том числе файл нужен, чтобы разгрузить main

from __future__ import annotations 
from typing import TYPE_CHECKING 


from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov 

from input_handlers import MainGameEventHandler 
from render_functions import render_bar 

if TYPE_CHECKING: 
    from entity import Actor 
    from game_map import GameMap 
    from input_handlers import EventHandler 


class Engine:
    game_map: GameMap 

    def __init__(self, player: Actor): 
        self.event_handler: EventHandler = MainGameEventHandler(self) 
        self.player = player

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}: 
            if entity.ai:
                entity.ai.perform()

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

    def render(self, console: Console, context: Context) -> None:
        self.game_map.render(console)

        render_bar(   
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20,
        )

        context.present(console)

        console.clear()

# render управляет отрисовкой экрана, объектов, шкалы
