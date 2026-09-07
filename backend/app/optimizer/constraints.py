from ortools.sat.python import cp_model
import json
from datetime import datetime, timedelta
import datetime

def add_duration_constraints(model: cp_model.CpModel, tasks: list, starts: dict, ends: dict, durations: dict, scheduled: dict):
    """Constraint 1: end - start >= required_block_duration (in minutes, integer-scaled)."""
    for task in tasks:
        t_id = task['task_id']
        model.Add(ends[t_id] - starts[t_id] == durations[t_id]).OnlyEnforceIf(scheduled[t_id])

def add_corridor_availability_constraints(model, tasks, starts, ends, scheduled, corridors: dict, horizon_minutes: int):
    """Constraint 2: Tasks only within corridor availability windows."""
    horizon_days = horizon_minutes // 1440
    for task in tasks:
        t_id = task['task_id']
        c_id = task.get('corridor_id')
        if not c_id or c_id not in corridors:
            continue
        corr = corridors[c_id]
        windows_str = corr.get('availability_windows', '[]')
        if not windows_str:
            continue
            
        try:
            windows = json.loads(windows_str)
        except:
            windows = []
            
        if not windows:
            continue
            
        window_bools = []
        for i, w in enumerate(windows):
            base_start = w.get('start_hour', 0) * 60
            base_end = w.get('end_hour', 24) * 60
            if base_end < base_start:
                base_end += 1440
                
            day_spec = str(w.get('day', '0-6'))
            if '-' in day_spec:
                parts = day_spec.split('-')
                day_range = range(int(parts[0]), int(parts[1]) + 1)
            else:
                day_range = [int(day_spec)]
                
            for d in day_range:
                if d >= horizon_days:
                    continue
                w_start = d * 1440 + base_start
                w_end = d * 1440 + base_end
                
                w_bool = model.NewBoolVar(f'window_{t_id}_{i}_d{d}')
                window_bools.append(w_bool)
                
                model.Add(starts[t_id] >= w_start).OnlyEnforceIf(w_bool)
                model.Add(ends[t_id] <= w_end).OnlyEnforceIf(w_bool)
            
        if window_bools:
            model.Add(sum(window_bools) == 1).OnlyEnforceIf(scheduled[t_id])
            model.Add(sum(window_bools) == 0).OnlyEnforceIf(scheduled[t_id].Not())

def _train_runs_on_day(frequency: str, day_index: int, reference_start: datetime) -> bool:
    if not frequency:
        return True
    freq = frequency.lower()
    if freq == 'daily':
        return True
    
    target_date = reference_start.date() + timedelta(days=day_index)
    wd = target_date.weekday() # 0 = Monday, 6 = Sunday
    
    if freq == 'weekdays':
        return wd < 5
    if freq == 'weekends':
        return wd >= 5
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    if freq in days:
        return wd == days.index(freq)
        
    return True # unknown frequency string -> fail safe to "runs every day"

def add_train_conflict_constraints(model, tasks, starts, ends, scheduled, trains: list, horizon_minutes: int, reference_start: datetime):
    """Constraint 3: No overlap with high-priority train movements."""
    horizon_days = horizon_minutes // 1440
    critical_trains = []
    for tr in trains:
        if tr.get('priority') in ['High', 'Critical']:
            arr = tr.get('arrival_time', '00:00')
            dep = tr.get('departure_time', '23:59')
            try:
                h_a, m_a = map(int, arr.split(':')[:2])
                h_d, m_d = map(int, dep.split(':')[:2])
                arr_m = h_a * 60 + m_a
                dep_m = h_d * 60 + m_d
            except:
                continue
            if dep_m < arr_m:
                dep_m += 1440
            
            freq = tr.get('frequency', 'Daily')
            for d in range(horizon_days):
                if _train_runs_on_day(freq, d, reference_start):
                    critical_trains.append({
                        'train_id': f"{tr.get('train_id')}_d{d}",
                        'corridor_id': tr.get('corridor_id'),
                        'start': d * 1440 + arr_m,
                        'end': d * 1440 + dep_m
                    })
            
    for task in tasks:
        t_id = task['task_id']
        c_id = task.get('corridor_id')
        if not c_id:
            continue
        for tr in critical_trains:
            if tr['corridor_id'] == c_id:
                t_id_safe = str(t_id).replace('-', '_')
                tr_id_safe = str(tr['train_id']).replace('-', '_')
                left_bool = model.NewBoolVar(f"train_left_{t_id_safe}_{tr_id_safe}")
                right_bool = model.NewBoolVar(f"train_right_{t_id_safe}_{tr_id_safe}")
                
                model.Add(ends[t_id] <= tr['start']).OnlyEnforceIf(left_bool)
                model.Add(starts[t_id] >= tr['end']).OnlyEnforceIf(right_bool)
                
                model.AddBoolOr([left_bool, right_bool]).OnlyEnforceIf(scheduled[t_id])

