…# This Code is Heavily Inspired By The YouTuber: Cheesy AI
# Code Changed, Optimized And Commented By: NeuralNine (Florian Dedov)
# This code has again been hoisted by the CGS Digital Innovation Department
# giving credit to the above authors for the benfit of our education in ML

import math
import random
import sys
import os

import neat
import pygame

# Constants
# WIDTH = 1600
# HEIGHT = 880

WIDTH = 1920
HEIGHT = 1080

CAR_SIZE_X = 60
CAR_SIZE_Y = 60

BORDER_COLOR = (255, 255, 255, 255)  # Color To Crash on Hit

current_generation = 0  # Generation counter
"""
The Car Class 

Throughout this section, you will need to explore each function
and provide extenive comments in the spaces denoted by the 
triple quotes(block quotes) """ """.
Your comments should describe each function and what it is doing, 
why it is necessary and where it is being used in the rest of the program.

"""


class Car:
    """
1. This Function is a class constructor, setting up the car with its basic features.
The __init__ method starts a new instance of the car. The first 3 lines load the image of the car, scale it to the parameters that are set earlier (CAR_SIZE_X and CAR_SIZE_Y, lines 21, 22) and rotate the sprite. The next 3 lines set the starting position of the car in pixels on the screen. It should line up with where the start line is on the map. The self.speed_set variable flags whether or not the speed of the cars can change. It is set to false so that the default speed for the cars can be changed later on, as they may choose to go faster to prioritise distance/time or slower to try and survive. The center of the car is then calculated so that the radars can be attached to the center later on. It is found using the average of the position and the car size, both X and Y. Then, the radars are introduced and drawn. The radars are used for the car to have a sense of the track and where the paths end. After the car is set up, self.alive is set to true. This boolean variable checks if the car has crashed, once it has it is set to false and is no longer in the game. It must be set back to true in order for the cars to reappear and retry. Finally, the distance driven and time passed are reset to 0, which is important because the new generation of cars has not tested their abilities and their reward should not yet be there.

This function is necessary because without the car appearing in the simulation, nothing else would work, as the car one of the main features of the game, along with the track. Multiple cars are created at the start of each generation for the best chance of some of them improving their performance, which is tracked by the variables self.distance and self.time. 
    """

    def __init__(self):
        # Load Car Sprite and Rotate
        self.sprite = pygame.image.load("car.png").convert()  # Convert Speeds Up A Lot
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite

        # self.position = [690, 740] # Starting Position
        self.position = [830, 920]  # Starting Position
        self.angle = 0
        self.speed = 0

        self.speed_set = False  # Flag For Default Speed Later on

        self.center = [
            self.position[0] + CAR_SIZE_X / 2,
            self.position[1] + CAR_SIZE_Y / 2,
        ]  # Calculate Center

        self.radars = []  # List For Sensors / Radars
        self.drawing_radars = []  # Radars To Be Drawn

        self.alive = True  # Boolean To Check If Car is Crashed

        self.distance = 0  # Distance Driven
        self.time = 0  # Time Passed

    """ 
2. This Function draws the car on the screen using pygame. Blit is another term for a sprite. The previous function sets up the car, however never actually gets it to appear, which is what this one does. screen.blit is used to add self.rotated_sprite and self.position to the screen and then the radars are drawn to the screen using self.draw_radar(screen).

This function is necessary because for the simulation to appear and work, the cars have to be on the screen. The radars being seen is not as important, however it is useful to see more of what might be going on with the cars. This function is used every time a new generation is needed, because in each generation, new cars must appear.
    """

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position)  # Draw Sprite
        self.draw_radar(screen)  # OPTIONAL FOR SENSORS

    """ 
3. This Function draws all of the radars that check for collisions. It has a for loop for the radars to be drawn in different positions. Their lines are drawn from the center of the car using the self.center variable which was calculated in function 1. The circles are drawn at the end of the lines furthest from the car. The cars have 5 radars, one in front, one diagonally in front either way and one left and right of the car. These different positions are drawn using the loop, as each time the loop runs, a different radar is drawn. The direction it points is found in the 1st index of each object in the self.radars array.

The radars being drawn isn't essential to the simulation, it just provides more details about what the code may be doing. New radars are drawn for each car when it is created.
    """

    def draw_radar(self, screen):
        # Optionally Draw All Sensors / Radars
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (0, 255, 0), position, 5)

    """ 
4. This Function checks if a car has had a collision. It takes in the parameters self and game_map, and first sets self.alive to true because it cannot check if a car that has died has collided. It is forever checking if the car has crashed, so needs to make sure that self.alive stays true until then. The function loops through the coordinates of the pixels on the corners of the car, assuming that it is rectangular (only these are needed as it is near impossible for an edge to escape the track without at least one of the corners doing so). Assuming that the car is rectuangular is benefitial as it saves so many loops from being needed, simplifying the function, and is quite practical as the car is close enough in shape to assume that if the rectangle goes out, it will too. The if statement in this code is checking if any of the corners of the car's bounding box (represented by self.corners) touch a border on the game map. If it finds that any corner is touching a border (which is indicated by the color of the pixel at that corner's location being the same as BORDER_COLOR), it sets self.alive to false, rendering the car in question dead.

This is one of the most essential functions for the simulation to actually happen, as the goal is to train the cars to drive around a track without colliding, and to do so, we need to know if a car has collided and remove it. It is used throughout the entire similulation, constantly checking if each individual car has crashed into the border of the track.
    """

    def check_collision(self, game_map):
        self.alive = True
        for point in self.corners:
            # If Any Corner Touches Border Color -> Crash
            # Assumes Rectangle
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                self.alive = False
                break

    """ 
5. This Function creates an actual use for the radars that were drawn earlier. The x and y variables calculate the radars location based on the cars current angle and center, using trigonometry. The while loop is the primary part of this function, using the radars to continuously scan until one of two conditions are meant: radar hits a border colour (indicating that it has detected an obstacle/ boundary) or the length exceeds 300 units (so the radar doesn't scan indefinetely). Within the loop, length is increased by one each iteration, and the x and y values of the radar are updated so that the radar moves further from the car until the border is detected, or the length limit is reached. The final part of this function involves calculating the distance from the center of the car to the point where a radar can scan a border/ meet the length limit using the Euclidean formula. This is then appended to the self.radars list.

This function is necessary because it creates more of a use for the radars, which allow the car to sense obstacles. Later on, these calculations to sense obstacles are used to allow the cars to learn to steer away from them and improve their overall fitness.
    
    """

    def check_radar(self, degree, game_map):
        length = 0
        x = int(
            self.center[0]
            + math.cos(math.radians(360 - (self.angle + degree))) * length
        )
        y = int(
            self.center[1]
            + math.sin(math.radians(360 - (self.angle + degree))) * length
        )

        # While We Don't Hit BORDER_COLOR AND length < 300 (just a max) -> go further and further
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 300:
            length = length + 1
            x = int(
                self.center[0]
                + math.cos(math.radians(360 - (self.angle + degree))) * length
            )
            y = int(
                self.center[1]
                + math.sin(math.radians(360 - (self.angle + degree))) * length
            )

        # Calculate Distance To Border And Append To Radars List
        dist = int(
            math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2))
        )
        self.radars.append([(x, y), dist])

    """
6. This Function sets the original speed for the first generation of the cars and updates the cars speed, position, rotation and collision detection throughout the simulation. This function starts by setting the car's speed to 20, but only if it hasn't been set before (initial speed). Then, the sprite (blit) image is rotated and the x position of the car is updated using trigonometric functions sin and cos to move it in the direction of the specified angle. Due to limits max and min of the position, the cars x position is limited within the game map. Distance and time is increased, which is important as it is the reward system for the car. The same occurs for the y position of the car. A new center of the car is calculated by averaging the x and y values of the car. The 4 corners of the cars hit-box are recalculated based on the updated position. The check collision function is called to check if the car has crashed during it's movements and the stored data in the radars list is cleared, allowing for the process to repeat. The last part of the function loops through degrees in steps of 45 degrees, each time calling the check_radar function to perform a scan in that direction.

This function is essential because it allows the simulation to run continuously, moving the car on the screen and updating its position so that the radars can scan for new objects, and so that the check_collision function can use the cars cooridinates to check for collisions.
    
    """

    def update(self, game_map):
        # Set The Speed To 20 For The First Time
        # Only When Having 4 Output Nodes With Speed Up and Down
        if not self.speed_set:
            self.speed = 20
            self.speed_set = True

        # Get Rotated Sprite And Move Into The Right X-Direction
        # Don't Let The Car Go Closer Than 20px To The Edge
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 20)
        self.position[0] = min(self.position[0], WIDTH - 120)

        # Increase Distance and Time
        self.distance += self.speed
        self.time += 1

        # Same For Y-Position
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], WIDTH - 120)

        # Calculate New Center
        self.center = [
            int(self.position[0]) + CAR_SIZE_X / 2,
            int(self.position[1]) + CAR_SIZE_Y / 2,
        ]

        # Calculate Four Corners
        # Length Is Half The Side
        length = 0.5 * CAR_SIZE_X
        left_top = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length,
        ]
        right_top = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length,
        ]
        left_bottom = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length,
        ]
        right_bottom = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length,
        ]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        # Check Collisions And Clear Radars
        self.check_collision(game_map)
        self.radars.clear()

        # From -90 To 120 With Step-Size 45 Check Radar
        for d in range(-90, 120, 45):
            self.check_radar(d, game_map)

    """ 
7. This Function formats the data from the radars to be used in the machine learning algorithm. It first assigns the radar data from the cars to the radars variable, and sets up return values. It next loops through the radar data. Enumerate means that it will go through each radar reading. It takes the distance that each radar has scanned and saves it to its corresponding index in the return_values variable. This variable is then returned.

This is a necessary function because it allows the data from the radars to be later used for the cars. Without it, the data would not be preprocessed and the algorithm may not be able to read the data, meaning that the simulation would not work.
    """

    def get_data(self):
        # Get Distances To Border
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)

        return return_values

    """ 
8. This Function returns a boolean value. It takes in a parameter of self and returns self.alive, which is also used in the check_collision function; if a collision is detected self.alive is set to false. This function is important because it confirms if the car is alive with a basic function.
    
    """

    def is_alive(self):
        # Basic Alive Function
        return self.alive

    """ 
9. This Function calculates the reward for the cars based on distance the car has travelled. The reward value is standardised by dividing the distance travelled by half of the cars width, meaning that the cars progress is relative to its size.

This function is essential because the NEAT algorithm relies on a reward factor so that the alorithm can determine which mutations are benefitial. In this case, a higher value for distance is more desirable, so later on, this reward will be used to determine which behaviours can lead to a ligher distance.
    
    """

    def get_reward(self):
        # Calculate Reward
        # return self.distance / 50.0
        return self.distance / (CAR_SIZE_X / 2)

    """
10. This Function is used within function 6 and first obtains the bounding box of the input image using image.get_rect() and storing it in a variable called rectangle. Following that, the function  generates a rotated version of the image using Pygame's transformation capabilities, with the rotation angle specified by the angle parameter. This rotated image is saved in the rotated_image variable. The function then duplicates the original image's rectangle to create rotated_rectangle. The next step ensures that the center of rotated_rectangle aligns precisely with the center of the newly rotated image's rectangle. Lastly, the function extracts a cropped section from the rotated image, corresponding in size and position to the original image's rectangle with a centered alignment. This cropped image is then assigned to rotated_image and returned as the function's output.

This function is necessary to accurately rotate an image around its center point (whilst ensuring that the dimensions of the cars remain the same), which is essential for the cars when turning.
    
    """

    def rotate_center(self, image, angle):
        # Rotate The Rectangle
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image


