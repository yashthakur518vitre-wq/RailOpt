import uuid
import datetime
from typing import List, Dict, Any
import json

class BaselineService:
    @staticmethod
    def generate_baseline(tasks: List[Dict], corridors: List[Dict], availability_windows: Dict, trains: List[Dict]) -> Dict[str, Any]:
        scheduled_tasks = []
        unscheduled_tasks = []
        blocks = []
        total_block_hours = 0.0
        
        # Build lookup dictionaries
        corridors_by_id = {c['corridor_id']: c for c in corridors}
        
        def sort_key(t):
            d = t.get('due_date')
            if isinstance(d, datetime.datetime): dt = d.date()
            elif hasattr(d, 'isoformat'): dt = d
            elif isinstance(d, str): 
                dt = datetime.datetime.fromisoformat(d).date() if 'T' in d else datetime.datetime.strptime(d[:10], '%Y-%m-%d').date()
            else: dt = datetime.datetime.max.date()
            p = t.get('ai_priority_score')
            p = p if p is not None else 0
            return (dt, -p)
            
        sorted_tasks = sorted(tasks, key=sort_key)
        now = datetime.datetime.now()
        days_ahead = 0 if now.weekday() == 0 else 7 - now.weekday()
        ref_start = (now + datetime.timedelta(days=days_ahead)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        corridor_schedule = {c['corridor_id']: [] for c in corridors}
        
        for task in sorted_tasks:
            dur_mins = int(float(task.get('required_block_duration', 1.0)) * 60)
            c_id = task.get('corridor_id')
            raw_windows = availability_windows.get(c_id, [])
            
            # Convert dict windows to minute offsets from reference_start
            # Each window dict has start_hour/end_hour (0-24) and day (e.g. "0-6")
            windows_minutes = []
            for w in raw_windows:
                if isinstance(w, dict):
                    sh = w.get('start_hour', 0)
                    eh = w.get('end_hour', 24)
                    # For each day in the horizon, create a window
                    day_spec = str(w.get('day', '0-6'))
                    if '-' in day_spec:
                        parts = day_spec.split('-')
                        day_range = range(int(parts[0]), int(parts[1]) + 1)
                    else:
                        day_range = [int(day_spec)]
                    for d in day_range:
                        w_start_min = d * 24 * 60 + int(sh * 60)
                        w_end_min = d * 24 * 60 + int(eh * 60)
                        windows_minutes.append((w_start_min, w_end_min))
                elif isinstance(w, (list, tuple)) and len(w) >= 2:
                    windows_minutes.append((w[0], w[1]))
            
            scheduled = False
            for (w_start, w_end) in windows_minutes:
                if w_end - w_start >= dur_mins:
                    proposed_start = w_start
                    proposed_end = w_start + dur_mins
                    
                    # Basic corridor conflict avoidance
                    overlap = any(not (proposed_end <= cs or proposed_start >= ce) for (cs, ce) in corridor_schedule.get(c_id, []))
                    if not overlap:
                        # Convert to datetimes to check train conflicts
                        b_start_dt = ref_start + datetime.timedelta(minutes=proposed_start)
                        b_end_dt = ref_start + datetime.timedelta(minutes=proposed_end)
                        
                        # Basic train conflict avoidance
                        train_conflict = False
                        for tr in trains:
                            if tr.get('corridor_id') == c_id:
                                try:
                                    arr_time = datetime.datetime.strptime(tr.get('arrival_time', '00:00'), '%H:%M').time()
                                    dep_time = datetime.datetime.strptime(tr.get('departure_time', '23:59'), '%H:%M').time()
                                    if b_start_dt.time() <= dep_time and b_end_dt.time() >= arr_time:
                                        train_conflict = True
                                        break
                                except Exception:
                                    pass
                        if train_conflict:
                            continue
                            
                        scheduled = True
                        task['start_time'] = b_start_dt.isoformat()
                        task['end_time'] = b_end_dt.isoformat()
                        task['duration_hours'] = dur_mins / 60.0
                        
                        scheduled_tasks.append(task)
                        corridor_schedule[c_id].append((proposed_start, proposed_end))
                        
                        blocks.append({
                            "block_id": f"BASE-BLK-{uuid.uuid4().hex[:6].upper()}",
                            "corridor_id": c_id, 
                            "start_time": b_start_dt.isoformat(), 
                            "end_time": b_end_dt.isoformat(),
                            "duration": task['duration_hours'], 
                            "department": task.get('department'),
                            "reason": task.get('description', 'Baseline scheduled')
                        })
                        total_block_hours += task['duration_hours']
                        break
                        
            if not scheduled: 
                unscheduled_tasks.append(task)
                
        metrics = {
            "maintenance_completion": (len(scheduled_tasks) / len(tasks) * 100) if tasks else 0.0,
            "estimated_availability_proxy": 80.0 + (len(scheduled_tasks) / len(tasks) * 15.0) if tasks else 80.0,
            "train_impact": sum((t.get('ai_train_impact_score') if t.get('ai_train_impact_score') is not None else 50.0) for t in unscheduled_tasks)
        }
            
        return {
            "scheduled_tasks": scheduled_tasks, "unscheduled_tasks": unscheduled_tasks,
            "blocks": blocks, "total_block_hours": total_block_hours, "metrics": metrics
        }

    @staticmethod
    def compare_plans(optimized: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
        def calc_imp(opt_val, base_val, higher_is_better=True):
            if base_val == 0:
                return 0.0
            diff = opt_val - base_val
            pct = (diff / base_val) * 100
            return pct if higher_is_better else -pct

        # Compute optimized metrics from actual optimizer result data
        opt_stats = optimized.get("stats", {})
        opt_total = opt_stats.get("total_tasks", 1)
        opt_scheduled = opt_stats.get("scheduled_count", len(optimized.get("scheduled_tasks", [])))
        opt_unscheduled = opt_stats.get("unscheduled_count", len(optimized.get("unscheduled_tasks", [])))
        
        opt_maintenance_completion = (opt_scheduled / opt_total * 100) if opt_total > 0 else 0.0
        opt_estimated_availability_proxy = 80.0 + (opt_scheduled / opt_total * 15.0) if opt_total > 0 else 80.0
        
        # Train impact: residual risk (sum of impact scores of unscheduled tasks)
        opt_train_impact = sum(
            (t.get("impact_score") if t.get("impact_score") is not None else 50.0) for t in optimized.get("unscheduled_tasks", [])
        )
        
        opt_coordination = opt_stats.get("coordination_count", 0)

        return {
            "estimated_availability_proxy": {
                "optimized": round(opt_estimated_availability_proxy, 2),
                "baseline": baseline.get("metrics", {}).get("estimated_availability_proxy", 0),
                "improvement": round(calc_imp(opt_estimated_availability_proxy, baseline.get("metrics", {}).get("estimated_availability_proxy", 0)), 2)
            },
            "train_impact": {
                "optimized": round(opt_train_impact, 2),
                "baseline": baseline.get("metrics", {}).get("train_impact", 0),
                "improvement": round(calc_imp(opt_train_impact, baseline.get("metrics", {}).get("train_impact", 0), False), 2)
            },
            "num_blocks": {
                "optimized": len(optimized.get("blocks", [])),
                "baseline": len(baseline.get("blocks", [])),
                "improvement": round(calc_imp(len(optimized.get("blocks", [])), len(baseline.get("blocks", [])), False), 2)
            },
            "maintenance_completion": {
                "optimized": round(opt_maintenance_completion, 2),
                "baseline": baseline.get("metrics", {}).get("maintenance_completion", 0),
                "improvement": round(calc_imp(opt_maintenance_completion, baseline.get("metrics", {}).get("maintenance_completion", 0)), 2)
            },
            "overdue_tasks": {
                "optimized": opt_unscheduled,
                "baseline": len(baseline.get("unscheduled_tasks", [])),
                "improvement": round(calc_imp(opt_unscheduled, max(1, len(baseline.get("unscheduled_tasks", []))), False), 2)
            },
            "coordinated_tasks": {
                "optimized": opt_coordination,
                "baseline": 0,
                "improvement": 0.0
            }
        }
