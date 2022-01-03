# GNU Make file for the automation of pytest for date2name.
#
# While the test script is written for Python 3.9.2, you might need to
# adjust the following instruction once in case your OS includes pytest
# for legacy Python 2 side by side to Python 3, or only hosts pytest
# for Python 3.  The tests in script test_date2name.py are set up to
# work with pytest for Python 3; dependent on your installation, which
# may be named pytest-3, or (again) pytest.
#
# Put this file like test_date2name.py in the root folder of date2name
# fetched from PyPi or GitHub.  Then run
#
# chmod +x *
# make ./Makefile
#
# to run the tests.  If you want pytest to exit the test sequence
# right after the first test failing, use the -x flag to the
# instructions on the CLI in addition to the verbosity flag to (-v).

# pytest -v test_date2name.py     # only pytest for Python 3 is present
pytest-3 -v test_date2name.py   # pytest if Python 2 and Python 3 coexist