""" This Function:
Empty Collections Initialization: Two lists, nets and cars, are initialized. nets will hold the neural networks corresponding to each genome, while cars will store instances of the Car class. These collections are essential for tracking and controlling the simulation's neural network-car interactions.

Initializing PyGame and Display: The Pygame library is initialized, and a display window is created with the specified dimensions (WIDTH and HEIGHT). This step sets up the graphical environment for the simulation, enabling the rendering of game elements and user interactions.

Creating Neural Networks and Cars: For each genome passed into the run_simulation function, a neural network is generated using the 'neat.nn.FeedForwardNetwork.create(g, config)' method. This network is associated with a specific genome and configuration. The neural network is added to the nets list, and the genome's fitness is initialized to zero. Additionally, a new instance of the Car class is created and added to the cars list. These cars will be controlled by their respective neural networks during the simulation.

Clock and Font Settings: The code establishes a Pygame clock to regulate the frame rate of the simulation, ensuring that it runs at a consistent speed. Different fonts are loaded to display information on the screen, enhancing the user's understanding of the simulation's progress.

Updating the Generation Counter: The current_generation global variable is incremented, reflecting the current generation being simulated. This provides a reference point for tracking the progress of the NEAT algorithm.

Main Simulation Loop: The core of the simulation is a loop that runs indefinitely, managing the behavior of each car and updating their associated neural networks. This loop forms the backbone of the NEAT algorithm's execution.

Event Handling: Within the loop, the code processes Pygame events. It checks for user interactions, such as closing the window or pressing the escape key, allowing users to control the simulation's execution.

Car Actions and Neural Network Activation: For each car, the neural network is activated with the car's sensor data, obtained using nets[i].activate(car.get_data()). The highest value in the neural network's output determines the car's action, whether it should turn left, turn right, slow down, or speed up. This step enables the neural networks to influence the cars' movements.

Updating Fitness and Car Movement: For cars that are still alive, their fitness scores are increased based on their progress, and their positions and movements are updated accordingly. This step is crucial for training the neural networks to improve car performance.

Checking Car Survival: The code counts the number of cars that are still alive in the simulation. If no cars remain alive, indicating that the simulation has reached its termination condition, the simulation loop is exited.

Time Limit for Simulation: A simple counter is used to roughly limit the duration of the simulation. In this case, the counter helps prevent the simulation from running indefinitely and ensures it ends after a predefined duration.

Drawing the Game Environment: Within the loop, the code draws the game map onto the screen. Additionally, for each alive car, it renders the car's image on the screen, visualizing their movements and interactions with the environment.

Displaying Information: The code displays textual information about the current generation, the number of cars still alive, and the mean fitness of the population. These details offer insights into the simulation's progress and the performance of evolving neural networks.

Updating Display and Frame Rate: After drawing the game environment and information, the display is updated to reflect these changes. The frame rate is controlled using the Pygame clock, ensuring a maximum of 60 frames per second for smooth and consistent simulation playback.
"""


