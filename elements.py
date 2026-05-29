import math

class Ball:
    mass = 2.0
    gravity = 9.81
    def __init__(self, x, y, radius, vx=0.0, vy=0.0):
        self.x = x # position
        self.y = y
        self.radius = radius
        self.vx = vx # impulse velocity
        self.vy = vy

    def move(self, dx, dy):
        # dx and dy are incremental changes to position
        self.x += dx
        self.y += dy

    def get_position(self):
        return (self.x, self.y)
    
    def elasticity(self):
        # if it is 1, there is perpetual bouncing, if it is 0, there is no bounce at all
        return 0.8

    def apply_impulse(self, fx, fy):
        self.vx += fx / self.mass
        self.vy += fy / self.mass

    def apply_acceleration(self, ax, ay, dt):
        # velocity is a function of both acceleration and time
        self.vx += ax * dt
        self.vy += ay * dt

    def update(self, dt):
        # distance = velocity * time
        self.x += self.vx * dt
        self.y += self.vy * dt

        if self.y < 0:
            self.y = 0
            new_vy = -self.vy * self.elasticity()
            # prevents perpetual bounces
            if abs(new_vy) < 0.1:
                self.vy = 0
              # apply friction to horizontal component
                self.vx *= 0.99
            else:
                self.vy = new_vy


class Force:
    def __init__(self, magnitude, direction):
        self.magnitude = magnitude
        self.direction = direction

    def apply_to(self, ball, dt):
        fx = self.magnitude * math.cos(self.direction)
        fy = self.magnitude * math.sin(self.direction)

        # f=ma
        ax = fx / ball.mass
        ay = fy / ball.mass
        ball.apply_acceleration(ax, ay, dt)

class rigidObject:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def get_position(self):
        return (self.x, self.y)

    def get_dimensions(self):
        return (self.width, self.height)
    
    def is_colliding_with(self, ball):
        # Collision detection between ball and objects
        if (ball.x + ball.radius > self.x and
            ball.x - ball.radius < self.x + self.width and
            ball.y + ball.radius > self.y and
            ball.y - ball.radius < self.y + self.height):
            return True
        return False
    