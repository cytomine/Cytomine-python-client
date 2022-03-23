# -*- coding: utf-8 -*-

# * Copyright (c) 2009-2022. Authors: see NOTICE file.
# *
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# *
# *      http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = "Stevens Benjamin"
__contributors__ = ["Rubens Ulysse <urubens@uliege.be>", "Marée Raphaël <raphael.maree@uliege.be>"]
__copyright__ = "Copyright 2010-2022 University of Liège, Belgium, http://www.cytomine.be/"

import math
import numpy as np
import threading
import copy
import requests

from io import BytesIO

try:
    import queue as queue
except ImportError:
    import Queue as queue

try:
    import Image
except ImportError:
    from PIL import Image


class ThreadUrl(threading.Thread):
    def __init__(self, queue_, out_queue, terminate_event, verbose=True):
        threading.Thread.__init__(self)
        self.verbose = verbose
        self.queue = queue_
        self.out_queue = out_queue
        self.terminate_event = terminate_event

    def run(self):
        from cytomine import Cytomine
        while not self.terminate_event.is_set():
            try:
                url, box = self.queue.get_nowait()
            except queue.Empty:
                continue

            response = requests.get(url)
            if response.status_code in [200, 304] and response.headers['Content-Type'] == 'image/jpeg':
                try:
                    tile = Image.open(BytesIO(response.content))
                    self.out_queue.put((tile, box))
                    Cytomine.get_instance().logger.info("Reader fetched {}".format(url))
                except IOError as e:
                    Cytomine.get_instance().logger.error(e)
                    print(e)
            else:
                Cytomine.get_instance().logger.error("Bad request: {}".format(url))

            self.queue.task_done()