def run_simulation(genomes, config):
    # Empty Collections For Nets and Cars
    nets = []
    cars = []

    # Initialize PyGame And The Display
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)

    # For All Genomes Passed Create A New Neural Network
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        cars.append(Car())

    # Clock Settings
    # Font Settings & Loading Map
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 30)
    alive_font = pygame.font.SysFont("Arial", 20)
    game_map = pygame.image.load("map.png").convert()  # Convert Speeds Up A Lot

    global current_generation
    current_generation += 1

    # Simple Counter To Roughly Limit Time (Not Good Practice)
    counter = 0

    while True:
        # Exit On Quit Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # For Each Car Get The Acton It Takes
        for i, car in enumerate(cars):
            output = nets[i].activate(car.get_data())
            choice = output.index(max(output))
            if choice == 0:
                car.angle += 10  # Left
            elif choice == 1:
                car.angle -= 10  # Right
            elif choice == 2:
                if car.speed - 2 >= 12:
                    car.speed -= 2  # Slow Down
            else:
                car.speed += 2  # Speed Up

        # Check If Car Is Still Alive
        # Increase Fitness If Yes And Break Loop If Not
        still_alive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                still_alive += 1
                car.update(game_map)
                genomes[i][1].fitness += car.get_reward()

        if still_alive == 0:
            break

        counter += 1
        if counter == 30 * 40:  # Stop After About 20 Seconds
            break

        # Draw Map And All Cars That Are Alive
        screen.blit(game_map, (0, 0))
        for car in cars:
            if car.is_alive():
                car.draw(screen)

        # Display Info
        text = generation_font.render(
            "Generation: " + str(current_generation), True, (0, 0, 0)
        )
        text_rect = text.get_rect()
        text_rect.center = (900, 450)
        screen.blit(text, text_rect)

        text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (900, 490)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)  # 60 FPS


