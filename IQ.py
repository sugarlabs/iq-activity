#!/usr/bin/python
# IQ.py

# Copyright (C) 2011  Peter Hewitt
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import pygame
import os
import sys
import random
try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
except ModuleNotFoundError:
    pass

RED, BLUE, GREEN, BLACK, WHITE = (
    255, 0, 0), (0, 0, 255), (0, 255, 0), (0, 0, 0), (255, 255, 255)
CYAN, ORANGE, CREAM, YELLOW = (
    0, 255, 255), (255, 165, 0), (255, 255, 192), (255, 255, 0)
MAGENTA = (255, 0, 255)


class Piece:
    def __init__(self):
        self.xy = None
        self.img = None
        self.on_grid = False


class TN:
    def __init__(self, x, y, img):
        self.xy = (x, y)
        self.img = img


class IQ:

    def __init__(self, parent):
        self.parent = parent
        self.journal = True  # set to False if we come in via main()
        # set to the pygame canvas if we come in via activity.py
        self.canvas = None
        self.loaded = []  # list of strings
        # numbered 0 to 9 - piece 0 is fixed in top left
        self.puzzles = [
            ['3a', '1a', '2a', '4a', '5a', '6a', '7a', '8a', '9a', '10a'],
            ['7b', '1b', '2b', '3b', '4b', '5b', '6b', '8b', '9b', '10b'],
            ['5c', '1a', '2a', '3c', '4c', '6c', '7c', '8c', '9c', '10c'],
            ['10d', '1b', '2b', '3d', '4d', '5d', '6d', '7d', '8d', '9d'],
            ['2a', '1b', '3b', '4c', '5e', '6d', '7a', '8c', '9a', '10b'],
            ['6a', '1a', '2b', '3c', '4d', '5f', '7b', '8d', '9b', '10c'],
            ['1b', '6b', '2a', '3d', '4a', '5g', '7c', '8a', '9c', '10d'],
            ['8b', '1b', '2b', '3e', '4e', '5c', '6d', '7a', '9a', '10e'],
            ['9d', '1b', '2b', '3f', '4d', '5c', '6c', '7d', '8c', '10f'],
            ['4b', '1b', '2b', '3f', '5c', '6c', '7d', '8c', '9b', '10f']
        ]
        # numbered 0 to 9
        self.pieces = []
        self.tns = []
        self.z = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    def display(self):
        self.screen.fill((128, 0, 0))
        self.draw()
        if self.complete():
            self.centre_blit(self.screen, self.smiley, self.smiley_c)

    def do_click(self):
        return self.click()

    def do_button(self, bu):
        if bu == 'new':
            pass

    def do_key(self, key):
        if key in self.SQUARE:
            self.do_button('new')
            return
        if key == pygame.K_v:
            self.version_display = not self.version_display
            return

    def flush_queue(self):
        flushing = True
        while flushing:
            flushing = False
            if self.journal:
                while Gtk.events_pending():
                    Gtk.main_iteration()
            for event in pygame.event.get():
                flushing = True

    def load(self, f):
        try:
            for line in f.readlines():
                self.loaded.append(line)
        except Exception:
            pass

    def save(self, f):
        f.write(str(self.solved)+'\n')

    # note need for rstrip() on strings

    def retrieve(self):
        if len(self.loaded) > 0:
            self.solved = int(self.loaded[0])

    def init(self):  # called by run()
        random.seed()

        self.redraw = True
        self.version_display = False
        self.screen = pygame.display.get_surface()
        # pygame.display.set_caption(app)
        self.screen.fill((128, 0, 0))
        pygame.display.flip()
        self.w, self.h = self.screen.get_size()
        if float(self.w)/float(self.h) > 1.5:  # widescreen
            # we assume 4:3 - centre on widescreen
            self.offset = (self.w-4*self.h/3)/2
        else:
            self.h = int(.75*self.w)  # allow for toolbar - works to 4:3
            self.offset = 0
        # measurement scaling factor (32x24 = design units)
        self.factor = float(self.h)/24
        # image scaling factor - all images built for 1200x900
        self.imgf = float(self.h)/900
        self.clock = pygame.time.Clock()
        if pygame.font:
            self.t = int(40*self.imgf)
            self.font1 = pygame.font.Font(None, self.t)
            self.t = int(80*self.imgf)
            self.font2 = pygame.font.Font(None, self.t)
        self.message = ''
        self.pos = pygame.mouse.get_pos()
        self.pointer = pygame.image.load('data/pointer.png')
        pygame.mouse.set_visible(False)

        # this activity only

        self.solved = 0
        self.puzzle_n = 0
        self.carry = None
        self.dx = 0
        self.dy = 0
        self.sq = 0
        self.x0, self.y0 = self.sx(9.56), self.sy(2.2)  # top left of grid
        self.finished = False
        try:
            self.frame = self.load_image('frame.png', True)
            self.bgd = self.frame.get_at((50, 50))
        except Exception as e:
            self.frame = pygame.image.load('data/frame.png')
            self.bgd = self.frame.get_at((50, 50))
            print("Peter says: Fallback to pygame image loader. Warning : ", e)
        self.frame2 = self.load_image('frame2.png', False)
        self.redrawn = False  # used to make sure new puzzle thumbnail appears
        self.smiley = self.load_image('smiley.png', True)
        self.smiley_c = (self.sx(27.5), self.sy(9))

    def sx(self, f):  # scale x function
        return int(f*self.factor+self.offset+.5)

    def sy(self, f):  # scale y function
        return int(f*self.factor+.5)

    def run(self):
        pygame.init()
        screen = pygame.display.get_surface()
        screen.fill((0, 0, 0))
        pygame.display.update()

        self.init()
        if not self.journal:
            self.qload()
        self.retrieve()
        self.puzzle_n = self.solved
        if self.puzzle_n == 10:
            self.puzzle_n = 0
        self.iqinit()
        self.iqsetup()

        if self.canvas is not None:
            self.canvas.grab_focus()

        ctrl = False
        pygame.key.set_repeat(600, 120)
        key_ms = pygame.time.get_ticks()
        going = True
        while going:

            if self.journal:
                # Pump GTK messages.
                while Gtk.events_pending():
                    Gtk.main_iteration()

            # Pump PyGame messages.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if not self.journal:
                        self.qsave()
                    going = False
                elif event.type == pygame.MOUSEMOTION:
                    self.pos = event.pos
                    self.redraw = True
                    if self.canvas is not None:
                        self.canvas.grab_focus()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.redraw = True
                    if event.button == 1:
                        self.do_click()
                        self.flush_queue()
                elif event.type == pygame.KEYDOWN:
                    # throttle keyboard repeat
                    if pygame.time.get_ticks()-key_ms > 110:
                        key_ms = pygame.time.get_ticks()
                        if ctrl:
                            if event.key == pygame.K_q:
                                if not self.journal:
                                    self.save()
                                going = False
                                break
                            else:
                                ctrl = False
                        if event.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                            ctrl = True
                            break
                        self.do_key(event.key)
                        self.redraw = True
                        self.flush_queue()
                elif event.type == pygame.KEYUP:
                    ctrl = False
            if not going:
                break
            if self.redraw:
                self.display()
                if self.version_display:
                    self.version_display()
                self.screen.blit(self.pointer, self.pos)
                pygame.display.flip()
                self.redraw = False
                self.complete()
                if self.finished and not self.redrawn:
                    self.redraw = True
                    self.redrawn = True
            self.clock.tick(40)
            pygame.display.update()

    def exit(self):
        self.save()
        pygame.display.quit()
        pygame.quit()
        sys.exit()

    def qsave(self):
        dir = ''
        dir = os.environ.get('SUGAR_ACTIVITY_ROOT')
        if dir is None:
            dir = ''
        fname = os.path.join(dir, 'data', 'iq.dat')
        f = open(fname, 'w')
        self.save(f)
        f.close

    def qload(self):
        dir = ''
        dir = os.environ.get('SUGAR_ACTIVITY_ROOT')
        if dir is None:
            dir = ''
        fname = os.path.join(dir, 'data', 'iq.dat')
        try:
            f = open(fname, 'r')
        except Exception:
            return None  # ****
        try:
            self.load(f)
        except Exception:
            pass
        f.close

    def version_display(self):
        self.message = self.app+' '+self.ver
        self.message += '  '+str(self.screen.get_width())+' x ' + \
            str(self.screen.get_height())
        message(self.screen, self.font1, self.message)

    # loads an image (eg pic.png) from the data subdirectory
    # converts it for optimum display
    # resizes it using the image scaling factor, self.imgf
    #   so it is the right size for the current screen resolution
    #   all images are designed for 1200x900

    def load_image(self, file1, alpha=False, subdir=''):  # eg subdir='glow'
        data = 'data'
        if subdir != '':
            data = os.path.join('data', subdir)
        fname = os.path.join(data, file1)
        try:
            img = pygame.image.load(fname)
        except:
            print("Peter says: Can't find "+fname)
            exit()
        if alpha:
            img = img.convert_alpha()
        else:
            img = img.convert()
        if abs(self.imgf-1.0) > .1:  # only scale if factor <> 1
            w = img.get_width()
            h = img.get_height()
            try:
                img = pygame.transform.smoothscale(
                    img, (int(self.imgf*w), int(self.imgf*h)))
            except:
                img = pygame.transform.scale(
                    img, (int(self.imgf*w), int(self.imgf*h)))
        return img

    # eg new_list=copy_list(old_list)

    def copy_list(self, l):
        new_list = []
        new_list.extend(l)
        return new_list

    def shuffle(self, lst):
        l1 = lst
        lt = []
        for i in range(len(lst)):
            ln = len(l1)
            r = random.randint(0, ln-1)
            lt.append(lst[r])
            l1.remove(lst[r])
        return lt

    def centre_blit(self, screen, img, xxx_todo_changeme, angle=0):  # rotation is clockwise
        (cx, cy) = xxx_todo_changeme
        img1 = img
        if angle != 0:
            img1 = pygame.transform.rotate(img, -angle)
        rect = img1.get_rect()
        screen.blit(img1, (cx-rect.width/2, cy-rect.height/2))

    def text_blit(self, screen, s, font, xxx_todo_changeme1, xxx_todo_changeme2, shadow=True):
        (cx, cy) = xxx_todo_changeme1
        (r, g, b) = xxx_todo_changeme2
        if shadow:
            text = font.render(s, True, (0, 0, 0))
            rect = text.get_rect()
            rect.centerx = cx+2
            rect.centery = cy+2
            screen.blit(text, rect)
        text = font.render(s, True, (r, g, b))
        rect = text.get_rect()
        rect.centerx = cx
        rect.centery = cy
        screen.blit(text, rect)
        return rect

    def text_blit1(self, screen, s, font, xxx_todo_changeme3, xxx_todo_changeme4, shadow=True):
        (x, y) = xxx_todo_changeme3
        (r, g, b) = xxx_todo_changeme4
        if shadow:
            text = font.render(s, True, (0, 0, 0))
            rect = text.get_rect()
            rect.x = x+2
            rect.y = y+2
            screen.blit(text, rect)
        text = font.render(s, True, (r, g, b))
        rect = text.get_rect()
        rect.x = x
        rect.y = y
        screen.blit(text, rect)
        return rect

    # m is the message
    # d is the # of pixels in the border around the text
    # (cx,cy) = co-ords centre - (0,0) means use screen centre

    def message(self, screen, font, m, xxx_todo_changeme5=(0, 0), d=20):
        (cx, cy) = xxx_todo_changeme5
        if m != '':
            if pygame.font:
                text = font.render(m, True, (255, 255, 255))
                shadow = font.render(m, True, (0, 0, 0))
                rect = text.get_rect()
                if cx == 0:
                    cx = screen.get_width()/2
                if cy == 0:
                    cy = screen.get_height()/2
                rect.centerx = cx
                rect.centery = cy
                bgd = pygame.Surface((rect.width+2*d, rect.height+2*d))
                bgd.fill((0, 255, 255))
                bgd.set_alpha(128)
                screen.blit(bgd, (rect.left-d, rect.top-d))
                screen.blit(shadow, (rect.x+2, rect.y +
                                     2, rect.width, rect.height))
                screen.blit(text, rect)

    def mouse_on_img(self, img, xxx_todo_changeme6):  # x,y=top left
        (x, y) = xxx_todo_changeme6
        w = img.get_width()
        h = img.get_height()
        mx, my = self.pos
        if mx < x:
            return False
        if mx > (x+w):
            return False
        if my < y:
            return False
        if my > (y+h):
            return False
        try:  # in case out of range
            col = img.get_at((int(mx-x), int(my-y)))
        except:
            return False
        if col[3] < 10:
            return False
        return True

    def mouse_on_img1(self, img, xxx_todo_changeme7):
        (cx, cy) = xxx_todo_changeme7
        xy = centre_to_top_left(img, (cx, cy))
        return mouse_on_img(img, xy)

    def mouse_on_img_rect(self, img, xxx_todo_changeme8):
        (cx, cy) = xxx_todo_changeme8
        w2 = img.get_width()/2
        h2 = img.get_height()/2
        x1 = cx-w2
        y1 = cy-h2
        x2 = cx+w2
        y2 = cy+h2
        return mouse_in(x1, y1, x2, y2)

    def mouse_in(self, x1, y1, x2, y2):
        mx, my = self.pos
        if x1 > mx:
            return False
        if x2 < mx:
            return False
        if y1 > my:
            return False
        if y2 < my:
            return False
        return True

    def mouse_in_rect(self, rect):  # x,y,w,h
        return mouse_in(rect[0], rect[1], rect[0]+rect[2], rect[1]+rect[3])

    def display_score(self):
        if pygame.font:
            text = self.font2.render(str(self.score), True, ORANGE, BLUE)
            w = text.get_width()
            h = text.get_height()
            x = self.sx(5.7)
            y = self.sy(18.8)
            d = self.sy(.3)
            pygame.draw.rect(
                self.screen, BLUE, (x-d-self.sy(.05), y-d, w+2*d, h+2*d))
            self.screen.blit(text, (x, y))
            centre_blit(self.screen, self.sparkle,
                        (x-d+self.sy(.05), y+h/2-self.sy(.2)))

    def display_number(self, n, xxx_todo_changeme9, font, colour=BLACK, bgd=None, outline_font=None):
        (cx, cy) = xxx_todo_changeme9
        if pygame.font:
            if bgd == None:
                text = font.render(str(n), True, colour)
            else:
                text = font.render(str(n), True, colour, bgd)
            if outline_font != None:
                outline = outline_font.render(str(n), True, BLACK)
                centre_blit(self.screen, outline, (cx, cy))
            centre_blit(self.screen, text, (cx, cy))

    def display_number1(self, n, xxx_todo_changeme10, font, colour=BLACK):
        (x, cy) = xxx_todo_changeme10
        if pygame.font:
            text = font.render(str(n), True, colour)
            y = cy-text.get_height()/2
            self.screen.blit(text, (x, y))

    def display_number2(self, screen, n, xxx_todo_changeme11, font, colour=BLACK):
        (cx, cy) = xxx_todo_changeme11
        if pygame.font:
            text = font.render(str(n), True, colour)
            centre_blit(screen, text, (cx, cy))

    def display_number3(self, screen, n, xxx_todo_changeme12, font, colour=BLACK):
        (x, y) = xxx_todo_changeme12
        if pygame.font:
            lead = 0
            if n < 10:
                one = font.render('1', True, colour)
                lead = one.get_width()
            s = str(n)
            text = font.render(s, True, colour)
            screen.blit(text, (lead+x, y))

    def top_left_to_centre(self, img, xxx_todo_changeme13):
        (x, y) = xxx_todo_changeme13
        cx = x+img.get_width()/2
        cy = y+img.get_height()/2
        return (cx, cy)

    def centre_to_top_left(self, img, xxx_todo_changeme14):
        (cx, cy) = xxx_todo_changeme14
        x = cx-img.get_width()/2
        y = cy-img.get_height()/2
        return (x, y)

    def sign(self, n):
        if n < 0:
            return -1
        return 1

    def which_piece(self):
        for ind in range(1, 10):  # piece 0 is fixed
            ind1 = 10-ind
            pce = self.pieces[self.z[ind1]]
            if self.mouse_on_img(pce.img, pce.xy):
                i = self.z[ind1]
                self.z.remove(i)
                self.z.append(i)  # move to top
                return pce
        return None

    def which_tn(self):
        n = self.solved+1
        if n == 11:
            n = 10
        for ind in range(n):
            tn = self.tns[ind]
            if self.mouse_on_img(tn.img, tn.xy):
                return ind  # puzzle number
        return -1

    # Code from self.py STARTS HERE

    def iqinit(self):

        for ind in range(10):
            self.pieces.append(Piece())
        x = 0
        y = 0
        hh = 0
        for ind in range(10):
            self.puzzle = self.puzzles[ind]
            self.piece = self.puzzle[0]
            img = self.load_image(self.piece+'.png', True, 'pieces')
            f = .5
            w = int(img.get_width()*f+.5)
            h = int(img.get_height()*f+.5)
            if hh == 0:
                hh = h  # take height from 1st piece
                self.sq = int(img.get_width()*.5+.5)  # and grid square side
            dy = (hh-h)/2
            img = pygame.transform.scale(img, (w, h))
            self.tns.append(TN(x, y+dy, img))
            x += img.get_width()+self.sy(.5)
        ww = x-self.sy(.5)
        x0 = (self.w-ww)/2
        y0 = self.screen.get_height()-hh-self.sy(1)
        for ind in range(10):
            self.tn = self.tns[ind]
            x, y = self.tn.xy
            x += x0
            y += y0
            self.tn.xy = (x, y)

    def iqsetup(self):
        self.puzzle = self.puzzles[self.puzzle_n]
        x1 = self.sx(.2)
        x2 = self.sx(8.2)
        y1 = self.sy(1)
        y2 = self.sy(16)
        for ind in range(10):
            pce = self.pieces[ind]
            pce.img = self.load_image(self.puzzle[ind]+'.png', True, 'pieces')
            w = pce.img.get_width()
            h = pce.img.get_height()
            x = random.randint(x1, x2-w)
            y = random.randint(y1, y2-h)
            pce.on_grid = False
            if ind == 0:
                x, y = self.x0, self.y0
                pce.on_grid = True
            pce.xy = x, y
            if ind == 4:
                x1 = self.sx(23.5)
                x2 = self.sx(31.5)
        self.carry = None
        self.finished = False
        self.redrawn = False

    def draw(self):
        x, y = self.tns[0].xy
        dx = self.sy(.5)
        dy = self.sy(.45)
        x -= dx
        y -= dy
        self.screen.blit(self.frame2, (x, y))
        n = self.solved+1
        if n == 11:
            n = 10
        for ind in range(n):
            tn = self.tns[ind]
            self.screen.blit(tn.img, tn.xy)
        t = self.sy(.32)
        self.screen.blit(self.frame, (self.x0-t, self.y0-t))
        for ind in range(10):
            pce = self.pieces[self.z[ind]]
            if pce != self.carry:
                self.screen.blit(pce.img, pce.xy)
        if self.carry != None:
            mx, my = self.pos
            x = mx-self.dx
            y = my-self.dy
            self.screen.blit(self.carry.img, (x, y))

    def click(self):
        if self.carry != None:
            mx, my = self.pos
            x = mx-self.dx
            y = my-self.dy
            self.carry.xy = x, y
            self.try_grid()
            self.carry = None
            return True
        pce = self.which_piece()
        if pce != None:
            x, y = pce.xy
            mx, my = self.pos
            self.dx = mx-x
            self.dy = my-y
            self.carry = pce
            pce.on_grid = False
            self.finished = False
            return True
        n = self.which_tn()
        if n > -1:
            self.puzzle_n = n
            self.iqsetup()
            return True
        return False

    def try_grid(self):
        pce = self.carry
        w = pce.img.get_width()
        h = pce.img.get_height()
        x, y = pce.xy
        d = self.sq*.5
        x2 = self.x0+self.sq*8
        y2 = self.y0+self.sq*8
        y1 = self.y0
        for r in range(8):
            x1 = self.x0
            for c in range(8):
                if (y1+h) <= y2:
                    if abs(x-x1) <= d and abs(y-y1) <= d:
                        pce.xy = x1, y1
                        pce.on_grid = True
                        return
                x1 += self.sq
                if (x1+w) > x2:
                    break
            y1 += self.sq

    def complete(self):
        if self.finished:
            return True
        for pce in self.pieces:
            if not pce.on_grid:
                return False
        y1 = self.y0+2
        for r in range(8):
            x1 = self.x0+2
            for c in range(8):
                if self.screen.get_at((x1, y1)) == self.bgd:
                    return False
                x1 += self.sq
            y1 += self.sq
        self.finished = True
        if self.solved < self.puzzle_n+1:
            self.solved = self.puzzle_n+1
        self.redraw = True
        return True


# Code from self.py ENDS HERE


if __name__ == "__main__":
    pygame.init()
    pygame.display.set_mode((1024, 768))
    game = IQ(None)
    game.journal = False
    game.run()
    pygame.display.quit()
    pygame.quit()
    sys.exit(0)
