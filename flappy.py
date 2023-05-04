#!/usr/bin/env python3
# Copyright (C) 2023  Cristina Bolaños Peño
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>

import math
import sys
import os.path
from argparse import ArgumentParser
from random import randint
import json

import mediapipe as mp
import pygame
import pygame.camera

ASSETS_DIR = os.path.join(os.path.abspath(
    os.path.dirname(__file__))) + '/assets'


def load_image(name: str, display_width: int,
               display_height: int) -> pygame.Surface:
    path = os.path.join(ASSETS_DIR, f'{name}.png')
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    img = pygame.image.load(path)
    return pygame.transform.scale(img, (
        img.get_width() * display_width // 1920,
        img.get_height() * display_height // 1080))


def load_fonts(name: str, display_height: int) -> tuple[pygame.font.Font]:
    path = os.path.join(ASSETS_DIR, f'{name}.ttf')
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    return (pygame.font.Font(path, int(display_height * 0.20)),
            pygame.font.Font(path, int(display_height * 0.10)))


class FlappySprite(pygame.sprite.Sprite):
    def __init__(self, center_x: int, center_y: int,
                 images: list[pygame.Surface],
                 speed: int = 1) -> None:
        super().__init__()
        self.images = images
        self.image = self.images[0]
        self.image_idx = 0
        self.rect = self.image.get_rect()
        self.rect.center = [center_x, center_y]
        self.y_delta = speed * 5

    def update(self, direction: int = 0,
               game_over: bool = False) -> None:
        # Update sprite image
        self.image_idx += 1
        if self.image_idx >= len(self.images):
            self.image_idx = 0
        self.image = self.images[self.image_idx]
        if game_over:
            # Lower position and rotate on game over
            self.rect.y += self.y_delta
            self.image = pygame.transform.rotate(self.image, 90)
        elif direction != 0:
            # Move towards direction
            self.rect.y -= direction * self.y_delta
            self.image = pygame.transform.rotate(
                self.image, direction//abs(direction)*25)


class PipeSprite(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int,
                 pair_id: int,
                 image: pygame.Surface,
                 speed: int = 1,
                 upside_down: bool = False) -> None:
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        if upside_down:
            self.image = pygame.transform.flip(
                self.image, False, True)
            self.rect.bottomleft = [x, y]
        else:
            self.rect.topleft = [x, y]
        self.pair_id = pair_id
        self.x_delta = speed * 5

    def update(self, game_over: bool = False) -> None:
        if game_over:  # Do not move on game over
            return
        self.rect.x -= self.x_delta
        if self.rect.x < -self.rect.width:
            # Kill if outside game bounds
            self.kill()


class GroundSprite(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int,
                 image: pygame.Surface,
                 speed: int = 1) -> None:
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = [x, y]
        self.x_delta = speed * 5

    def update(self, game_over: bool = False) -> None:
        if game_over:  # Do not move on game over
            return
        self.rect.x -= self.x_delta
        if self.rect.x < -self.rect.width // 2:
            # Re-position at the screen end
            self.rect.x = 0


class Button:
    def __init__(self, cx: int, cy: int,
                 text: str, font: pygame.font.Font) -> None:
        self.clicked = False
        self.text = font.render(text, True, (255, 255, 255))
        self.shadow = font.render(text, True, (189, 78, 21))
        self.bg = pygame.Surface((self.text.get_width() * 1.1,
                                  self.text.get_height() * 1.1))
        self.bg.fill((230, 97, 29))
        self.rect = self.bg.get_rect()
        self.rect.center = [cx, cy]
        self.text_x = cx - self.text.get_width() // 2
        self.text_y = cy - self.text.get_height() * 0.75

    def draw(self, display: pygame.Surface) -> bool:
        retval = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
                retval = True
        if not pygame.mouse.get_pressed()[0]:
            self.clicked = False

        display.blit(self.bg, (self.rect.x, self.rect.y))
        display.blit(self.shadow, (self.text_x, self.text_y +
                                   self.text.get_height() * 0.05))
        display.blit(self.text, (self.text_x, self.text_y))
        return retval


class Game:
    def __init__(self, camera_path: str = '/dev/video0',
                 detector_precision: int = 1,
                 level: int = 1, speed: int = 1) -> None:
        self.display = pygame.display.set_mode(
            (0, 0), pygame.FULLSCREEN)
        self.font, self.font_btn = load_fonts(
            'font', self.display.get_height())
        # Controls
        self.score = 0
        self.best = 0
        self.speed = min(4, max(1, speed))
        self.level = min(4, max(1, level))
        self.start_btn = Button(
            self.display.get_width() // 2,
            self.display.get_height() // 2,
            'start', self.font_btn)
        self.restart_btn = Button(
            self.display.get_width() // 2,
            self.display.get_height() * 0.9,
            'restart', self.font_btn)
        # Background
        self.background = load_image('bg', self.display.get_width(),
                                     self.display.get_height())
        self.background_blur = pygame.Surface(self.background.get_size(), pygame.SRCALPHA, 32)
        self.background_blur.convert_alpha()
        self.background_blur.fill((255, 255, 255, 64))
        # Ground
        self.ground_grp = pygame.sprite.Group()
        ground_img = load_image('ground', self.display.get_width(),
                                self.display.get_height())
        sprite = GroundSprite(
            0, self.display.get_height() - ground_img.get_height(),
            ground_img, speed)
        self.ground_grp.add(sprite)
        # Flappy
        self.flappy = FlappySprite(
            int(self.display.get_width() * 0.25),
            self.display.get_height() // 2,
            tuple(load_image(f'bird{i}', self.display.get_width(),
                             self.display.get_height()) for i in range(1, 4)),
            speed)
        self.flappy_grp = pygame.sprite.Group()
        self.flappy_grp.add(self.flappy)
        # Pipes
        self.pipe_grp = pygame.sprite.Group()
        self.pipe_gap_px = max(self.display.get_height() * 0.25,
                               self.flappy.rect.height)
        self.last_pipe_id = 1
        self.x_pipe_gen_trigger = self.display.get_width() - 78 * (  # TODO Change name
            10 - self.level)
        self.generate_pipe_pair()
        # Camera & Detector
        self.camera = pygame.camera.Camera(camera_path)  # 640x480
        self.detector = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=min(2, max(1, detector_precision)))

    def generate_pipe_pair(self) -> None:
        center_y = randint(104, self.ground_grp.sprites()[
            0].rect.top - 104)
        self.pipe_grp.add(PipeSprite(
            self.display.get_width(),
            center_y + self.pipe_gap_px // 2,
            self.last_pipe_id,
            load_image('pipe', self.display.get_width(),
                       self.display.get_height()),
            self.speed))
        self.pipe_grp.add(PipeSprite(
            self.display.get_width(),
            center_y - self.pipe_gap_px // 2,
            self.last_pipe_id,
            load_image('pipe', self.display.get_width(),
                       self.display.get_height()),
            self.speed, True))
        self.last_pipe_id += 1

    def update_score(self) -> None:
        for pipe in self.pipe_grp.sprites():
            if self.score >= pipe.pair_id:
                continue
            elif pipe.rect.bottomright[
                    0] <= self.flappy.rect.bottomleft[0]:
                self.score = pipe.pair_id
                self.best = max(self.score, self.best)

    def get_direction(self, frame: pygame.Surface,
                      right_arm: bool = True) -> int:
        # FIXME arm change not implemented
        detection = self.detector.process(pygame.surfarray.array3d(frame))
        if not detection.pose_landmarks:
            # raise ValueError('No detection.')
            return 0
        indexes = [23, 11, 15] if right_arm else [24, 12, 16]
        joints = [detection.pose_landmarks.landmark[
            i] for i in indexes]
        if any([j.visibility < 0.5 for j in joints]):
            # FIXME hardcoded threshold
            # raise ValueError('Bad detection.')
            return 0
        # 0:up 180:down
        angle = min(180, max(0, math.degrees(
            math.atan2(joints[2].y - joints[1].y,
                       joints[2].x - joints[1].x) -
            math.atan2(joints[1].y - joints[0].y,
                       joints[1].x - joints[0].x))))
        # Transform to [-45:45] range
        angle = min(45, max(-45, angle - 90))
        # Normalize
        return round(angle / 45 * -1)

    def check_collision(self) -> bool:
        retval = len(pygame.sprite.spritecollide(  # Collided
            self.flappy, self.pipe_grp, False)) > 0
        retval |= self.flappy.rect.top <= 0  # Touched top
        retval |= self.flappy.rect.bottom >= self.ground_grp.sprites()[
            0].rect.top  # Touched ground
        return retval

    def draw_text(self, text: str, position: str = 'middle',
                  shadow: bool = True) -> None:
        x = self.display.get_width() // 2
        if position == 'top':
            y = self.display.get_height() * 0.1
        elif position == 'bottom':
            y = self.display.get_height() * 0.9
        else:
            y = self.display.get_height() // 2
        _text = self.font.render(text, True, (255, 255, 255))
        x -= _text.get_width() // 2
        y -= _text.get_height() // 2
        if shadow:
            self.display.blit(
                self.font.render(text, True, (38, 38, 38)),
                (x, y + _text.get_height() * 0.05))
        self.display.blit(_text, (x, y))

    def restart(self) -> None:
        self.score = 0
        self.flappy_grp.update()
        self.flappy.rect.center = [
            int(self.display.get_width() * 0.25),
            self.display.get_height() // 2]
        self.pipe_grp.empty()
        self.generate_pipe_pair()

    def run(self, delay_ms: int = 5000) -> None:
        # Flags
        running = True
        started = False
        game_over = False
        clock = pygame.time.Clock()
        ts = pygame.time.get_ticks()
        self.camera.start()
        while running:
            clock.tick(60)
            elapsed_ms = pygame.time.get_ticks() - ts
            # Draw scene
            self.display.blit(self.background, (0, 0))
            self.flappy_grp.draw(self.display)
            self.pipe_grp.draw(self.display)
            self.ground_grp.draw(self.display)
            frame = self.camera.get_image()
            display_frame = pygame.transform.scale(frame, (
                self.display.get_height() * 0.3 * frame.get_width() // frame.get_height(),
                self.display.get_height() * 0.3))
            self.display.blit(display_frame, (
                self.display.get_width() - display_frame.get_width(),
                self.display.get_height() - display_frame.get_height()))
            # Check exiting
            for ev in pygame.event.get(pygame.KEYDOWN):
                if ev.key == pygame.K_ESCAPE:
                    running = False
                    break
            if not running:
                pygame.display.flip()  # Show display and exit
                break

            if not started:  # Wait for start button clicked
                self.display.blit(self.background_blur, (0,0))
                self.start_btn.draw(self.display)
                started = self.start_btn.clicked
                ts = pygame.time.get_ticks()
                pygame.display.flip()  # Show display and continue loop
                continue
            elif elapsed_ms <= delay_ms:  # Wait some time for preparing after start...
                self.display.blit(self.background_blur, (0,0))
                self.draw_text('Starting in {}'.format(5 - elapsed_ms // 1000))
                pygame.display.flip()  # Show display and continue loop
                continue

            # Playing
            game_over |= self.check_collision()
            direction = self.get_direction(frame)
            # Update sprites
            self.ground_grp.update(game_over=game_over)
            self.pipe_grp.update(game_over=game_over)
            if self.display.get_rect().contains(self.flappy.rect):
                self.flappy_grp.update(
                    direction=direction, game_over=game_over)
            # Check if need to generate pipes
            if self.pipe_grp.sprites()[
                    -1].rect.x < self.x_pipe_gen_trigger and not game_over:
                self.generate_pipe_pair()
            # Update score
            self.update_score()
            if game_over:
                self.display.blit(self.background_blur, (0,0))
                self.draw_text(
                    f'Score: {self.score} Best: {self.best}', position='top')
                self.draw_text('Game Over')
                self.restart_btn.draw(self.display)
                if self.restart_btn.clicked:
                    self.restart()
                    ts = pygame.time.get_ticks()
                    game_over = False
            else:
                self.draw_text(str(self.score), position='top')
            pygame.display.flip()
        self.camera.stop()


if __name__ == '__main__':
    parser = ArgumentParser(
        description='Flappy Bird game using pose estimation,')
    parser.add_argument(
        '--config', default=None, help='Configuration file (JSON).')
    parser.add_argument(
        '-c', '--camera', default='/dev/video0',
        help='Camera device. Default is "/dev/video0".')
    parser.add_argument(
        '-s', '--speed', metavar='1',
        type=int, default=1,
        help='Movement speed. Default is 1.')
    parser.add_argument(
        '-l', '--level', metavar='1',
        type=int, default=1,
        help='Level of difficulty (affects the space ' +
        'between pipes). Default is 1.')
    parser.add_argument(
        '-p', '--precision', metavar='1',
        type=int, choices=(1, 2), default=1,
        help='Detector (MediaPipe) precision. Choices are: 1, 2. ' +
        'Default is 1.')
    args = parser.parse_args()
    if args.config is not None:
        if not os.path.exists(args.config):
            parser.error(f'File not found: {args.config}')
        with open(args.config) as fr:
            data = json.load(fr)
        for k, v in data.items():
            if k == 'camera' and args.camera == '/dev/video0':
                setattr(args, 'camera', v)
            elif getattr(args, k, 1) == 1:
                setattr(args, k, v)
    pygame.init()
    pygame.camera.init()
    Game(args.camera, args.precision,
         min(4, max(1, abs(int(args.level)))),
         min(4, max(1, abs(int(args.speed))))).run()
    pygame.quit()
    sys.exit(0)
