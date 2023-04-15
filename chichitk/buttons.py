import cv2, os
import numpy as np
from PIL import Image, ImageTk
from tkinter import Frame, Button, Label

from .tool_tip import ToolTip


def hex_to_rgb(hex_code:str):
    '''converts hex code to uint8 rgb'''
    return tuple([int(h, 16) for h in (hex_code[1:3], hex_code[3:5], hex_code[5:])])

def image_replace_colors(img:np.array, colors_list:list):
    '''replaces all white pixels (255, 255, 255) in img with color
        :param colors_list: list[tuple(str, str)] - hex codes'''
    for value, replace in colors_list:
        img[np.all(img == hex_to_rgb(value), axis=-1)] = hex_to_rgb(replace)
    return img


class BaseButton(Frame):
    ''' Parent class for all icon buttons and label buttons
    
        Callback command is called whenever button is clicked. If button is
        selectable, the color of the button will change depending on select
        status.

        BaseButton includes a bar at the bottom of the button which can change
        color based on hover/select status.

        Optionally, a popup will appear when the user hovers the mouse over
        button. The popup is directly above the button by default, but its
        position is adjusted if necessary to keep the popup in view. For
        example, if the button is at the very top of the window, the popup will
        appear beneath the button instead.
    '''
    def __init__(self, master, command, popup_label:str=None, font_name:str='Segoe UI', font_size:int=10,
                padx:int=0, pady:int=0, selectable:bool=True, select_on_click:bool=True, selected=False,
                tool_tip_font_name:str='Segoe UI', tool_tip_font_size:int=10, bar_height:int=0, bar_side='bottom',
                active_bg:str='#070708', inactive_bg:str='#000000', active_hover_bg=None,
                inactive_hover_bg=None, active_fg:str='#13ce12', inactive_fg:str='#888888',
                active_hover_fg:str='#74d573', inactive_hover_fg:str='#74d573', popup_bg=None,
                active_bar_color=None, inactive_bar_color=None, active_hover_bar_color:str=None,
                inactive_hover_bar_color:str='#dcdcdc', off_fg:str='#555555'):
        '''inherits from tk.Frame - base button for inheritance from IconButton, LabelButton, ToggleIconButton, etc
        BaseButton only contains bottom bar - everything else must be added by child class
        child class must contain function config_colors

        Parameters
        ----------
            master : frame in which to put button
            command : function - function to be executed when button is clicked
            popup_label : str - text to appear as tool tip when cursor hovers on button
            padx : Int - internal x pad for button
            pady : Int - internal y pad for button
            selectable : Boolean - if True, button can be selected
            bar_height : Int - height of bar at the bottom of button
            bar_side : Literal['top', 'bottom', 'left', 'right'] - pack side for bar if bar_height > 0
            
            active_bg : str (hex code) - background when button is selected
            inactive_bg : str (hex code) - background when button is not selected
            active_hover_bg : str (hex code) - background when selected and cursor is hovering - if None: same as active_bg
            inactive_hover_bg : str (hex code) - background when not selected and cursor if hovering - if None: same as inactive_bg

            active_fg : str (hex code) - icon and label fg when button is selected
            inactive_fg : str (hex code) - icon and label fg when button is not selected
            active_hover_fg : str (hex code) - icon and label fg when selected and cursor is hovering - if None: same as active_fg
            inactive_hover_fg : str (hex code) - icon and label fg when not selected and cursor is hovering - if None: same as inactive_fg

            active_bar_color : str (hex code) - bar color when selected - if None: same as active_fg
            inactive_bar_color : str (hex code) - bar color when not selected - if None: same as inactive_bg
            active_hover_bar_color : str (hex code) - bar color when selected and cursor is hovering - if None: same as active_bar_color
            inactive_hover_bar_color : str (hex code) - bar color when not selected and cursor is hovering - if None: same as inactive_bar_color
        '''
        Frame.__init__(self, master)
        self.padx, self.pady = padx, pady
        self.selected, self.hovering = selected, False
        self.active = True # if not active, button will not be responsive
        self.click_command = command
        self.font_name, self.font_size = font_name, font_size
        self.selectable, self.select_on_click = selectable, select_on_click
        self.popup_labels = [popup_label + ' : Inactive' if popup_label else None, popup_label] # either both text or both None
        self.off_fg = off_fg
        self.bg_colors = [[inactive_bg, inactive_hover_bg if inactive_hover_bg else inactive_bg],
                            [active_bg, active_hover_bg if active_hover_bg else active_bg]]
        self.fg_colors = [[inactive_fg, inactive_hover_fg if inactive_hover_fg else inactive_fg],
                            [active_fg, active_hover_fg if active_hover_fg else active_fg]]
        active_bar_color = active_bar_color if active_bar_color else active_fg
        inactive_bar_color = inactive_bar_color if inactive_bar_color else inactive_bg
        self.bar_colors = [[inactive_bar_color, inactive_hover_bar_color if inactive_hover_bar_color else inactive_bar_color],
                            [active_bar_color, active_hover_bar_color if active_hover_bar_color else active_bar_color]]

        self.tool_tip = ToolTip(self, bg=popup_bg if popup_bg else self.bg_colors[0][0], fg='#ffffff',
                                font=(tool_tip_font_name, tool_tip_font_size))
        self.bar = Frame(self, height=bar_height, width=bar_height)
        if bar_height > 0:
            bar_fills = {'top':'x', 'bottom':'x', 'left':'y', 'right':'y'} # fill depends on bar pack side
            self.bar.pack(side=bar_side, fill=bar_fills[bar_side], expand=True)

        self.bind("<Enter>", self.hover_enter)
        self.bind("<Leave>", self.hover_leave)
        self.bind("<Button-1>", self.click_button)
        self.bar.bind("<Button-1>", self.click_button)

    def config_colors(self):
        '''placeholder - this method must be replaced in inheritance classes'''

    def set_color(self, color:str, which:str='bg', selected:bool=False, hover:bool=False, all:bool=False):
        '''sets a single color
        
        Parameters
        ----------
            :param color: str (hex code)
            :param which: str - options: ['bg', 'fg', 'bar']
            :param selected: bool - selected color
            :param hover: bool - hover color
            :param all bool - if True, changes color for all selected and hover statuses
        '''
        if all:
            for s in [True, False]:
                for h in [True, False]:
                    [self.bg_colors, self.fg_colors, self.bar_colors][['bg', 'fg', 'bar'].index(which)][s][h] = color
        else:
            [self.bg_colors, self.fg_colors, self.bar_colors][['bg', 'fg', 'bar'].index(which)][selected][hover] = color
        self.config_colors()

    def turn_on(self):
        self.active = True
        self.config_colors()

    def turn_off(self):
        self.active = False
        self.config_colors()

    def hover_enter(self, event):
        if not self.hovering:
            self.hovering = True
            if self.popup_labels[0]: # tool tip
                self.tool_tip.fadein(0, self.popup_labels[self.active], event) # 0 is initial alpha
            if self.active:
                self.config_colors()

    def hover_leave(self, event):
        if self.hovering:
            self.hovering = False
            if self.popup_labels[0]: # remove tool tip
                self.tool_tip.fadeout(1, event) # first argument is initial alpha
            if self.active:
                self.config_colors()
            
    def click_button(self, event=None):
        if self.active:
            self.click_command()
            if self.select_on_click:
                self.select()

    def select(self):
        if self.selectable and not self.selected:
            self.selected = True
            self.config_colors()

    def deselect(self):
        if self.selected:
            self.selected = False
            self.config_colors()

