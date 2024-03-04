from __future__ import annotations
from enum import Enum
import typing
import urwid

if typing.TYPE_CHECKING:
    from collections.abc import Callable, Hashable, Iterable

from .vms import virtualbox


hostvms = virtualbox("foice")


class SnapshotAction(Enum):
    LIST = 1
    TAKE = 2
    DELETE = 3


def exit_program(button: urwid.Button) -> typing.NoReturn:
    raise urwid.ExitMainLoop()


def execute_esc(button: urwid.Button):
    """usually used in the cancel button"""
    top.keypress(size=0, key="esc")


def create_radio_button(
    g: list[urwid.RadioButton],
    name: str,
    font: urwid.Font,
    fn: Callable[[urwid.RadioButton, bool], typing.Any],
) -> urwid.AttrMap:
    w = urwid.RadioButton(g, name, False, on_state_change=fn)
    if font is not None:
        w.font = font
    w = urwid.AttrMap(w, "button normal", "button select")
    return w


def create_disabled_radio_button(name: str) -> urwid.AttrMap:
    w = urwid.Text(f"{name}")
    w = urwid.AttrMap(w, "button disabled")
    return w


def create_alert(text: str):
    button_canc = menu_button("Cancel", execute_esc)
    top.open_box(urwid.Filler(urwid.Pile([urwid.Text(text), button_canc])))


def menu_button(
    caption: str | tuple[Hashable, str] | list[str | tuple[Hashable, str]],
    callback: Callable[[urwid.Button], typing.Any],
) -> urwid.AttrMap:
    button = urwid.Button(caption, on_press=callback)
    return urwid.AttrMap(button, None, focus_map="reversed")


def sub_menu(
    caption: str | tuple[Hashable, str] | list[str | tuple[Hashable, str]],
    choices: Iterable[urwid.Widget],
) -> urwid.Widget:
    contents = menu(caption, choices)

    def open_menu(button: urwid.Button) -> None:
        return top.open_box(contents)

    return menu_button([caption, "..."], open_menu)


def menu(
    title: str | tuple[Hashable, str] | list[str | tuple[Hashable, str]],
    choices: Iterable[urwid.Widget],
) -> urwid.ListBox:
    body = [urwid.Text(title), urwid.Divider(), *choices]
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))


def item_runningvms(button: urwid.Button) -> None:
    result = hostvms.runningvms()
    text = "Running VMs\n"
    text += "|{}|{}|\n".format("-" * 22, "-" * 42)
    text += "| {:20s} | {:40s} |\n".format("Name", "UUID")
    text += "|{}|{}|\n".format("-" * 22, "-" * 42)
    text += "\n".join([f"| {r['name']:20s} | {r['uid']:40s} |" for r in result])
    text += "\n|{}|{}|\n".format("-" * 22, "-" * 42)
    response = urwid.Text([text])
    done = menu_button("Ok", execute_esc)
    top.open_box(urwid.Filler(urwid.Pile([response, done])))


def item_vms(button: urwid.Button) -> None:
    result = hostvms.vms()
    text = "Configured VMs\n"
    text += "|{}|{}|\n".format("-" * 22, "-" * 42)
    text += "| {:20s} | {:40s} |\n".format("Name", "UUID")
    text += "|{}|{}|\n".format("-" * 22, "-" * 42)
    text += "\n".join([f"| {r['name']:20s} | {r['uid']:40s} |" for r in result])
    text += "\n|{}|{}|\n".format("-" * 22, "-" * 42)
    response = urwid.Text([text])
    done = menu_button("Ok", execute_esc)
    top.open_box(urwid.Filler(urwid.Pile([response, done])))


def item_hostinfo(button: urwid.Button) -> None:
    result = hostvms.hostinfo()
    text = result
    response = urwid.Text([text])
    # done = menu_button("Ok", execute_esc)
    top.open_box(urwid.ScrollBar(urwid.Scrollable(response)))


