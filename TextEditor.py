import pygame
from pygame.locals import *

# COLORS
DEFAULT_BG_COLOR = (11, 14, 20)
DEFAULT_CURSOR_COLOR = (255, 255, 255)

# helper function
def cnv_to_per(percent, of=100):
    result = percent/100 * of
    return result


class TextEditor:
    # Cslass Constructor
    def __init__(self, pos, size, bg_color = DEFAULT_BG_COLOR, tab_size = 4, cursor_color = DEFAULT_CURSOR_COLOR, cursor_style="filled_box", font = "Consolas", font_size = 18, line_num_color = (255, 255, 0), line_bgrectcolor = (55, 55, 55)):
        # CONSTANTS
        self.MARGIN = 10
        self.TAB_SIZE = tab_size

        # screen
        pygame.init()
        pygame.font.init()
        self.te_display = pygame.display.get_surface()
        self.te_pos = pos
        self.te_size = size
        self.te_surf = pygame.Surface(self.te_size)

        # colors
        self.bg_color = bg_color
        self.fg_color = (255, 255, 255)
        
        # font
        self.font = pygame.font.SysFont(font, font_size)
        self.font_size = self.font.size("a")
        self.text = [""]

        # line numbers
        self.line_num = 0
        self.line_num_color = line_num_color
        self.line_num_w = 30
        self.space_after_ln = 4
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

        # var for backspacehold 
        self.isBackspaceHold = False
        self.backspaceHoldTimer = 50    # 50 mili second

        # var for vertical scroll
        self.vertical_scroll = self.font_size[1] # 5 * self.font_size[1]
        self.cursor_scroll = 1 # just true(1) or false(0)
        self.vscroll_num = 0

        # var for horizontal scroll
        self.horizontal_scroll = self.font_size[0]
        self.overflow = 0
        self.hscroll_num = 0

        # selection
        self.selection_start_col = 0
        self.selected_col = 0
        self.selected_row = 0
        self.selection_dir = 0 # selection direction



    # Handle Events
    def handle_events(self, event):
        # Keyboard events
        if event.type == pygame.KEYDOWN:
            # Backspace
            if event.key == pygame.K_BACKSPACE:
                self.isBackspaceHold = True
                if self.text[self.line_num] or self.text[self.line_num - 1] or self.text[self.line_num - 1] == "":
                    # print(self.curr_row, self.curr_col)
                    # if (self.text[self.line_num - 1] or self.text[self.line_num - 1] == "") and self.text[self.line_num] == "":
                    #     print("before line")
                    #     if self.line_num > 0:
                    #         self.cursor_surf_rect.y = self.font_size[1] * (self.line_num)
                    #         self.cursor_surf_rect.x = self.font.size(self.text[self.line_num - 1])[0] + self.cursor_posx
                    #         self.line_num -= 1
                    #         self.text.pop(self.line_num + 1)
                    # else:
                    if self.text[self.line_num] and self.curr_col != 0:
                        self.cursor_surf_rect.x -= self.font_size[0]
                        self.delete_text()
                    else:
                        if self.line_num > 0:
                            self.cursor_surf_rect.y = self.font_size[1] * (self.line_num)
                            self.cursor_surf_rect.x = self.font.size(self.text[self.line_num - 1])[0] + self.cursor_posx
                            self.text[self.line_num] = self.text[self.line_num - 1] + self.text[self.line_num] 
                            self.line_num -= 1
                            self.text.pop(self.line_num)
                    self.get_row_n_col(self.cursor_surf_rect.topleft) # recalculate col and row

            # Enter 
            elif event.key == pygame.K_RETURN:
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
            elif event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                self.ctrl = True
            elif event.key == pygame.K_LALT or event.key == pygame.K_RALT:
                pass
            elif self.ctrl and event.key == pygame.K_s: #  CTRL + s -> for saving file
                self.save_file()
            elif self.ctrl and event.key == pygame.K_o: #  CTRL + o -> for opening file
                self.open_file()
            # Tab
            elif event.key == pygame.K_TAB:
                self.cursor_surf_rect.x += self.font_size[0] * self.TAB_SIZE
                self.text[self.line_num] += ' ' * self.TAB_SIZE
            # Motion Keys (i.e Left, Right, Up, Down)
            # Right Key
            elif event.key == pygame.K_RIGHT:
                # Motion
                self.update_cursor_according_to_keys(horizontalDir = 1)
                # Selection
                if self.shift:
                    self.selection_dir = 1
                    self.selected_col += 1
                    self.get_selection()
                self.insert_text()
            # Left Key
            elif event.key == pygame.K_LEFT:
                # Motion
                self.update_cursor_according_to_keys(horizontalDir = -1)
                # Selection
                if self.shift:
                    self.selection_dir = -1
                    self.selected_col += 1
                    self.get_selection()
                self.insert_text()
            # Down Key
            elif event.key == pygame.K_DOWN:
                self.update_cursor_according_to_keys(verticalDir = 1)
                self.cursor_scroll = 1
                self.scroll_window() # scroll window downwards if the cursor is at end of screen
                self.insert_text()
            # Up Key
            elif event.key == pygame.K_UP:
                self.update_cursor_according_to_keys(verticalDir = -1)
                if(self.cursor_surf_rect.topleft[1] <= self.font_size[1] and self.line_num != 0):
                    self.cursor_scroll = 0
                    self.vscroll_num -= 1
                    self.line_num -= 1 
                self.scroll_window() # scroll window upwards if the cursor is at top of screen and if there are lines up
                self.insert_text()

            # Other keys
            else:
                self.cursor_surf_rect.x += self.font_size[0]
                # insertion
                self.insert_text(event.unicode)
                

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

        # Mouse Events
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.update_cursor_according_to_mouse()


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
            self.cursor_surf = pygame.Surface((4,self.font_size[1] + 2))
    

    # update cursor pos
    def update_cursor_according_to_mouse(self):
        self.mouse_pos = pygame.mouse.get_pos()
        row = round(self.mouse_pos[1] / self.font_size[1])
        col = round(self.mouse_pos[0] / self.font_size[0])
        self.cursor_surf_rect.x = col * self.font_size[0]
        self.cursor_surf_rect.y = row * self.font_size[1]
        self.line_num = row - 1
        print(row, col)


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
                self.line_num += verticalDir
                self.cursor_surf_rect.x = self.font.size(self.text[self.line_num])[0] + self.cursor_posx
                self.cursor_surf_rect.y += (verticalDir * self.font_size[1])


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


    # Save file
    def save_file(self):
        file_path = input("Enter file path : ")
        with open(file_path, "w") as file:
            file.write("\n".join(self.text))
            print("File Saved Successfully")


    # Open file
    def open_file(self, fpath=None):
        if fpath:
            file_path = fpath
        else:
            file_path = input("Enter file path : ")
        with open(file_path, "r") as file:
            txt = file.read()
            self.text = txt.split("\n")
            print("File Opened Successfully")
            self.line_num = len(self.text) - 1
            self.cursor_surf_rect.x = self.font.size(self.text[-1])[0] + self.cursor_posx    
            self.cursor_surf_rect.y = self.font.size(self.text[-1])[1] * len(self.text)


    # =================== Selection ===========
    def get_selection(self):
        if not self.selection_start_col:
            self.selection_start_col = round(self.cursor_surf_rect.topleft[0] / self.font_size[0]) - 4
        if self.selection_dir == 1:
            print(self.text[self.line_num][self.selection_start_col - 1:self.selection_start_col + self.selected_col])
            print("selection from left to right")
        elif self.selection_dir == -1:
            print(self.text[self.line_num][self.selection_start_col - self.selected_col:self.selection_start_col])
            print("selection from right to left")
        print(self.selection_start_col)
    
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

    # Draw 
    def draw(self):
        # drawing surf
        self.te_display.blit(self.te_surf, self.te_pos)
        self.te_surf.fill(self.bg_color)
        
        # drawing line number bg rect
        #pygame.draw.rect(self.te_surf, self.line_bgrectcolor, pygame.Rect(0, 0, self.line_num_w, self.te_size[1]))
            
        # Hold backspace
        self.backspace_hold()

        # Scroll
        # self.scroll_window()
        self.scroll_horizontal_horizontal()

        # Selection 
        # self.get_selection()
        
        # display the text
        for ln, text in enumerate(self.text):
            txt = self.font.render(text, 1, self.fg_color)
            txt_posx = self.MARGIN + self.line_num_w + self.space_after_ln
            txt_posy = self.font_size[1] * (ln + 1)
            self.txt_rect = txt.get_rect(topleft= (txt_posx - (self.horizontal_scroll * self.hscroll_num), txt_posy - (self.vertical_scroll * self.vscroll_num) ))
            self.te_surf.blit(txt, self.txt_rect)

            # Displaying the line numbers
            ln_text = self.font.render(str(ln + 1), 1, self.line_num_color)
            self.ln_txt_rect = ln_text.get_rect(topright = (self.line_num_w - (self.horizontal_scroll * self.hscroll_num), self.font_size[1] * (ln + 1) - (self.vertical_scroll * self.vscroll_num)))
            if(ln == self.line_num):
                self.ln_txt_rect.x -= 10
            self.te_surf.blit(ln_text, self.ln_txt_rect)
        

        # Draw cursor
        self.te_surf.blit(self.cursor_surf, self.cursor_surf_rect)