from datetime import datetime
from app.optimizer.constraints import _train_runs_on_day

def test_train_runs_on_day():
    # 2026-09-07 is a Monday (0)
    ref = datetime(2026, 9, 7)
    
    # Monday day_index=0
    assert _train_runs_on_day('weekdays', 0, ref) is True
    assert _train_runs_on_day('weekends', 0, ref) is False
    assert _train_runs_on_day('monday', 0, ref) is True
    assert _train_runs_on_day('tuesday', 0, ref) is False
    
    # Saturday day_index=5
    assert _train_runs_on_day('weekdays', 5, ref) is False
    assert _train_runs_on_day('weekends', 5, ref) is True
    assert _train_runs_on_day('saturday', 5, ref) is True
    assert _train_runs_on_day('monday', 5, ref) is False
    
    # Unknown -> default True
    assert _train_runs_on_day('some_unknown_frequency', 0, ref) is True