class Bounds(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __str__(self):
        return "Bounds : {}, {}, {}, {}".format(self.x, self.y, self.width, self.height)


class CytomineReader(object):
    def __init__(self, whole_slide, window_position=Bounds(0, 0, 1024, 1024), overlap=0, zoom=0, rgb2bgr=False):
        self.whole_slide = whole_slide
        self.window_position = window_position
        self.overlap = overlap
        self.zoom = zoom
        self.rgb2bgr = rgb2bgr

        self.threads = []
        self.data = None
        self.queue = None
        self.out_queue = None
        self.terminate_event = None

    def find_tile_group(self, zoom, col, row):
        num_tile = np.sum([self.whole_slide.levels[i]['level_num_tiles']
                           for i in range(self.whole_slide.depth - zoom, self.whole_slide.depth)])
        num_tile += col + row * self.whole_slide.levels[zoom]['x_tiles']
        return int(num_tile / self.whole_slide.tile_size)

    def read(self):
        # prevent reading outside of image and change window position accordingly
        if (self.window_position.x + self.window_position.width) > self.whole_slide.levels[self.zoom]['level_width']:
            self.window_position.x = self.whole_slide.levels[self.zoom]['level_width'] - self.window_position.width

        if (self.window_position.y + self.window_position.height) > self.whole_slide.levels[self.zoom]['level_height']:
            self.window_position.y = self.whole_slide.levels[self.zoom]['level_height'] - self.window_position.height

        row0 = int(math.floor(self.window_position.y / self.whole_slide.tile_size))
        col0 = int(math.floor(self.window_position.x / self.whole_slide.tile_size))
        row1 = int(math.floor(min(self.whole_slide.levels[self.zoom]['level_height'],
                                  (self.window_position.y + self.window_position.height) / self.whole_slide.tile_size)))
        col1 = int(math.floor(min(self.whole_slide.levels[self.zoom]['level_width'],
                                  (self.window_position.x + self.window_position.width) / self.whole_slide.tile_size)))
        cols = col1 - col0 + 1
        rows = row1 - row0 + 1
        mode = 'RGB' if self.whole_slide.image.colorspace == 'RGB' else 'L'
        self.data = Image.new(mode, (self.window_position.width, self.window_position.height), 'white')

        if self.queue:
            with self.queue.mutex:
                self.queue.queue.clear()
            with self.out_queue.mutex:
                self.out_queue.queue.clear()
        else:
            self.queue = queue.Queue()
            self.out_queue = queue.Queue()

        if not self.terminate_event:
            self.terminate_event = threading.Event()

        # spawn a pool of threads, and pass them queue instance
        for i in range(8):
            t = ThreadUrl(self.queue, self.out_queue, self.terminate_event)
            self.threads.append(t)
            t.setDaemon(True)
            t.start()

        for r in range(rows):
            for c in range(cols):
                row = row0 + r
                col = col0 + c
                url = "{}&tileGroup={}&z={}&x={}&y={}&mimeType={}".format(self.whole_slide.random_server_url(),
                                                                          self.find_tile_group(self.zoom, col, row),
                                                                          self.whole_slide.depth - self.zoom,
                                                                          col, row, self.whole_slide.mime)

                x_paste = int((col * self.whole_slide.tile_size) - self.window_position.x)
                y_paste = int((row * self.whole_slide.tile_size) - self.window_position.y)
                self.queue.put((url, (x_paste, y_paste)))
        self.queue.join()

        # terminate pool of threads
        self.terminate_event.set()
        while len(self.threads) > 0:
            self.threads = [t for t in self.threads if t.is_alive()]
        self.terminate_event.clear()

        while not self.out_queue.empty():
            image_tile, box = self.out_queue.get()
            self.data.paste(image_tile, box)

    def result(self):
        if self.rgb2bgr:
            return transform_rgb_to_bgr(self.data)
        return self.data

    def read_window(self):
        from cytomine import Cytomine
        window = copy.copy(self.window_position)
        window.width = window.width * pow(2, self.zoom)
        window.height = window.height * pow(2, self.zoom)
        window.x = window.x * pow(2, self.zoom)
        window.y = window.y * pow(2, self.zoom)

        url = "imageinstance/{}/window-{}-{}-{}-{}.png".format(self.whole_slide.image.id, window.x, window.y,
                                                               window.width, window.height)
        response = Cytomine.get_instance()._get(url, {"zoom": self.zoom})
        if response.status_code in [200, 304] and response.headers['Content-Type'] == 'image/jpeg':
            image = Image.open(BytesIO(response.content))
            return transform_rgb_to_bgr(image) if self.rgb2bgr else image
        else:
            return False

    def left(self):
        previous_x = self.window_position.x
        self.window_position.x = max(0, self.window_position.x - (self.window_position.width - self.overlap))
        return previous_x != self.window_position.x

    def right(self):
        if self.window_position.x >= (self.whole_slide.levels[self.zoom]['level_width'] - self.window_position.width):
            return False
        else:
            new_x = self.window_position.x + (self.window_position.width - self.overlap)
            if new_x > (self.whole_slide.levels[self.zoom]['level_width'] - self.window_position.width):
                new_x = self.whole_slide.levels[self.zoom]['level_width'] - self.window_position.width

            self.window_position.x = new_x
            return True

    def up(self):
        previous_y = self.window_position.y
        self.window_position.y = max(0, self.window_position.y - (self.window_position.height - self.overlap))
        return previous_y != self.window_position.y

    def down(self):
        if self.window_position.y >= (self.whole_slide.levels[self.zoom]['level_height'] - self.window_position.height):
            return False
        else:
            new_y = self.window_position.y + (self.window_position.height - self.overlap)
            if new_y > (self.whole_slide.levels[self.zoom]['level_height'] - self.window_position.height):
                new_y = self.whole_slide.levels[self.zoom]['level_height'] - self.window_position.height

            self.window_position.y = new_y
            return True

    def next(self):
        if self.right():
            return True
        else:
            self.window_position.x = 0
            return self.down()

    def previous(self):
        if self.left():
            return True
        else:
            while self.right():
                continue
            return self.up()

    def increase_zoom(self):
        previous_zoom = self.zoom
        self.zoom = max(0, self.zoom - 1)
        if previous_zoom != self.zoom:
            zoom_factor = pow(2, abs(previous_zoom - self.zoom))
            self.translate_to_zoom(zoom_factor)
        return previous_zoom != self.zoom

    def decrease_zoom(self):
        previous_zoom = self.zoom
        self.zoom = min(self.whole_slide.depth, self.zoom + 1)
        if previous_zoom != self.zoom:
            zoom_factor = pow(2, abs(previous_zoom - self.zoom))
            self.translate_to_zoom(zoom_factor)
        return previous_zoom != self.zoom

    def translate_to_zoom(self, zoom_factor):
        half_width = self.window_position.width / 2
        half_height = self.window_position.height / 2
        x_middle = self.window_position.x + half_width
        y_middle = self.window_position.y + half_height
        new_x_middle = x_middle / zoom_factor
        new_y_middle = y_middle / zoom_factor
        self.window_position.x = int(max(0, new_x_middle - half_width) / self.whole_slide.tile_size) * self.whole_slide.tile_size
        self.window_position.y = int(max(0, new_y_middle - half_height) / self.whole_slide.tile_size) * self.whole_slide.tile_size

    # Deprecated method names. Keep for backwards compatibility.
    inc_zoom = increase_zoom
    dec_zoom = decrease_zoom


def transform_rgb_to_bgr(image):
    sub = image.convert("RGB")
    data = np.array(sub)
    red, green, blue = data.T
    data = np.array([blue, green, red])
    data = data.transpose()
    return Image.fromarray(data)
