from fabweave.api import health, demo_snapshot
from fabweave.dispatch.priority import dispatch_score
from fabweave.yielding.rollup import geometric_yield
from fabweave.reticle.reservation import can_reserve
from fabweave.spc.control import western_electric_signal
from fabweave.lot.merge import mergeable

def test_health(): assert health()["status"] == "ok"
def test_demo(): assert demo_snapshot()["service"] == "fabweave"
def test_dispatch(): assert dispatch_score(10, 5, 1, .2) > dispatch_score(20, 5, 1, .2)
def test_yield(): assert round(geometric_yield([.9,.8]), 3) == .72
def test_reticle_touching_ok(): assert can_reserve(10,20,[(0,10),(20,30)])
def test_spc_three_sigma(): assert western_electric_signal([0,0,4],0,1)
def test_merge(): assert mergeable({"product":"A","route":"R","step":"S","recipe_rev":1,"hold":0},{"product":"A","route":"R","step":"S","recipe_rev":1,"hold":0})
