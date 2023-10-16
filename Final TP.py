from cmu_112_graphics import*
from tkinter import*
import math
import random
#################################################
# Helper functions 
#################################################
def almostEqual(d1, d2, epsilon=10**-7):
# note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

import decimal
def roundHalfUp(d):
# Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
# See other rounding options here:
# https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

#####################################################################
#SPLASH SCREEN
#####################################################################
#https://www.cs.cmu.edu/~112/notes/notes-animations-part4.html#usingModes
NAME = input("Enter your name:")
def splashScreenMode_redrawAll(app, canvas):
    canvas.create_image(app.width/2, app.height/2, image=ImageTk.PhotoImage(app.splashImageScale))
    font = 'Times 50 bold'
    canvas.create_text(app.width/2, app.height/2-150, 
                        text='The Bee Game', 
                            fill = 'orange',
                            font=font)
    canvas.create_text(app.width/2, app.height/2-10, 
                        text='Rules: \n The Bee follows the cursor\n Collect the solid circles(pollen)\n Pollinate by flying to ringed circles (flowers)\n Avoid the spiders or you will be eaten!\n Do not kill the bee\n Your time will be recorded\n',
                            anchor = 'c', 
                            fill='sky blue',
                            font='Times 15 bold')
    canvas.create_text(app.width/2, app.height/2+75, 
                        text='Press any key to start the game!',
                        fill = 'salmon',
                        font='Times 25 bold')
    canvas.create_text(app.width/2, app.height/2-100, 
                        text = f"{NAME}'s Score = {app.timerScore//1000}", 
                        fill = 'orange',
                        font='Times 25 bold')
    
def splashScreenMode_keyPressed(app, event):
    if (event.key =='r'): 
        appStarted(app)
        app.pause = not app.pause
        # app.timerScore = 0
        # app.isGameover = True
        # app.mode = 'gameMode'
    app.mode = 'gameMode'
#####################################################################
#BEE CLASS
#####################################################################
class Player(object): #bee traits 
    def __init__(self, cx = 20, cy = 20, r=10,color='yellow'): 
        self.cx = cx 
        self.cy = cy 
        self.r = r 
        self.color = color 
  
    def redrawPlayer(self,app,canvas): #creating bee
        canvas.create_oval(self.cx-self.r, self.cy-self.r,
                            self.cx+self.r, self.cy+self.r,
                                fill= self.color,
                                    outline=self.color, 
                                        width=20)
        canvas.create_image(self.cx,self.cy, image=ImageTk.PhotoImage(app.beeScale))
        
#####################################################################
#FLOWER CLASS
#####################################################################
class Flower(object): #creating flowers
    def __init__(self,sinCentre,cx=10,cy=10,r=3): 
        self.cx = cx 
        self.cy = cy
        self.r = r
        self.sinCentre = sinCentre 
        self.color = self.getRandomColor() 
        self.growing = False

    def flowerTimerFired(self): 
        self.cy-=10 
        #sinusoidal movement of circles
        self.cx = self.sinCentre + math.sin(self.cy*10)*10

    def getRandomColor(self): 
        colors = ['salmon', 'sandy brown', 'pink', 'violet']
        return random.choice(colors)

    def redrawFlower(self,canvas):
        canvas.create_oval(self.cx-self.r, self.cy-self.r,
                                self.cx+self.r, self.cy+self.r,
                                    fill= self.color,
                                        width=0) 

class Pollen(Flower): #subclass of pollen
    def __init__(self,sinCentre,cx=10,cy=10,r=3): 
        super().__init__(sinCentre,cx=cx,cy=cy,r=r)

    def redrawFlower(self,canvas):
        canvas.create_oval(self.cx-self.r, self.cy-self.r,
                                self.cx+self.r, self.cy+self.r,
                                    fill= self.color,
                                        width=0) 

