# отвечает за шкалу здоровья
from __future__ import annotations

from typing import TYPE_CHECKING

import color

if TYPE_CHECKING:
    from tcod import Console


def render_bar(   #шкала здоровья
    console: Console, current_value: int, maximum_value: int, total_width: int
) -> None:
    bar_width = int(float(current_value) / maximum_value * total_width)

    console.draw_rect(x=0, y=63, width=20, height=1, ch=1, bg=color.bar_empty) #рисует красную полосу

    if bar_width > 0:
        console.draw_rect(
            x=0, y=63, width=bar_width, height=1, ch=1, bg=color.bar_filled #рисует зеленую поверх красной
        )

    console.print(
        x=1, y=63, string=f"HP: {current_value}/{maximum_value}", fg=color.bar_text
    )
