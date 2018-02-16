# -*- coding: utf-8 -*-
from __future__ import division

#
# * Copyright (c) 2009-2015. Authors: see NOTICE file.
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
# */


__author__ = "Stévens Benjamin <b.stevens@ulg.ac.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@ulg.ac.be>", "Rollus Loïc <lrollus@ulg.ac.be"]
__copyright__ = "Copyright 2010-2015 University of Liège, Belgium, http://www.cytomine.be/"
__version__ = '0.1'

import random
import math
import numpy
import threading
import copy

import Queue
from PIL import Image
from StringIO import StringIO


class Reader(object):
    def __init__(self):
        return

    def rgb2bgr(self, image):
        # RGB -> BGR
        sub = image.convert("RGB")
        data = numpy.array(sub)
        red, green, blue = data.T
        data = numpy.array([blue, green, red])
        data = data.transpose()
        image = Image.fromarray(data)
        return image

    def read(self, async=False):
        raise NotImplementedError("Should have implemented this")

    def left(self):
        raise NotImplementedError("Should have implemented this")

    def right(self):
        raise NotImplementedError("Should have implemented this")

    def up(self):
        raise NotImplementedError("Should have implemented this")

    def down(self):
        raise NotImplementedError("Should have implemented this")

    def next(self):
        raise NotImplementedError("Should have implemented this")

    def previous(self):
        raise NotImplementedError("Should have implemented this")

    def inc_zoom(self):
        raise NotImplementedError("Should have implemented this")

    def dec_zoom(self):
        raise NotImplementedError("Should have implemented this")


class OpenSlideReader(Reader):
    def __init__(self, position):
        super(Reader, self).__init__()
        self.position = position


def _paste_image(cytomine, url):
    resp, content = cytomine.fetch_url(url)
    return resp, content


class ThreadUrl(threading.Thread):
    def __init__(self, queue, out_queue, cytomine, terminate_event, verbose=True):
        threading.Thread.__init__(self)
        self.verbose = verbose
        self.queue = queue
        self.out_queue = out_queue
        self.cytomine = copy.deepcopy(cytomine)
        self.terminate_event = terminate_event

    def run(self):
        while (not self.terminate_event.is_set()):
            # grabs host from queue
            try:
                url, box = self.queue.get_nowait()
            except Queue.Empty:
                continue

            # grabs urls of hosts and prints first 1024 bytes of page
            resp, content = self.cytomine.fetch_url(url)

            short_url = url[len(url) - 10:len(url)]
            if (resp['status'] == "200") or (resp['status'] == "304") and (resp['content-type'] == "image/jpeg"):
                try:
                    image_tile = Image.open(StringIO(content))
                    self.out_queue.put((image_tile, box))
                    if self.verbose: print("%s Fetched and pasted : %s " % (resp['status'], short_url))
                except IOError:
                    print("IOError for %s" % short_url)

            else:
                if self.verbose:
                    print("Error while requesting %s " % short_url)
                    print("Response %s " % resp)

            # signals to queue job is done
            self.queue.task_done()


class Bounds(object):

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __str__(self):
        return "Bounds : %d, %d, %d, %d" % (self.x, self.y, self.width, self.height)


