import numpy as np
import transformations as t
import pygame

class Axis():
    AXIS_LENGTH = 10

    def __init__(self, pos):
        self.pos = pos

    def draw(display):
        pass

class Cube():
    # V - E + F
    num_vertices = 8
    num_edges = 12
    num_faces = 6

    def __init__(self, side_length):
        self.alpha = 0
        self.beta = 0
        self.gamma = 0
        self.side_length = side_length
        self.vertices = self.vertices()
        self.center_of_mass = self.center_of_mass()
        self.edges = self.edges()
        self.faces = self.faces()
    
    def vertices(self):
        vertices_matrix = np.zeros((Cube.num_vertices, 3))

        vertice = 0
        for a in [0, self.side_length]:
            for b in [0, self.side_length]:
                for c in [0, self.side_length]:
                    vertices_matrix[vertice] = [a, b, c]
                    vertice += 1

        center_of_mass = np.sum(vertices_matrix, axis=0)/Cube.num_vertices

        for vertice in range(Cube.num_vertices):
            vertices_matrix[vertice] = t.translation(vertices_matrix[vertice], -center_of_mass)

        return vertices_matrix

    def edges(self):
        edges_matrix = np.zeros((Cube.num_vertices, 4, 3))

        for vertice in range(Cube.num_vertices):
            edges_matrix[vertice][0] = self.vertices[vertice]
            k = 1
            for j in range(Cube.num_vertices):
                if np.linalg.norm(self.vertices[j]-edges_matrix[vertice][0]) == self.side_length:
                    edges_matrix[vertice][k] = self.vertices[j]
                    k += 1

        return edges_matrix
    
    def faces(self):
        faces_matrix = np.zeros((Cube.num_faces, 4, 3))

        coord = 0
        for face in range(Cube.num_faces):
            point = 0
            for vertice in range(Cube.num_vertices):
                if self.vertices[vertice][coord % 3] == int(face / 3) * self.side_length:
                    faces_matrix[face][point] = self.vertices[vertice]
                    point += 1
            coord += 1
        
        return faces_matrix

    def center_of_mass(self):
        # We consider the solid to be a set of points in space,
        #  all of them with the same constant mass (hence mass does
        #  not play a role in computing the center of mass).
        # This set of points will be the vertices of the object.
        coords = np.sum(self.vertices, axis=0)/Cube.num_vertices
        return coords
    
    def update(self, delta_time):
        SPEED = 1
        update_vertices = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.alpha -= SPEED * delta_time
            update_vertices = True
        if keys[pygame.K_s]:
            self.alpha += SPEED * delta_time
            update_vertices = True
        if keys[pygame.K_a]:
            self.beta -= SPEED * delta_time
            update_vertices = True
        if keys[pygame.K_d]:
            self.beta += SPEED * delta_time
            update_vertices = True
        if keys[pygame.K_e]:
            self.gamma -= SPEED * delta_time
            update_vertices = True
        if keys[pygame.K_q]:
            self.gamma += SPEED * delta_time
            update_vertices = True
        
        if update_vertices:
            for vertice in range(Cube.num_vertices):
                # self.vertices[vertice] = t.rotation(t.translation(self.vertices[vertice], -self.center_of_mass), self.alpha, self.beta, self.gamma)
                self.vertices[vertice] = t.rotation(self.vertices[vertice], self.alpha, self.beta, self.gamma)
        
    def draw(self, display, pos, draw = 'edges', color = 'blue'):
        match draw:
            case 'vertices':
                for vertice in self.vertices:
                    point = t.xy_projection(t.translation(vertice, pos))
                    pygame.draw.circle(display, color, point, 1)

            case 'edges':
                for vertice in range(Cube.num_vertices):
                    p_init = t.xy_projection(t.translation(t.rotation(t.translation(self.edges[vertice][0], -self.center_of_mass), self.alpha, self.beta, self.gamma), pos))
                    for point in range(4):
                        p_fin = t.xy_projection(t.translation(t.rotation(t.translation(self.edges[vertice][point], -self.center_of_mass), self.alpha, self.beta, self.gamma), pos))
                        pygame.draw.aaline(display, color, p_init, p_fin)

            case 'faces':
                for face in self.faces:
                    lst = []
                    for point in face:
                        pnt = t.xy_projection(t.translation(t.rotation(t.translation(point, -self.center_of_mass), self.alpha, self.beta, self.gamma), pos))
                        lst.append(pnt)
                    pygame.draw.polygon(display, color, lst)

            case _:
                print("Error. Please introduce a correct object to draw ('vertices', 'edges', 'faces').")

