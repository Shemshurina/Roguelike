# ввод с клавиатуры (обработка инпута)
from __future__ import annotations
from typing import Callable, Optional, Tuple, TYPE_CHECKING, Union
import tcod.event

import actions
from actions import (
   Action,
   BumpAction,
   PickupAction,
   WaitAction
)
import color
import exceptions


if TYPE_CHECKING:
    from engine import Engine
    from entity import Item

MOVE_KEYS = {
   # Передвижение с помощью стрелок.
   tcod.event.K_UP: (0, -1),
   tcod.event.K_DOWN: (0, 1),
   tcod.event.K_LEFT: (-1, 0),
   tcod.event.K_RIGHT: (1, 0),
   tcod.event.K_HOME: (-1, -1),
   tcod.event.K_END: (-1, 1),
   tcod.event.K_PAGEUP: (1, -1),
   tcod.event.K_PAGEDOWN: (1, 1),
   # Передвижение с помощью numpad.
   tcod.event.K_KP_1: (-1, 1),
   tcod.event.K_KP_2: (0, 1),
   tcod.event.K_KP_3: (1, 1),
   tcod.event.K_KP_4: (-1, 0),
   tcod.event.K_KP_6: (1, 0),
   tcod.event.K_KP_7: (-1, -1),
   tcod.event.K_KP_8: (0, -1),
   tcod.event.K_KP_9: (1, -1),
   # Передвижение с помощью букв.
   tcod.event.K_h: (-1, 0),
   tcod.event.K_j: (0, 1),
   tcod.event.K_k: (0, -1),
   tcod.event.K_l: (1, 0),
   tcod.event.K_y: (-1, -1),
   tcod.event.K_u: (1, -1),
   tcod.event.K_b: (-1, 1),
   tcod.event.K_n: (1, 1),
}

WAIT_KEYS = {
   tcod.event.K_PERIOD,
   tcod.event.K_KP_5,
   tcod.event.K_CLEAR,
}

CONFIRM_KEYS = {
   tcod.event.K_RETURN,
   tcod.event.K_KP_ENTER,
}

ActionOrHandler = Union[Action, "BaseEventHandler"]
"""Обработчик событий возвращает значение, которое может запустить действие или переключить активные обработчики.

Если обработчик возвращен то он станет активным обработчиком для будущих событий.
Если действие возвращается, оно будет предпринято, и если оно действительно, то
MainGameEventHandler станет активным обработчиком.
"""


class BaseEventHandler(tcod.event.EventDispatch[ActionOrHandler]):
    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Обрабатывает событие и возвращает следующий активный обработчик событий."""
        state = self.dispatch(event)
        if isinstance(state, BaseEventHandler):
            return state
        assert not isinstance(state, Action), f"{self!r} can not handle actions."
        return self

    def on_render(self, console: tcod.Console) -> None:
        raise NotImplementedError()

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()

class EventHandler(BaseEventHandler):
    def __init__(self, engine: Engine):
        self.engine = engine

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Обрабатывает события для input handlers с помощью engine."""
        action_or_state = self.dispatch(event)
        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        if self.handle_action(action_or_state):
            # Совершено правильное действие
            if not self.engine.player.is_alive:
                # Игрок убит во время или после действия.
                return GameOverEventHandler(self.engine)
            return MainGameEventHandler(self.engine)  # Возвращение к основному handler.
        return self

    def handle_action(self, action: Optional[Action]) -> bool:
        """Управляет действиями, возвращенными из event методов.

        Возвращает True если действие продвинет ход.
        """
        if action is None:
            return False

        try:
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.message_log.add_message(exc.args[0], color.impossible)
            return False  # Пропускает ход врага в exceptions.

        self.engine.handle_enemy_turns()

        self.engine.update_fov()
        return True


    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None: # запись информации о местонахождении мыши
        if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
            self.engine.mouse_location = event.tile.x, event.tile.y

    def on_render(self, console: tcod.Console) -> None:
        self.engine.render(console)

class AskUserEventHandler(EventHandler):
   """Управляет инпутами игрока, которые требуют особый инпут."""


   def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
       """По умолчанию любой ключ выходит из этого input handler."""
       if event.sym in {  # Ignore modifier keys.
           tcod.event.K_LSHIFT,
           tcod.event.K_RSHIFT,
           tcod.event.K_LCTRL,
           tcod.event.K_RCTRL,
           tcod.event.K_LALT,
           tcod.event.K_RALT,
       }:
           return None
       return self.on_exit()

   def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
       """По умолчанию любой клик мышью выходит из этого input handler."""
       return self.on_exit()

   def on_exit(self) -> Optional[ActionOrHandler]:
       """Вызывается, когда игрок пытается выйти или отменить действие.

       By default this returns to the main event handler.
       """
       return MainGameEventHandler(self.engine)