class CytomineReader(Reader):

    def __init__(self, cytomine, whole_slide, window_position=Bounds(0, 0, 1024, 1024), overlap=0, zoom=0):
        print("Reader construct")
        super(Reader, self).__init__()
        self.window_position = window_position
        self.zoom = zoom
        self.cytomine = cytomine
        self.image = whole_slide
        self.overlap = overlap
        self.threads = []
        self.data = None
        self.queue = None
        self.terminate_event = None

    def findTileGroup(self, zoom, col, row):
        num_tile = 0
        for i in range(self.image.depth - zoom, self.image.depth):
            num_tile += self.image.levels[i]['level_num_tiles']

        num_tile += col + row * self.image.levels[zoom]['x_tiles']

        tileGroup = num_tile / self.image.tile_size

        return tileGroup

    def read(self, async=False):

        # assert(self.window_position.x % self.image.tile_size == 0)
        # assert(self.window_position.y % self.image.tile_size == 0)

        # prevent reading outside of image and change window position accordingly
        if (self.window_position.x + self.window_position.width) > self.image.levels[self.zoom]['level_width']:
            self.window_position.x = self.image.levels[self.zoom]['level_width'] - self.window_position.width
        if (self.window_position.y + self.window_position.height) > self.image.levels[self.zoom]['level_height']:
            self.window_position.y = self.image.levels[self.zoom]['level_height'] - self.window_position.height

        row0 = int(math.floor(self.window_position.y / self.image.tile_size))
        col0 = int(math.floor(self.window_position.x / self.image.tile_size))
        row1 = int(math.floor(min(self.image.levels[self.zoom]['level_height'],
                                  (self.window_position.y + self.window_position.height) / self.image.tile_size)))
        col1 = int(math.floor(min(self.image.levels[self.zoom]['level_width'],
                                  (self.window_position.x + self.window_position.width) / self.image.tile_size)))
        cols = col1 - col0 + 1
        rows = row1 - row0 + 1

        self.data = Image.new('RGB', (self.window_position.width, self.window_position.height), 'white')

        if self.queue:
            with self.queue.mutex:
                self.queue.queue.clear()
            with self.out_queue.mutex:
                self.out_queue.queue.clear()
        else:
            self.queue = Queue.Queue()
            self.out_queue = Queue.Queue()

        if not self.terminate_event:
            self.terminate_event = threading.Event()

        print(rows)
        print(cols)

        # spawn a pool of threads, and pass them queue instance
        for i in range(8):
            t = ThreadUrl(self.queue, self.out_queue, self.cytomine, self.terminate_event)
            self.threads.append(t)
            t.setDaemon(True)
            t.start()

        for r in range(rows):
            for c in range(cols):
                row = row0 + r
                col = col0 + c

                tile_group = self.findTileGroup(self.zoom, col, row)
                base_url = self.image.server_urls[random.randint(0, len(self.image.server_urls) - 1)]
                # url = "%sTileGroup%d/%d-%d-%d.jpg" % (base_url, tile_group, self.image.depth - self.zoom, col, row)
                url = "%s&tileGroup=%d&z=%d&x=%d&y=%d&mimeType=%s" % (base_url, tile_group,
                                                                      self.image.depth - self.zoom, col, row,
                                                                      self.image.mime)
                url = url.replace(" ", "%20")
                x_paste = int((col * self.image.tile_size) - self.window_position.x)
                y_paste = int((row * self.image.tile_size) - self.window_position.y)
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

        # print "done"

    def result(self):
        return self.rgb2bgr(self.data)

    def read_window(self):
        window = copy.copy(self.window_position)
        window.width = window.width * pow(2, self.zoom)
        window.height = window.height * pow(2, self.zoom)
        window.x = window.x * pow(2, self.zoom)
        window.y = window.y * pow(2, self.zoom)
        url = "%s%s%s%s?zoom=%d" % (self.cytomine._protocol, self.cytomine._host, self.cytomine._base_path,
                                    self.image.getCropURL(window), self.zoom)
        resp, content = self.cytomine.fetch_image(url)
        image = Image.open(StringIO(content))
        return self.rgb2bgr(image)

    def left(self):
        previous_x = self.window_position.x
        self.window_position.x = max(0, self.window_position.x - (self.window_position.width - self.overlap))
        return previous_x != self.window_position.x

    def right(self):
        # print "overlap = %f" % self.overlap
        # print "oldx = %d" % self.window_position.x

        if self.window_position.x >= (self.image.levels[self.zoom]['level_width'] - self.window_position.width):
            return False
        else:
            new_x = self.window_position.x + (self.window_position.width - self.overlap)
            if new_x > (self.image.levels[self.zoom]['level_width'] - self.window_position.width):
                new_x = self.image.levels[self.zoom]['level_width'] - self.window_position.width

            self.window_position.x = new_x
            print("newx = %d" % self.window_position.x)
            return True

    def up(self):
        previous_y = self.window_position.y
        self.window_position.y = max(0, self.window_position.y - (self.window_position.height - self.overlap))
        return previous_y != self.window_position.y

    def down(self):
        if self.window_position.y >= (self.image.levels[self.zoom]['level_height'] - self.window_position.height):
            return False
        else:
            new_y = self.window_position.y + (self.window_position.height - self.overlap)
            if new_y > (self.image.levels[self.zoom]['level_height'] - self.window_position.height):
                new_y = self.image.levels[self.zoom]['level_height'] - self.window_position.height

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

    def inc_zoom(self):
        previous_zoom = self.zoom
        self.zoom = max(0, self.zoom - 1)
        if previous_zoom != self.zoom:
            zoom_factor = pow(2, abs(previous_zoom - self.zoom))
            self.translate_to_zoom(zoom_factor)
        return previous_zoom != self.zoom

    def dec_zoom(self):
        previous_zoom = self.zoom
        self.zoom = min(self.image.depth, self.zoom + 1)
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
        self.window_position.x = int(max(0, new_x_middle - half_width) / self.image.tile_size) * self.image.tile_size
        self.window_position.y = int(max(0, new_y_middle - half_height) / self.image.tile_size) * self.image.tile_size
