# g.py - globals
import pygame,utils,random

app='IQ'; ver='1.0'
ver='21'
ver='22'
# flush_queue() doesn't use gtk on non-XO

UP=(264,273)
DOWN=(258,274)
LEFT=(260,276)
RIGHT=(262,275)
CROSS=(259,120)
CIRCLE=(265,111)
SQUARE=(263,32)
TICK=(257,13)
NUMBERS={pygame.K_1:1,pygame.K_2:2,pygame.K_3:3,pygame.K_4:4,\
           pygame.K_5:5,pygame.K_6:6,pygame.K_7:7,pygame.K_8:8,\
           pygame.K_9:9,pygame.K_0:0}

def init(): # called by run()
    random.seed()
    global redraw
    global screen,w,h,font1,font2,clock
    global factor,offset,imgf,message,version_display
    global pos,pointer
    redraw=True
    version_display=False
    screen = pygame.display.get_surface()
    pygame.display.set_caption(app)
    screen.fill((128,0,0))
    pygame.display.flip()
    w,h=screen.get_size()
    if float(w)/float(h)>1.5: #widescreen
        offset=(w-4*h/3)/2 # we assume 4:3 - centre on widescreen
    else:
        h=int(.75*w) # allow for toolbar - works to 4:3
        offset=0
    factor=float(h)/24 # measurement scaling factor (32x24 = design units)
    imgf=float(h)/900 # image scaling factor - all images built for 1200x900
    clock=pygame.time.Clock()
    if pygame.font:
        t=int(40*imgf); font1=pygame.font.Font(None,t)
        t=int(80*imgf); font2=pygame.font.Font(None,t)
    message=''
    pos=pygame.mouse.get_pos()
    pointer=utils.load_image('pointer.png',True)
    pygame.mouse.set_visible(False)
    
    # this activity only
    global solved,puzzle_n # 0-10, 0-9
    global carry,dx,dy,sq # sq=side of grid square
    global x0,y0,finished,frame,bgd,frame2,redrawn,smiley,smiley_c
    solved=0; puzzle_n=0
    carry=None; dx=0; dy=0; sq=0
    x0,y0=sx(9.56),sy(2.2) # top left of grid
    finished=False
    frame=utils.load_image('frame.png',False)
    bgd=frame.get_at((50,50))
    frame2=utils.load_image('frame2.png',False)
    redrawn=False # used to make sure new puzzle thumbnail appears
    smiley=utils.load_image('smiley.png',True); smiley_c=(sx(27.5),sy(9))
    
def sx(f): # scale x function
    return int(f*factor+offset+.5)

def sy(f): # scale y function
    return int(f*factor+.5)
