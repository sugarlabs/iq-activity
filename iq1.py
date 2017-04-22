#iq1.py
import g,utils,random,pygame

# numbered 0 to 9 - piece 0 is fixed in top left
puzzles=[\
        ['3a','1a','2a','4a','5a','6a','7a','8a','9a','10a'],\
        ['7b','1b','2b','3b','4b','5b','6b','8b','9b','10b'],\
        ['5c','1a','2a','3c','4c','6c','7c','8c','9c','10c'],\
        ['10d','1b','2b','3d','4d','5d','6d','7d','8d','9d'],\
        ['2a','1b','3b','4c','5e','6d','7a','8c','9a','10b'],\
        ['6a','1a','2b','3c','4d','5f','7b','8d','9b','10c'],\
        ['1b','6b','2a','3d','4a','5g','7c','8a','9c','10d'],\
        ['8b','1b','2b','3e','4e','5c','6d','7a','9a','10e'],\
        ['9d','1b','2b','3f','4d','5c','6c','7d','8c','10f'],\
        ['4b','1b','2b','3f','5c','6c','7d','8c','9b','10f']\
        ]
# numbered 0 to 9
pieces=[]
tns=[]
z=[0,1,2,3,4,5,6,7,8,9]

class Piece:
    def __init__(self):
        self.xy=None
        self.img=None
        self.on_grid=False

class TN:
    def __init__(self,x,y,img):
        self.xy=(x,y)
        self.img=img

def init():
    global pieces,tns
    for ind in range(10): pieces.append(Piece())
    x=0; y=0; hh=0
    for ind in range(10):
        puzzle=puzzles[ind]; piece=puzzle[0]
        img=utils.load_image(piece+'.png',True,'pieces')
        f=.5; w=int(img.get_width()*f+.5); h=int(img.get_height()*f+.5)
        if hh==0:
            hh=h # take height from 1st piece
            g.sq=int(img.get_width()*.5+.5) # and grid square side
        dy=(hh-h)/2
        img=pygame.transform.scale(img,(w,h))
        tns.append(TN(x,y+dy,img))
        x+=img.get_width()+g.sy(.5)
    ww=x-g.sy(.5); x0=(g.w-ww)/2; y0=g.screen.get_height()-hh-g.sy(1)
    for ind in range(10):
        tn=tns[ind]; x,y=tn.xy; x+=x0; y+=y0; tn.xy=(x,y)

def setup():
    puzzle=puzzles[g.puzzle_n]
    x1=g.sx(.2); x2=g.sx(8.2); y1=g.sy(1); y2=g.sy(16)
    for ind in range(10):
        pce=pieces[ind]
        pce.img=utils.load_image(puzzle[ind]+'.png',True,'pieces')
        w=pce.img.get_width(); h=pce.img.get_height()
        x=random.randint(x1,x2-w); y=random.randint(y1,y2-h)
        pce.on_grid=False
        if ind==0: x,y=g.x0,g.y0; pce.on_grid=True
        pce.xy=x,y
        if ind==4: x1=g.sx(23.5); x2=g.sx(31.5)
    g.carry=None; g.finished=False; g.redrawn=False

def draw():
    x,y=tns[0].xy; dx=g.sy(.5); dy=g.sy(.45)
    x-=dx; y-=dy; g.screen.blit(g.frame2,(x,y))
    n=g.solved+1
    if n==11: n=10
    for ind in range(n):
        tn=tns[ind]; g.screen.blit(tn.img,tn.xy)
    t=g.sy(.32); g.screen.blit(g.frame,(g.x0-t,g.y0-t))
    for ind in range(10):
        pce=pieces[z[ind]]
        if pce!=g.carry: g.screen.blit(pce.img,pce.xy)
    if g.carry!=None:
        mx,my=g.pos; x=mx-g.dx; y=my-g.dy
        g.screen.blit(g.carry.img,(x,y))

def click():
    if g.carry!=None:
        mx,my=g.pos; x=mx-g.dx; y=my-g.dy; g.carry.xy=x,y
        try_grid()
        g.carry=None
        return True
    pce=which_piece()
    if pce!=None:
        x,y=pce.xy; mx,my=g.pos
        g.dx=mx-x; g.dy=my-y
        g.carry=pce; pce.on_grid=False; g.finished=False
        return True
    n=which_tn()
    if n>-1:
        g.puzzle_n=n; setup(); return True
    return False

def try_grid():
    pce=g.carry
    w=pce.img.get_width(); h=pce.img.get_height(); x,y=pce.xy; d=g.sq*.5
    x2=g.x0+g.sq*8; y2=g.y0+g.sq*8
    y1=g.y0
    for r in range(8):
        x1=g.x0
        for c in range(8):
            if (y1+h)<=y2:
                if abs(x-x1)<=d and abs(y-y1)<=d:
                    pce.xy=x1,y1; pce.on_grid=True; return
            x1+=g.sq
            if (x1+w)>x2: break
        y1+=g.sq
        
def complete():
    if g.finished: return True
    for pce in pieces:
        if not pce.on_grid: return False
    y1=g.y0+2
    for r in range(8):
        x1=g.x0+2
        for c in range(8):
            if g.screen.get_at((x1,y1))==g.bgd:return False
            x1+=g.sq
        y1+=g.sq
    g.finished=True
    if g.solved<g.puzzle_n+1: g.solved=g.puzzle_n+1
    g.redraw=True
    return True
    
def which_piece():
    for ind in range(1,10): # piece 0 is fixed
        ind1=10-ind
        pce=pieces[z[ind1]]
        if utils.mouse_on_img(pce.img,pce.xy):
            i=z[ind1]; z.remove(i); z.append(i) # move to top
            return pce
    return None

def which_tn():
    n=g.solved+1
    if n==11: n=10
    for ind in range(n):
        tn=tns[ind]
        if utils.mouse_on_img(tn.img,tn.xy): return ind # puzzle number
    return -1