class normalFlower(Flower): #subclass of normal flowers
    def __init__(self,sinCentre,cx=15,cy=15,r=5): 
        super().__init__(sinCentre,cx=cx,cy=cy,r=r)
    def redrawFlower(self,canvas): 
        canvas.create_oval(self.cx-self.r, self.cy-self.r,
                            self.cx+self.r, self.cy+self.r,
                                fill= self.color,
                                    width=0) 
        canvas.create_oval((self.cx-self.r)+7, (self.cy-self.r)+7,
                                (self.cx+self.r)-7, (self.cy+self.r)-7,
                                    fill= self.color, 
                                        outline = 'white', 
                                            width=3)
#####################################################################
#Spider Class
##################################################################### 
class Spider(object): #creating soiders
    def __init__(self,sinCentre,cx=10,cy=10,r=3): 
        self.cx = cx 
        self.cy = cy
        self.r = r
        self.sinCentre = sinCentre 
        self.color = 'black'
        self.growing = False
    #load image, resize it, store it in spider class, spider draw function#caching images 

    def spiderTimerFired(self): 
        self.cy-=10 
        #sinusoidal movement of circles
        self.cx = self.sinCentre + math.sin(self.cy*10)*40

    def redrawSpider(self,app,canvas):
        canvas.create_image(self.cx,self.cy, image=ImageTk.PhotoImage(app.spiderScale))
#####################################################################
#Generate Terrain 
#https://learn.64bitdragon.com/articles/computer-science/procedural-generation/the-diamond-square-algorithm
#https://www.cs.cmu.edu/~112/notes/student-tp-guides/Terrain.pdf
#https://bitesofcode.wordpress.com/2016/12/23/landscape-generation-using-midpoint-displacement/
##################################################################### 
def generateTerrain(app): 
    row2 = []  
    randomDisplacement = random.randint(0,app.height*0.7)
    row2.append(random.randint(app.height*0.45,app.height*0.6))
    row2.append(random.randint(app.height*0.45,app.height*0.6))
    row2=recursiveMidpoint(row2[0],row2[1],0,randomDisplacement)
    app.row2 = row2

def recursiveMidpoint(left,right,depth,displacement): 
    #base case 
    if depth >=10: 
        return [left,right]
    #recursive call 
    displacement1 = random.choice([-displacement,displacement])
    midpoint = (left+right)/2
    midpoint+=displacement1
    depth+=1
    return(recursiveMidpoint(left,midpoint,depth,int(displacement*0.7))+recursiveMidpoint(midpoint,right,depth,int(displacement*0.7)))

def drawTerrain(app,canvas): 
    gaps = app.width/49
    points2=[]
    for i in range(len(app.row2)-1): 
        canvas.create_line(gaps*i, app.row2[i], gaps*(i+1), app.row2[i+1],
                                fill = 'sea green')
        points2.append(gaps*i)
        points2.append(app.row2[i])
    points2.append(app.width)
    points2.append(app.row2[-1])
    newList = [] 
    for points in range(0,len(points2),2): 
        newList.append(points2[points])
        newList.append(points2[points+1])
    canvas.create_polygon(*points2,app.width,app.height,0,app.height,fill = 'sea green', outline = 'LightSalmon4', width = 8)

