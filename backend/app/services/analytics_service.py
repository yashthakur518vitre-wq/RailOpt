from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.models import Asset, MaintenanceTask, Block, Train, Plan, Corridor, Resource, Defect


class AnalyticsService:
    @staticmethod
    def get_asset_availability(db: Session) -> Dict[str, Any]:
        total_assets = db.query(Asset).count()
        available_assets = db.query(Asset).filter(
            func.upper(Asset.availability_status) == "AVAILABLE"
        ).count()
        overall = round((available_assets / total_assets * 100), 2) if total_assets > 0 else 0.0

        corridors = db.query(Corridor).all()
        by_corridor = {}
        for c in corridors:
            c_assets = db.query(Asset).filter(Asset.corridor_id == c.corridor_id).count()
            c_avail = db.query(Asset).filter(
                Asset.corridor_id == c.corridor_id,
                func.upper(Asset.availability_status) == "AVAILABLE"
            ).count()
            by_corridor[c.corridor_id] = round((c_avail / c_assets * 100), 2) if c_assets > 0 else 0.0

        # Fallback if no Corridor rows exist but assets have corridor_id
        if not by_corridor:
            asset_corridors = [row[0] for row in db.query(Asset.corridor_id).distinct().all() if row[0]]
            for cid in asset_corridors:
                c_assets = db.query(Asset).filter(Asset.corridor_id == cid).count()
                c_avail = db.query(Asset).filter(
                    Asset.corridor_id == cid,
                    func.upper(Asset.availability_status) == "AVAILABLE"
                ).count()
                by_corridor[cid] = round((c_avail / c_assets * 100), 2) if c_assets > 0 else 0.0

        return {
            "overall_percentage": overall,
            "by_corridor": by_corridor
        }

    @staticmethod
    def get_maintenance_completion(db: Session) -> Dict[str, Any]:
        total = db.query(MaintenanceTask).count()
        completed = db.query(MaintenanceTask).filter(
            func.upper(MaintenanceTask.status) == "COMPLETED"
        ).count()
        overdue = db.query(MaintenanceTask).filter(
            func.upper(MaintenanceTask.status) == "OVERDUE"
        ).count()

        dept_records = db.query(MaintenanceTask.department).distinct().all()
        departments = [d[0] for d in dept_records if d[0]]
        if not departments:
            departments = ["Engineering", "S&T", "Traction", "Track", "Signal", "OHE"]

        by_dept = {}
        for d in departments:
            d_total = db.query(MaintenanceTask).filter(MaintenanceTask.department == d).count()
            d_comp = db.query(MaintenanceTask).filter(
                MaintenanceTask.department == d,
                func.upper(MaintenanceTask.status) == "COMPLETED"
            ).count()
            by_dept[d] = round((d_comp / d_total * 100), 2) if d_total > 0 else 0.0

        return {
            "completion_percentage": round((completed / total * 100), 2) if total > 0 else 0.0,
            "overdue_count": overdue,
            "by_department": by_dept
        }

    @staticmethod
    def _parse_time_to_minutes(time_val: Any) -> Optional[int]:
        """Convert HH:MM string or time object to minutes from midnight."""
        if not time_val:
            return None
        if isinstance(time_val, str):
            try:
                parts = time_val.strip().split(":")
                return int(parts[0]) * 60 + int(parts[1])
            except Exception:
                return None
        if hasattr(time_val, "hour") and hasattr(time_val, "minute"):
            return time_val.hour * 60 + time_val.minute
        return None

    @staticmethod
    def get_train_impact(db: Session, plan: Any = None) -> Dict[str, Any]:
        """
        Calculate actual impact by querying Block and Train tables.
        Counts how many blocks overlap with train corridors, calculates impact scores
        based on actual block-train proximity, train priority, and occupancy.
        If a plan object or plan_id is passed, filters blocks by plan_id.
        """
        plan_id = None
        if isinstance(plan, str):
            plan_id = plan
        elif plan is not None and hasattr(plan, "plan_id"):
            plan_id = plan.plan_id

        block_query = db.query(Block)
        if plan_id:
            block_query = block_query.filter(Block.plan_id == plan_id)
        blocks = block_query.all()

        trains = db.query(Train).all()
        corridors = db.query(Corridor).all()

        corridor_ids = set(c.corridor_id for c in corridors if c.corridor_id)
        corridor_ids.update(b.corridor_id for b in blocks if b.corridor_id)
        corridor_ids.update(t.corridor_id for t in trains if t.corridor_id)

        priority_weights = {
            "CRITICAL": 2.0,
            "HIGH": 1.5,
            "MEDIUM": 1.0,
            "LOW": 0.5
        }

        by_corridor = {}
        for cid in sorted(corridor_ids):
            corr_blocks = [b for b in blocks if b.corridor_id == cid]
            corr_trains = [t for t in trains if t.corridor_id == cid]

            if not corr_blocks:
                by_corridor[cid] = 0.0
                continue

            if not corr_trains:
                block_hours = sum(float(b.duration or 0) for b in corr_blocks)
                by_corridor[cid] = round(min(100.0, block_hours * 5.0), 2)
                continue

            corridor_impact_sum = 0.0

            for b in corr_blocks:
                b_start = b.start_time
                b_duration = float(b.duration) if b.duration is not None else 1.0

                if b_start:
                    b_start_min = b_start.hour * 60 + b_start.minute
                else:
                    b_start_min = 0
                b_dur_min = max(1, int(b_duration * 60))

                b_mod_start = b_start_min % 1440
                b_mod_end = b_mod_start + b_dur_min
                if b_mod_end > 1440:
                    b_intervals = [(b_mod_start, 1440), (0, b_mod_end % 1440)]
                else:
                    b_intervals = [(b_mod_start, b_mod_end)]

                block_train_impact = 0.0
                for tr in corr_trains:
                    p_weight = priority_weights.get(str(tr.priority or "").upper(), 1.0)
                    occ_factor = (float(tr.occupancy) / 100.0) if tr.occupancy is not None else 0.7
                    weight = p_weight * occ_factor

                    arr_min = AnalyticsService._parse_time_to_minutes(tr.arrival_time)
                    dep_min = AnalyticsService._parse_time_to_minutes(tr.departure_time)

                    if arr_min is None or dep_min is None:
                        block_train_impact += 2.0 * weight
                        continue

                    if arr_min == dep_min:
                        dep_min = arr_min + 60

                    if dep_min < arr_min:
                        t_intervals = [(arr_min, 1440), (0, dep_min)]
                    else:
                        t_intervals = [(arr_min, dep_min)]

                    # Direct overlap check
                    overlap_mins = 0
                    for (bs, be) in b_intervals:
                        for (ts, te) in t_intervals:
                            os = max(bs, ts)
                            oe = min(be, te)
                            if oe > os:
                                overlap_mins += (oe - os)

                    if overlap_mins > 0:
                        impact = (overlap_mins / 60.0) * 15.0 * weight
                    else:
                        min_gap = float("inf")
                        for (bs, be) in b_intervals:
                            for (ts, te) in t_intervals:
                                if be <= ts:
                                    gap = ts - be
                                elif te <= bs:
                                    gap = bs - te
                                else:
                                    gap = 0
                                if gap < min_gap:
                                    min_gap = gap

                        if min_gap <= 120:
                            proximity_factor = (1.0 - min_gap / 120.0)
                            impact = proximity_factor * 6.0 * weight
                        else:
                            impact = 0.5 * weight

                    block_train_impact += impact

                corridor_impact_sum += block_train_impact

            corr_score = min(100.0, corridor_impact_sum / max(1, len(corr_blocks)))
            by_corridor[cid] = round(corr_score, 2)

        overall_score = round(sum(by_corridor.values()) / len(by_corridor), 2) if by_corridor else 0.0

        return {
            "overall_score": overall_score,
            "by_corridor": by_corridor
        }

    @staticmethod
    def get_department_performance(db: Session) -> Dict[str, Any]:
        """
        Query MaintenanceTask grouped by department, calculate actual completion rates and efficiency.
        """
        dept_records = db.query(MaintenanceTask.department).distinct().all()
        departments = [d[0] for d in dept_records if d[0]]
        if not departments:
            departments = ["Engineering", "S&T", "Traction", "Track", "Signal", "OHE"]

        result = {}
        for dept in departments:
            tasks = db.query(MaintenanceTask).filter(MaintenanceTask.department == dept).all()
            total_tasks = len(tasks)
            if total_tasks == 0:
                result[dept] = {"completion": 0.0, "efficiency": 0.0}
                continue

            completed_count = len([t for t in tasks if str(t.status).upper() == "COMPLETED"])
            overdue_count = len([t for t in tasks if str(t.status).upper() == "OVERDUE"])

            completion_rate = round((completed_count / total_tasks * 100), 2)

            on_time_ratio = (total_tasks - overdue_count) / total_tasks
            duration_adherences = [
                min(1.0, float(t.estimated_duration) / float(t.required_block_duration))
                for t in tasks
                if t.required_block_duration and t.required_block_duration > 0 and t.estimated_duration
            ]
            avg_duration_adh = sum(duration_adherences) / len(duration_adherences) if duration_adherences else 0.85

            efficiency = round((0.6 * on_time_ratio + 0.4 * avg_duration_adh) * 100, 2)
            result[dept] = {
                "completion": completion_rate,
                "efficiency": efficiency
            }

        return result

    @staticmethod
    def calculate_kpis(db: Session, plan: Any = None) -> Dict[str, Any]:
        """
        Calculate all KPIs from actual database data:
        - Asset Availability %: from Asset table
        - Maintenance Completion %: from MaintenanceTask table
        - Critical Task Completion %: filter by criticality='HIGH' or 'Critical'
        - Overdue Tasks: count OVERDUE status
        - Average Downtime: from Block durations
        - Total Block Hours: sum of Block.duration
        - Number of Blocks: count of blocks
        - Train Impact Score: from get_train_impact
        - Resource Utilization %: calculate from Resource and Block data
        - Multi-Department Coordination %: from blocks with multiple departments

        If a plan object is passed, filter blocks by plan_id.
        """
        plan_id = None
        if isinstance(plan, str):
            plan_id = plan
        elif plan is not None and hasattr(plan, "plan_id"):
            plan_id = plan.plan_id

        # 1. Asset Availability %
        total_assets = db.query(Asset).count()
        available_assets = db.query(Asset).filter(
            func.upper(Asset.availability_status) == "AVAILABLE"
        ).count()
        asset_availability = round((available_assets / total_assets * 100), 2) if total_assets > 0 else 0.0

        # 2. Maintenance Completion %
        total_tasks = db.query(MaintenanceTask).count()
        completed_tasks = db.query(MaintenanceTask).filter(
            func.upper(MaintenanceTask.status) == "COMPLETED"
        ).count()
        maintenance_completion = round((completed_tasks / total_tasks * 100), 2) if total_tasks > 0 else 0.0

        # 3. Critical Task Completion %
        critical_tasks = db.query(MaintenanceTask).filter(
            func.upper(MaintenanceTask.criticality).in_(["HIGH", "CRITICAL"])
        ).all()
        total_critical = len(critical_tasks)
        completed_critical = len([t for t in critical_tasks if str(t.status).upper() == "COMPLETED"])
        critical_task_completion = round((completed_critical / total_critical * 100), 2) if total_critical > 0 else 0.0

        # 4. Overdue Tasks
        overdue_tasks = db.query(MaintenanceTask).filter(
            func.upper(MaintenanceTask.status) == "OVERDUE"
        ).count()

        # 5. Blocks (filtered by plan_id if provided)
        block_query = db.query(Block)
        if plan_id:
            block_query = block_query.filter(Block.plan_id == plan_id)
        blocks = block_query.all()

        number_of_blocks = len(blocks)
        total_block_hours = round(sum(float(b.duration) for b in blocks if b.duration is not None), 2)
        average_downtime = round(total_block_hours / number_of_blocks, 2) if number_of_blocks > 0 else 0.0

        # 6. Train Impact Score
        train_impact_res = AnalyticsService.get_train_impact(db, plan=plan)
        train_impact_score = train_impact_res.get("overall_score", 0.0)

        # 7. Resource Utilization %
        resources = db.query(Resource).all()
        total_resource_units = sum(int(r.quantity) for r in resources if r.quantity is not None)
        busy_resource_units = sum(
            int(r.quantity) for r in resources
            if r.quantity is not None and str(r.availability or "").upper() in ["BUSY", "ALLOCATED", "IN_USE"]
        )

        if total_resource_units > 0:
            if busy_resource_units > 0:
                resource_utilization = round((busy_resource_units / total_resource_units * 100), 2)
            elif total_block_hours > 0:
                resource_utilization = round(min(100.0, (total_block_hours / (total_resource_units * 10.0)) * 100), 2)
            else:
                resource_utilization = 0.0
        else:
            resource_utilization = 0.0

        # 8. Multi-Department Coordination %
        if number_of_blocks > 0:
            multi_dept_count = 0
            for b in blocks:
                dept_str = str(b.department or "").strip().upper()
                if (
                    "MULTI" in dept_str or
                    "JOINT" in dept_str or
                    "," in dept_str or
                    "&" in dept_str or
                    "/" in dept_str or
                    "+" in dept_str
                ):
                    multi_dept_count += 1

            if multi_dept_count == 0 and number_of_blocks > 1:
                corridor_blocks: Dict[str, List[Block]] = {}
                for b in blocks:
                    corridor_blocks.setdefault(b.corridor_id, []).append(b)

                coordinated_ids = set()
                for cid, c_blks in corridor_blocks.items():
                    for i, b1 in enumerate(c_blks):
                        for j, b2 in enumerate(c_blks):
                            if i != j and b1.department != b2.department:
                                if b1.start_time and b1.end_time and b2.start_time and b2.end_time:
                                    if not (b1.end_time <= b2.start_time or b1.start_time >= b2.end_time):
                                        coordinated_ids.add(b1.block_id or b1.id)
                                        coordinated_ids.add(b2.block_id or b2.id)
                multi_dept_count = len(coordinated_ids)

            multi_dept_coordination = round((multi_dept_count / number_of_blocks * 100), 2)
        else:
            multi_dept_coordination = 0.0

        return {
            "Asset Availability %": asset_availability,
            "Maintenance Completion %": maintenance_completion,
            "Critical Task Completion %": critical_task_completion,
            "Overdue Tasks": overdue_tasks,
            "Average Downtime": average_downtime,
            "Total Block Hours": total_block_hours,
            "Number of Blocks": number_of_blocks,
            "Train Impact Score": train_impact_score,
            "Resource Utilization %": resource_utilization,
            "Multi-Department Coordination %": multi_dept_coordination
        }