""" This Section: entry point for the script, ensuring that the contained code executes only when the script is run directly, not when it's imported as a module.

The configuration settings defined in the config.txt file are loaded into the config variable using neat.Config(). The various components include neat.DefaultGenome, which specifies options controlling genome characteristics such as node activation, bias, connection management, and architecture. Additionally, parameters like num_hidden, num_inputs, and num_outputs collectively define the neural network's structure.

neat.DefaultReproduction defines settings related to genome reproduction, including the number of elite genomes (elitism) directly passed to the next generation and the survival_threshold that determines which genomes are considered for reproduction.

neat.DefaultSpeciesSet sets the compatibility threshold (compatibility_threshold) used to distinguish species, while neat.DefaultStagnation defines parameters such as the species fitness function (species_fitness_func), maximum stagnation generations (max_stagnation), and species elitism (species_elitism).

By encapsulating these configurations within the config variable, this section establishes the foundation for the NEAT algorithm's behavior and species management, necessary for guiding the evolution of neural networks controlling the simulated cars.

In the other part of this section, 'neat.StdOutReporter(True)' is added to allow real-time updates to be printed to the console. This report provides information on the status of each generation as they are simulated.

Additionally, a neat.StatisticsReporter() is added to collect various evolution statistics. This reporter helps monitor and record data such as the mean fitness of the population and other relevant metrics throughout the simulation.

Finally, the population.run(run_simulation, 1000) statement initiates the NEAT algorithm to run the simulation for a maximum of 1000 generations. During this process, the population of neural networks evolves, and the provided run_simulation function controls the behavior of the simulated cars.

This section is essential as it serves as the main driver for running the NEAT algorithm and simulating the evolution of neural networks controlling the cars.
    
"""
if __name__ == "__main__":
    # Load Config
    config_path = "./config.txt"
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )

    # Create Population And Add Reporters
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Run Simulation For A Maximum of 1000 Generations
    population.run(run_simulation, 1000)
