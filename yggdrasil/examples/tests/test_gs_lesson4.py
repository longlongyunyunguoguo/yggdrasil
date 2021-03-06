import os
from yggdrasil.examples.tests import TestExample


class TestExampleGS4(TestExample):
    r"""Test the Getting Started Lesson 4 example."""

    example_name = 'gs_lesson4'

    @property
    def input_files(self):
        r"""Input file."""
        return [os.path.join(self.yamldir, 'Input', 'input.txt')]

    @property
    def output_files(self):
        r"""Output file."""
        return [os.path.join(self.yamldir, 'output.txt')]