def start_stop_vms(button: urwid.Button) -> None:
    """

        TODO: change vm selection to CHECKBOX, then this method dispatches all action at the same time

    """
    running = hostvms.runningvms()
    config = hostvms.vms()
    # running = [{"name": "afirewall", "UUID": "aaaaa"}, {"name": "bfirewall", "UUID": "bbbbbb"}]
    # config = [{"name": "afirewall", "UUID": "aaaaa"}, {"name": "bfirewall", "UUID": "bbbbbb"}, {"name": "cfirewall", "UUID": "cccccc"}]
    group = []  # list with the all radio buttons
    can_start = []  # list of the names of the vms that can be started

    rb_start = []  # save the "start" radio buttons widgets
    for r in config:
        if any([x["name"] == r["name"] for x in running]):
            # is running, so cannot be started again
            continue
        rb = create_radio_button(group, r["name"], font=None, fn=None)
        rb_start.append(rb)
        can_start.append(r["name"])

    rb_stop = []
    for r in running:
        rb = create_radio_button(group, r["name"], font=None, fn=None)
        rb_stop.append(rb)

    # Place the "start" and "stop" RBs on two-column format
    p_start = urwid.Pile([urwid.Text("Start:"), *rb_start])
    p_stop = urwid.Pile([urwid.Text("Stop:"), *rb_stop])
    options = urwid.Columns([p_start, p_stop])

    cb_headless = urwid.CheckBox("Start headless (no GUI)", state=True)
    headless = urwid.AttrMap(cb_headless, None, focus_map="reversed")

    cb_force_down = urwid.CheckBox("Force shutdown", state=False)
    force_down = urwid.AttrMap(cb_force_down, None, focus_map="reversed")

    def execute_command(button: urwid.Button):
        action = {"start": [], "stop": []}
        results = f"force={cb_force_down.get_state()}\nheadless={cb_headless.get_state()}\n"
        for r in group:
            if r.state:
                # selected
                if r.label in can_start:
                    action["start"].append(r.label)
                    result = f"start {r.label}"
                    # result = hostvms.start_vm(vmname=r.label, headless=cb_headless.get_state())
                else:
                    action["stop"].append(r.label)
                    result = f"stop {r.label}"
                    # result = hostvms.stop_vm(vmname=r.label, force=cb_force_down.get_state())

                results += result + "\n"

        create_alert(results)

    button_exec = menu_button("Execute command", execute_command)
    button_canc = menu_button("Cancel", execute_esc)

    sep = urwid.Text("")

    top.open_box(urwid.Filler(urwid.Pile([options, sep, headless, sep, force_down, sep, button_exec, button_canc])))


def item_showvminfo(button: urwid.Button) -> None:
    result = hostvms.showvminfo(vmname=button.label)
    text = result
    response = urwid.Text([text])
    top.open_box(urwid.ScrollBar(urwid.Scrollable(response)))


def sub_menu_showvminfo() -> urwid.Widget:
    caption = "VM information"
    choices = [
        menu_button(vm["name"], item_showvminfo) for vm in hostvms.vms()
    ]
    contents = menu(caption, choices)

    def open_menu(button: urwid.Button) -> None:
        return top.open_box(contents)

    return menu_button([caption, "..."], open_menu)


