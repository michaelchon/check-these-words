import unittest
from ddt import ddt, data
from input_manager import InputManager


@ddt
class TestInputManager(unittest.TestCase):
    def setUp(self) -> None:
        self.prompt = 'prompt'
        self.error_message = 'error message'
        self.conversion = int
        self.input_manager = InputManager(self.prompt, self.error_message, self.conversion)

    def test_init(self):
        self.assertEqual(self.input_manager.prompt, self.prompt)
        self.assertEqual(self.input_manager.error_message, self.error_message)
        self.assertEqual(self.input_manager.conversion, self.conversion)

    @data([None, 'error message', int], ['prompt', None, int], ['prompt', 'error message', None])
    def test_init_passing_argument_with_wrong_type(self, params):
        prompt, error_message, conversion = params

        self.assertRaises(TypeError, InputManager(prompt, error_message, conversion))


if __name__ == '__main__':
    unittest.main()