class IconButton(BaseButton):
    ''' Extension of BaseButton with an icon besode the label. The label can
        also be an empty string which results in only an icon.
        
        Given the path to a black and white .png file, the foreground and
        background color (set specifically for each hover/select status) can
        be changed with **kwargs passed to BaseButton
    '''
    def __init__(self, master, icon_path:str, command, label:str='', bar_height:int=3, **kwargs):
        '''
        Parameters
        ----------
            master : frame in which to put button
            icon_path : str - path to .png file
            click_command : 0 argument function - function to be executed when button is clicked
            bar_height : Int - height of bar at the bottom of button
        '''
        BaseButton.__init__(self, master, command, bar_height=bar_height, **kwargs) # bar already packed buttom
        self.icon_frame = Frame(self)
        self.icon_frame.pack(side='top', padx=self.padx, pady=self.pady)
        self.icon = Button(self.icon_frame, borderwidth=0, command=self.click_button)
        self.icon.pack(side='left')
        self.label = Label(self.icon_frame, text=label, font=(self.font_name, self.font_size), bd=0)
        self.label.pack(side='right', fill='y')

        self.icon_frame.bind("<Button-1>", self.click_button)
        self.label.bind("<Button-1>", self.click_button)
        
        # Create Icons
        self.images = [[None, None], [None, None]]
        self.base_img = cv2.imread(icon_path)
        for x, y in [[0, 0], [0, 1], [1, 0], [1, 1]]:
            temp_img = image_replace_colors(self.base_img.copy(), [('#ffffff', self.fg_colors[x][y]), ('#000000', self.bg_colors[x][y])])
            self.images[x][y] = ImageTk.PhotoImage(image=Image.fromarray(temp_img), master=self.icon_frame)
        off_img = image_replace_colors(self.base_img.copy(), [('#ffffff', self.off_fg), ('#000000', self.bg_colors[0][0])])
        self.off_icon = ImageTk.PhotoImage(image=Image.fromarray(off_img), master=self.icon_frame)

        self.config_colors()

    def config_colors(self):
        '''sets colors based on self.selected, self.hovering, and self.active'''
        if self.active:
            bg, fg = self.bg_colors[self.selected][self.hovering], self.fg_colors[self.selected][self.hovering]
            bar_color, image = self.bar_colors[self.selected][self.hovering], self.images[self.selected][self.hovering]
        else:
            bg, fg, bar_color, image = self.bg_colors[0][0], self.off_fg, self.bg_colors[0][0], self.off_icon
        self.config(bg=bg)
        self.bar.config(bg=bar_color)
        self.label.config(bg=bg, fg=fg)
        self.icon.config(image=image, bg=bg, activebackground=bg)

    def set_color(self, color:str, which:str='bg', selected:bool=False, hover:bool=False):
        '''sets a single color
        
        color : str (hex code)
        which : str - options: ['bg', 'fg', 'bar']
        selected : bool - selected color
        hover : bool - hover color
        '''
        if which == 'bg':
            self.bg_colors[selected][hover] = color
            temp_img = image_replace_colors(self.base_img.copy(), [('#ffffff', self.fg_colors[selected][hover]), ('#000000', color)])
            self.images[selected][hover] = ImageTk.PhotoImage(image=Image.fromarray(temp_img), master=self.icon_frame)
        elif which == 'fg':
            self.fg_colors[selected][hover] = color
            temp_img = image_replace_colors(self.base_img.copy(), [('#ffffff', color), ('#000000', self.bg_colors[selected][hover])])
            self.images[selected][hover] = ImageTk.PhotoImage(image=Image.fromarray(temp_img), master=self.icon_frame)
        elif which == 'bar':
            self.bar_colors[selected][hover] = color
        self.config_colors()

