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
        self.x += dx
        self.y += dy

    def get_position(self):
        return (self.x, self.y)
    
    def elasticity(self):
        return 0.8

    def apply_impulse(self, fx, fy):
        self.vx += fx / self.mass
        self.vy += fy / self.mass

    def apply_acceleration(self, ax, ay, dt):
        # velocity is a function of both acceleration and time
        self.vx += ax * dt
        self.vy += ay * dt

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        # simple ground collision at y = 0
        if self.y < 0:
            self.y = 0
            # compute post-collision vertical velocity
            new_vy = -self.vy * self.elasticity()
            # if the bounce is very small, stop vertical motion to avoid endless tiny bounces
            if abs(new_vy) < 0.1:
                self.vy = 0
                # apply ground friction when resting
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

        # convert force to acceleration and apply over time dt
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
        # `Simple collision detection (AABB)
        if (ball.x + ball.radius > self.x and
            ball.x - ball.radius < self.x + self.width and
            ball.y + ball.radius > self.y and
            ball.y - ball.radius < self.y + self.height):
            return True
        return False
    


def main():
    ball1 = Ball(0, 10, 1)
    appliedForce = Force(10, math.pi / 4)

    dt = 0.05
    steps = 0
    max_steps = 1000
    # apply the external force once as an initial impulse
    appliedForce.apply_to(ball1, dt)
    while steps < max_steps:
        # gravity
        ball1.apply_acceleration(0, -Ball.gravity, dt)
        # physics update
        ball1.update(dt)
        print(ball1.get_position(), "vel=({:.2f},{:.2f})".format(ball1.vx, ball1.vy))
        # stop when ball is resting on the ground
        if ball1.y == 0 and abs(ball1.vy) < 0.1:
            break
        steps += 1

    print("Ball has hit the ground and come to rest.")


if __name__ == "__main__":
    main()