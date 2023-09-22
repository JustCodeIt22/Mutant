import pygame
from pygame.locals import *
import json
import os  # for accessing the directories and files
from data.algorithms import *
from data.plugins.FileManager import *
from data.plugins.IntelliSense import *

# COLORS
DEFAULT_BG_COLOR = (11, 14, 20)
DEFAULT_CURSOR_COLOR = (255, 255, 255)

class TextEditor:
    # Class Constructor
    def __init__(self, pos, size, bg_color = DEFAULT_BG_COLOR, tab_size = 4, cursor_color = DEFAULT_CURSOR_COLOR, cursor_style="filled_box", font_size = 18, line_num_color = (170, 170, 0), curr_ln_indi_color = (41, 46, 57) ,line_bgrectcolor = (55, 55, 55)):
        # CONSTANTS
        self.MARGIN = 10
        self.TAB_SIZE = tab_size

        # screen
        pygame.init()
        pygame.font.init()
        self.te_display = pygame.display.get_surface()
        self.te_pos = (pos[0] + 3, pos[1] + 3) #pos
        self.te_size = size
        self.te_surf = pygame.Surface((self.te_size[0] - 6, self.te_size[1] - 6))
        self.file_path = ""
        self.file_extension = self.file_path.split(".")[-1]

        # colors
        self.bg_color = bg_color
        self.fg_color = (255, 255, 255)
        
        # font
        self.font = pygame.font.SysFont("Consolas", font_size)
        self.font_size = self.font.size("a")
        self.text = [""] # list of strings each element is new line

        # line numbers
        self.line_num = 0
        self.line_num_color = line_num_color
        self.line_num_w = 30
        self.space_after_ln = 4
        self.offset = self.font_size[0] * self.space_after_ln
        self.num_line_screen_can_display = self.te_size[1] // self.font_size[1] - 1
        # self.line_bgrectcolor = line_bgrectcolor

        # Cursor
        self.cursor_color = cursor_color
        self.set_cursor_style(cursor_style)
        self.cursor_surf.fill(self.cursor_color)
        self.cursor_surf.set_alpha(150)
        self.cursor_posx = self.line_num_w + self.space_after_ln + self.font_size[0]
        self.cursor_surf_rect = self.cursor_surf.get_rect(topleft=(self.cursor_posx , self.font_size[1]))

        # === helper variables
        # var for ctrl and shift btn pressed for various shortcuts and key bindings
        self.ctrl = False
        self.shift = False
        self.curr_row = 0
        self.curr_col = 0

        # current line indicator 
        self.curr_ln_indi_color = curr_ln_indi_color
        self.curr_ln_indi_surf = pygame.Surface((self.te_size[0], self.font_size[1]))
        self.curr_ln_indi_surf.fill(self.curr_ln_indi_color)
        self.curr_ln_indi_surf.set_alpha(100)
        self.clis_rect = self.curr_ln_indi_surf.get_rect() # current line indicator rect

        # var for backspacehold 
        self.isBackspaceHold = False
        self.backspaceHoldTimer = 50  # 50 mili second

        # var for vertical scroll
        self.vertical_scroll = self.font_size[1] # 5 * self.font_size[1]
        self.cursor_scroll = 1 # just true(1) or false(0)
        self.vscroll_num = 0

        # var for horizontal scroll
        self.horizontal_scroll = self.font_size[0]
        self.overflow = 0
        self.hscroll_num = 0

        # var for mouse scroll
        self.mscroll_num = 0
        self.mouse_scroll_speed = 3

        # var for selection
        self.selection_start_col = 0
        self.selected_col = 0
        self.selected_row = 0
        self.selected_text = ""
        self.selection_rect = pygame.Rect((0, 0),(0, self.font_size[1]))
        self.selection_color = (64, 22, 187)

        # var for selection using mouse
        self.mselection_color = (45, 83, 126)
        self.mstart_indicator_color = (0, 255, 0)
        self.mend_indicator_color = (255, 0, 0)
        self.mouseLeftBtnDown = False
        self.mselection_start_row_n_col = (0, 0)
        self.mselection_end_row_n_col = (0, 0)
        self.mselected_text = [] # list of strings each element is new line
        self.mLBD_N_mMotion = False # mouse left btn down and mouse in motion
        self.dispMouseSelection = False

        # var for copying text
        self.copied_text = ""

        # var for popup window
        self.win_is_open = False
        # self.relative_path = os.path.dirname(__file__)  # __file__ -> gives the relative path its changes according to the apps loc
        # self.popup_window_surf = pygame.image.load(self.relative_path + "\\data/imgs/bg_popup_window.png").convert_alpha()
        self.popup_window_surf = pygame.image.load("data/imgs/bg_popup_window.png").convert_alpha()

        # var for tabAutoCompleteFileNames
        self.pwd = os.getcwd()
        self.all_dirs = os.listdir(self.pwd)

        # var for saving and opening files
        self.toSave = False # for if to save a file or not
        self.toOpen = False # for if to open a file or not

        # var for Syntax HighLighting
        with open("data/settings.json", "r") as file:
            self.builtin_keywords_for_all_langs = json.load(file)
        
        self.builtin_keywords = []
        self.builtin_keyword_color = (90, 245, 0)
        self.comment_symbol = self.builtin_keywords_for_all_langs["all_comments_symbol"]
        self.comment_color = (103, 75, 110)
        self.string_color = (245, 39, 91)
        self.escape_char_color = (200, 0, 0)
        self.function_color = (255, 77, 41)
        self.object_color = (138, 99, 255) #(0, 157, 255)
        # specifict for python self word
        self.self_color = (42, 184, 245)

        # var for Undo and Redo
        self.undo_history = Stack()

        # Lazy Loading variables
        self.text_to_display = [""]
        self.scroll_y = 0

        """ ==== Plugins ====== """
        # File Manager
        self.fileManager_bgcolor = (15, 17, 42)#(11, 14, 20)#(125, 125, 215)
        self.fileManager_fgcolor = (67, 255, 167)#(61, 91, 102)
        self.fileManager_width = cnv_to_per(30, self.te_size[0])
        self.fileManager = FileManager(self.fileManager_bgcolor, self.fileManager_width, self.te_size[1],  fg_color=self.fileManager_fgcolor)

        # Intellisense
        self.intellisense = IntelliSense()

        # Mutant Mode
        self.mutantMode = False
        self.cmd = ""
        self.prev_cmd = ""
        self.mode_indi_rect = pygame.Rect(10, 4, 10, 10)
        self.mutant_mode_color = (18, 255, 117)
        self.normal_mode_color = bg_color
        self.mode_color = self.normal_mode_color


    # Handle Events
    def handle_events(self, event):
        # Drag and Drop files
        if event.type == pygame.DROPFILE:
            self.file_path = event.file
            try:
                self.toOpen = True
                if self.toOpen : self.open_file()
                self.toOpen = False
            except UnicodeDecodeError:
                # TODO : display alert window saying ("File Not Supported !!") 
                print("File Format Not Supported !!")

        # Keyboard events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.file_path = ""
                self.win_is_open = False
                self.toSave = False
                self.toOpen = False
                
            # Backspace
            elif event.key == pygame.K_BACKSPACE:
                if self.win_is_open:
                    self.file_path = self.file_path[:-1]
                elif self.selected_col > 0:
                    self.text[self.line_num] = self.text[self.line_num][:self.curr_col]
                    self.reset_selection()
                else:
                    self.isBackspaceHold = True
                    if self.text[self.line_num] or self.text[self.line_num - 1] or self.text[self.line_num - 1] == "":
                        if (self.mselection_start_row_n_col[1] < self.mselection_end_row_n_col[1]):
                            self.delete_selected_text()
                        elif self.text[self.line_num] and self.curr_col != 0: # This is for char deletion
                            self.cursor_surf_rect.x -= self.font_size[0]
                            self.delete_text()
                        else:
                            if self.line_num > 0: # This is for the line deletion when the cursor is at the start of the line 
                                self.cursor_surf_rect.y = self.font_size[1] * (self.line_num - self.vscroll_num - self.mscroll_num)
                                self.cursor_surf_rect.x = self.font.size(self.text[self.line_num - 1])[0] + self.cursor_posx
                                self.text[self.line_num] = self.text[self.line_num - 1] + self.text[self.line_num] 
                                self.text.pop(self.line_num - 1)
                                self.line_num -= 1
                                if(self.cursor_surf_rect.topleft[1] <= self.font_size[1] and self.line_num > 0):
                                    self.cursor_scroll = 0
                                    self.vscroll_num -= 1
                                # self.scroll_window() # scroll window upwards if the cursor is at top of screen and if there are lines up
                        self.get_row_n_col(self.cursor_surf_rect.topleft) # recalculate col and row
                        self.undo_history = Stack()

            # Enter 
            elif event.key == pygame.K_RETURN:
                if self.intellisense.haveSuggestions() and self.intellisense.dispAutoCompleteWindow:
                    active_word = self.intellisense.complete()[len(self.intellisense.curr_word):]
                    self.text[self.line_num] += active_word
                    self.intellisense.active_idx = 0 # reseting the autocomplete index
                    self.cursor_surf_rect.x += (len(active_word) * self.font_size[0])
                    self.get_row_n_col(self.cursor_surf_rect.topleft)
                    self.intellisense.dispAutoCompleteWindow = False
                elif self.win_is_open:
                    if self.toSave : self.save_file()
                    elif self.toOpen : self.open_file()
                    self.win_is_open = False
                    self.toSave = False
                    self.toOpen = False
                    # load the syntax highlighting
                    self.file_extension = self.file_path.split(".")[-1]
                    if self.file_extension:
                        try:
                            self.builtin_keywords = self.builtin_keywords_for_all_langs[self.file_extension]
                        except KeyError:
                            print(f"Syntax Highlighting for {self.file_extension} is not implemented till now !!")
                else:
                    self.cursor_surf_rect.y += self.font_size[1]
                    self.cursor_surf_rect.x = self.cursor_posx
                    # self.text.append("")
                    self.text.insert(self.line_num + 1, self.text[self.line_num][self.curr_col:])
                    self.text[self.line_num] = self.text[self.line_num][:self.curr_col]
                    self.line_num += 1
                    self.scroll_window() # scroll window downwards if the cursor is at end of screen
                    self.get_row_n_col(self.cursor_surf_rect.topleft) # recalculate col and row
                
            # Shifts
            elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                self.shift = True
                self.selection_start_col = self.curr_col
            elif event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                self.ctrl = True
            elif event.key == pygame.K_LALT or event.key == pygame.K_RALT:
                self.mutantMode = not self.mutantMode
                if self.mutantMode: # if mutant mode enabled
                    self.mode_color = self.mutant_mode_color
                else: # if mutant mode disabled
                    self.mode_color = self.normal_mode_color
                    self.mutantMode = False
                    self.cmd = ""
                    self.prev_cmd = ""
            elif event.key == pygame.K_CAPSLOCK:
                pass 
            elif self.ctrl and event.key == pygame.K_s: #  CTRL + s -> for saving file
                self.win_is_open = True
                self.toSave = True
                # self.save_file()
            elif self.ctrl and event.key == pygame.K_o: #  CTRL + o -> for opening file
                self.file_path = ""    # reseting the file path
                self.win_is_open = True
                self.toOpen = True
                # self.open_file()
            elif self.ctrl and event.key == pygame.K_n: # #  CTRL + n -> open a new untitled file
                # self.text = [""]
                # self.line_num = 0
                # self.curr_col = 0
                pass
            elif self.fileManager.handle_events(event, self.ctrl) or self.intellisense.handle_events(event, self.ctrl): # Then dont add char to text
                pass
            elif self.ctrl and event.key == pygame.K_z: #  CTRL + z -> for undo
                self.undo_func()
            elif self.ctrl and event.key == pygame.K_y: # CTRL + y -> for redo
                self.redo_func()
            elif self.ctrl and event.key == pygame.K_c: # CTRL + c -> for Copying text
                self.mouse_get_selection()
                self.dispMouseSelection = False
                if self.selected_text:
                    self.copied_text = self.selected_text
                elif self.mselected_text:
                    self.copied_text = self.mselected_text
                self.reset_selection()
            elif self.ctrl and event.key == pygame.K_v: # CTRL + v -> for Pasting the copied text
                if isinstance(self.copied_text, str):
                    self.text[self.line_num] = self.text[self.line_num][:self.curr_col] + self.copied_text + self.text[self.line_num][self.curr_col:]
                    self.cursor_surf_rect.x += len(self.copied_text) * self.font_size[0]
                # Pasting for multiple lines
                elif isinstance(self.copied_text, list):
                    # pasting on the line having text
                    if self.text[self.line_num]:
                        self.text[self.line_num] = self.text[self.line_num][:self.curr_col] + self.copied_text[0] + self.text[self.line_num][self.curr_col:]
                        self.text[self.line_num + 1:self.line_num] = self.copied_text[1:]
                        self.line_num += len(self.copied_text[1:])
                        self.cursor_surf_rect.x = (len(self.copied_text[-1]) + self.space_after_ln) * self.font_size[0] + self.space_after_ln
                        self.cursor_surf_rect.y += len(self.copied_text[1:]) * self.font_size[1]
                    # pasting on the line having no text 
                    else: 
                        self.text.pop(self.line_num)
                        self.text[self.line_num:self.line_num] = self.copied_text
                        self.line_num += len(self.copied_text) - 1
                        self.cursor_surf_rect.x += len(self.copied_text[-1]) * self.font_size[0]
                        self.cursor_surf_rect.y += (len(self.copied_text) - 1) * self.font_size[1]
                    
                self.get_row_n_col(self.cursor_surf_rect.topleft) # recalculate


            # Tab
            elif event.key == pygame.K_TAB:
                if self.intellisense.haveSuggestions() and self.intellisense.dispAutoCompleteWindow:
                    active_word = self.intellisense.complete()[len(self.intellisense.curr_word):]
                    self.text[self.line_num] += active_word
                    self.intellisense.active_idx = 0 # reseting the autocomplete index
                    self.cursor_surf_rect.x += (len(active_word) * self.font_size[0])
                    self.get_row_n_col(self.cursor_surf_rect.topleft)
                    self.intellisense.dispAutoCompleteWindow = False
                elif self.win_is_open:
                    self.tabAutoCompleteFileNames()
                else:
                    self.cursor_surf_rect.x += self.font_size[0] * self.TAB_SIZE
                    tab = ' ' * self.TAB_SIZE
                    self.text[self.line_num] = self.text[self.line_num][:self.curr_col] + tab + self.text[self.line_num][self.curr_col:]
            # Motion Keys (i.e Left, Right, Up, Down)
            # Right Key
            elif event.key == pygame.K_RIGHT:
                # Motion
                self.update_cursor_according_to_keys(horizontalDir = 1)
                # Selection
                if self.shift:
                    self.selected_col += 1
                    self.get_selection(1)
                self.insert_text()
            # Left Key
            elif event.key == pygame.K_LEFT:
                # Motion
                self.update_cursor_according_to_keys(horizontalDir = -1)
                # Selection
                if self.shift:
                    self.selected_col += 1
                    self.get_selection(-1)
                self.insert_text()
            # Down Key
            elif event.key == pygame.K_DOWN:
                if self.intellisense.haveSuggestions() and self.intellisense.dispAutoCompleteWindow:
                    self.intellisense.update_active_index(1)
                else:
                    self.update_cursor_according_to_keys(verticalDir = 1)
                    self.cursor_scroll = 1
                    self.scroll_window() # scroll window downwards if the cursor is at end of screen
                    self.insert_text()
            # Up Key
            elif event.key == pygame.K_UP:
                if self.intellisense.haveSuggestions() and self.intellisense.dispAutoCompleteWindow:
                    self.intellisense.update_active_index(-1)
                else:
                    self.update_cursor_according_to_keys(verticalDir = -1)
                    if(self.cursor_surf_rect.topleft[1] <= self.font_size[1] and self.line_num != 0):
                        self.cursor_scroll = 0
                        self.vscroll_num -= 1
                        self.line_num -= 1 
                    self.scroll_window() # scroll window upwards if the cursor is at top of screen and if there are lines up
                    self.insert_text()

            # Other keys
            else:
                if self.win_is_open:
                    self.file_path += event.unicode
                elif self.mutantMode:
                    self.cmd += event.unicode
                else:
                    self.cursor_surf_rect.x += self.font_size[0]
                    # insertion
                    self.insert_text(event.unicode)
                    self.intellisense.dispAutoCompleteWindow = True
                    self.intellisense.active_idx = 0
                
        # Keyboard Keyup Events 
        if event.type == pygame.KEYUP:
            # Backspace
            if event.key == pygame.K_BACKSPACE:
                self.isBackspaceHold = False
            # Ctrl
            elif event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                self.ctrl = False
            # Shifts
            elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                self.shift = False
                self.selection_start_col = 0
            elif event.key == pygame.K_LALT or event.key == pygame.K_RALT:
                # self.mutantMode = False
                pass

        # Mouse Events
        if event.type == pygame.MOUSEBUTTONDOWN:
            match(event.button):
                case 1: # Left Mouse Button
                    self.update_cursor_according_to_mouse()
                    self.mouseLeftBtnDown = True
                    self.dispMouseSelection = False
                    self.mselected_text = []
                    self.mouse_pos = pygame.mouse.get_pos()
                    self.mselection_start_row_n_col = (self.mouse_pos[0]//self.font_size[0] - self.space_after_ln, self.mouse_pos[1]//self.font_size[1] - 1)
                case 4: # Scroll Up
                    # print("Scroll Up")
                    if self.ctrl: # CTRL + mouse scroll -> increases the mouse scrolling speed
                        if self.mscroll_num > 0:
                            self.mouse_scroll(-self.mouse_scroll_speed * 2)# mscroll speed becomes twice
                            self.cursor_surf_rect.y += (self.font_size[1] * self.mouse_scroll_speed * 2)
                    else:
                        if self.mscroll_num > 0:
                            self.mouse_scroll(-self.mouse_scroll_speed)
                            self.cursor_surf_rect.y += self.font_size[1] * self.mouse_scroll_speed
                    # print(self.mscroll_num)
                case 5: # Scroll Down
                    # checking if there are more line down or not
                    if self.ctrl:
                        if  (self.te_size[1] // self.font_size[1]) - 1 + self.mscroll_num < len(self.text):
                            self.mouse_scroll(self.mouse_scroll_speed * 2) # mscroll speed becomes twice
                            # print("Scroll Down")
                            self.cursor_surf_rect.y -= (self.font_size[1] * self.mouse_scroll_speed * 2)
                    else:
                        if  (self.te_size[1] // self.font_size[1]) - 1 + self.mscroll_num < len(self.text):
                            self.mouse_scroll(self.mouse_scroll_speed)
                            # print("Scroll Down")
                            self.cursor_surf_rect.y -=  self.font_size[1] * self.mouse_scroll_speed
                    # print(self.mscroll_num)
        if event.type == pygame.MOUSEBUTTONUP:
            match(event.button):
                case 1: # Left Mouse Button
                    self.mouseLeftBtnDown = False
        
        if event.type == pygame.MOUSEMOTION and self.mouseLeftBtnDown:
            self.mouse_pos = pygame.mouse.get_pos()
            if self.text:
                try:
                    cols_condition = len(self.text[self.mouse_pos[1]//self.font_size[1] - 1]) > (self.mouse_pos[0]//self.font_size[0] - self.space_after_ln - 1)
                    rows_condition = len(self.text) > self.mouse_pos[1]//self.font_size[1] - 1
                    if cols_condition and rows_condition:
                        self.mselection_end_row_n_col = (self.mouse_pos[0]//self.font_size[0] - self.space_after_ln - 1, self.mouse_pos[1]//self.font_size[1] - 1)
                except IndexError:
                    pass               
            self.dispMouseSelection = True


    # Get the current column and row
    def get_row_n_col(self, relative_pos):
        self.curr_col = round(relative_pos[0] / self.font_size[0]) - 4
        self.curr_row = round(relative_pos[1] / self.font_size[1])
        


    # Backspace Hold -> # if user holds space for 20ms or more then it should delete chars faster   
    def backspace_hold(self):
        if self.isBackspaceHold and self.backspaceHoldTimer > 0:
            self.backspaceHoldTimer -= 1
        else:
            self.backspaceHoldTimer = 50 # reset the timer

        # if user holds space for 20ms or more then it should delete chars faster    
        if self.backspaceHoldTimer <= 30:
            if self.text[self.line_num]:
                self.cursor_surf_rect.x -= self.font_size[0]
                self.text[self.line_num] = self.text[self.line_num][:-1]
    


    # cursor_type 
    def set_cursor_style(self, cursor_style):
        if cursor_style == "filled_box":
            self.cursor_surf = pygame.Surface(self.font_size)
        elif cursor_style == "bar":
            self.cursor_surf = pygame.Surface((4, self.font_size[1] + 2))
    


    # update cursor pos according to mouse pos
    def update_cursor_according_to_mouse(self):
        # reset the selection
        self.reset_selection()
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_pos = (self.mouse_pos[0] - self.te_pos[0], self.mouse_pos[1] - self.te_pos[1])
        row = self.mouse_pos[1] // self.font_size[1]
        col = self.mouse_pos[0] // self.font_size[0]
        if row >= 1 and col >= 4:
            if (0 <= row - 1 < len(self.text)):
                if col - 4 <= len(self.text[row - 1 + self.vscroll_num + self.mscroll_num]):
                    self.curr_col = col - 4
                    self.cursor_surf_rect.x = col * self.font_size[0] + 4
                    self.cursor_surf_rect.y = row * self.font_size[1]
                    self.line_num = row - 1 + self.vscroll_num + self.mscroll_num
                else:
                    self.curr_col = col - 4
                    self.line_num = row - 1 + self.vscroll_num + self.mscroll_num
                    self.cursor_surf_rect.x = (len(self.text[self.line_num]) + 4) * self.font_size[0] + 4
                    self.cursor_surf_rect.y = row * self.font_size[1] 



    # update cursor pos according to up/down/left/right keys
    def update_cursor_according_to_keys(self, horizontalDir = 0, verticalDir = 0):
        posAfterMotion = (self.cursor_surf_rect.x + (horizontalDir * self.font_size[0]), self.cursor_surf_rect.y + (verticalDir * self.font_size[1]))
        rowAfterMotion = round(posAfterMotion[1] / self.font_size[1])
        colAfterMotion = round((posAfterMotion[0] - (4 * self.font_size[0])) / self.font_size[0])

        # print(col, len(self.text[self.line_num]), colAfterMotion)
        if horizontalDir:
            if (0 <= colAfterMotion <= len(self.text[self.line_num])):
                self.cursor_surf_rect.x += (horizontalDir * self.font_size[0])
        if verticalDir and self.line_num + verticalDir < len(self.text):
            if (0 < rowAfterMotion <= len(self.text)):
                tmp_line_num = self.line_num
                self.line_num += verticalDir
                if (self.curr_col > len(self.text[tmp_line_num + verticalDir])):
                    self.cursor_surf_rect.x = self.font.size(self.text[self.line_num])[0] + self.cursor_posx
                    self.cursor_surf_rect.y += (verticalDir * self.font_size[1])
                else:
                    self.cursor_surf_rect.y += (verticalDir * self.font_size[1])
                # self.cursor_surf_rect.x = self.font.size(self.text[self.line_num])[0] + self.cursor_posx


    
    # scroll
    def scroll_window(self):
        pos = self.cursor_surf_rect.bottomleft
        if(pos[1] >= self.te_size[1]): # cnv_to_per(90, self.te_size[1])
            self.cursor_surf_rect.y -= (self.vertical_scroll * self.cursor_scroll) 
            self.vscroll_num += 1
    


    # horizontal scroll
    def scroll_horizontal_horizontal(self):
        pos = self.cursor_surf_rect.right
        if(pos >= self.te_size[0]): # cnv_to_per(90, self.te_size[0])
            self.cursor_surf_rect.x -= self.horizontal_scroll
            self.hscroll_num += 1
        elif(self.curr_col > 0  and self.cursor_surf_rect.left <= 10):
            self.cursor_surf_rect.x += self.horizontal_scroll
            self.hscroll_num -= 1



    def mouse_scroll(self, mscorll_dir):
        self.mscroll_num += mscorll_dir
        self.get_row_n_col(self.cursor_surf_rect)



    # Save file
    def save_file(self):
        with open(self.file_path, "w") as file:
            file.write("\n".join(self.text))
            self.fileManager.reload()
            print("File Saved Successfully")



    # Open file
    def open_file(self):
        try:
            if len(self.file_path.split(".")) == 2: # means the file path is file
                with open(self.file_path, "r") as file:
                    txt = file.read()
                    self.text = txt.split("\n")
                    print("File Opened Successfully")
                    # Reseting all
                    self.line_num = 0 #len(self.text) - 1
                    self.cursor_surf_rect.x = self.cursor_posx   
                    self.cursor_surf_rect.y = self.font_size[1]
                    self.scroll_y = 0
                    self.vscroll_num = 0
                    self.hscroll_num = 0
                    self.mscroll_num = 0
                    #self.cursor_surf_rect.x = self.font.size(self.text[-1])[0] + self.cursor_posx    
                    #self.cursor_surf_rect.y = self.font.size(self.text[-1])[1] * len(self.text)
            elif self.file_path == "..":
                pwd = os.getcwd()
                os.chdir("/".join(pwd.split("\\")[:-1]))
                print("/".join(pwd.split("\\")[:-1]))
                self.fileManager.reload()
            elif len(self.file_path.split(".")) == 1: # if the file path is of folder than change director to that folder
                pwd = os.getcwd()
                print(f"current -> {pwd}")
                os.chdir(self.file_path)
                pwd = os.getcwd()
                self.file_path = pwd
                print(f"changed -> {pwd}")
                # Reloading all files and folders
                self.pwd = os.getcwd()
                self.all_dirs = os.listdir(self.pwd)
                self.fileManager.reload()
        except FileNotFoundError:
            print("File Not Found")

    # Undo Function
    def undo_func(self):
        if self.text[self.line_num]:
            last_word = self.text[self.line_num].split()[-1]
            self.undo_history.push(last_word)
            if len(self.text[self.line_num].split()) == 1:
                self.text[self.line_num] = self.text[self.line_num][:-(len(last_word))]
                self.cursor_surf_rect.x -= (len(last_word)) * self.font_size[0]
            else:
                self.text[self.line_num] = self.text[self.line_num][:-(len(last_word) + 1)]
                self.cursor_surf_rect.x -= (len(last_word) + 1) * self.font_size[0]
            self.get_row_n_col(self.cursor_surf_rect.topleft)

    def redo_func(self):
        if not self.undo_history.isEmpty():
            if len(self.text[self.line_num].split()):
                top_word = " " + self.undo_history.pop()
            else:
                top_word = self.undo_history.pop()
            self.text[self.line_num] += (top_word)
            self.cursor_surf_rect.x += (len(top_word) * self.font_size[0])
            self.get_row_n_col(self.cursor_surf_rect.topleft)



    # For tab Auto compelet file names present in that working directory
    def tabAutoCompleteFileNames(self):
        for files in self.all_dirs:
            if self.file_path.split(".")[0] in files: # files.startswith(self.file_path[0]):
                self.file_path = files
                self.all_dirs.remove(self.file_path)
                break



    # =================== Selection ===========

    def get_selection(self, selection_dir):
        if selection_dir == -1:
            self.selected_text = self.text[self.line_num][self.selection_start_col - self.selected_col:self.selection_start_col + 1]
            self.selection_rect.w = self.font_size[0] * (self.selected_col + 1)
            self.selection_rect.x = (self.curr_col * self.font_size[0]) + self.line_num_w + self.space_after_ln
            self.selection_rect.y = (self.line_num + 1) * self.font_size[1]
            print(self.selected_text)
        elif selection_dir == 1:
            self.selected_text = self.text[self.line_num][self.selection_start_col:self.selection_start_col + self.selected_col + 1]
            self.selection_rect.w = self.font_size[0] * (self.selected_col + 1)
            self.selection_rect.x = ((self.selection_start_col + 1) * self.font_size[0])  + self.line_num_w + self.space_after_ln
            self.selection_rect.y = (self.line_num + 1) * self.font_size[1]
            print(self.selected_text)
        

    # ================== Selection Using mouse ============== #
    def mouse_get_selection(self):
        start_col, start_row = self.mselection_start_row_n_col
        start_row += self.mscroll_num
        end_col, end_row = self.mselection_end_row_n_col
        end_row += self.mscroll_num

        if (start_row >= 0 and end_row < len(self.text)):
            if start_row == end_row: # For same line selection
                # self.selected_text = self.text[start_row][start_col:end_col + 1]
                self.mselected_text = self.text[start_row][start_col:end_col + 1]
            if start_row < end_row: # For up to down selection
                for i in range(start_row, end_row + 1):
                    if i == start_row: # For the start row
                        self.mselected_text.append(self.text[i][start_col:len(self.text[i]) + 1])
                    if start_row < i < end_row: # For row between the start row and end row
                        self.mselected_text.append(self.text[i][0:len(self.text[i]) + 1])
                    if i == end_row: # For the end row
                        self.mselected_text.append(self.text[i][0:end_col + 1])
                print(self.mselected_text)
            else: # For down to up selection
                # Want to implement down to up
                pass
                # raise Exception("Want to implement down to up selection!")
    
    def draw_mouse_selection(self):
        start_col, start_row = self.mselection_start_row_n_col
        start_row += self.mscroll_num
        end_col, end_row = self.mselection_end_row_n_col
        end_row += self.mscroll_num
        if (start_row >= 0 and end_row < len(self.text)):
            if start_row == end_row:
                px = (start_col + self.space_after_ln) * self.font_size[0] + self.space_after_ln
                py = (start_row + 1) * self.font_size[1]
                w = (end_col - start_col + 1) * self.font_size[0]
                h = self.font_size[1]
                pygame.draw.rect(self.te_surf, (0, 0, 255), ((px, py), (w, h)))

            """ Multi line selection implemented just disabled for now """
            if start_row < end_row: 
                spx = (start_col * self.font_size[0] + self.offset) - self.font_size[0] + 4 
                spy = (start_row + 1) * self.font_size[1] - 2 - (self.vertical_scroll * self.mscroll_num) - (self.vertical_scroll * self.vscroll_num) 
                if (self.mouse_pos[0]//self.font_size[0]) < len(self.text[end_row]) + self.space_after_ln:
                    epx = ((self.mouse_pos[0]//self.font_size[0]) * self.font_size[0] + self.font_size[0]) - 6
                else:
                    epx = len(self.text[end_row]) * self.font_size[0] + self.offset + 3
                epy = (end_row + 1) * self.font_size[1] - 2 - (self.vertical_scroll * self.mscroll_num) - (self.vertical_scroll * self.vscroll_num) 
                w, h = self.font_size

                if self.mouseLeftBtnDown == False:
                    inc = 3
                    h += inc
                    spy -= inc/2
                    epy -= inc/2


                # #Rectangle selection
                for i in range(start_row, end_row + 1):
                    if i == start_row:
                        x = self.cursor_surf_rect.x
                        width = len(self.text[start_row][start_col:]) * self.font_size[0]
                    elif i == end_row:
                        x = self.offset 
                        width = len(self.text[end_row][:end_col]) * self.font_size[0]  + self.font_size[0] + self.space_after_ln
                    else:
                        x = self.offset
                        width = len(self.text[i]) * self.font_size[0] + self.space_after_ln
                    height = self.font_size[1]
                    y = (height * (i + 1)) - (self.vertical_scroll * self.mscroll_num) - (self.vertical_scroll * self.vscroll_num) 
                    pygame.draw.rect(self.te_surf, self.mselection_color, ((x, y), (width, height)))

                pygame.draw.rect(self.te_surf, self.mstart_indicator_color, ((spx, spy), (w, h + 4))) # Start indicator
                pygame.draw.rect(self.te_surf, self.mend_indicator_color, ((epx, epy), (w, h + 4))) # end indicator

    
    def reset_selection(self):
        self.selected_col = 0
        self.selection_rect.w = 0
        self.selected_text = ""

        # var for selection using mouse
        self.mouseLeftBtnDown = False
        self.mselection_start_row_n_col = (0, 0)
        self.mselection_end_row_n_col = (0, 0)
        self.mselected_text = [] # list of strings each element is new line
        self.mLBD_N_mMotion = False # mouse left btn down and mouse in motion
        self.dispMouseSelection = False


    # =================== Insertion ============
    def insert_text(self, text = ""):
        self.get_row_n_col(self.cursor_surf_rect.topleft)
        if self.curr_col != len(self.text[self.line_num]) - 1:
            txt_list = list(self.text[self.line_num])
            txt_list.insert(self.curr_col - 1, text)
            join_txt = "".join(txt_list)
            self.text[self.line_num] = join_txt
        else:
            self.text[self.line_num] += text



    # ================ Deletion ==============
    def delete_text(self):
        self.get_row_n_col(self.cursor_surf_rect.topleft)
        if self.curr_col != len(self.text[self.line_num]) - 1:
            txt_list = list(self.text[self.line_num])
            txt_list.pop(self.curr_col)
            join_txt = "".join(txt_list)
            self.text[self.line_num] = join_txt
        else:
            self.text[self.line_num] = self.text[self.line_num][:-1]
    
    def delete_selected_text(self):
        start_col, start_row = self.mselection_start_row_n_col
        start_row += self.mscroll_num
        end_col, end_row = self.mselection_end_row_n_col
        end_row += self.mscroll_num

        
        if end_row > start_row:
            # self.text[start_row] = self.text[start_row][:start_col]
            # self.text[end_row] = self.text[end_row][end_col + 1:]
            # self.text = self.text[:start_row + 1] + self.text[end_row:]
            pop_cnt = 0
            # For moving cursor 
            if (end_row == len(self.text) - 1):
                self.cursor_surf_rect.y -= self.font_size[1]

            # For deleting start row line
            if start_col == 0 and start_row != 0:
                self.text.pop(start_row)
                pop_cnt += 1
            else:
                self.text[start_row] = self.text[start_row][:start_col]
            # For deleting end row line
            if end_col == len(self.text[end_row - pop_cnt]) - 1:
                self.text.pop(end_row - pop_cnt)
            else:
                self.text[end_row - pop_cnt] = self.text[end_row - pop_cnt][end_col + 1:]
            
            # For deleting lines between (start_row, end_row) open interval
            self.text = self.text[:start_row + 1 - pop_cnt] + self.text[end_row - pop_cnt:]

            

            self.reset_selection()
            return True
        return False
    
    

    # =============== Taking File path =============
    def draw_popup_window(self):
        if self.win_is_open:
            # self.relative_path = os.path.dirname(__file__) # recalculating relative path
            f = self.font.render(self.file_path, 1, (0, 0, 0))
            self.te_surf.blit(self.popup_window_surf, (self.te_size[0]//2 - 200, self.te_size[1]//2 - 150//2))
            self.te_surf.blit(f, (self.te_size[0]//2 - 200 + 36, self.te_size[1]//2 - 150//2 + 66))


    # ============== Syntax Highlighting ============== #
    def syntax_hightlighting(self, curr_ln, keyword, keyword_color):
        all_pos = findString(self.text[curr_ln], keyword)
        for pos in all_pos:
            hl_txt = self.font.render(keyword, 1, keyword_color)
            x = self.font_size[0] * (pos + 4) + self.space_after_ln - (self.horizontal_scroll * self.hscroll_num)
            y = self.font_size[1] * (curr_ln + 1) - (self.vertical_scroll * self.mscroll_num) - (self.vertical_scroll * self.vscroll_num)
            hl_txt_rect = hl_txt.get_rect(topleft = (x, y))
            # pygame.draw.rect(self.te_surf, (0, 255, 0), ((x, y), self.font_size))
            self.te_surf.blit(hl_txt, hl_txt_rect)
    
    def builtin_keyword_sh(self, curr_ln):
        for keyword in self.builtin_keywords:
            self.syntax_hightlighting(curr_ln, keyword, self.builtin_keyword_color)

    def comment_sh(self, curr_ln):
        for i in range(len(self.text[curr_ln])):
            if self.text[curr_ln][i] == "#":
                self.syntax_hightlighting(curr_ln, self.text[curr_ln][i:], self.comment_color)
    
    def escape_char_sh(self, curr_ln):
        for i in range(len(self.text[curr_ln])):
            if self.text[curr_ln][i] == "\\":
                self.syntax_hightlighting(curr_ln, self.text[curr_ln][i:i+2], self.escape_char_color)
    
    def string_sh(self, curr_ln):
        quote_cnt = 0
        start = -1
        end = len(self.text[curr_ln])
        for i in range(len(self.text[curr_ln])):
            if self.text[curr_ln][i] == "\"":
                quote_cnt += 1
                if quote_cnt == 1:
                    start = i
                elif quote_cnt >= 2:
                    end = i
                    quote_cnt = 0
        if start != -1:
            self.syntax_hightlighting(curr_ln, self.text[curr_ln][start:end + 1], self.string_color)
    
    def function_sh(self, curr_ln):
        temp = self.text[curr_ln].split(".")
        for i in temp:
            if "(" in i:
                a = i.find("(")
                self.syntax_hightlighting(curr_ln, i[:a].split()[-1], self.function_color)
            
    def object_sh(self, curr_ln):
        temp = self.text[curr_ln].split()
        for i in temp:
            if "." in i:
                a = i.find(".")
                self.syntax_hightlighting(curr_ln, i[:a], self.object_color)

    def html_sh(self, curr_ln):
        angular_brackets_cnt = 0
        start = -1
        end = len(self.text[curr_ln])
        for i in range(len(self.text[curr_ln])):
            if self.text[curr_ln][i] == "\"":
                angular_brackets_cnt += 1
                if angular_brackets_cnt == 1:
                    start = i
                elif angular_brackets_cnt >= 2:
                    end = i
                    angular_brackets_cnt = 0
        if start != -1:
            self.syntax_hightlighting(curr_ln, self.text[curr_ln][start:end + 1], self.string_color)
    
    # Enable the syntax_highlighting
    def enable_syntax_highlighting(self, curr_ln):
        # syntax highlighting 
        self.builtin_keyword_sh(curr_ln)
        self.function_sh(curr_ln)
        self.object_sh(curr_ln)
        self.syntax_hightlighting(curr_ln, "self", self.self_color) # specific for python 
        self.string_sh(curr_ln)
        self.escape_char_sh(curr_ln)
        self.comment_sh(curr_ln)

    

    # ======================== Mutant Mode ======================== #
    def enableMutantMode(self):
        self.get_row_n_col(self.cursor_surf_rect.topleft)
        if self.cmd == "dd":
            self.deleteSingleLine()
        elif self.cmd.startswith("d"):
            if len(self.cmd) > 1:
                if self.cmd[1] == "b": # for deleting from current line till bottom of the text file
                    self.text = self.text[:self.line_num + 1]
                elif self.cmd[1] == "t": # for deleting from current line till top of the text fil
                    self.deleteTillTop()
                else: # for deleting from current line till the given cmd_line
                    if int(self.cmd[1]) < len(self.text):
                        self.text = self.text[:self.line_num] + self.text[self.line_num + int(self.cmd[1]):]
                    else:
                        self.text = self.text[:self.line_num + 1]
                self.cmd = ""
                    
        elif self.cmd.startswith("r"): # For replacing the charactere under the cursor
            if len(self.cmd) > 1:
                self.text[self.line_num] = self.text[self.line_num][:self.curr_col] + self.cmd[1] + self.text[self.line_num][self.curr_col + 1:]
                self.cmd = ""
        elif self.cmd == "x": # for deleting the character under the cursor
            if self.text[self.line_num] and self.text[self.line_num][self.curr_col]:
                self.text[self.line_num] = self.text[self.line_num][:self.curr_col] + self.text[self.line_num][self.curr_col + 1:]
                self.prev_cmd = self.cmd
                self.cmd = ""
                if self.curr_col == len(self.text[self.line_num]):
                    if self.curr_col >= 1:
                        self.cursor_surf_rect.x = (len(self.text[self.line_num]) + self.space_after_ln - 1) * self.font_size[0] + self.space_after_ln
        elif self.cmd == ".": # for repeating the previous cmd
            self.cmd = self.prev_cmd
        else:
            if self.cmd:
                self.prev_cmd = self.cmd
            self.cmd = ""

        self.get_row_n_col(self.cursor_surf_rect.topleft) # recalculate 
    
    # Delete Functions
    def deleteSingleLine(self):
        if len(self.text) > 1:
            if self.line_num + 1 < len(self.text):
                self.cursor_surf_rect.x = len(self.text[self.line_num + 1]) * self.font_size[0] + self.offset + 4
                self.text.pop(self.line_num)
            else:
                self.cursor_surf_rect.x = len(self.text[self.line_num - 1]) * self.font_size[0] + self.offset + 4
                self.cursor_surf_rect.y -= self.font_size[1]
                self.text.pop(self.line_num)
                self.line_num -= 1
        elif len(self.text) == 1:
            print("working")
            self.cursor_surf_rect.x = self.offset + self.space_after_ln
            self.text[self.line_num] = ""
        self.prev_cmd = self.cmd
        self.cmd = ""

    def deleteTillTop(self):
        self.cursor_surf_rect.y -= len(self.text[:self.line_num]) * self.font_size[1]
        temp = self.line_num
        self.line_num -= len(self.text[:self.line_num])
        self.text = self.text[temp:]

    
    # ======================== Mutant Mode ======================== #
    
    # Draw 
    def draw(self):
        # mode indicatior
        self.te_display.fill(self.mode_color)

        # drawing surf
        self.te_display.blit(self.te_surf, self.te_pos)
        self.te_surf.fill(self.bg_color)
        
        # drawing line number bg rect
        #pygame.draw.rect(self.te_surf, self.line_bgrectcolor, pygame.Rect(0, 0, self.line_num_w, self.te_size[1]))
            
        # Hold backspace
        self.backspace_hold()

        # Scroll
        # self.scroll_window()
        self.scroll_horizontal_horizontal()  # Need to implement for left

        # Selection 
        # self.get_selection()
        if self.selected_col > 0:
            pygame.draw.rect(self.te_surf, self.selection_color, self.selection_rect)
        
        # display the mouse selection
        if self.dispMouseSelection:
            self.draw_mouse_selection()


        # Display mode indicator
        pygame.draw.rect(self.te_surf, self.mode_color, self.mode_indi_rect, border_radius=5)

        
        # Draw cursor
        self.te_surf.blit(self.cursor_surf, self.cursor_surf_rect)

        # enable mutantMode
        if self.mutantMode:
            self.enableMutantMode()

        
        # display the text
        # Adding Lazy loading
        # Want to add vscroll self.text_to_display = self.text[self.mscroll_num + self.vscroll:self.num_line_screen_can_display + self.mscroll_num + self.vscorll]
        self.text_to_display = self.text[self.mscroll_num + self.vscroll_num:self.num_line_screen_can_display + self.mscroll_num + self.vscroll_num]
        for ln, text in enumerate(self.text_to_display):
            # Displaying the line numbers
            self.scroll_y = ln + self.mscroll_num + self.vscroll_num
            ln_text = self.font.render(str(self.scroll_y + 1), 1, self.line_num_color)
            self.ln_txt_rect = ln_text.get_rect(topright = (self.line_num_w - (self.horizontal_scroll * self.hscroll_num), self.font_size[1] * (self.scroll_y + 1) - (self.vertical_scroll * self.mscroll_num) - (self.vertical_scroll * self.vscroll_num)))
            if(self.scroll_y == self.line_num):
                self.clis_rect.y = self.font_size[1] * (self.scroll_y + 1) - (self.vertical_scroll * self.mscroll_num) - (self.vertical_scroll * self.vscroll_num)
                self.te_surf.blit(self.curr_ln_indi_surf, self.clis_rect)

            self.te_surf.blit(ln_text, self.ln_txt_rect)

            # Displaying the code text
            txt = self.font.render(text, 1, self.fg_color)
            txt_posx = self.MARGIN + self.line_num_w + self.space_after_ln
            txt_posy = self.font_size[1] * (self.scroll_y + 1)
            self.txt_rect = txt.get_rect(topleft= (txt_posx - (self.horizontal_scroll * self.hscroll_num), txt_posy - (self.vertical_scroll * self.mscroll_num) - (self.vertical_scroll * self.vscroll_num) ))
            self.te_surf.blit(txt, self.txt_rect)

            # Enabling the Syntax Highlighting
            self.enable_syntax_highlighting(self.scroll_y)
        

        # Draw Plugins
        self.fileManager.draw(self.te_surf)
        self.intellisense.draw(self.te_surf, self.cursor_surf_rect.bottomright, self.text, self.line_num, self.curr_col)

        # popup window for taking file path
        self.draw_popup_window()