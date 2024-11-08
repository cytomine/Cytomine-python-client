# -*- coding: utf-8 -*-

# * Copyright (c) 2009-2024. Authors: see NOTICE file.
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

from collections import namedtuple

from cytomine.models._utilities.pattern_matching import resolve_pattern


class TestPatternMatching:
    def get_fake_type(self):
        return namedtuple("fakeobj", ["lst", "atomstr", "atomfloat"])

    def test_no_iterable_pattern(self):
        fake = self.get_fake_type()(lst=1, atomstr="aa", atomfloat=1.5)
        resolved = sorted(resolve_pattern("{lst}/{atomstr}_{atomfloat}.png", fake))

        assert len(resolved) == 1
        assert resolved[0] == "1/aa_1.5.png"

    def test_single_iterable_pattern(self):
        fake = self.get_fake_type()(lst=[1, 2, 3], atomstr="aa", atomfloat=1.5)
        resolved = sorted(resolve_pattern("{lst}/{atomstr}_{atomfloat}.png", fake))

        assert len(resolved) == 3
        assert resolved[0] == "1/aa_1.5.png"
        assert resolved[1] == "2/aa_1.5.png"
        assert resolved[2] == "3/aa_1.5.png"

    def test_no_placeholder(self):
        fake = self.get_fake_type()(lst=[1, 2, 3], atomstr="aa", atomfloat=1.5)
        resolved = resolve_pattern("no_placeholder", fake)

        assert len(resolved) == 1
