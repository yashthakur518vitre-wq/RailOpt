from ortools.sat.python import cp_model

class ObjectiveWeights:
    """Configurable weights for multi-objective optimization."""
    PRIORITY_SATISFACTION = 100      # Weight for scheduling high-priority tasks
    CRITICAL_TASK_COMPLETION = 200   # Weight for completing critical tasks
    COORDINATION_BONUS = 80          # Weight for multi-department coordination
    TRAIN_IMPACT_PENALTY = -60       # Penalty for train disruption
    LATENESS_PENALTY = -40           # Penalty for overdue tasks remaining unscheduled

def build_objective(model: cp_model.CpModel, tasks: list, scheduled: dict, starts: dict, ends: dict, 
                    priority_scores: dict, risk_scores: dict, impact_scores: dict,
                    coordination_vars: dict, weights: ObjectiveWeights = None) -> None:
    """Build the multi-objective function for CP-SAT."""
    if weights is None:
        weights = ObjectiveWeights()
        
    objective_terms = []
    
    for task in tasks:
        t_id = task['task_id']
        is_sched = scheduled[t_id]
        
        # Maximize scheduling of high-priority tasks
        p_val = priority_scores.get(t_id)
        p_val = p_val if p_val is not None else 0.0
        p_score = int(p_val * 10)
        objective_terms.append(is_sched * p_score * weights.PRIORITY_SATISFACTION)
        
        # Maximize critical task completion
        crit_val = task.get('criticality')
        is_critical = 1 if (crit_val or '').lower() == 'critical' else 0
        objective_terms.append(is_sched * is_critical * weights.CRITICAL_TASK_COMPLETION)
        
        # Minimize train impact penalty
        i_val = impact_scores.get(t_id)
        i_val = i_val if i_val is not None else 0.0
        i_score = int(i_val * 10)
        objective_terms.append(is_sched * i_score * weights.TRAIN_IMPACT_PENALTY)
        
        # Minimize lateness for unscheduled (if overdue)
        urg_val = task.get('urgency')
        is_overdue = 1 if (urg_val or '').lower() == 'high' else 0
        not_sched = model.NewBoolVar(f'not_sched_{t_id}')
        model.Add(not_sched == 1 - is_sched)
        objective_terms.append(not_sched * is_overdue * weights.LATENESS_PENALTY)
        
    # Add coordination bonuses
    for coord_id, coord_var in coordination_vars.items():
        objective_terms.append(coord_var * weights.COORDINATION_BONUS)
        
    # Prevent monthly bunching by adding a small penalty for scheduling tasks early.
    # This acts as a temporal balancing force. Non-critical tasks will prefer later dates 
    # to avoid clumping, if they can. 
    for task in tasks:
        t_id = task['task_id']
        is_sched = scheduled[t_id]
        start_var = starts[t_id]
        
        urg_val = task.get('urgency')
        is_urgent = (urg_val or '').lower() == 'high'
        crit_val = task.get('criticality')
        is_critical = (crit_val or '').lower() == 'critical'
        
        # If not critical/urgent, add start_var to objective (Maximize start_var = push later)
        if not is_urgent and not is_critical:
            # Let's create an intermediate variable:
            task_start_if_sched = model.NewIntVar(0, 44000, f'start_if_sched_{t_id}')
            # If is_sched == 1, task_start_if_sched == start_var. If 0, == 0.
            model.Add(task_start_if_sched == start_var).OnlyEnforceIf(is_sched)
            model.Add(task_start_if_sched == 0).OnlyEnforceIf(is_sched.Not())
            
            # Since we maximize, adding task_start_if_sched pushes it later.
            # We use a very small weight (e.g. 1) to just act as a tie-breaker.
            objective_terms.append(task_start_if_sched * 1)
        
    model.Maximize(sum(objective_terms))
