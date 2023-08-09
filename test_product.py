import io
import sys
from unittest.mock import patch
from gfx_perps_sdk import Product

def test_print_hello_world():
    expected_output = 'init_by_name\n'  # The print function adds a newline at the end
    #with patch('sys.stdout', new=io.StringIO()) as fake_output:
    #    Product.init_by_name()
    #assert fake_output.getvalue() == expected_output
