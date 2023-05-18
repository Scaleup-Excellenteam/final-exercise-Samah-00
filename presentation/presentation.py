from dataclasses import dataclass
from collections import namedtuple
from typing import Dict

from mySlide import Slide


@dataclass
class Presentation:
    filepath: str
    explanations: namedtuple = None
    slides: Dict[int, Slide] = None

    def __post_init__(self):
        self.slides = {}

    def parse(self):
        pass
