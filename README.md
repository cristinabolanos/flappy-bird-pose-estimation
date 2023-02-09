<div align="center">

# Flappy Bird game with Pose Estimation

### [Introduction](#introduction) | [Requirements](#requirements) | [Usage](#usage) | [License](#license) | [Pyenv](#execution-with-pyenv)

</div>

## Introduction

Play the famous Flappy Bird game using **your body**! 

This program combines the mechanics of [Flappy Bird game](https://flappybird.io) with [MediaPipe](https://mediapipe.dev/) pose estimation solution. To play it, put yourself in front of the camera, execute the program, and control Flappy with your **right arm**. Although, make sure both your right **hip, shoulder and wrist** are fully visible! To exit the game, just press the `Escape` key.

Based on [russs123](https://github.com/russs123) Flappy implementation, available in this [repository](https://github.com/russs123/flappy_bird).

## Requirements

* Linux OS (tested on Ubuntu 22.04 LTS).
* Python3 installed (tested on 3.10.6 version).
* A camera device connected to your computer. Note its path, it should be some like `/dev/videoX`. You can use `v4l2-ctl --list-devices` command to find your camera decvice (`v4l-utils` package needed).
* A display. It is recommended one with 1920 x 1080 resolution. Make sure it is your **primary** screen, because the game will be displayed **fullscreen**. 

> DISCLAIMER: Other versions were not tested. To assure correct functionality, read [execution with pyenv instructions](#execution-with-pyenv).

## Usage

```bash
usage: flappy.py [-h] [-c CAMERA] [-s 1] [-l 1] [-p 1]

Flappy Bird game using pose estimation,

options:
  -h, --help            show this help message and exit
  -c CAMERA, --camera CAMERA
                        Camera device. Default is "/dev/video0".
  -s 1, --speed 1       Movement speed. Default is 1.
  -l 1, --level 1       Level of difficulty (affects the space between pipes). Default is 1.
  -p 1, --precision 1   Detector (MediaPipe) precision. Choices are: 1, 2. Default is 1.
```

## Execution with [pyenv](https://github.com/pyenv/pyenv)

To configure `pyenv`, follow steps below:

1. Install `python` build dependencies as told in [this page](https://github.com/pyenv/pyenv/wiki#suggested-build-environment).

2. Install `pyenv` with its [automatic installer](https://github.com/pyenv/pyenv#automatic-installer).

    `curl https://pyenv.run | bash`

3. Follow post-installation instructions: adding pyenv to PATH and init environment. Add the following lines to `~/.bashrc`:

    ```
    export PYENV_ROOT="$HOME/.pyenv"
    command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
    ```

3. Install target `python` version and create a virtual environment.

    ```
    pyenv install 3.10.6
    pyenv virtualenv 3.10.6 flppy-game-env
    pyenv activate flappy-game-env
    ```

4. Install requirements.

    `pip3 install -r requirements.txt`

5. You are ready to run Flappy game!

## License

Copyright (C) 2023  Cristina Bolaños Peño \<cristinabope@gmail.com\>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.