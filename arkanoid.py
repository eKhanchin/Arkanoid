#!/usr/bin/env python3

import sys
sys.path.append(
    '/usr/intel/pkgs/python3/3.7.4/modules/r1/lib/python3.7/site-packages/'
)

import json
import math
import os
from PIL import Image, ImageTk
from random import randint
import time
from tkinter import Canvas
from tkinter import CENTER
from tkinter import StringVar
from tkinter import Tk
from tkinter import ttk

from game_objects import Ball
from game_objects import Block
from game_objects import Platform


class ArkanoidGame:
    '''A classic game where the main target is to hit all blocks with
    a ball without dropping it using a platform.
    
    Attributes
    ----------
        master : object
            tkinter root window object
    '''

    def __init__(self, master):
        self.master = master
        master.title('Arkanoid')

        # Size of a window
        self.width = 1200
        self.height = 820
        master.geometry(f'{self.width}x{self.height}+100+200')
        master.resizable(False, False)

        # Game's common variables
        self.initiate_common_attributes()

        # Configures game's style
        self.configure_style()

        # Creates a welcome screen
        self.create_welcome_screen()

    def initiate_common_attributes(self):
        '''Initiates common game\'s attributes'''

        self._job = None
        game_dir = os.path.realpath(__file__)
        self.game_dir = os.path.dirname(game_dir)
        self.platform_width = 90
        self.platform_height = 20
        self.ball_width = 15
        self.ball_height = 15
        self.ball_shot = False
        self.rows = 12
        self.columns = 18
        self.blocks_variations = 7
        self.block_width = 58
        self.block_height = 37
        self.labels_coordinates = {
            'level': (521, 5),
            'gameover': (478, 5),
            'win': (507, 5)
        }

    def configure_style(self):
        '''Configures game\'s overall style'''
        
        # Game's colors
        colors = {
            'info_background': '#14262e',
            'game_background': '#324851',
            'play_button_background': '#59a3c2',
            'play_button_foreground': '#ffffff',
            'play_button_active': '#6fc8ed',
            'title': '#ffffff',
            'window_background': '#000000'
        }
        self.color_map = colors

        # Defines game's styles
        style = ttk.Style()

        # Game window style
        self.master.configure(background=colors['window_background'])

        # Start button style
        if sys.platform == 'linux':
            style.configure(
                'Start.TButton',
                font=('Calibri', 16, 'bold'),
                background=colors['play_button_background'],
                foreground=colors['play_button_foreground']
            )
        else:
            style.configure(
                'Start.TButton',
                font=('Calibri', 16, 'bold')
            )

        style.map(
            'Start.TButton',
            background=[('active', colors['play_button_active'])]
        )
        
        # Info labels style
        style.configure(
            'Info.TLabel',
            font=('Calibri', 18, 'bold'),
            background=colors['info_background'],
            foreground=colors['title']
        )

        # Level labels style
        style.configure(
            'Level.TLabel',
            font=('Calibri', 32, 'bold'),
            background=colors['game_background'],
            foreground=colors['title']
        )

    def create_welcome_screen(self):
        '''Creates game\'s welcome screen'''

        colors = self.color_map

        # Spatial UI that has information about level, score, and amount
        # of lives
        canvas = Canvas(
            self.master,
            width=self.width-20,
            height=65,
            background=colors['info_background'],
            highlightthickness=0
        )
        canvas.place(x=8, y=10)
        self.info_bar = canvas

        # Gameplay space
        canvas = Canvas(
            self.master,
            width=self.width-20,
            height=self.height-90,
            background=colors['game_background'],
            highlightthickness=0
        )
        canvas.place(x=8, y=80)
        self.playground_canvas = canvas

        # Title
        title = canvas.create_text(
            594, 198,
            fill=colors['title'],\
            font=('Calibri', 36, 'bold'),
            text="ARKANOID"
        )
        self.title = title

        # Play button
        button = ttk.Button(
            canvas,
            text='START THE GAME',
            style='Start.TButton',
            command=self.prepare_for_game
        )
        button.place(x=492, y=443, width=200, height=50)
        self.start_button = button
    
    def prepare_for_game(self):
        '''Prepares to start the game'''

        canvas = self.playground_canvas
        
        # Clears playground by removing the widgets
        canvas.delete(self.title)
        self.start_button.destroy()

        # Initializes the game
        self.create_info_bar()

        # Creates a platform object and image
        self.create_platform()

        # Creates a ball object and image
        self.create_ball()

        # Creates level
        self.create_level()

        # Hides mouse cursor
        self.master.config(cursor='none')

    def create_info_bar(self):
        '''Creates labels of info bar'''

        info_canvas = self.info_bar

        # Level label
        self.level = StringVar()
        self.level.set('1')

        ttk.Label(
            info_canvas,
            text='Level',
            style='Info.TLabel'
        ).place(x=362, y=5)

        label = ttk.Label(
            info_canvas,
            textvariable=self.level,
            style='Info.TLabel',
            anchor='center',
            width=10
        )
        if sys.platform == 'linux':
            label.place(x=336, y=34)
        else:
            label.place(x=331, y=34)

        self.level_label = label

        # Score label
        self.score = StringVar()
        self.score.set('0')

        ttk.Label(
            info_canvas,
            text='Score',
            style='Info.TLabel'
        ).place(x=567, y=5)

        label = ttk.Label(
            info_canvas,
            textvariable=self.score,
            style='Info.TLabel',
            anchor='center',
            width=10
        )
        if sys.platform == 'linux':
            label.place(x=544, y=34)
        else:
            label.place(x=534, y=34)

        self.score_label = label

        # Lives label
        self.lives = StringVar()
        self.lives.set('3')

        ttk.Label(
            info_canvas,
            text='Lives',
            style='Info.TLabel'
        ).place(x=772, y=5)

        label = ttk.Label(
            info_canvas,
            textvariable=self.lives,
            style='Info.TLabel',
            anchor='center',
            width=10
        )
        if sys.platform == 'linux':
            label.place(x=744, y=34)
        else:
            label.place(x=734, y=34)

        self.lives_label = label
    
    def create_platform(self):
        '''Creates a platform'''

        canvas = self.playground_canvas

        image = ImageTk.PhotoImage(
            Image.open(self.game_dir + '/pics/platform.png')
        )

        # x,y of platform's center
        x = 571
        y = 680

        self.platform_image = canvas.create_image(
            x, y,
            anchor=CENTER,
            image=image
        )
        self.platform = Platform(image, x, y)
    
    def create_ball(self):
        '''Creates in game ball'''

        canvas = self.playground_canvas
        image = ImageTk.PhotoImage(
            Image.open(self.game_dir + '/pics/ball.png')
        )

        # x,y of ball's center
        x = self.platform.x
        y = self.platform.y - self.platform_height/2 - self.ball_height/2

        self.ball_image = canvas.create_image(
            x, y,
            anchor=CENTER,
            image=image
        )
        self.ball = Ball(image, x, y)

        canvas.bind('<Button-1>', self.move_ball)

    def create_level(self, level=1):
        '''Creates blocks of the next level.
        
        Parameters
        ----------
            level : int
                Number of a level
        '''

        canvas = self.playground_canvas

        # Gets next level
        level_str = 'level' + str(level)
        with open(self.game_dir+'/levels/levels.json', 'r') as f:
            levels = json.load(f)
        level_blocks = levels[level_str]

        self.block_images = []
        self.blocks = []
        
        for i in range(self.rows):
            for j in range(self.columns):
                if level_blocks[i][j]:
                    block_indexber = randint(1, self.blocks_variations)
                    image = ImageTk.PhotoImage(
                        Image.open(self.game_dir + '/pics/block_' + str(block_indexber)\
                            + '.png')
                    )

                    # x,y of block's center
                    x = 100 + j*self.block_width
                    y = 100 + i*self.block_height

                    block_image = canvas.create_image(
                        x, y,
                        anchor=CENTER,
                        image=image
                    )
                    self.block_images.append(block_image)
                    self.blocks.append(Block(image, x, y))
        
        self.block_images.reverse()
        self.blocks.reverse()

        # Show label presenting current level
        x, y = self.labels_coordinates['level']
        self.show_label('LEVEL '+str(level), x=x, y=y)

    def move_platform(self, event=None):
        '''Redraws platform image on a new x coordinate'''

        canvas = self.playground_canvas
        new_x = canvas.canvasx(event.x)

        # Stops platform at the left edge
        if new_x < self.platform_width/2:
            new_x = self.platform_width/2
        
        # Stops platform at the right edge
        canvas_width = float(canvas.cget('width'))
        if canvas_width-self.platform_width/2 < new_x:
            new_x = canvas_width - self.platform_width/2

        # Redraws the platform 
        canvas.delete(self.platform_image)
        self.platform.x = new_x
        self.platform_image = canvas.create_image(
            self.platform.x,
            self.platform.y,
            anchor=CENTER,
            image=self.platform.image
        )

        if not self.ball_shot:
            # Redraws the ball to be in the center of the platform
            canvas.unbind('<Button-1>')
            canvas.delete(self.ball_image)
            self.create_ball()

        return 'break'

    def move_ball(self, event=None):
        '''Moves a piece down'''

        self.ball_shot = True

        canvas = self.playground_canvas
        canvas.unbind('<Button-1>')
        
        self.ball.move()
        result = self.check_collision()

        if result == 'LOST LIFE':
            self.master.after_cancel(self._job)
            self._job = None
            
            # Reduces one life
            lives = int(self.lives.get())
            lives -= 1
            self.lives.set(str(lives))

            if lives == 0:
                print('GAME OVER')

                x, y = self.labels_coordinates['gameover']
                self.show_label(text='GAME OVER', x=x, y=y)

                self.playground_canvas.unbind('<Motion>')
            else:
                # Redraws the platform at the beginning
                self.redraw_objects()

            return
        elif result == 'WIN':
            print('FINISHED LEVEL')

            # Disables ball's movement
            self.master.after_cancel(self._job)
            self._job = None

            # Increases level
            level = int(self.level.get())
            level += 1
            if level < 3:
                # Updates level
                self.level.set(str(level))
            else:
                print('FINISHED GAME')

                x, y = self.labels_coordinates['win']
                self.show_label(text='YOU WIN', x=x, y=y)

                return

            # Creates next level
            self.redraw_objects()
            self.create_level(level=level)
            
            return

        # Redraws the ball
        self.redraw_ball()

        if sys.platform == 'linux':
            self._job = self.master.after(1, self.move_ball)
        else:
            self._job = self.master.after(2, self.move_ball)

    def check_collision(self):
        '''Checks ball\'s collision.
        
        Returns
        -------
            result : str
                Whether the ball fell or everything is ok
        '''

        # Checks ball collision with canvas boundaries
        result = self.check_boundary_collision()
        if result == 'LOST LIFE':
            return result
        
        # Checks ball collision with the platform
        self.check_platform_collision()

        # Checks ball collision with the block
        result = self.check_block_collision()
        if result == 'HIT':
            # Calculates the score
            score = int(self.score.get())
            score += 100
            self.score.set(str(score))

            # Checks whether there are any blocks left
            if not self.blocks:
                return 'WIN'

        return 'OK'

    def check_boundary_collision(self):
        '''Checks ball\'s collision with canvas boundaries.
        
        Returns
        -------
            result : str
                Whether the ball fell or everything is ok
        '''

        canvas = self.playground_canvas
        ball_x = self.ball.x
        ball_y = self.ball.y

        # Ball reached left edge of the canvas
        if ball_x < self.ball_width/2:
            self.ball.x_direction = 1
            self.ball.x = self.ball_width/2
        
        # Ball reached right edge of the canvas
        canvas_width = float(canvas.cget('width'))
        if canvas_width-self.ball_width/2 < ball_x:
            self.ball.x_direction = -1
            self.ball.x = canvas_width - self.ball_width/2

        # Ball reached upper edge of the canvas
        if ball_y < self.ball_height/2:
            self.ball.y_direction = 1
            self.ball.y = self.ball_height/2
        
        # Ball reached bottom edge of the canvas
        canvas_height = float(canvas.cget('height'))
        if canvas_height-self.ball_height/2 < ball_y:
            return 'LOST LIFE'

        return 'OK'
    
    def check_platform_collision(self):
        '''Checks ball\'s collision with the platform'''

        ball_x = self.ball.x
        ball_y = self.ball.y

        # Ball's edges
        ball_bottom = ball_y + self.ball_height/2

        # Platform's edges
        platform_left = self.platform.x - self.platform_width/2
        platform_top = self.platform.y - self.platform_height/2
        platform_right = self.platform.x + self.platform_width/2
        platform_bottom = self.platform.y + self.platform_height/2

        # Hits platform's top
        if platform_left <= ball_x\
                and platform_top <= ball_bottom\
                and ball_x <= platform_right\
                and ball_bottom <= platform_bottom:
            self.ball.y_direction = -1
            self.ball.y = platform_top - self.ball_height/2
    
    def check_block_collision(self):
        '''Checks ball\'s collision with the block.
        
        Returns
        -------
            result : str
                Whether the ball hit the block
        '''

        for block_index, block in enumerate(self.blocks):
            ball_x = self.ball.x
            ball_y = self.ball.y

            # Block's edges
            block_left = block.x - self.block_width/2
            block_bottom = block.y + self.block_height/2
            block_right = block.x + self.block_width/2
            block_top = block.y - self.block_height/2

            # Ball's edges
            ball_left = ball_x - self.ball_width/2
            ball_bottom = ball_y + self.ball_height/2
            ball_right = ball_x + self.ball_width/2
            ball_top = ball_y - self.ball_height/2
            
            # Hits block's left
            if block_top<=ball_y and ball_y<=block_bottom\
                    and block_left<=ball_right\
                    and ball_right<=block_right:
                self.delete_block(block_index)
                self.ball.x_direction = -1
                return 'HIT'
            
            # Hits block's bottom
            if block_left<=ball_x and ball_x<=block_right\
                    and block_top<=ball_top\
                    and ball_top<=block_bottom:
                self.delete_block(block_index)
                self.ball.y_direction = 1
                return 'HIT'

            # Hits block's right
            if block_top<=ball_y and ball_y<=block_bottom\
                    and block_left<=ball_left\
                    and ball_left<=block_right:
                self.delete_block(block_index)
                self.ball.x_direction = 1
                return 'HIT'

            # Hits block's top
            if block_left<=ball_x and ball_x<=block_right\
                    and block_top<=ball_bottom\
                    and ball_bottom<=block_bottom:
                self.delete_block(block_index)
                self.ball.y_direction = -1
                return 'HIT'

        return 'OK'

    def redraw_objects(self):
        '''Redraws the platform and the ball'''

        canvas = self.playground_canvas

        self.ball_shot = False

        canvas.delete(self.platform_image)
        canvas.delete(self.ball_image)

        self.create_platform()
        self.create_ball()
    
    def redraw_ball(self):
        '''Redraws the ball only'''

        canvas = self.playground_canvas

        canvas.delete(self.ball_image)
        self.ball_image = canvas.create_image(
            self.ball.x,
            self.ball.y,
            anchor=CENTER,
            image=self.ball.image
        )
    
    def delete_block(self, block_index):
        '''Deletes block from the game.
        
        Parameters
        ----------
            block_index : int
                Index of a block
        '''

        canvas = self.playground_canvas

        del self.blocks[block_index]
        canvas.delete(self.block_images[block_index])
        del self.block_images[block_index]
    
    def show_label(self, text='', x=0, y=0, widget=None, time=2):
        '''Shows a label for 2 seconds.
        
        Parameters:
            text : str
                Text of the label
            x : int
                X coordinate of the label
            y : int
                Y coordinate of the label
            widget : object
                ttk label object
            time : int
                Seconds left to display the label
        '''

        # Unbinds platform motion
        self.playground_canvas.unbind('<Motion>')

        if not widget:
            widget = ttk.Label(
                self.playground_canvas,
                text=text,
                style='Level.TLabel'
            )
            widget.place(x=x, y=y)

        if time == 0:
            self.master.after_cancel(self._job)
            self._job = None

            widget.destroy()

            # Allows platform motion again
            self.playground_canvas.bind('<Motion>', self.move_platform)

            return

        self._job = self.master.after(
            1000,
            lambda: self.show_label(widget=widget, time=time-1)
        )


if __name__ == '__main__':
    root = Tk()
    app = ArkanoidGame(root)
    root.mainloop()