"""Module for testing the adjust model"""
from pathlib import Path

from rtctools_simulation.reservoir.model import ModelConfig, ReservoirModel

maxq_dir = Path(__file__).parent.resolve() / "maxq"


class MaxQModel(ReservoirModel):
    """Class for simulating a model with an adjust scheme."""

    def apply_schemes(self):
        """Always adjust volume H to H_observed."""

        if self.get_time_step() > 0:
            maxq = self.find_maxq("Case3")
            print(maxq)


def test_maxq():
    """Test the adjust model. Test for both volume to be correct"""
    config = ModelConfig(base_dir=maxq_dir)
    model = MaxQModel(config)
    model.simulate()
    # results = model.extract_results()
    # h_ref = np.array([5, 4, 3, 3])
    # q_out_ref = np.array([0, 3, 3, 0])
    # assert_array_almost_equal(results["Q_out"], q_out_ref)
    # assert_array_almost_equal(results["H"], h_ref)
