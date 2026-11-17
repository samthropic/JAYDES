import os

from states.load import load_state_coordinates
import states.query as qry


def test_load_state_coordinates_includes_seed_states():
    coords = load_state_coordinates(qry.STATES_CSV)
    assert coords['AL']['latitude'] == 32.318231
    assert coords['AL']['longitude'] == -86.902298
    assert coords['AK']['latitude'] == 63.588753
    assert coords['AZ']['longitude'] == -111.093731


def test_states_csv_path_exists():
    assert os.path.isfile(qry.STATES_CSV)