def add_resource_conflict_constraints(model, tasks, starts, ends, intervals: dict, scheduled, resources: dict):
    """Constraint 4: Resources cannot be double-booked."""
    resource_tasks = {}
    for task in tasks:
        req_res = task.get('required_resources')
        if req_res:
            res_list = req_res.split(',')
            for r in res_list:
                r = r.strip()
                if r not in resource_tasks:
                    resource_tasks[r] = []
                t_id = task['task_id']
                if t_id in intervals:
                    resource_tasks[r].append(intervals[t_id])
                    
    for r, inters in resource_tasks.items():
        if len(inters) > 1:
            model.AddNoOverlap(inters)

def add_corridor_conflict_constraints(model, tasks, starts, ends, intervals: dict, scheduled):
    """Constraint 5: No overlapping blocks on same corridor."""
    corridor_tasks = {}
    for task in tasks:
        c_id = task.get('corridor_id')
        if c_id:
            if c_id not in corridor_tasks:
                corridor_tasks[c_id] = []
            t_id = task['task_id']
            if t_id in intervals:
                corridor_tasks[c_id].append(intervals[t_id])
                
    for c_id, inters in corridor_tasks.items():
        if len(inters) > 1:
            model.AddNoOverlap(inters)

def add_dependency_constraints(model, tasks, starts, ends, scheduled):
    """Constraint 6: Dependent tasks respect ordering."""
    task_map = {t['task_id']: t for t in tasks}
    for task in tasks:
        t_id = task['task_id']
        dep_id = task.get('dependency_task_id')
        if dep_id and dep_id in task_map:
            both_scheduled = model.NewBoolVar(f'both_{t_id}_{dep_id}')
            model.AddBoolAnd([scheduled[t_id], scheduled[dep_id]]).OnlyEnforceIf(both_scheduled)
            model.Add(starts[t_id] >= ends[dep_id]).OnlyEnforceIf(both_scheduled)

def add_department_compatibility_constraints(model, tasks, resources: dict, resource_assignments: dict, scheduled):
    """Constraint 7: Resources must match department/capability."""
    for task in tasks:
        t_id = task['task_id']
        req_res = task.get('required_resources')
        dept = task.get('department')
        
        if req_res:
            res_list = [r.strip() for r in req_res.split(',')]
            for req in res_list:
                found = False
                for r_id, res in resources.items():
                    r_dept = res.get('department')
                    r_cap = res.get('capability')
                    r_name = res.get('name')
                    r_type = res.get('resource_type')
                    if r_dept == dept or r_cap == req or r_name == req or r_type == req:
                        found = True
                        break
                if not found:
                    model.Add(scheduled[t_id] == 0)
                    break

