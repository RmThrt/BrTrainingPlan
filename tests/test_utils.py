from brytonTrainerPlan.utils import increment_filename_if_necessary


def test_increment_filename():
    assert increment_filename_if_necessary('tests/test_utils.py') == 'tests/test_utils_1.py'
    assert increment_filename_if_necessary('tests/test_utilsksd.py') == 'tests/test_utilsksd.py'
    assert increment_filename_if_necessary('tests/test_utils_1.py') == 'tests/test_utils_2.py'
    assert increment_filename_if_necessary('tests/test_utils_102.py') == 'tests/test_utils_103.py'