class ToggleIconButton(IconButton):
    ''' Toggle version of IconButton. The callback command is given a boolean
        parameter which indicates whether the button is being turned on or off.
    '''
    def __init__(self, master, icon_path:str, command=None, label:str='', bar_height:int=3, **kwargs):
        '''Toggle version of IconButton
        
            :param command: 1 argument function (bool) - True for turn on, False for turn off
        '''
        IconButton.__init__(self, master, icon_path, self.click, label=label,
                            select_on_click=False, bar_height=bar_height,
                            **kwargs)
        self.toggle_command = command

    def click(self):
        '''called when button is clicked'''
        self.selected = not self.selected
        self.config_colors()
        if self.toggle_command is not None:
            self.toggle_command(self.selected)

class DoubleIconButton(Frame):
    ''' DoubleIconButton contains two IconButtons that swap when clicked.
        There are separate commands for the two IconButtons
    '''
    def __init__(self, master, icon1:str, icon2:str, command1, command2, label1:str='', label2:str='',
                 popup_label1=None, popup_label2=None, **kwargs):
        '''IconButton that changes when clicked
        
        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param icon1: str - icon path for first IconButton
            :param icon2: str - icon path for second button
            :param command1: 0 argument function - called when first button is clicked - changes to second button
            :param command2: 0 argument function - called when second button is clicked - changes to first button
        '''
        Frame.__init__(self, master)
        self.__command1, self.__command2 = command1, command2
        self.__double_status = False # False when button 1 is active and True when button 2 is active

        self.Button1 = IconButton(self, icon1, self.click1, label=label1, selectable=False,
                                    popup_label=popup_label1, **kwargs)
        self.Button2 = IconButton(self, icon2, self.click2, label=label2, selectable=False,
                                    popup_label=popup_label2, **kwargs)
        self.Button1.pack(fill='both', expand=True)

    def switch1(self):
        '''
        Purpose:
            switches to button1 without calling any command
        Pre-conditions:
            (none)
        Post-conditions:
            switches to button1
        Returns:
            (none)
        '''
        self.__double_status = False
        self.Button2.pack_forget()
        self.Button1.pack(fill='both', expand=True)

    def switch2(self):
        '''
        Purpose:
            switches to button2 without calling any command
        Pre-conditions:
            (none)
        Post-conditions:
            switches to button2
        Returns:
            (none)
        '''
        self.__double_status = True
        self.Button1.pack_forget()
        self.Button2.pack(fill='both', expand=True)

    def click1(self):
        '''
        Purpose:
            called when first button is clicked
            switches to button2 and calls command1
        Pre-conditions:
            (none)
        Post-conditions:
            changes active (visible) button
        Returns:
            (none)
        '''
        self.switch2()
        self.__command1()

    def click2(self):
        '''
        Purpose:
            called when second button is clicked
            switches to button1 and calls command2
        Pre-conditions:
            (none)
        Post-conditions:
            changes active (visible) button
        Returns:
            (none)
        '''
        self.switch1()
        self.__command2()

    def get(self):
        '''returns False if button1 is active and True if button2 is active'''
        return self.__double_status

