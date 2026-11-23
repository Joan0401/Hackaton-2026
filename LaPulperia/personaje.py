import math
import pygame


class Player:
    """Personaje jugable de La Pulperia con colisiones en los pies.

    x representa el centro horizontal del personaje y y la posicion de sus pies.
    El sprite se dibuja a 28x44 pixeles logicos y no usa imagenes externas.
    La hitbox pequeña de los pies permite acercarse a la parte trasera
    de los muebles sin atravesarlos.
    """

    WIDTH = 28
    BASE_HEIGHT = 40
    HEIGHT = 44
    SPEED = 105
    COLLISION_WIDTH = 18
    COLLISION_HEIGHT = 6
    WALK_FRAME_TIME = 0.14

    # Contorno y paleta
    OUTLINE = (45, 35, 34)
    OUTLINE_LIGHT = (76, 55, 46)
    HAIR = (73, 45, 35)
    HAIR_LIGHT = (125, 82, 52)
    SKIN = (229, 177, 132)
    SKIN_LIGHT = (245, 202, 157)
    SKIN_SHADOW = (184, 119, 85)
    SHIRT = (74, 128, 119)
    SHIRT_LIGHT = (137, 177, 153)
    SHIRT_DARK = (47, 88, 83)
    APRON = (224, 192, 128)
    APRON_LIGHT = (244, 221, 172)
    APRON_DARK = (151, 105, 66)
    PANTS = (58, 73, 84)
    PANTS_LIGHT = (91, 108, 113)
    SHOES = (77, 47, 37)
    SHOES_LIGHT = (137, 87, 55)
    EYE = (43, 36, 34)

    # Apariencias elegibles al darle JUGAR. Cada una cambia colores y,
    # en la pulpera, agrega cabello largo y un gancho de flor.
    SKINS = {
        "hombre": {"nombre": "PULPERO"},
        "mujer": {
            "nombre": "PULPERA",
            "HAIR": (62, 36, 31),
            "HAIR_LIGHT": (110, 66, 46),
            "SHIRT": (190, 92, 104),
            "SHIRT_LIGHT": (226, 148, 150),
            "SHIRT_DARK": (138, 60, 72),
        },
    }
    FLOR = (235, 112, 146)
    FLOR_CENTRO = (250, 214, 120)

    def __init__(self, x=320, y=248, skin="hombre"):
        self.start_x = float(x)
        self.start_y = float(y)
        self.x = float(x)
        self.y = float(y)
        self.direction = "down"
        self.frame = 0
        self.animation_time = 0.0
        self.skin = None
        self.set_skin(skin)

    def set_skin(self, skin):
        """Cambia la apariencia y vuelve a construir la animación."""
        if skin not in self.SKINS:
            skin = "hombre"
        # Restaurar la paleta base y aplicar la de esta apariencia.
        for clave in ("HAIR", "HAIR_LIGHT", "SHIRT", "SHIRT_LIGHT", "SHIRT_DARK"):
            self.__dict__.pop(clave, None)
        for clave, valor in self.SKINS[skin].items():
            if clave != "nombre":
                setattr(self, clave, valor)
        self.skin = skin
        self.frames = self._build_frames()

    @property
    def es_pulpera(self):
        return self.skin == "mujer"

    @staticmethod
    def _rect(surface, color, rect):
        pygame.draw.rect(surface, color, rect)

    def _draw_legs_front_back(self, sprite, frame, back=False):
        """Piernas de silueta estable; solo alternan los detalles del paso."""
        r = self._rect
        left_x, right_x = 7, 15

        r(sprite, self.OUTLINE, (left_x - 1, 29, 7, 8))
        r(sprite, self.OUTLINE, (right_x - 1, 29, 7, 8))
        r(sprite, self.PANTS, (left_x, 30, 5, 6))
        r(sprite, self.PANTS, (right_x, 30, 5, 6))

        # El brillo cambia de pierna entre fotogramas, sin alterar el contorno.
        highlight_x = left_x + 1 if frame == 0 else right_x + 1
        r(sprite, self.PANTS_LIGHT, (highlight_x, 31, 1, 3))
        r(sprite, self.PANTS_LIGHT, (right_x + 3 if frame == 0 else left_x + 3, 32, 1, 2))

        r(sprite, self.OUTLINE, (left_x - 2, 35, 8, 5))
        r(sprite, self.OUTLINE, (right_x - 1, 35, 8, 5))
        r(sprite, self.SHOES, (left_x - 1, 36, 6, 3))
        r(sprite, self.SHOES, (right_x, 36, 6, 3))
        r(sprite, self.SHOES_LIGHT, (left_x if frame == 0 else left_x + 2, 36, 2, 1))
        r(sprite, self.SHOES_LIGHT, (right_x + 1 if frame == 0 else right_x + 3, 36, 2, 1))

    def _build_front_back(self, direction, frame):
        sprite = pygame.Surface((self.WIDTH, self.BASE_HEIGHT), pygame.SRCALPHA)
        r = self._rect

        # Piernas y zapatos, detrás del delantal.
        self._draw_legs_front_back(sprite, frame, back=(direction == "up"))

        # Brazos con contorno fijo; solo cambia un brillo de la manga.
        r(sprite, self.OUTLINE, (2, 17, 6, 13))
        r(sprite, self.SHIRT, (3, 18, 4, 9))
        r(sprite, self.SKIN, (3, 26, 4, 4))
        r(sprite, self.OUTLINE, (20, 17, 6, 13))
        r(sprite, self.SHIRT, (21, 18, 4, 9))
        r(sprite, self.SKIN, (21, 26, 4, 4))
        r(sprite, self.SHIRT_LIGHT, (4 if frame == 0 else 5, 20, 1, 3))
        r(sprite, self.SHIRT_LIGHT, (22 if frame == 0 else 21, 20, 1, 3))

        # Torso y camisa.
        r(sprite, self.OUTLINE, (5, 15, 18, 17))
        r(sprite, self.SHIRT_DARK, (6, 16, 16, 14))
        r(sprite, self.SHIRT, (7, 16, 14, 12))
        r(sprite, self.SHIRT_LIGHT, (8, 17, 4, 2))
        r(sprite, self.SHIRT_LIGHT, (17, 17, 3, 2))

        # Delantal de cajero, con tirantes y bolsillo.
        r(sprite, self.APRON_DARK, (9, 18, 10, 13))
        r(sprite, self.APRON, (10, 19, 8, 11))
        r(sprite, self.APRON_LIGHT, (11, 20, 3, 2))
        r(sprite, self.APRON_DARK, (12, 26, 5, 1))
        r(sprite, self.APRON_DARK, (11, 28, 6, 1))
        r(sprite, self.APRON_DARK, (9, 17, 2, 4))
        r(sprite, self.APRON_DARK, (17, 17, 2, 4))

        # Cuello.
        r(sprite, self.OUTLINE, (11, 12, 7, 6))
        r(sprite, self.SKIN_SHADOW, (12, 13, 5, 4))
        r(sprite, self.SKIN, (13, 13, 3, 3))

        # Cabeza, un poco mas grande que la version anterior.
        r(sprite, self.OUTLINE, (5, 1, 18, 16))
        r(sprite, self.SKIN_SHADOW, (6, 4, 16, 11))
        r(sprite, self.SKIN, (7, 4, 14, 10))
        r(sprite, self.SKIN_LIGHT, (9, 5, 5, 2))

        if direction == "down":
            # Flequillo y rostro frontal.
            r(sprite, self.HAIR, (5, 1, 18, 7))
            r(sprite, self.HAIR_LIGHT, (8, 2, 10, 2))
            r(sprite, self.HAIR, (6, 6, 4, 4))
            r(sprite, self.HAIR, (18, 6, 4, 4))
            r(sprite, self.EYE, (10, 9, 2, 2))
            r(sprite, self.EYE, (17, 9, 2, 2))
            r(sprite, self.SKIN_SHADOW, (13, 11, 2, 1))
            r(sprite, self.OUTLINE, (12, 13, 4, 1))
            if self.es_pulpera:
                # Cabello largo a los lados de la cara, hasta los hombros.
                r(sprite, self.OUTLINE, (3, 5, 6, 16))
                r(sprite, self.OUTLINE, (19, 5, 6, 16))
                r(sprite, self.HAIR, (4, 5, 4, 15))
                r(sprite, self.HAIR, (20, 5, 4, 15))
                r(sprite, self.HAIR_LIGHT, (5, 8, 1, 8))
                r(sprite, self.HAIR_LIGHT, (21, 8, 1, 8))
                # Pestañas y gancho de flor.
                r(sprite, self.EYE, (9, 8, 1, 1))
                r(sprite, self.EYE, (19, 8, 1, 1))
                self._flor(sprite, 18, 1)
        else:
            # Vista trasera: cabello completo, sin rasgos faciales.
            r(sprite, self.HAIR, (5, 1, 18, 13))
            r(sprite, self.HAIR_LIGHT, (8, 3, 11, 2))
            r(sprite, self.HAIR_LIGHT, (10, 9, 8, 2))
            r(sprite, self.HAIR, (7, 12, 14, 3))
            r(sprite, self.SHIRT_DARK, (9, 16, 10, 2))
            if self.es_pulpera:
                # Cabello largo cayendo por la espalda.
                r(sprite, self.OUTLINE, (4, 4, 20, 19))
                r(sprite, self.HAIR, (5, 4, 18, 18))
                r(sprite, self.HAIR_LIGHT, (8, 3, 11, 2))
                r(sprite, self.HAIR_LIGHT, (9, 10, 2, 9))
                r(sprite, self.HAIR_LIGHT, (16, 10, 2, 9))
                r(sprite, self.OUTLINE, (5, 1, 18, 3))
                r(sprite, self.HAIR, (6, 2, 16, 3))
                self._flor(sprite, 18, 1)

        return sprite

    def _build_side_right(self, frame):
        """Perfil mirando a la derecha. El perfil izquierdo es su espejo exacto."""
        sprite = pygame.Surface((self.WIDTH, self.BASE_HEIGHT), pygame.SRCALPHA)
        r = self._rect

        # Perfil con silueta constante. La animacion alterna los brillos
        # y la separacion interior de las piernas, nunca el ancho o la altura.
        r(sprite, self.OUTLINE, (8, 29, 15, 9))
        r(sprite, self.PANTS, (9, 30, 13, 7))
        seam_x = 15 if frame == 0 else 14
        r(sprite, self.OUTLINE, (seam_x, 30, 1, 6))
        if frame == 0:
            r(sprite, self.PANTS_LIGHT, (11, 31, 1, 3))
            r(sprite, self.PANTS_LIGHT, (18, 32, 1, 2))
        else:
            r(sprite, self.PANTS_LIGHT, (11, 32, 1, 2))
            r(sprite, self.PANTS_LIGHT, (18, 31, 1, 3))

        # Ambos zapatos conservan la misma silueta y linea de suelo.
        r(sprite, self.OUTLINE, (7, 35, 9, 5))
        r(sprite, self.SHOES, (8, 36, 7, 3))
        r(sprite, self.OUTLINE, (15, 35, 9, 5))
        r(sprite, self.SHOES, (16, 36, 7, 3))
        r(sprite, self.SHOES_LIGHT, (9, 36, 3, 1))
        r(sprite, self.SHOES_LIGHT, (17, 36, 3, 1))

        # Brazo posterior.
        r(sprite, self.OUTLINE, (7, 18, 6, 12))
        r(sprite, self.SHIRT_DARK, (8, 19, 4, 8))
        r(sprite, self.SKIN, (8, 26, 4, 4))

        # Torso de perfil.
        r(sprite, self.OUTLINE, (8, 15, 15, 17))
        r(sprite, self.SHIRT_DARK, (9, 16, 13, 14))
        r(sprite, self.SHIRT, (10, 16, 11, 12))
        r(sprite, self.SHIRT_LIGHT, (12, 17, 5, 2))

        # Delantal visto de lado, sin cambiar el ancho del torso al caminar.
        r(sprite, self.APRON_DARK, (13, 19, 9, 12))
        r(sprite, self.APRON, (14, 20, 7, 10))
        r(sprite, self.APRON_LIGHT, (15, 21, 3, 2))
        r(sprite, self.APRON_DARK, (16, 27, 4, 1))

        # Brazo delantero y mano.
        r(sprite, self.OUTLINE, (19, 18, 6, 12))
        r(sprite, self.SHIRT, (20, 19, 4, 8))
        r(sprite, self.SKIN, (20, 26, 4, 4))

        # Cuello y cabeza de perfil. La nariz apunta a la derecha.
        r(sprite, self.OUTLINE, (11, 11, 7, 7))
        r(sprite, self.SKIN_SHADOW, (12, 12, 5, 4))
        r(sprite, self.OUTLINE, (8, 1, 16, 16))
        r(sprite, self.SKIN_SHADOW, (10, 4, 12, 11))
        r(sprite, self.SKIN, (11, 4, 10, 10))
        r(sprite, self.SKIN_LIGHT, (13, 5, 5, 2))

        # Cabello y patilla en la parte posterior de la cabeza.
        r(sprite, self.HAIR, (8, 1, 15, 7))
        r(sprite, self.HAIR_LIGHT, (11, 2, 9, 2))
        r(sprite, self.HAIR, (8, 6, 5, 7))
        r(sprite, self.HAIR, (18, 5, 5, 3))

        # Rasgos faciales reorientados: se mueve el ojo, la nariz y la boca
        # al lado opuesto sin reflejar ni deformar la cabeza o el cuerpo.
        r(sprite, self.EYE, (11, 8, 2, 2))
        r(sprite, self.SKIN_SHADOW, (8, 10, 3, 2))
        r(sprite, self.SKIN_LIGHT, (8, 10, 2, 1))
        r(sprite, self.OUTLINE, (10, 13, 3, 1))

        if self.es_pulpera:
            # Cabello largo detrás de la cabeza, cayendo sobre la espalda.
            r(sprite, self.OUTLINE, (16, 4, 8, 18))
            r(sprite, self.HAIR, (17, 4, 6, 17))
            r(sprite, self.HAIR_LIGHT, (19, 7, 1, 10))
            r(sprite, self.EYE, (10, 7, 1, 1))
            self._flor(sprite, 17, 1)

        return sprite

    def _flor(self, sprite, x, y):
        """Gancho de flor de 3x3 en el cabello."""
        r = self._rect
        r(sprite, self.FLOR, (x, y + 1, 3, 1))
        r(sprite, self.FLOR, (x + 1, y, 1, 3))
        r(sprite, self.FLOR_CENTRO, (x + 1, y + 1, 1, 1))

    def _build_frames(self):
        frames = {
            "down": (
                self._build_front_back("down", 0),
                self._build_front_back("down", 1),
            ),
            "up": (
                self._build_front_back("up", 0),
                self._build_front_back("up", 1),
            ),
        }

        # Construimos un solo perfil hacia la derecha y generamos el izquierdo
        # reflejandolo. Asi no se invierten accidentalmente los rostros.
        side_base_frames = (
            self._build_side_right(0),
            self._build_side_right(1),
        )

        # El perfil base actual tiene el rostro orientado hacia la izquierda.
        # Se usa su reflejo para caminar a la derecha y la vista base para
        # caminar a la izquierda. No se modifica el dibujo del personaje.
        right_frames = tuple(
            pygame.transform.flip(frame, True, False)
            for frame in side_base_frames
        )
        left_frames = side_base_frames

        frames["right"] = right_frames
        frames["left"] = left_frames

        # Estiramiento vertical moderado: conserva el pixel art y el punto
        # de apoyo inferior, aumentando la altura visual de 40 a 44 px.
        for direction, direction_frames in frames.items():
            frames[direction] = tuple(
                pygame.transform.scale(frame, (self.WIDTH, self.HEIGHT))
                for frame in direction_frames
            )

        return frames

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.direction = "down"
        self.frame = 0
        self.animation_time = 0.0

    def _feet_rect_at(self, x, y):
        """Hitbox compacta en los pies, no alrededor de todo el sprite."""
        left = round(x - self.COLLISION_WIDTH / 2)
        top = round(y - self.COLLISION_HEIGHT)
        return pygame.Rect(
            left,
            top,
            self.COLLISION_WIDTH,
            self.COLLISION_HEIGHT
        )

    def _collides_at(self, x, y, obstacles):
        if not obstacles:
            return False

        feet = self._feet_rect_at(x, y)
        return any(feet.colliderect(obstacle) for obstacle in obstacles)

    def _move_axis(self, amount, axis, obstacles):
        """Mueve en un eje con pasos pequeños para evitar atravesar muebles."""
        if amount == 0:
            return False

        # Subpasos de como maximo un pixel evitan el tunneling en dt grandes.
        steps = max(1, math.ceil(abs(amount)))
        step = amount / steps
        moved = False

        for _ in range(steps):
            next_x = self.x + step if axis == "x" else self.x
            next_y = self.y + step if axis == "y" else self.y

            if self._collides_at(next_x, next_y, obstacles):
                break

            self.x = next_x
            self.y = next_y
            moved = True

        return moved

    def update(self, dt, keys, map_width, map_height, obstacles=None, floor_top=96):
        """Mueve al personaje sin permitir que atraviese muebles."""
        if obstacles is None:
            obstacles = []

        dx = 0
        dy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1

        moving_input = dx != 0 or dy != 0
        moved = False

        if moving_input:
            length = math.hypot(dx, dy)
            dx /= length
            dy /= length

            # La direccion sigue la tecla pulsada, incluso si hay una pared.
            if abs(dx) > abs(dy):
                self.direction = "right" if dx > 0 else "left"
            else:
                self.direction = "down" if dy > 0 else "up"

            move_x = dx * self.SPEED * dt
            move_y = dy * self.SPEED * dt

            # Separar los ejes permite deslizarse junto a los muebles.
            moved_x = self._move_axis(move_x, "x", obstacles)
            moved_y = self._move_axis(move_y, "y", obstacles)
            moved = moved_x or moved_y

        if moved:
            self.animation_time += dt
            self.frame = int(self.animation_time / self.WALK_FRAME_TIME) % 2
        else:
            self.animation_time = 0.0
            self.frame = 0

        # Limites del mapa y de la zona transitable.
        # La hitbox de los pies debe quedar completamente sobre el piso:
        # su borde superior no puede entrar en la pared.
        half_w = self.WIDTH // 2
        min_feet_y = floor_top + self.COLLISION_HEIGHT

        self.x = max(half_w, min(map_width - half_w, self.x))
        self.y = max(min_feet_y, min(map_height, self.y))

    def draw(self, surface):
        # Sombra estable bajo los pies.
        shadow_rect = pygame.Rect(
            round(self.x - 9), round(self.y - 3), 18, 5
        )
        pygame.draw.ellipse(surface, (55, 48, 43), shadow_rect)

        sprite = self.frames[self.direction][self.frame]
        sprite_rect = sprite.get_rect(
            midbottom=(round(self.x), round(self.y))
        )
        surface.blit(sprite, sprite_rect)
        # Ropa comprada en el ARMARIO (sombrero, lentes): ver cosmeticos.py
        ropa = self.__dict__.get("ropa")
        if ropa:
            ropa(surface, self, sprite_rect)