class ControlsEventHandler(AskUserEventHandler):
  TITLE = "Controls"
  def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        console.draw_frame(
            x=x,
            y=0,
            width=35,
            height=8,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )
        console.print(x=x + 1, y=1, string="m - to open the message log")
        console.print(x=x + 1, y=2, string="g - to take an item")
        console.print(x=x + 1, y=3, string="i - to open inventory log")
        console.print(x=x + 1, y=4, string="space - to use the stairs")
        console.print(x=x + 1, y=5, string="enter - to use the weapon")


class InventoryEventHandler(AskUserEventHandler):
   """Этот handler позволяет игроку выбирать предмет.

   То, что происходит дальше, зависит от подкласса.
   """

   TITLE = "<missing title>"

   def on_render(self, console: tcod.Console) -> None:
       """Визуализирует меню инвентаря, которое отображает предметы и буквы, с помощью которых можно их выбрать.
       Перемещается в разные места, основываясь на том, где расположен игрок.
       """
       super().on_render(console)
       number_of_items_in_inventory = len(self.engine.player.inventory.items)

       height = number_of_items_in_inventory + 2

       if height <= 3:
           height = 3

       if self.engine.player.x <= 30:
           x = 40
       else:
           x = 0

       y = 0

       width = len(self.TITLE) + 4

       console.draw_frame(
           x=x,
           y=y,
           width=width,
           height=height,
           title=self.TITLE,
           clear=True,
           fg=(255, 255, 255),
           bg=(0, 0, 0),
       )

       if number_of_items_in_inventory > 0:
           for i, item in enumerate(self.engine.player.inventory.items):
               item_key = chr(ord("a") + i)
               console.print(x + 1, y + i + 1, f"({item_key}) {item.name}")
       else:
           console.print(x + 1, y + 1, "(Empty)")

   def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
       player = self.engine.player
       key = event.sym
       index = key - tcod.event.K_a

       if 0 <= index <= 26:
           try:
               selected_item = player.inventory.items[index]
           except IndexError:
               self.engine.message_log.add_message("Invalid entry.", color.invalid)
               return None
           return self.on_item_selected(selected_item)
       return super().ev_keydown(event)

   def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
       """Вызывается, когда игрок выбирает валидный предмет."""
       raise NotImplementedError()

class InventoryActivateHandler(InventoryEventHandler):
   """Управляет использованием предмета инвентаря."""

   TITLE = "Select an item to use"

   def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
       """Возвращает действие для выбранного предмета."""
       return item.consumable.get_action(self.engine.player)

class SelectIndexHandler(AskUserEventHandler):
   """Управляет запрашиванием у игрока указания на карту."""

   def __init__(self, engine: Engine):
       """Устанавливает курсор на текущее местоположение игрока."""
       super().__init__(engine)
       player = self.engine.player
       engine.mouse_location = player.x, player.y

   def on_render(self, console: tcod.Console) -> None:
       """Выделяет (подсвечивает) плитку под курсором."""
       super().on_render(console)
       x, y = self.engine.mouse_location
       console.tiles_rgb["bg"][x, y] = color.white
       console.tiles_rgb["fg"][x, y] = color.black

   def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
       """Проверяет ввод с помощью ключей движения/подтверждения."""
       key = event.sym
       if key in MOVE_KEYS:
           modifier = 1  # Удержание modifier keys (а также удержание shift/control/alt месте с modifier keys) ускорит передвижение курсора с помощью ключей.
           if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
               modifier *= 5
           if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
               modifier *= 10
           if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
               modifier *= 20

           x, y = self.engine.mouse_location
           dx, dy = MOVE_KEYS[key]
           x += dx * modifier
           y += dy * modifier
           # Фиксирует указатель курсора в соответствии с размером карты.
           x = max(0, min(x, self.engine.game_map.width - 1))
           y = max(0, min(y, self.engine.game_map.height - 1))
           self.engine.mouse_location = x, y
           return None
       elif key in CONFIRM_KEYS:
           return self.on_index_selected(*self.engine.mouse_location)
       return super().ev_keydown(event)

   def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
       """Клик левой кнопкой мыши возвращает местонахождение курсора."""
       if self.engine.game_map.in_bounds(*event.tile):
           if event.button == 1:
               return self.on_index_selected(*event.tile)
       return super().ev_mousebuttondown(event)

   def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
       """Вызывается, когда index выбран."""
       raise NotImplementedError()


class LookHandler(SelectIndexHandler):
   """Позволяет игроку осмотрться используя клавиатуру."""

   def on_index_selected(self, x: int, y: int) -> MainGameEventHandler:
       """Возвращается к main handler."""
       return MainGameEventHandler(self.engine)