class CheckButton(DoubleIconButton):
    ''' Special version of DoubleIconButton that has a checkbox icon - checked and unchecked
        Takes a single callback command - passes boolean to indicate new checkbox status
    '''
    def __init__(self, master, command, label:str='', active_popup_label=None,
                 inactive_popup_label=None, active=False, **kwargs):
        '''Button1 is unchecked and Button2 is checked
        when Button1 is clicked, calls command(True) because checkbox is being selected

        Parameters
        ----------
            :param master: tk.Frame - parent widget
            :param command: 1 argument function (bool) called when button is clicked
            :param label: str - text to the left of button
            :param active_popup_label: str or None - hover popup text when button is selected
            :param inactive_popup_label: str or None - hover popup text when button is not selected
            :param active: bool - initial status of CheckButton
        '''
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons")
        path1 = os.path.join(image_path, "box.png")
        path2 = os.path.join(image_path, "checkbox.png")
        DoubleIconButton.__init__(self, master, path1, path2,
                                  lambda: command(True), lambda: command(False),
                                  label1=label, label2=label,
                                  popup_label1=inactive_popup_label,
                                  popup_label2=active_popup_label, **kwargs)
        if active:
            self.Button1.click_button()

class LabelButton(BaseButton):
    ''' LabelButton includes bar underneath the label. The parameter
        'bar_height' can be set to 0 to remove the bar.
        
        Background and foreground color can change based on select/hover status.
    '''
    def __init__(self, master, command, label:str='', **kwargs):
        '''just like IconButton but with no icon'''
        BaseButton.__init__(self, master, command, **kwargs)
        self.label = Label(self, text=label, font=(self.font_name, self.font_size), bd=0)
        self.label.pack(side='top', padx=self.padx, pady=self.pady)
        self.label.bind("<Button-1>", self.click_button)

        self.config_colors()

    def config_colors(self):
        '''sets colors based on self.selected, self.hovering, and self.active'''
        if self.active:
            bg, fg = self.bg_colors[self.selected][self.hovering], self.fg_colors[self.selected][self.hovering]
            bar_color = self.bar_colors[self.selected][self.hovering]
        else:
            bg, fg, bar_color = self.bg_colors[0][0], self.off_fg, self.bg_colors[0][0]
        self.config(bg=bg)
        self.bar.config(bg=bar_color)
        self.label.config(bg=bg, fg=fg)

