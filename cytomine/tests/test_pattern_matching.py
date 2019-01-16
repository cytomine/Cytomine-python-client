from collections import namedtuple

from cytomine.models._utilities.pattern_matching import resolve_pattern


class TestPatternMatching:
    def get_fake_type(self):
        return namedtuple("fakeobj", ["lst", "atomstr", "atomfloat"])

    def test_no_iterable_pattern(self):
        fake = self.get_fake_type()(lst=1, atomstr="aa", atomfloat=1.5)
        resolved = sorted(resolve_pattern("{lst}/{atomstr}_{atomfloat}.png", fake))
        assert(len(resolved) == 1)
        assert(resolved[0] == "1/aa_1.5.png")

    def test_single_iterable_pattern(self):
        fake = self.get_fake_type()(lst=[1, 2, 3], atomstr="aa", atomfloat=1.5)
        resolved = sorted(resolve_pattern("{lst}/{atomstr}_{atomfloat}.png", fake))
        assert(len(resolved) == 3)
        assert(resolved[0] == "1/aa_1.5.png")
        assert(resolved[1] == "2/aa_1.5.png")
        assert(resolved[2] == "3/aa_1.5.png")

    def test_no_placeholder(self):
        fake = self.get_fake_type()(lst=[1, 2, 3], atomstr="aa", atomfloat=1.5)
        resolved = resolve_pattern("no_placeholder", fake)
        assert(len(resolved) == 1)
