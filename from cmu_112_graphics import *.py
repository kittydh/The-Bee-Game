from cmu_112_graphics import *
import random
from dataclasses import make_dataclass

Dot = make_dataclass('Dot', ['cx', 'cy', 'r', 'counter', 'color'])

def appStarted(app):
    app.dots = [ ]

def pointIsInDot(x, y, dot):
    return (((dot.cx - x)**2 + (dot.cy - y)**2)**0.5 <= dot.r)

def getRandomColor():
    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'pink',
              'lightGreen', 'gold', 'magenta', 'maroon', 'salmon',
              'cyan', 'brown', 'orchid', 'purple']
    return random.choice(colors)

def mousePressed(app, event):
    # go through dots in reverse order so that
    # we find the topmost dot that intersects
    for dot in reversed(app.dots):
        if pointIsInDot(event.x, event.y, dot):
            dot.counter += 1
            dot.color = getRandomColor()
            return
    # mouse click was not in any dot, so create a new dot
    newDot = Dot(cx=event.x, cy=event.y, r=20, counter=0, color='cyan')
    app.dots.append(newDot)

def keyPressed(app, event):
    if (event.key == 'd'):
        if (len(app.dots) > 0):
            app.dots.pop(0)
        else:
            print('No more dots to delete!')

def redrawAll(app, canvas):
    # draw the dots and their counters
    for dot in app.dots:
        canvas.create_oval(dot.cx-dot.r, dot.cy-dot.r,
                           dot.cx+dot.r, dot.cy+dot.r,
                           fill='white', outline=dot.color, width=15)
        canvas.create_text(dot.cx, dot.cy, text=str(dot.counter))
    # draw the text
    canvas.create_text(app.width/2, 20,
                       text='Example: Adding and Deleting Shapes')
    canvas.create_text(app.width/2, 40,
                       text='Mouse clicks outside dots create new dots')
    canvas.create_text(app.width/2, 60,
                       text='Mouse clicks inside dots increase their counter')
    canvas.create_text(app.width/2, 70,
                       text='and randomize their color.')
    canvas.create_text(app.width/2, 90,
                       text='Pressing "d" deletes circles')

runApp(width=400, height=400)