class SingleRangedAttackHandler(SelectIndexHandler):
   """Целится в одного врага. Только выбранный враг пострадает."""

   def __init__(
       self, engine: Engine, callback: Callable[[Tuple[int, int]], Optional[Action]]
   ):
       super().__init__(engine)

       self.callback = callback

   def on_index_selected(self, x: int, y: int) -> Optional[Action]:
       return self.callback((x, y))

class AreaRangedAttackHandler(SelectIndexHandler):
   """Целится в какую-либо область в заданном радиусе. Любой объект, находящийся в этой области, пострадает."""

   def __init__(
       self,
       engine: Engine,
       radius: int,
       callback: Callable[[Tuple[int, int]], Optional[Action]],
   ):
       super().__init__(engine)

       self.radius = radius
       self.callback = callback

   def on_render(self, console: tcod.Console) -> None:
       """Выделяет плитку под курсором."""
       super().on_render(console)

       x, y = self.engine.mouse_location

       # Рисует прямоугольник вокруг области, к которую целится игрок, так что он может видеть потенциальную зону поражения.
       console.draw_frame(
           x=x - self.radius - 1,
           y=y - self.radius - 1,
           width=self.radius ** 2,
           height=self.radius ** 2,
           fg=color.red,
           clear=False,
       )

   def on_index_selected(self, x: int, y: int) -> Optional[Action]:
       return self.callback((x, y))


class MainGameEventHandler(EventHandler): 
    
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]: 
        action: Optional[Action] = None 

        key = event.sym
        modifier = event.mod

        player = self.engine.player 

        if key == tcod.event.K_SPACE:
            return actions.TakeStairsAction(player)
  
        if key in MOVE_KEYS: 
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        elif key in WAIT_KEYS:
            action = WaitAction(player) 

        elif key == tcod.event.K_ESCAPE:
            raise SystemExit()
        elif key == tcod.event.K_m:
            return HistoryViewer(self.engine)
        elif key == tcod.event.K_g:
            action = PickupAction(player)
        elif key == tcod.event.K_i:
            return InventoryActivateHandler(self.engine)
        elif key == tcod.event.K_SLASH:
            return LookHandler(self.engine)
        elif key == tcod.event.K_TAB:
            return ControlsEventHandler(self.engine)

        # Был нажат невалидный ключ.
        return action

class GameOverEventHandler(EventHandler): 
   def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym == tcod.event.K_ESCAPE:
            raise SystemExit()

CURSOR_Y_KEYS = {
   tcod.event.K_UP: -1,
   tcod.event.K_DOWN: 1,
   tcod.event.K_PAGEUP: -10,
   tcod.event.K_PAGEDOWN: 10,
}


class HistoryViewer(EventHandler):
   """Печатает историю в бОльшем окне, по которому можно перемещаться."""

   def __init__(self, engine: Engine):
       super().__init__(engine)
       self.log_length = len(engine.message_log.messages)
       self.cursor = self.log_length - 1

   def on_render(self, console: tcod.Console) -> None:
       super().on_render(console)  # Рисует основное состояние в качестве фона.

       log_console = tcod.Console(console.width - 6, console.height - 6)

       # Рисует рамку с пользовательским заголовком.
       log_console.draw_frame(0, 0, log_console.width, log_console.height)
       log_console.print_box(
           0, 0, log_console.width, 1, "┤Message history├", alignment=tcod.CENTER
       )

       # Предоставляет журнал сообщений, используя курсор.
       self.engine.message_log.render_messages(
           log_console,
           1,
           1,
           log_console.width - 2,
           log_console.height - 2,
           self.engine.message_log.messages[: self.cursor + 1],
       )
       log_console.blit(console, 3, 3)

   def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[MainGameEventHandler]:
       # Fancy conditional movement to make it feel right.
       if event.sym in CURSOR_Y_KEYS:
           adjust = CURSOR_Y_KEYS[event.sym]
           if adjust < 0 and self.cursor == 0:
               # Only move from the top to the bottom when you're on the edge.
               self.cursor = self.log_length - 1
           elif adjust > 0 and self.cursor == self.log_length - 1:
               # Same with bottom to top movement.
               self.cursor = 0
           else:
               # Otherwise move while staying clamped to the bounds of the history log.
               self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
       elif event.sym == tcod.event.K_HOME:
           self.cursor = 0  # Перемещается сразу к верхнему сообщению.
       elif event.sym == tcod.event.K_END:
           self.cursor = self.log_length - 1  # Перемещается сразу к оследнему сообщению.
       else:  # Любой другой ключ перемещает к основному состоянию игры.
           return MainGameEventHandler(self.engine)
       return None

# "v" открывает журнал сообщений
# "вверх", "вниз" используются для пролистывания сообщений