#####################################################################
#MAIN APP 
#####################################################################
def appStarted(app): 
    generateTerrain(app)
    app.flowers = [Flower(sinCentre = app.width/2,
                    cx=app.width/2,
                    cy=app.height,
                    r=10)]
    app.player = Player(app.width//2,app.height//2)
    app.pollen = [Pollen(sinCentre = app.width/2,
                            cx=app.width/2,
                            cy=app.height,
                            r=10)]
    app.pollenScore = [] 
    app.pollenGrowing = False
    #Spider 
    app.spider = [Spider(sinCentre = app.width/2,
                    cx=app.width/2,
                    cy=app.height,
                    r=10)]
    #score list dimensions 
    app.cxScore = 30 
    app.cyScore = 30
    app.rScore = 12
    app.alreadyPollinated = set()
    #splashscreen
    #https://pngtree.com/freebackground/nature-landscape-background-with-funny-design-suitable-for-kids_1170743.html
    app.mode = 'splashScreenMode'
    app.homeScreen = False
    app.splashImage = app.loadImage('splashScreenBackground.png')
    app.splashImageScale = app.scaleImage(app.splashImage,1/5)
    #Game over conidtions 
    app.isGameOver = False 
    app.lastX = app.width//2
    app.lastY = app.height//2 
    #pausing 
    app.pause = False
    app.timerDelay = 80
    app.timerScore = 0
    app.sprites = []
    #bee https://www.pngmart.com/image/243329
    app.beeImage = app.loadImage('bee.png')
    app.beeScale = app.scaleImage(app.beeImage, 1/8)
    #spider
    #https://www.pngmart.com/image/4198
    app.spiderImage = app.loadImage('spider.png')
    app.spiderScale = app.scaleImage(app.spiderImage, 1/5)

def gameMode_keyPressed(app,event):
    #press p to pause, when you pause you can click anywhere on the screen to move the bee 
    if (event.key == 'p'): 
        app.pause = not app.pause
    #press h to go back to help screen 
    elif (event.key =='h') and app.isGameOver == False: 
        app.homeScreen = True
        app.pause = not app.pause 
    elif (event.key =='h') and app.isGameOver==True: 
        app.homeScreen = True
    #press r to reset game 
    elif (event.key =='r') and app.isGameOver == False: 
        app.timerScore = 0
        app.flowers = [Flower(sinCentre = app.width/2,
                    cx=app.width/2,
                    cy=app.height,
                    r=10)]
        app.player = Player(app.width//2,app.height//2)
        app.pollen = [Pollen(sinCentre = app.width/2,
                            cx=app.width/2,
                            cy=app.height,
                            r=10)]
        app.spider = [Spider(sinCentre = app.width/2,
                    cx=app.width/2,
                    cy=app.height,
                    r=10)]
        app.pollenScore = [] 



def gameMode_mouseMoved(app,event): 
    #moves according to distance between the bee and the cursor
    #when the cursor is further, bee moves faster 
    #when the cursor is closer, bee moves slower
    app.lastX = event.x 
    app.lastY = event.y
    checkIntersectionPollen(app)
    checkIntersectionFlower(app)
    checkIntersectionSpider(app)

def gameMode_mousePressed(app,event): 
    app.player = Player(event.x, event.y)

def gameMode_timerFired(app): 
    if (not app.pause and not app.isGameOver): 
        driftMouse(app)
        generateStuff(app)
        gradualGrowthOfFlowers(app)
        app.timerScore+=app.timerDelay
    # elif not app.isGameOver:
    #     driftMouse(app)
    #     generateStuff(app)
    #     gradualGrowthOfFlowers(app)
    #     app.timerScore+=app.timerDelay

def driftMouse(app):
    #drifting mouse
    distance = math.dist((app.lastX,app.lastY),(app.player.cx,app.player.cy))
    distanceX = (app.lastX-app.player.cx )*(distance/250) 
    distanceY = (app.lastY-app.player.cy )*(distance/250) 
    app.player.cx+=distanceX
    app.player.cy+=distanceY

def generateStuff(app): #generate flowers, pollen and spiders
    for flower in app.flowers: 
        flower.flowerTimerFired()
    for pollen in app.pollen: 
        pollen.flowerTimerFired()
    for spider in app.spider: 
        spider.spiderTimerFired()
    spiderNum = random.randint(0,50)
    if spiderNum == 0: 
        sinCentreRandom = random.randint(0,app.width) 
        spiders = Spider(sinCentreRandom,
                                    cx=app.width/2,
                                    cy=app.height,
                                    r=20)
        app.spider.append(spiders)
    number = random.randint(0,10) #randomly generate number
    #if num is 0, generate a normal flower within the dimensions of the game
    if number == 0: 
        sinCentreRandom = random.randint(0,app.width) 
        flower = normalFlower(sinCentreRandom,
                                cx=app.width/2,
                                cy=app.height,
                                r=20)
        app.flowers.append(flower)
    #if num is 1, generate pollen within the dimensions of the game
    elif number == 1: 
        sinCentreRandom = random.randint(0,app.width)
        pollen = Pollen(sinCentreRandom,
                            cx=app.width/2,
                            cy=app.height,
                            r=15)
        app.pollen.append(pollen)
    
def gradualGrowthOfFlowers(app):
    #gradual growth of flowers and pollen
    checkIntersectionFlower(app)
    for flower in app.flowers: 
        x1,y1 = flower.cx,flower.cy 
        if flower.growing:  
            if flower.r>=40: 
                flower.growing = False
            else:
                flower.r += 1
    for pollen in app.pollen: 
        x1,y1 = pollen.cx,pollen.cy 
        if pollen.growing:  
            if  pollen.r>=40: 
                pollen.growing = False
            else:
                pollen.r += 1

#check to see if bee is touching a pollen or a flower 
def distance(x1,y1,x2,y2):
    #distance between circles 
    return ((x1-x2)**2 + (y1-y2)**2)**0.5

#check if bee is intersecting with pollen
def checkIntersectionPollen(app): 
    (x2, y2) = app.player.cx, app.player.cy
    for location in app.pollen: 
        x1,y1 = location.cx,location.cy
        if distance(x1,y1,x2,y2) < 20:
            if (location, location.color) not in app.pollenScore:
                app.pollenScore.append((location, location.color))
        if (len(app.pollenScore) > 6): #check if pollen score is greater than or equal to 6 
           app.pollenScore.pop(0)

def checkIntersectionSpider(app): 
    (x2, y2) = app.player.cx, app.player.cy
    for spider in app.spider: 
        x1,y1 = spider.cx,spider.cy
        if distance(x1,y1,x2,y2) < 20:
            app.isGameOver = True


def checkIntersectionFlower(app): 
    (x2, y2) = app.player.cx, app.player.cy
    for flower in app.flowers: 
        x1,y1 = flower.cx,flower.cy
        if distance(x1,y1,x2,y2) < 20 and flower not in app.alreadyPollinated:
            lastPollen = len(app.pollenScore)-1
            if lastPollen >= 0 and flower.color in app.pollenScore[lastPollen]:
                pollen = app.pollenScore[lastPollen][0]
                # newFlower = normalFlower(pollen.sinCentre)
                # app.flowers.append(newFlower)
                app.pollenScore.pop(lastPollen)
                app.alreadyPollinated.add(flower)
                flower.growing = True 
                pollen.growing = True

def drawPollenScore(app,canvas): 
    #pollen collection on top left hand corner 
    for index in range(len(app.pollenScore)):
        canvas.create_oval((app.cxScore+(20*index))+app.rScore, app.cyScore+app.rScore,
                        (app.cxScore+(20*index))-app.rScore, app.cyScore-app.rScore, 
                        fill = app.pollenScore[index][1],width=0)
def gameMode_redrawAll(app,canvas): 
    canvas.create_rectangle(0,0,app.width,app.height,fill='Deep Sky Blue')
    canvas.create_text(app.width//2,app.height//2-350, text =f'Time elapsed:{(app.timerScore+20)//1000}',
                                font='Times 25 bold', fill ='white')
    drawTerrain(app,canvas)
    app.player.redrawPlayer(app,canvas)
    for flower in app.flowers: 
        flower.redrawFlower(canvas)
    for pollen in app.pollen: 
        pollen.redrawFlower(canvas)
    for spider in app.spider:  
        spider.redrawSpider(app,canvas)
    drawPollenScore(app, canvas)
    if app.isGameOver:
        canvas.create_rectangle(0, app.height/2-20, app.width, 
                                (app.height)/3-50,
                                fill = 'white', width = 0)
        canvas.create_text(app.width/2, (app.height)/3+10, 
            text='Game over :( bee is dead \nPress h to return to homescreen',anchor = 'c',font='Times 50 bold', fill = 'salmon')
    if app.homeScreen: 
        splashScreenMode_redrawAll(app, canvas)  

runApp(width = 800, height = 800)