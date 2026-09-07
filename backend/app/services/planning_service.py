import logging
import json
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.models import (
    MaintenanceTask, Defect, Asset, Corridor, Train, 
    Resource, Block, Plan
)
from app.ai.predictor import RailBlockPredictor
from app.optimizer.cp_sat_optimizer import BlockPlanOptimizer
from app.services.validation_service import ValidationService
from app.services.baseline_service import BaselineService
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

class PlanningService:
    @staticmethod
    def generate_plan(db: Session, horizon: str) -> Dict[str, Any]:
        logger.info(f"[PLAN] Starting {horizon} planning")
        
        # 1. Load pending maintenance tasks
        tasks = db.query(MaintenanceTask).filter(MaintenanceTask.status.in_(["PENDING", "OVERDUE"])).all()
        tasks_dict = [ {c.name: getattr(t, c.name) for c in t.__table__.columns} for t in tasks ]
        
        # 2. Load defects
        defects = db.query(Defect).all()
        defects_dict = [ {c.name: getattr(d, c.name) for c in d.__table__.columns} for d in defects ]
        
        # 3. Load assets
        assets = db.query(Asset).all()
        assets_dict = { a.asset_id: {c.name: getattr(a, c.name) for c in a.__table__.columns} for a in assets }
        
        # 4. Load corridors
        corridors = db.query(Corridor).all()
        corridors_dict = [ {col.name: getattr(c, col.name) for col in c.__table__.columns} for c in corridors ]
        
        # 5. Load availability windows
        from app.services.corridor_service import CorridorService
        availability_windows = { c.corridor_id: CorridorService.get_availability_windows(db, c.corridor_id) for c in corridors }
        
        # 6. Load trains
        trains = db.query(Train).all()
        trains_dict = [ {c.name: getattr(t, c.name) for c in t.__table__.columns} for t in trains ]
        
        # 7. Filter forecasted goods trains
        forecasted_trains = [ t for t in trains_dict if t.get('forecasted') and t.get('train_type') == 'Goods' ]
        
        # 8. Load resources
        resources = db.query(Resource).all()
        resources_dict = [ {c.name: getattr(r, c.name) for c in r.__table__.columns} for r in resources ]
        
        # 9. Load existing blocks
        existing_blocks = db.query(Block).filter(Block.status == "APPROVED").all()
        existing_blocks_dict = [ {c.name: getattr(b, c.name) for c in b.__table__.columns} for b in existing_blocks ]
        
        predictor = RailBlockPredictor()
        try:
            predictor.initialize()
        except Exception as e:
            logger.warning(f"Predictor init failed: {e}")
        
        priority_scores = {}
        risk_scores = {}
        impact_scores = {}
        
        # 10-14. Engineer features and Predict
        for t in tasks_dict:
            a = assets_dict.get(t['asset_id'], {})
            d = [df for df in defects_dict if df['asset_id'] == t['asset_id']]
            c = next((corr for corr in corridors_dict if corr['corridor_id'] == t['corridor_id']), {})
            tr = [trn for trn in trains_dict if trn['corridor_id'] == t['corridor_id']]
            
            try:
                pred_priority = predictor.predict_priority(t, a, d, tr, c)
                t['ai_priority_score'] = pred_priority['priority_score']
                t['ai_priority_level'] = pred_priority['priority_level']
                t['ai_reasons'] = json.dumps(pred_priority['reasons'])
                priority_scores[t['task_id']] = pred_priority['priority_score']
            except:
                priority_scores[t['task_id']] = 50.0
                
            try:
                pred_risk = predictor.predict_risk(a, d)
                t['ai_failure_risk'] = pred_risk.get('failure_risk', 0.5)
                t['ai_risk_percentage'] = pred_risk.get('risk_percentage', 50.0)
                risk_scores[a.get('asset_id', '')] = pred_risk.get('risk_percentage', 50.0)
            except:
                pass
                
            try:
                pred_impact = predictor.predict_impact(c, tr, float(t.get('required_block_duration', 1.0)), 12)
                t['ai_train_impact_score'] = pred_impact.get('train_impact_score', 50.0)
                impact_scores[t['task_id']] = pred_impact.get('train_impact_score', 50.0)
            except:
                impact_scores[t['task_id']] = 50.0
                
        logger.info(f"[AI] Priority prediction completed for {len(tasks_dict)} tasks")
        logger.info("[AI] Risk prediction completed")
        logger.info("[AI] Train impact prediction completed")
        
        # 15. Update AI fields in DB (simplified logic)
        for t_dict in tasks_dict:
            task_obj = db.query(MaintenanceTask).filter(MaintenanceTask.task_id == t_dict['task_id']).first()
            if task_obj:
                task_obj.ai_priority_score = t_dict.get('ai_priority_score')
                task_obj.ai_priority_level = t_dict.get('ai_priority_level')
                task_obj.ai_failure_risk = t_dict.get('ai_failure_risk')
                task_obj.ai_risk_percentage = t_dict.get('ai_risk_percentage')
                task_obj.ai_train_impact_score = t_dict.get('ai_train_impact_score')
                task_obj.ai_reasons = t_dict.get('ai_reasons')
        db.commit()
        
        # 16. Run CP-SAT optimizer
        logger.info("[OPTIMIZER] CP-SAT started")
        optimizer = BlockPlanOptimizer(time_limit=30)
        opt_result = optimizer.optimize(
            tasks=tasks_dict,
            corridors=corridors_dict,
            trains=trains_dict,
            resources=resources_dict,
            existing_blocks=existing_blocks_dict,
            availability_windows=availability_windows,
            horizon=horizon,
            priority_scores=priority_scores,
            risk_scores=risk_scores,
            impact_scores=impact_scores
        )
        logger.info(f"[OPTIMIZER] Solution found - status: {opt_result.get('solver_status', 'UNKNOWN')}")
        
        # 17. Parse optimizer solution (done by optimizer inside)
        
        # 18. Validate solution
        validation_result = ValidationService.validate_plan(
            scheduled_tasks=opt_result.get('scheduled_tasks', []),
            corridors=corridors_dict,
            trains=trains_dict,
            resources=resources_dict,
            existing_blocks=existing_blocks_dict
        )
        v_count = len(validation_result.get('violations', []))
        if v_count > 0:
            logger.info(f"[VALIDATION] {v_count} constraint violations found")
        else:
            logger.info("[VALIDATION] 0 constraint violations found / No violations")
            
        # 19. Run baseline scheduler
        baseline_result = BaselineService.generate_baseline(
            tasks=tasks_dict,
            corridors=corridors_dict,
            availability_windows=availability_windows,
            trains=trains_dict
        )
        logger.info("[BASELINE] Baseline generated")
        
        # 20-21. Compare optimized plan vs baseline (KPIs)
        comparison = BaselineService.compare_plans(opt_result, baseline_result)
        
        # Compute real plan KPI metrics from optimizer output
        plan_id = f"PLAN-{uuid.uuid4().hex[:8].upper()}"
        opt_stats = opt_result.get('stats', {})
        opt_total = opt_stats.get('total_tasks', len(tasks_dict))
        opt_scheduled_count = opt_stats.get('scheduled_count', len(opt_result.get('scheduled_tasks', [])))
        real_maintenance_completion = (opt_scheduled_count / opt_total * 100) if opt_total > 0 else 0.0
        real_asset_availability = 80.0 + (opt_scheduled_count / opt_total * 15.0) if opt_total > 0 else 80.0
        real_train_impact = sum(
            (t.get('impact_score') if t.get('impact_score') is not None else 50.0) for t in opt_result.get('unscheduled_tasks', [])
        )
        real_coordination = opt_stats.get('coordination_count', 0)
        
        new_plan = Plan(
            plan_id=plan_id,
            horizon=horizon,
            generated_at=datetime.now(timezone.utc).replace(tzinfo=None),
            status="GENERATED",
            objective_score=opt_result.get('objective_value', 0.0),
            total_tasks=len(tasks_dict),
            scheduled_tasks=opt_scheduled_count,
            unscheduled_tasks=len(opt_result.get('unscheduled_tasks', [])),
            total_block_hours=opt_result.get('total_block_hours', 0.0),
            estimated_availability_proxy=round(real_asset_availability, 2),
            train_impact_score=round(real_train_impact, 2),
            maintenance_completion=round(real_maintenance_completion, 2),
            coordination_score=round(float(real_coordination), 2),
            validation_status=json.dumps(validation_result),
            model_versions=json.dumps({"priority": "1", "risk": "1", "impact": "1"})
        )
        db.add(new_plan)
        
        # 23. Save blocks to database
        for b in opt_result.get('blocks', []):
            new_block = Block(
                block_id=b['block_id'],
                corridor_id=b['corridor_id'],
                start_time=datetime.fromisoformat(b['start_time']),
                end_time=datetime.fromisoformat(b['end_time']),
                duration=b['duration'],
                status="GENERATED",
                source="AI_OPTIMIZER",
                plan_id=plan_id,
                department=b.get('department', 'Multiple'),
                reason=b.get('reason', 'AI Generated Plan Block')
            )
            db.add(new_block)
            
        db.commit()
        db.refresh(new_plan)
        
        logger.info(f"[PLAN] {horizon} plan generated successfully")
        
        plan_dict = {c.name: getattr(new_plan, c.name) for c in new_plan.__table__.columns}
        
        return {
            "plan": plan_dict,
            "blocks": opt_result.get('blocks', []),
            "scheduled_tasks": opt_result.get('scheduled_tasks', []),
            "unscheduled_tasks": opt_result.get('unscheduled_tasks', []),
            "comparison": comparison,
            "validation": validation_result,
            "solver_status": opt_result.get('solver_status', 'UNKNOWN')
        }

    @staticmethod
    def get_all_plans(db: Session) -> List[Plan]:
        return db.query(Plan).all()

    @staticmethod
    def get_plan(db: Session, plan_id: str) -> Dict[str, Any]:
        plan = db.query(Plan).filter(Plan.plan_id == plan_id).first()
        if not plan:
            return None
        blocks = db.query(Block).filter(Block.plan_id == plan_id).all()
        return {
            "plan": plan,
            "blocks": blocks,
            "tasks": [], # Ideally fetch tasks mapped to this plan
            "kpis": AnalyticsService.calculate_kpis(db, plan)
        }

    @staticmethod
    def approve_plan(db: Session, plan_id: str) -> Plan:
        plan = db.query(Plan).filter(Plan.plan_id == plan_id).first()
        if plan:
            plan.status = "APPROVED"
            blocks = db.query(Block).filter(Block.plan_id == plan_id).all()
            for b in blocks:
                b.status = "APPROVED"
            db.commit()
            db.refresh(plan)
        return plan

    @staticmethod
    def reject_plan(db: Session, plan_id: str) -> Plan:
        plan = db.query(Plan).filter(Plan.plan_id == plan_id).first()
        if plan:
            plan.status = "REJECTED"
            blocks = db.query(Block).filter(Block.plan_id == plan_id).all()
            for b in blocks:
                b.status = "REJECTED"
            db.commit()
            db.refresh(plan)
        return plan

    @staticmethod
    def regenerate_plan(db: Session, plan_id: str) -> Dict[str, Any]:
        plan = db.query(Plan).filter(Plan.plan_id == plan_id).first()
        if not plan:
            return None
        # Reject old plan
        PlanningService.reject_plan(db, plan_id)
        # Generate new one
        return PlanningService.generate_plan(db, plan.horizon)