def add_safety_constraints(model, tasks, starts, ends, scheduled, trains: list, horizon_minutes: int, reference_start: datetime):
    """Constraint 8: Critical safety tasks get adequate protected windows."""
    horizon_days = horizon_minutes // 1440
    all_trains = []
    for tr in trains:
        arr = tr.get('arrival_time', '00:00')
        dep = tr.get('departure_time', '23:59')
        try:
            h_a, m_a = map(int, arr.split(':')[:2])
            h_d, m_d = map(int, dep.split(':')[:2])
            arr_m = h_a * 60 + m_a
            dep_m = h_d * 60 + m_d
        except:
            continue
        if dep_m < arr_m:
            dep_m += 1440
        
        freq = tr.get('frequency', 'Daily')
        for d in range(horizon_days):
            if _train_runs_on_day(freq, d, reference_start):
                all_trains.append({
                    'train_id': f"{tr.get('train_id')}_d{d}",
                    'corridor_id': tr.get('corridor_id'),
                    'start': d * 1440 + arr_m,
                    'end': d * 1440 + dep_m
                })
        
    for task in tasks:
        if task.get('safety_impact') == 'High':
            t_id = task['task_id']
            c_id = task.get('corridor_id')
            if not c_id:
                continue
            for tr in all_trains:
                if tr['corridor_id'] == c_id:
                    t_id_safe = str(t_id).replace('-', '_')
                    tr_id_safe = str(tr['train_id']).replace('-', '_')
                    left_bool = model.NewBoolVar(f"safety_left_{t_id_safe}_{tr_id_safe}")
                    right_bool = model.NewBoolVar(f"safety_right_{t_id_safe}_{tr_id_safe}")
                    
                    model.Add(ends[t_id] <= tr['start']).OnlyEnforceIf(left_bool)
                    model.Add(starts[t_id] >= tr['end']).OnlyEnforceIf(right_bool)
                    
                    model.AddBoolOr([left_bool, right_bool]).OnlyEnforceIf(scheduled[t_id])

def add_max_block_duration_constraints(model, tasks, starts, ends, scheduled, max_duration_minutes: int = 480):
    """Constraint 9: No block exceeds 8 hours (480 min) by default."""
    for task in tasks:
        t_id = task['task_id']
        model.Add(ends[t_id] - starts[t_id] <= max_duration_minutes).OnlyEnforceIf(scheduled[t_id])

def _parse_time_to_minutes(time_val):
    if not time_val: return 0
    if isinstance(time_val, datetime.datetime):
        return time_val.hour * 60 + time_val.minute
    s = str(time_val)
    try:
        if 'T' in s:
            time_part = s.split('T')[1]
        elif ' ' in s:
            time_part = s.split(' ')[1]
        else:
            time_part = s
        parts = time_part.split(':')
        if len(parts) >= 2:
            return int(parts[0]) * 60 + int(parts[1])
    except:
        pass
    return 0

def add_existing_block_constraints(model, tasks, starts, ends, intervals: dict, scheduled, existing_blocks: list):
    """Constraint 10: Cannot overlap with existing approved blocks."""
    parsed_blocks = []
    for eb in existing_blocks:
        st_m = _parse_time_to_minutes(eb.get('start_time'))
        en_m = _parse_time_to_minutes(eb.get('end_time'))
        if en_m < st_m:
            en_m += 1440
            
        parsed_blocks.append({
            'block_id': eb.get('block_id', 'unknown'),
            'corridor_id': eb.get('corridor_id'),
            'start': st_m,
            'end': en_m
        })
            
    for task in tasks:
        t_id = task['task_id']
        c_id = task.get('corridor_id')
        if not c_id:
            continue
        for i, b in enumerate(parsed_blocks):
            if b['corridor_id'] == c_id:
                t_id_safe = str(t_id).replace('-', '_')
                b_id_safe = str(b['block_id']).replace('-', '_')
                left_bool = model.NewBoolVar(f"eblock_left_{t_id_safe}_{b_id_safe}_{i}")
                right_bool = model.NewBoolVar(f"eblock_right_{t_id_safe}_{b_id_safe}_{i}")
                
                model.Add(ends[t_id] <= b['start']).OnlyEnforceIf(left_bool)
                model.Add(starts[t_id] >= b['end']).OnlyEnforceIf(right_bool)
                
                model.AddBoolOr([left_bool, right_bool]).OnlyEnforceIf(scheduled[t_id])
