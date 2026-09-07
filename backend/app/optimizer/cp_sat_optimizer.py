import logging
from datetime import datetime, timedelta
from ortools.sat.python import cp_model

from .constraints import (
    add_duration_constraints, add_corridor_availability_constraints,
    add_train_conflict_constraints, add_resource_conflict_constraints,
    add_corridor_conflict_constraints, add_dependency_constraints,
    add_department_compatibility_constraints, add_safety_constraints,
    add_max_block_duration_constraints, add_existing_block_constraints
)
from .objective import build_objective, ObjectiveWeights
from .solution_parser import SolutionParser

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger

class BlockPlanOptimizer:
    def __init__(self, time_limit: int = 30):
        self.time_limit = time_limit
        self.logger = get_logger('optimizer')
    
    def optimize(self, tasks: list[dict], corridors: list[dict], trains: list[dict],
                 resources: list[dict], existing_blocks: list[dict],
                 availability_windows: dict, horizon: str = 'weekly',
                 priority_scores: dict = None, risk_scores: dict = None,
                 impact_scores: dict = None) -> dict:
        
        priority_scores = priority_scores or {}
        risk_scores = risk_scores or {}
        impact_scores = impact_scores or {}
        
        horizon_days = 7 if horizon == 'weekly' else 30
        horizon_minutes = horizon_days * 24 * 60
        
        now = datetime.now()
        # Reference start
        days_ahead = 0 if now.weekday() == 0 else 7 - now.weekday()
        reference_start = (now + timedelta(days=days_ahead)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        model = cp_model.CpModel()
        
        scheduled = {}
        starts = {}
        ends = {}
        intervals = {}
        durations = {}
        
        for task in tasks:
            t_id = task['task_id']
            dur_mins = int(float(task.get('required_block_duration', 1.0)) * 60)
            durations[t_id] = dur_mins
            
            scheduled[t_id] = model.NewBoolVar(f'scheduled_{t_id}')
            starts[t_id] = model.NewIntVar(0, horizon_minutes, f'start_{t_id}')
            ends[t_id] = model.NewIntVar(0, horizon_minutes, f'end_{t_id}')
            intervals[t_id] = model.NewOptionalIntervalVar(
                starts[t_id], dur_mins, ends[t_id], scheduled[t_id], f'interval_{t_id}'
            )
            
        corridors_dict = {c['corridor_id']: c for c in corridors}
        resources_dict = {r['resource_id']: r for r in resources}
        
        add_duration_constraints(model, tasks, starts, ends, durations, scheduled)
        add_corridor_availability_constraints(model, tasks, starts, ends, scheduled, corridors_dict, horizon_minutes)
        add_train_conflict_constraints(model, tasks, starts, ends, scheduled, trains, horizon_minutes, reference_start)
        add_resource_conflict_constraints(model, tasks, starts, ends, intervals, scheduled, resources_dict)
        # add_corridor_conflict_constraints(model, tasks, starts, ends, intervals, scheduled) # REMOVED: Tasks CAN overlap to form shared blocks!
        add_dependency_constraints(model, tasks, starts, ends, scheduled)
        add_department_compatibility_constraints(model, tasks, resources_dict, {}, scheduled)
        add_safety_constraints(model, tasks, starts, ends, scheduled, trains, horizon_minutes, reference_start)
        add_max_block_duration_constraints(model, tasks, starts, ends, scheduled, max_duration_minutes=480)
        add_existing_block_constraints(model, tasks, starts, ends, intervals, scheduled, existing_blocks)
        
        exclusion_reasons = {}
        for t in tasks:
            t_id = t['task_id']
            # Lightweight heuristic to guess the most likely reason for unschedulable tasks
            c_id = t.get('corridor_id')
            c_obj = corridors_dict.get(c_id, {})
            req_dur = t.get('required_block_duration', 1.0)
            deps = t.get('dependencies', [])
            req_res = t.get('required_resources', [])
            
            reasons = []
            if req_dur > 8.0:
                reasons.append('Task duration exceeds maximum absolute safe window (8 hours).')
            if c_obj.get('status') == 'MAINTENANCE':
                reasons.append(f'Corridor {c_id} is already under maintenance.')
            if c_obj.get('status') == 'CLOSED':
                reasons.append(f'Corridor {c_id} is closed.')
            if len(deps) > 0:
                reasons.append('Task dependencies cannot be resolved within horizon.')
            if len(req_res) > 0:
                reasons.append('Missing or conflicting required resource constraint.')
            
            # Additional heuristic: check train conflicts loosely
            if any(tr.get('corridor_id') == c_id for tr in trains if tr.get('train_type') == 'Express'):
                reasons.append('All windows conflict with critical train schedules on this corridor.')
                
            if len(reasons) > 0:
                exclusion_reasons[t_id] = reasons[0]
                
        # Multi-department coordination logic (REAL CP-SAT DECISIONS)
        coordination_vars = {}
        
        # Group candidate tasks by corridor to avoid O(N^2) over entire task space
        corridor_tasks = {}
        for t in tasks:
            c = t.get('corridor_id')
            if c:
                if c not in corridor_tasks:
                    corridor_tasks[c] = []
                corridor_tasks[c].append(t)
                
        # Generate boolean variables for compatible task pairs that could share a mega-block
        for c_id, c_tasks in corridor_tasks.items():
            for i in range(len(c_tasks)):
                for j in range(i + 1, len(c_tasks)):
                    t1 = c_tasks[i]
                    t2 = c_tasks[j]
                    
                    id1 = t1['task_id']
                    id2 = t2['task_id']
                    
                    dept1 = t1.get('department')
                    dept2 = t2.get('department')
                    
                    # SIH REQUIREMENT: Only reward multi-department coordination
                    if dept1 == dept2:
                        continue
                        
                    # SAFETY CHECK: If spatial or asset isolation is incompatible, DO NOT allow coordination.
                    # As a prototype heuristic: we only allow coordination if they explicitly 
                    # do not request the exact same specialized single-use resource 
                    # (which is already handled by add_resource_conflict_constraints).
                    # We will assume tasks on the same corridor CAN safely be bundled into one traffic block.
                    
                    overlap = model.NewBoolVar(f'coord_{id1}_{id2}')
                    
                    # Condition: starts[id1] <= ends[id2] AND starts[id2] <= ends[id1]
                    s1_le_e2 = model.NewBoolVar(f's1_le_e2_{id1}_{id2}')
                    model.Add(starts[id1] <= ends[id2]).OnlyEnforceIf(s1_le_e2)
                    model.Add(starts[id1] > ends[id2]).OnlyEnforceIf(s1_le_e2.Not())
                    
                    s2_le_e1 = model.NewBoolVar(f's2_le_e1_{id1}_{id2}')
                    model.Add(starts[id2] <= ends[id1]).OnlyEnforceIf(s2_le_e1)
                    model.Add(starts[id2] > ends[id1]).OnlyEnforceIf(s2_le_e1.Not())
                    
                    model.AddBoolAnd([scheduled[id1], scheduled[id2], s1_le_e2, s2_le_e1]).OnlyEnforceIf(overlap)
                    model.AddBoolOr([scheduled[id1].Not(), scheduled[id2].Not(), s1_le_e2.Not(), s2_le_e1.Not()]).OnlyEnforceIf(overlap.Not())

                    # A coordinated physical block must remain within the same
                    # 8-hour safety ceiling used by the individual task constraint.
                    min_start = model.NewIntVar(0, horizon_minutes, f"coord_min_start_{id1}_{id2}")
                    max_end = model.NewIntVar(0, horizon_minutes, f"coord_max_end_{id1}_{id2}")
                    model.AddMinEquality(min_start, [starts[id1], starts[id2]])
                    model.AddMaxEquality(max_end, [ends[id1], ends[id2]])
                    model.Add(max_end - min_start <= 480).OnlyEnforceIf(overlap)

                    coordination_vars[f"{id1}_{id2}"] = overlap
        
        build_objective(model, tasks, scheduled, starts, ends, 
                        priority_scores, risk_scores, impact_scores,
                        coordination_vars)
                        
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = self.time_limit
        
        status_enum = solver.Solve(model)
        
        if status_enum == cp_model.OPTIMAL:
            solver_status = 'OPTIMAL'
        elif status_enum == cp_model.FEASIBLE:
            solver_status = 'FEASIBLE'
        elif status_enum == cp_model.INFEASIBLE:
            solver_status = 'INFEASIBLE'
        else:
            solver_status = 'UNKNOWN'
            
        parser = SolutionParser()
        result = parser.parse(solver, model, tasks, scheduled, starts, ends, 
                              coordination_vars, reference_start, 
                              priority_scores, risk_scores, impact_scores, exclusion_reasons,
                              solver_status=solver_status)
        result['solver_status'] = solver_status
        result['objective_value'] = solver.ObjectiveValue() if solver_status in ['OPTIMAL', 'FEASIBLE'] else 0
        
        return result
