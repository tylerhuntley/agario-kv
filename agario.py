from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty, ObjectProperty, ReferenceListProperty
from kivy.graphics import Ellipse, Color
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from random import randint, random
from math import sqrt


class Cell(Widget):
    
    mass = NumericProperty(50)
    diameter = NumericProperty()
    offset = ListProperty([0, 0])
##    speed = NumericProperty(250)
##    (v_x, v_y) = (NumericProperty(0), NumericProperty(0))
##    velocity = ReferenceListProperty(v_x, v_y)
    
    def __init__(self, **kwargs):
        super(Cell, self).__init__(**kwargs)
        self.diameter = 5*sqrt(self.mass)
        self.size = (self.diameter, self.diameter)
        self.bind(pos=self.shift_camera, size=self.shift_camera)

    @property
    def speed(self):
        return 5000/sqrt(self.mass)

    def shift_camera(self, *args):
        self.offset = (Window.width / 2 - self.x,
                       Window.height / 2 - self.y)
        self.parent.offset = self.offset

##    @property
##    def diameter(self):
##        return 5*sqrt(self.mass)
        
    def on_mass(self, *args):
        self.diameter = 5*sqrt(self.mass)
    
    def move(self):
        self.dest = Vector(Window.mouse_pos)
        self.velocity = (self.dest-self.pos).normalize()*self.speed/60
        if (self.dest-self.pos).length() < self.diameter:
            self.velocity *= (self.dest-self.pos).length()/self.diameter
        self.pos = Vector(*self.velocity) + self.pos

        #Restrict cell movement to within field boundary
        self.x = sorted([0, self.x, self.parent.width])[1]
        self.y = sorted([0, self.y, self.parent.height])[1]

    def can_eat(self, food):
        return (Vector(food.pos)-self.pos).length() <= self.diameter/2

    def eat(self, morsel):
        self.mass += 10
        self.parent.food.remove(morsel)
        self.parent.remove_widget(morsel)


class Food(Widget):
    color = ListProperty([random(), random(), random()])
    offset = ListProperty([0, 0])

    def __init__(self, parent, **kwargs):
        super(Food, self).__init__(**kwargs)
        parent.food.append(self)
        self.offset = parent.offset
        self.color = random(), random(), random()


class Field(Widget):
    player = ObjectProperty(None)
    offset = ListProperty([0, 0])
    border = ListProperty()
    
    def __init__(self, **kwargs):
        super(Field, self).__init__(**kwargs)
        self.size = (800, 800)
        self.food = []

    def on_offset(self, *args):
        (x, y) = self.offset
        self.border_x = [x, x, self.width+x, self.width+x]
        self.border_y = [y, self.height+y, self.height+y, y]
        self.border = zip(self.border_x, self.border_y)
        for item in self.food:
            item.offset = self.offset

    def spawn_player(self):
        self.player.pos = self.center

    def spawn_food(self, dt):
        if len(self.food) < 100:
            spawn = (randint(10, self.width-10), randint(10, self.height-10))
            self.add_widget(Food(self, pos=spawn))
            # self.add_widget(self.food[-1])
            
           # with self.food[-1].canvas:
           #     Color(1,0,0,mode='rgb')
           #     Ellipse(pos=spawn, size=(5,5))
    
    def update(self, dt):
        self.player.move()
        for morsel in self.food:
            if self.player.can_eat(morsel):
                self.player.eat(morsel)
        
        # if (self.player.y < 0) or (self.player.top > self.height):
        #     self.player.velocity_y *= -1
        # if (self.player.x < 0) or (self.player.right > self.width):
        #     self.player.velocity_x *= -1
   

class MainApp(App):
    def build(self):
        root = Widget()
        field = Field()
        root.add_widget(field)
        field.spawn_player()
        Clock.schedule_interval(field.spawn_food, 1/5)
        Clock.schedule_interval(field.update, 1.0/60.0)
        return root


if __name__ == '__main__': 
    MainApp().run()
