"""Handle the loading and initialization of game sessions."""
from __future__ import annotations

import copy
from typing import Optional

import tcod

import color
from engine import Engine
import entity_factories
from game_map import GameWorld
import input_handlers


background_image = tcod.image.load("menu_background.png")[:, :, :3]


def new_game(lvl: int) -> Engine:
    """Return a brand new game session as an Engine instance."""
    map_width = 100
    map_height = 46

    room_max_size = 16
    room_min_size = 9
    max_rooms = 60

    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player=player)

    engine.game_world = GameWorld(
        engine=engine,
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        lvl=lvl
    )

    engine.game_world.generate_floor()
    engine.update_fov()

    engine.message_log.add_message(
        "Hello and welcome, stranger, to the spaceship!", color.welcome_text
    )
    return engine


class MainMenu(input_handlers.BaseEventHandler):
    """Обрабатывает рендеринг меню и инпут."""

    def on_render(self, console: tcod.Console) -> None:
        """Рендерит главное меню на фоновом изображении."""
        console.draw_semigraphics(background_image, 0, 0)

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "SPACESHIP DEFENDER",
            fg=color.white,
            bg=(34, 2, 87),
            bg_blend=tcod.BKGND_ALPHA(50),
            alignment=tcod.CENTER,
        )
        console.print(
            console.width // 2,
            console.height - 2,
            "By Sasha and Liza",
            fg=color.menu_title,
            alignment=tcod.CENTER,
        )

        menu_width = 24
        for i, text in enumerate(
            ["                                          ",
            " Hello, stranger!                         ", 
            " You are exploring the universe but your  ", 
            " shuttle has been attacked by aliens.     ",
            " They have damaged the system and         ",
            " your mission is to fight the enemies     ",
            " making your way in the darkness. Also,   ",
            " the key of the spaceship has been lost   ",
            " and you will have to find it to continue ",
            " travelling. You'll find some arms and    ",
            " medicine which will help you.            ", 
            "                Good luck!                ",
            "",]
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=color.menu_text,
                bg=color.black,
                alignment=tcod.CENTER,
                bg_blend=tcod.BKGND_ALPHA(64),
            )

        for i, text in enumerate(
            ["    [3] Easy",
             "    [5] Normal",
             "    [8] Hard",
            ]
        ):
            console.print(
                console.width // 2,
                38 + i,
                text.ljust(menu_width),
                fg=(52, 163, 42),
                bg=color.black,
                alignment=tcod.CENTER,
                bg_blend=tcod.BKGND_ALPHA(64),
            )

        for i, text in enumerate(
            ["    [Q] Quit",
            "",]
        ):
            console.print(
                console.width // 2,
                41 + i,
                text.ljust(menu_width),
                fg=(196, 0, 0),
                bg=color.black,
                alignment=tcod.CENTER,
                bg_blend=tcod.BKGND_ALPHA(64),
            )

    def ev_keydown(
        self, event: tcod.event.KeyDown
    ) -> Optional[input_handlers.BaseEventHandler]:
        if event.sym in (tcod.event.K_q, tcod.event.K_ESCAPE):
            raise SystemExit()
        elif event.sym == tcod.event.K_3:
            return input_handlers.MainGameEventHandler(new_game(3))
        elif event.sym == tcod.event.K_5:
            return input_handlers.MainGameEventHandler(new_game(5))
        elif event.sym == tcod.event.K_8:
            return input_handlers.MainGameEventHandler(new_game(8))

        return None