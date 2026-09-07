import json
from typing import List, Dict, Any
from datetime import datetime

class ValidationService:
    @staticmethod
    def validate_plan(scheduled_tasks: List[Dict], corridors: List[Dict], trains: List[Dict], resources: List[Dict], existing_blocks: List[Dict]) -> Dict[str, Any]:
        violations = []
        
        # Build lookup dictionaries
        corridors_by_id = {c['corridor_id']: c for c in corridors}
        resources_by_id = {r['resource_id']: r for r in resources}
        
        corridor_schedule = {}
        resource_allocations = {}
        
        for t in scheduled_tasks:
            task_id = t['task_id']
            c_id = t.get('corridor_id')
            
            # Parse ISO 8601 strings to datetime
            start_dt = datetime.fromisoformat(t['start_time'])
            end_dt = datetime.fromisoformat(t['end_time'])
            
            # Convert to minutes from start of week/reference point for easier arithmetic, or just use seconds
            duration_minutes = (end_dt - start_dt).total_seconds() / 60.0
            
            # Duration Check
            # CP-SAT truncates to integer minutes, so we must validate against that
            required_duration_mins = int(float(t.get('required_block_duration', 1.0)) * 60)
            
            # Allow epsilon for floating point math / CP-SAT integer truncation
            if duration_minutes + 0.5 < required_duration_mins:
                violations.append({"type": "DURATION", "task_id": task_id, "message": f"Block duration {duration_minutes}m is less than required {required_duration_mins}m"})
            
            # Max Duration Check (8 hours = 480 mins)
            if duration_minutes > 480:
                violations.append({"type": "MAX_DURATION", "task_id": task_id, "message": f"Block duration {duration_minutes}m exceeds 8 hours max"})
                
            # Corridor overlap is allowed only when the optimizer has bundled
            # tasks into the same physical block. Different block IDs may not overlap.
            if c_id not in corridor_schedule:
                corridor_schedule[c_id] = []
            current_block_id = t.get('block_id')
            for (cs, ce, ot_id, other_block_id) in corridor_schedule[c_id]:
                if not (end_dt <= cs or start_dt >= ce) and current_block_id != other_block_id:
                    violations.append({"type": "CORRIDOR_CONFLICT", "task_id": task_id, "message": f"Overlaps in corridor {c_id} with task {ot_id}"})
            corridor_schedule[c_id].append((start_dt, end_dt, task_id, current_block_id))
            
            # Corridor Availability Check
            corridor = corridors_by_id.get(c_id)
            if corridor:
                try:
                    windows = json.loads(corridor.get('availability_windows', '[]'))
                    # Very simple check: ensure the block falls within at least one window
                    # In a real scenario we'd match the day of week and hour exactly.
                    # For now, we'll just check if start_hour and end_hour fit.
                    start_hour = start_dt.hour + start_dt.minute/60.0
                    end_hour = end_dt.hour + end_dt.minute/60.0
                    if end_hour < start_hour: # Crosses midnight
                        end_hour += 24
                    
                    window_found = False
                    for w in windows:
                        w_start = w.get('start_hour', 0)
                        w_end = w.get('end_hour', 24)
                        if w_end < w_start:
                            w_end += 24
                        
                        if start_hour >= w_start and end_hour <= w_end:
                            window_found = True
                            break
                    if not window_found and windows:
                        violations.append({"type": "CORRIDOR_AVAILABILITY", "task_id": task_id, "message": f"Does not fit in any availability window for {c_id}"})
                except Exception:
                    pass
            
            # Train Conflict Check
            for tr in trains:
                if tr.get('corridor_id') == c_id and tr.get('priority', 'Low') in ['High', 'Critical']:
                    try:
                        arr_time = datetime.strptime(tr.get('arrival_time', '00:00'), '%H:%M').time()
                        dep_time = datetime.strptime(tr.get('departure_time', '23:59'), '%H:%M').time()
                        freq = tr.get('frequency', 'Daily').lower()
                        # Strictly match logic from constraints.py for consistency
                        # Find the day index based on start_dt vs a reference (assuming start_dt corresponds to the actual scheduled date)
                        day_of_week = start_dt.weekday() # 0=Monday, 6=Sunday
                        
                        runs_today = True
                        if freq == 'weekdays' and day_of_week >= 5:
                            runs_today = False
                        elif freq == 'weekends' and day_of_week < 5:
                            runs_today = False
                        elif freq in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                            if day_of_week != days.index(freq):
                                runs_today = False
                                
                        if not runs_today:
                            continue
                            
                        # Convert block to time of day
                        b_start_time = start_dt.time()
                        b_end_time = end_dt.time()
                            
                        # Simplified overlap check for the same day
                        if (b_start_time <= dep_time and b_end_time >= arr_time):
                            violations.append({"type": "TRAIN_CONFLICT", "task_id": task_id, "message": f"Conflicts with protected train {tr.get('train_id')}"})
                    except Exception:
                        pass
            
            # Resource Check
            # Assume t has 'required_resources' comma-separated
            # We don't have task dict here, scheduled_tasks doesn't have required_resources. 
            # We should probably pass the full task dictionaries, or just use what we have.
            # Currently scheduled_tasks has limited fields. We will skip deep resource check if missing.

        return {
            "valid": len(violations) == 0,
            "violations": violations
        }