def sub_menu_snapshots(action: SnapshotAction) -> urwid.Widget:

    def item_snapshot_take(button: urwid.Button) -> None:
        result = hostvms.take_snapshot(vmname=button.label)
        create_alert(result)

    def item_snapshot_list(button: urwid.Button) -> None:
        """
            create a group with one checkbox for each snapshot
            after selection, click on "delete" button remove all selected snapshots
        """
        result = hostvms.list_snapshots(vmname=button.label)
        caption = "Snapshots:"
        choices = [
            urwid.Text([f'{r["name"]} {r["uuid"]} {"active" if r["active"] else ""}']) for r in result
        ]
        choices.extend([
            urwid.Text(['']),  # separator
            menu_button("Return", execute_esc)
        ])
        contents = menu(caption, choices)
        top.open_box(contents)

    def item_snapshot_delete(button: urwid.Button) -> None:
        """
            create a group with one checkbox for each snapshot
            after selection, click on "delete" button remove all selected snapshots
        """
        result = hostvms.list_snapshots(vmname=button.label)
        caption = "Snapshots:"
        choices = []
        cbs = dict()
        for r in result:
            text = f'{r["name"]} {r["uuid"]} {"active" if r["active"] else ""}'
            cb = urwid.CheckBox(text, state=False)
            entry = urwid.AttrMap(cb, None, focus_map="reversed")
            cbs[text] = {"checkbox": cb, "vmname": button.label, "snapname": r["name"]}
            choices.append(entry)

        def execute_command(button: urwid.Button):
            results = []
            for k in cbs:
                if cbs[k]["checkbox"].get_state():
                    # selected
                    result = hostvms.delete_snapshot(vmname=cbs[k]["vmname"], snapname=cbs[k]["snapname"])
                    results.append(result)
            create_alert("\n".join(results))

        choices.extend([
            urwid.Text(['']),  # separator
            menu_button("Delete", execute_command),
            menu_button("Return", execute_esc),
        ])
        contents = menu(caption, choices)
        top.open_box(contents)

    if action == SnapshotAction.LIST:
        caption = "List snapshots"
        choices = [
            menu_button(vm["name"], item_snapshot_list) for vm in hostvms.vms()
        ]
    elif action == SnapshotAction.TAKE:
        caption = "Take new snapshot"
        choices = [
            menu_button(vm["name"], item_snapshot_take) for vm in hostvms.vms()
        ]
    elif action == SnapshotAction.DELETE:
        caption = "Delete snapshots"
        choices = [
            menu_button(vm["name"], item_snapshot_delete) for vm in hostvms.vms()
        ]

    contents = menu(caption, choices)

    def open_menu(button: urwid.Button) -> None:
        return top.open_box(contents)

    return menu_button([caption, "..."], open_menu)


# ================================================================
#
#  MENU DEFINITION
#
# ================================================================
menu_top = menu(
    "Main Menu",
    [
        sub_menu(
            "VMs",
            [
                menu_button("Running vms", item_runningvms),
                menu_button("Configured vms", item_vms),
                sub_menu_showvminfo(),
                menu_button("Start/stop vm", start_stop_vms),
                sub_menu_snapshots(action=SnapshotAction.LIST),  # list
                sub_menu_snapshots(action=SnapshotAction.TAKE),  # take a new
                sub_menu_snapshots(action=SnapshotAction.DELETE),
            ],
        ),
        sub_menu(
            "Host",
            [
                menu_button("Host information", item_hostinfo),
            ],
        ),
        menu_button("Exit program", exit_program),
    ],
)


class CascadingBoxes(urwid.WidgetPlaceholder):
    max_box_levels = 4

    def __init__(self, box: urwid.Widget) -> None:
        super().__init__(urwid.SolidFill("/"))
        self.box_level = 0
        self.open_box(box)

    def open_box(self, box: urwid.Widget) -> None:
        self.original_widget = urwid.Overlay(
            urwid.LineBox(box),
            self.original_widget,
            align=urwid.CENTER,
            width=(urwid.RELATIVE, 80),
            valign=urwid.MIDDLE,
            height=(urwid.RELATIVE, 80),
            min_width=24,
            min_height=8,
            left=self.box_level * 3,
            right=(self.max_box_levels - self.box_level - 1) * 3,
            top=self.box_level * 2,
            bottom=(self.max_box_levels - self.box_level - 1) * 2,
        )
        self.box_level += 1

    def keypress(self, size, key: str) -> str | None:
        if key == "esc" and self.box_level > 1:
            self.original_widget = self.original_widget[0]
            self.box_level -= 1
            return None

        return super().keypress(size, key)


"""
Example:

cd src
python3 -m vtui
"""
if __name__ == "__main__":
    top = CascadingBoxes(menu_top)
    urwid.MainLoop(top, palette=[("reversed", "standout", "")]).run()
