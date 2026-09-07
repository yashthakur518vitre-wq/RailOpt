code = \"\"\"
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json
import uuid

class BaselineService:
    @staticmethod
    def generate_baseline(tasks: List[Dict], corridors: Dict, availability_windows: Dict, trains: List[Dict]) -> Dict[str, Any]:
        scheduled_tasks = []
        unscheduled_tasks = []
        blocks = []
        total_block_hours = 0.0
        
        # Sort tasks by EDD (due_date) then priority
        # Ensure due_date is date object or string parseable
        def sort_key(t):
            d = t.get('due_date')
            if isinstance(d, datetime):
                dt = d.date()
            elif hasattr(d, 'isoformat'):
                dt = d
            elif isinstance(d, str):
                dt = datetime.fromisoformat(d).date() if 'T' in d else datetime.strptime(d, '%Y-%m-%d').date()
            else:
                dt = datetime.max.date()
            
            p = t.get('ai_priority_score', 0)
            return (dt, -p)
            
        sorted_tasks = sorted(tasks, key=sort_key)
        
        now = datetime.now()
        days_ahead = 0 if now.weekday() == 0 else 7 - now.weekday()
        ref_start = (now + timedelta(days=days_ahead)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Keep track of corridor occupation
        corridor_schedule = {c: [] for c in corridors.keys()}
        
        for task in sorted_tasks:
            dur_mins = int(float(task.get('required_block_duration', 1.0)) * 60)
            c_id = task.get('corridor_id')
            windows = availability_windows.get(c_id, [])
            
            scheduled = False
            for w in windows:
                # find a non overlapping slot in this window
                w_start = w[0]
                w_end = w[1]
                if w_end - w_start >= dur_mins:
                    # check corridor overlap
                    proposed_start = w_start
                    proposed_end = w_start + dur_mins
                    
                    overlap = False
                    for (cs, ce) in corridor_schedule.get(c_id, []):
                        if not (proposed_end <= cs or proposed_start >= ce):
                            overlap = True
                            break
                            
                    if not overlap:
                        # Schedule it
                        scheduled = True
                        task['start_time'] = proposed_start
                        task['end_time'] = proposed_end
                        scheduled_tasks.append(task)
                        corridor_schedule[c_id].append((proposed_start, proposed_end))
                        
                        b_start_dt = ref_start + timedelta(minutes=proposed_start)
                        b_end_dt = ref_start + timedelta(minutes=proposed_end)
                        
                        blocks.append({
                            "block_id": f"BASE-BLK-{uuid.uuid4().hex[:6].upper()}",
                            "corridor_id": c_id,
                            "start_time": b_start_dt.isoformat(),
                            "end_time": b_end_dt.isoformat(),
                            "duration": float(task.get('required_block_duration', 1.0)),
                            "department": task.get('department'),
                            "reason": task.get('description', 'Baseline manual scheduled')
                        })
                        total_block_hours += float(task.get('required_block_duration', 1.0))
                        break
                        
            if not scheduled:
                unscheduled_tasks.append(task)
                
        metrics = {
            "maintenance_completion": (len(scheduled_tasks) / len(tasks) * 100) if tasks else 0.0,
            "asset_availability": 85.0 + (len(scheduled_tasks) / len(tasks) * 10.0) if tasks else 85.0,
            "train_impact": len(scheduled_tasks) * 2.0  # mock metric
        }
            
        return {
            "scheduled_tasks": scheduled_tasks,
            "unscheduled_tasks": unscheduled_tasks,
            "blocks": blocks,
            "total_block_hours": total_block_hours,
            "metrics": metrics
        }

    @staticmethod
    def compare_plans(optimized: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
        def calc_imp(opt_val, base_val, higher_is_better=True):
            if base_val == 0:
                return 0.0
            diff = opt_val - base_val
            pct = (diff / base_val) * 100
            return pct if higher_is_better else -pct

        return {
            "asset_availability": {
                "optimized": optimized.get("estimated_asset_availability", 0),
                "baseline": baseline.get("metrics", {}).get("asset_availability", 0),
                "improvement": calc_imp(optimized.get("estimated_asset_availability", 0), baseline.get("metrics", {}).get("asset_availability", 0))
            },
            "train_impact": {
                "optimized": optimized.get("train_impact_score", 0),
                "baseline": baseline.get("metrics", {}).get("train_impact", 0),
                "improvement": calc_imp(optimized.get("train_impact_score", 0), baseline.get("metrics", {}).get("train_impact", 0), False)
            },
            "num_blocks": {
                "optimized": len(optimized.get("blocks", [])),
                "baseline": len(baseline.get("blocks", [])),
                "improvement": calc_imp(len(optimized.get("blocks", [])), len(baseline.get("blocks", [])), False)
            },
            "maintenance_completion": {
                "optimized": optimized.get("maintenance_completion", 0),
                "baseline": baseline.get("metrics", {}).get("maintenance_completion", 0),
                "improvement": calc_imp(optimized.get("maintenance_completion", 0), baseline.get("metrics", {}).get("maintenance_completion", 0))
            },
            "overdue_tasks": {
                "optimized": 0,
                "baseline": 0,
                "improvement": 0
            },
            "coordinated_tasks": {
                "optimized": optimized.get("coordination_score", 0),
                "baseline": 0,
                "improvement": calc_imp(optimized.get("coordination_score", 0), 0)
            }
        }
\"\"\"
with open('backend/app/services/baseline_service.py', 'w') as f:
    f.write(code)
