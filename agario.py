from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.core.window import Window
from random import randint, uniform
from math import sqrt


class Cell(Widget):
    
    mass = NumericProperty()
    offset = ListProperty([0, 0])
    
    def __init__(self, **kwargs):
        super(Cell, self).__init__(**kwargs)
        self.mass = 50
        self.bind(pos=self.shift_camera, size=self.shift_camera)

    @property
    def speed(self):
        return 2000/(self.mass**0.33)

    @property
    def radius(self):
        return self.width/2

    def shift_camera(self, *args):
        self.offset = (Window.width / 2 - self.x,
                       Window.height / 2 - self.y)
        self.parent.offset = self.offset
        
    def on_mass(self, *args):
        diameter = 7.5*sqrt(self.mass)
        self.size = (diameter, diameter)
    
    def move(self):
        self.dest = Vector(Window.mouse_pos) - self.offset
        self.velocity = (self.dest-self.pos).normalize()*self.speed/60
        if (self.dest-self.pos).length() < self.radius:
            self.velocity *= (self.dest-self.pos).length()/self.radius
        self.pos = Vector(*self.velocity) + self.pos

        #Restrict cell movement to within field boundary
        self.x = sorted([0, self.x, self.parent.width])[1]
        self.y = sorted([0, self.y, self.parent.height])[1]

    def can_eat(self, food):
        return (Vector(food.pos)-self.pos).length() <= self.radius

    def eat(self, morsel):
        if isinstance(morsel, Food):
            self.mass += morsel.mass
            self.parent.food.remove(morsel)
            self.parent.remove_widget(morsel)
        elif isinstance(morsel, Cell):
            pass

    def on_touch_down(self, touch):
        if self.mass >= 50:
            self.mass -= 10
            blob_pos = Vector(touch.x, touch.y) - self.offset
            self.parent.add_widget(Blob(self.parent, pos=blob_pos))


class Food(Widget):
    color = ListProperty([1,1,1])
    offset = ListProperty([0, 0])

    def __init__(self, parent, **kwargs):
        super(Food, self).__init__(**kwargs)
        parent.food.append(self)
        self.mass = 10
        self.offset = parent.offset
        self.color = uniform(.2, .8), uniform(.2, .8), uniform(.2, .8)

class Blob(Food):
    pass

class Field(Widget):
    player = ObjectProperty(None)
    offset = ListProperty([0, 0])
    border = ListProperty()
    
    def __init__(self, **kwargs):
        super(Field, self).__init__(**kwargs)
        self.size = (1200, 1200)
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
        if len(self.food) < 500:
            spawn = (randint(10, self.width-10), randint(10, self.height-10))
            self.add_widget(Food(self, pos=spawn))
    
    def update(self, dt):
        self.player.move()
        for morsel in self.food:
            if self.player.can_eat(morsel):
                self.player.eat(morsel)
   

class MainApp(App):
    def build(self):
        root = Widget()
        field = Field()
        root.add_widget(field)
        field.spawn_player()
        Clock.schedule_interval(field.spawn_food, 1/10)
        Clock.schedule_interval(field.update, 1.0/60.0)
        return root


if __name__ == '__main__': 
    MainApp().run()
