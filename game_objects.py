#!/usr/bin/env python3

import sys


class Ball:
    '''Game\'s ball object that moves in all directions.
    
    Attributes
    ----------
        image : object
            Image of a ball as a PIL object
        x : float
            X coordinate of a ball\'s image
        y : float
            Y coordinate of a ball\'s image
    '''

    def __init__(self, image, x, y):
        self.image = image
        self.x = x
        self.y = y
        self.x_direction = 1
        self.y_direction = -1

        if sys.platform == 'linux':
            self.movement_speed = 6
        else:
            self.movement_speed = 1
    
    def move(self):
        '''Moves ball in a given direction'''

        self.x += self.movement_speed * self.x_direction
        self.y += self.movement_speed * self.y_direction


class Block:
    '''Game\'s block object that must be hit by the ball.
    
    Attributes
    ----------
        image : object
            Image of a block as a PIL object
        x : float
            X coordinate of a block\'s image
        y : float
            Y coordinate of a block\'s image
    '''

    def __init__(self, image, x, y):
        self.image = image
        self.x = x
        self.y = y


class Platform:
    '''Game\'s platform object that moves horizontally and catches the
    ball.
    
    Attributes
    ----------
        image : object
            Image of a platform as a PIL object
        x : float
            X coordinate of a platform\'s image
        y : float
            Y coordinate of a platform\'s image
    '''

    def __init__(self, image, x, y):
        self.image = image
        self.x = x
        self.y = y