class Torus():
    r_density = 16
    R_density = 16

    def __init__(self, r, R):
        self.alpha = 0
        self.beta = 0
        self.gamma = 0
        self.r = r
        self.R = R
        self.vertices = self.vertices()
        self.center_of_mass = self.center_of_mass()
        self.edges = self.edges()
        
    def vertices(self):
        i = 0
        vertices_matrix = np.zeros((Torus.r_density*Torus.R_density, 3))
        for k in range(Torus.R_density):
            for n in range(Torus.r_density):
                vertices_matrix[i] = [(self.R + self.r * np.cos(2*np.pi/Torus.r_density*n)) * np.cos(2*np.pi/Torus.R_density*k), (self.R + self.r * np.cos(2*np.pi/Torus.r_density*n)) * np.sin(2*np.pi/Torus.R_density*k), self.r * np.sin(2*np.pi/Torus.r_density*n)]
                i += 1
        return vertices_matrix

    def center_of_mass(self):
        # We consider the solid to be a set of points in space, all of them with the same constant mass.
        # This set of points will be the vertices of the Object.
        coords = np.sum(self.vertices, axis=0)/len(self.vertices)
        return coords

    
    def edges(self):
        edges_matrix = np.zeros((Torus.r_density*Torus.R_density, 5, 3))
        for i in range(len(self.vertices)):
            k = 0
            edges_matrix[i][k] = self.vertices[i]
            for j in range(len(self.vertices)):
                if i%Torus.r_density == 0:
                    if j == (i+1)%(Torus.r_density*Torus.r_density) or (j-i)%(Torus.r_density*Torus.r_density) == 15 or j == (i+Torus.r_density)%(Torus.r_density*Torus.r_density) or j == (i-Torus.r_density)%(Torus.r_density*Torus.r_density):
                        k += 1
                        edges_matrix[i][k] = self.vertices[j]    
                elif i%Torus.r_density == -1%Torus.r_density:
                    if (j+Torus.r_density-1) == i or (j+1) == i or j == (i+Torus.r_density)%(Torus.r_density*Torus.r_density) or j == (i-Torus.r_density)%(Torus.r_density*Torus.r_density):
                        k += 1
                        edges_matrix[i][k] = self.vertices[j]
                else:
                    if j == (i+1)%(Torus.r_density*Torus.r_density) or j == (i-1)%(Torus.r_density*Torus.r_density) or j == (i+Torus.r_density)%(Torus.r_density*Torus.r_density) or j == (i-Torus.r_density)%(Torus.r_density*Torus.r_density):
                        k += 1
                        edges_matrix[i][k] = self.vertices[j]
        return edges_matrix
    
    def rotate(self, alpha, beta, gamma):
        self.yaw(alpha)
        self.pitch(beta)
        self.roll(gamma)

    def yaw(self, deg):
        self.alpha = deg
    
    def pitch(self, deg):
        self.beta = deg

    def roll(self, deg):
        self.gamma = deg

    def draw(self, display, pos, color):
        for i in range(len(self.edges)):
            p_init = t.xy_projection(t.translation(t.rotation(t.translation(self.edges[i][0], -self.center_of_mass), self.alpha, self.beta, self.gamma), pos))
            for j in range(len(self.edges[i])):
                p_fin = t.xy_projection(t.translation(t.rotation(t.translation(self.edges[i][j], -self.center_of_mass), self.alpha, self.beta, self.gamma), pos))
                pygame.draw.aaline(display, color, p_init, p_fin)