class ToggleLabelButton(LabelButton):
    ''' Extension of LabelButton that passes a boolean argument to callback
        command to indicate whether buttons is being selected or deselected.
    '''
    def __init__(self, master, command=None, label:str='', **kwargs):
        '''Toggle version of LabelButton
        
            :param command: 1 argument function (bool) - True for turn on, False for turn off
        '''
        LabelButton.__init__(self, master, self.click, label=label, select_on_click=False, **kwargs)
        self.toggle_command = command

    def click(self):
        '''called when button is clicked'''
        self.selected = not self.selected
        self.config_colors()
        if self.toggle_command is not None:
            self.toggle_command(self.selected)

class PlayerButtons(Frame):
    ''' Collection of IconButtons for controlling the playback of music, a
        video, or something like that.
        
        Includes 6 buttons in the following order, with corresponding callbacks:
            previous - go to previous song or beginning of current song
            skip_back - go back by a given increment
            play/pause - toggle button to start/stop playback
            skip_forward - go forward by a given increment
            next - go to next song or end of current song
            loop (toggle) - turn looping on or off
            '''
    def __init__(self, master, bg, play_function, stop_function, step_forward_function,
                 step_back_function, next_function, previous_function,
                 active_icon_color='#ffffff', button_bar_height=0,
                 button_padx=7, active=True):
        '''buttons to control playback of MusicPlayer or VideoPlayer'''
        Frame.__init__(self, master, bg=bg)
        # for x padding so that buttons dont span full width of frame
        self.grid_columnconfigure(0, weight=6)
        self.grid_columnconfigure(7, weight=6)
        for i in range(6):
            self.grid_columnconfigure(i + 1, weight=1)
        
        # key-word arguments common to all buttons
        bkwargs = {'bar_height':button_bar_height, 'inactive_bg':bg,
                   'padx':button_padx}
        
        # Create buttons
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons")
        self.buttons: list[IconButton] = []
        previous_button = IconButton(self, os.path.join(image_path, "skip_back.png"),
                                     previous_function, popup_label='Skip to Start',
                                     selectable=False, **bkwargs)
        back_button = IconButton(self, os.path.join(image_path, "replay5.png"), step_back_function,
                                 popup_label='Back 5 Seconds', selectable=False,
                                 **bkwargs)
        self.play_button = DoubleIconButton(self, os.path.join(image_path, "play.png"),
                                            os.path.join(image_path, "pause.png"), play_function,
                                            stop_function, popup_label1='Play',
                                            popup_label2='Pause', **bkwargs)
        forward_button = IconButton(self, os.path.join(image_path, "forward5.png"),
                                    step_forward_function, popup_label='Forward 5 Seconds',
                                    selectable=False, **bkwargs)
        next_button = IconButton(self, os.path.join(image_path, "skip_forward.png"),
                                 next_function, popup_label='Skip to End',
                                 selectable=False, **bkwargs)
        self.loop_button = ToggleIconButton(self, os.path.join(image_path, "loop.png"),
                                            popup_label='Toggle Loop',
                                            bar_height=button_bar_height,
                                            active_bg=bg, inactive_bg=bg,
                                            active_fg=active_icon_color,
                                            padx=button_padx)

        # Grid buttons
        for i, button in enumerate([previous_button, back_button, self.play_button,
                                    forward_button, next_button, self.loop_button]):
            button.grid(row=0, column=i + 1)
            self.buttons.append(button)

        if not active:
            self.turn_off()

    def is_looped(self):
        '''returns True if looping is on, otherwise False'''
        return self.loop_button.selected
    
    def to_stop(self):
        '''switches play button to stop button without calling play command'''
        self.play_button.switch2()

    def to_play(self):
        '''switches stop button to play button without calling stop command'''
        self.play_button.switch1()

    def turn_on(self):
        for button in self.buttons:
            button.turn_on()

    def turn_off(self):
        for button in self.buttons:
            button.turn_off()
