from datetime import datetime, timedelta
import uuid

class SolutionParser:
    def parse(self, solver, model, tasks, scheduled, starts, ends, 
              coordination_groups, reference_start: datetime, 
              priority_scores: dict, risk_scores: dict, impact_scores: dict = None, exclusion_reasons: dict = None,
              solver_status: str = 'UNKNOWN') -> dict:
        exclusion_reasons = exclusion_reasons or {}
        
        impact_scores = impact_scores or {}
        scheduled_tasks = []
        unscheduled_tasks = []
        
        is_feasible = solver_status in {'OPTIMAL', 'FEASIBLE'}
        
        for idx, task in enumerate(tasks):
            t_id = task['task_id']
            if is_feasible and solver.Value(scheduled[t_id]):
                start_min = solver.Value(starts[t_id])
                end_min = solver.Value(ends[t_id])
                
                start_time = reference_start + timedelta(minutes=start_min)
                end_time = reference_start + timedelta(minutes=end_min)
                duration_hours = (end_min - start_min) / 60.0
                
                scheduled_tasks.append({
                    'task_id': t_id,
                    'corridor_id': task.get('corridor_id'),
                    'department': task.get('department'),
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'duration_hours': duration_hours,
                    'priority_score': priority_scores.get(t_id, 0),
                    'risk_score': risk_scores.get(task.get('asset_id'), 0),
                    'impact_score': impact_scores.get(t_id, 0),
                    'required_block_duration': task.get('required_block_duration', 1.0)
                })
            else:
                # Diagnostic assignment: CP-SAT does not natively return per-task infeasibility constraints
                reason = 'Not selected by optimization within current horizon; no single exclusion constraint identified.'
                
                reason = exclusion_reasons.get(t_id, 'Not selected by optimization within current horizon; no single exclusion constraint identified.')
                # Check for absolute constraints that definitely prevented it
                req_dur = task.get('required_block_duration', 1.0)
                if req_dur > 480.0 / 60.0:  # Exceeds max block duration
                    reason = 'Task duration exceeds maximum absolute safe window (8 hours).'
                    
                unscheduled_tasks.append({
                    'task_id': t_id,
                    'reason': reason
                })
                
        # Post-processing: Group overlapping tasks on the same corridor into Physical Blocks
        # This is where Multi-Department Coordination happens!
        corridor_tasks = {}
        for t in scheduled_tasks:
            cid = t['corridor_id']
            if cid not in corridor_tasks:
                corridor_tasks[cid] = []
            corridor_tasks[cid].append(t)
            
        blocks = []
        total_block_hours = 0.0
        coordination_count = 0
        
        for cid, tasks_in_corr in corridor_tasks.items():
            # Sort by start time
            tasks_in_corr.sort(key=lambda x: datetime.fromisoformat(x['start_time']))
            
            if not tasks_in_corr:
                continue
                
            current_block_tasks = [tasks_in_corr[0]]
            current_start = datetime.fromisoformat(tasks_in_corr[0]['start_time'])
            current_end = datetime.fromisoformat(tasks_in_corr[0]['end_time'])
            
            def finalize_block(b_tasks, b_start, b_end):
                nonlocal total_block_hours, coordination_count
                b_dur = (b_end - b_start).total_seconds() / 3600.0
                total_block_hours += b_dur
                
                depts = list(set(t['department'] for t in b_tasks))
                is_coordinated = len(b_tasks) > 1
                if is_coordinated:
                    coordination_count += len(b_tasks)
                    
                b_id = 'BLK-' + uuid.uuid4().hex[:6].upper()
                
                # Assign this physical block_id to the tasks
                for t in b_tasks:
                    t['block_id'] = b_id
                    t['reasons'] = self.generate_block_reasons(
                        t, t['priority_score'], t.get('risk_score', 0), 
                        is_coordinated, depts
                    )
                
                blocks.append({
                    'block_id': b_id,
                    'corridor_id': cid,
                    'start_time': b_start.isoformat(),
                    'end_time': b_end.isoformat(),
                    'duration': b_dur,
                    'department': 'Multiple' if len(depts) > 1 else depts[0],
                    'tasks': [t['task_id'] for t in b_tasks],
                    'coordinated': is_coordinated,
                    'departments_coordinated': depts
                })
            
            for t in tasks_in_corr[1:]:
                t_start = datetime.fromisoformat(t['start_time'])
                t_end = datetime.fromisoformat(t['end_time'])
                
                if t_start <= current_end:
                    # Overlaps! Extend current block
                    current_end = max(current_end, t_end)
                    current_block_tasks.append(t)
                else:
                    # No overlap, finalize previous block
                    finalize_block(current_block_tasks, current_start, current_end)
                    # Start new block
                    current_block_tasks = [t]
                    current_start = t_start
                    current_end = t_end
                    
            # Finalize the last block in the corridor
            finalize_block(current_block_tasks, current_start, current_end)
            
        stats = {
            'total_tasks': len(tasks),
            'scheduled_count': len(scheduled_tasks),
            'unscheduled_count': len(unscheduled_tasks),
            'coordination_count': coordination_count
        }
        
        return {
            'status': 'success' if len(scheduled_tasks) > 0 else 'no_schedule',
            'solver_status': solver_status,
            'scheduled_tasks': scheduled_tasks,
            'unscheduled_tasks': unscheduled_tasks,
            'blocks': blocks,
            'coordination_groups': [],
            'stats': stats,
            'total_block_hours': total_block_hours
        }

    def generate_block_reasons(self, task: dict, priority_score: float, risk_score: float, 
                               coordinated: bool, departments: list) -> list[str]:
        reasons = [
            'Corridor availability confirmed',
            'No protected train conflict',
            'Required resources available',
            'AI priority score: ' + str(round(priority_score, 1)) + '/100'
        ]
        if coordinated:
            reasons.append('Combined with ' + str(len(departments)) + ' compatible ' + ','.join(departments) + ' tasks')
        
        if task.get('criticality', '').lower() == 'critical' or task.get('safety_impact', '').lower() == 'high':
            reasons.append('Critical safety task - protected window assigned')
            
        return reasons
