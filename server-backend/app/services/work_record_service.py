"""
工作记录管理服务
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from fastapi import HTTPException
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

from ..models import User, WorkRecord
from ..schemas import ExportRequest, WorkRecordCreate, WorkRecordUpdate


class WorkRecordService:
    """工作记录管理服务类"""

    def __init__(self, db: Session):
        self.db = db

    def create_work_record(self, record_data: WorkRecordCreate) -> WorkRecord:
        """创建工作记录"""
        # 验证员工是否存在
        employee = (
            self.db.query(User).filter(User.id == record_data.employee_id).first()
        )
        if not employee:
            raise HTTPException(status_code=404, detail="员工不存在")

        db_record = WorkRecord(
            employee_id=record_data.employee_id,
            platform=record_data.platform,
            action_type=record_data.action_type,
            target_username=record_data.target_username,
            target_user_id=record_data.target_user_id,
            target_url=record_data.target_url,
            device_id=record_data.device_id,
            device_name=record_data.device_name,
            status="pending",
        )

        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def update_work_record(
        self, record_id: int, record_data: WorkRecordUpdate
    ) -> Optional[WorkRecord]:
        """更新工作记录"""
        record = self.db.query(WorkRecord).filter(WorkRecord.id == record_id).first()
        if not record:
            return None

        for field, value in record_data.dict(exclude_unset=True).items():
            setattr(record, field, value)

        if record_data.status == "success" and not record.executed_at:
            record.executed_at = datetime.now()

        self.db.commit()
        self.db.refresh(record)
        return record

    def get_work_records(
        self,
        employee_id: Optional[int] = None,
        platform: Optional[str] = None,
        action_type: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[WorkRecord]:
        """获取工作记录列表"""
        query = self.db.query(WorkRecord)

        if employee_id:
            query = query.filter(WorkRecord.employee_id == employee_id)

        if platform:
            query = query.filter(WorkRecord.platform == platform)

        if action_type:
            query = query.filter(WorkRecord.action_type == action_type)

        if status:
            query = query.filter(WorkRecord.status == status)

        if start_date:
            query = query.filter(WorkRecord.created_at >= start_date)

        if end_date:
            query = query.filter(WorkRecord.created_at <= end_date)

        return (
            query.order_by(desc(WorkRecord.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_work_records_by_user_admin(
        self,
        user_admin_id: int,
        platform: Optional[str] = None,
        action_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[WorkRecord]:
        """获取用户管理员下所有员工的工作记录"""
        query = (
            self.db.query(WorkRecord).join(User).filter(User.parent_id == user_admin_id)
        )

        if platform:
            query = query.filter(WorkRecord.platform == platform)

        if action_type:
            query = query.filter(WorkRecord.action_type == action_type)

        if start_date:
            query = query.filter(WorkRecord.created_at >= start_date)

        if end_date:
            query = query.filter(WorkRecord.created_at <= end_date)

        return (
            query.order_by(desc(WorkRecord.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_work_statistics_by_user_admin(self, user_admin_id: int) -> Dict[str, Any]:
        """获取用户管理员的工作统计"""
        # 获取所有员工ID
        employee_ids = (
            self.db.query(User.id).filter(User.parent_id == user_admin_id).all()
        )
        employee_ids = [emp[0] for emp in employee_ids]

        if not employee_ids:
            return {
                "total_follows": 0,
                "total_likes": 0,
                "total_comments": 0,
                "today_follows": 0,
                "today_likes": 0,
                "today_comments": 0,
                "success_rate": 0.0,
                "platform_stats": {},
                "employee_stats": [],
            }

        # 总体统计
        total_follows = (
            self.db.query(WorkRecord)
            .filter(
                and_(
                    WorkRecord.employee_id.in_(employee_ids),
                    WorkRecord.action_type == "follow",
                    WorkRecord.status == "success",
                )
            )
            .count()
        )

        total_likes = (
            self.db.query(WorkRecord)
            .filter(
                and_(
                    WorkRecord.employee_id.in_(employee_ids),
                    WorkRecord.action_type == "like",
                    WorkRecord.status == "success",
                )
            )
            .count()
        )

        total_comments = (
            self.db.query(WorkRecord)
            .filter(
                and_(
                    WorkRecord.employee_id.in_(employee_ids),
                    WorkRecord.action_type == "comment",
                    WorkRecord.status == "success",
                )
            )
            .count()
        )

        # 今日统计
        today = datetime.now().date()
        today_follows = (
            self.db.query(WorkRecord)
            .filter(
                and_(
                    WorkRecord.employee_id.in_(employee_ids),
                    WorkRecord.action_type == "follow",
                    WorkRecord.status == "success",
                    func.date(WorkRecord.created_at) == today,
                )
            )
            .count()
        )

        today_likes = (
            self.db.query(WorkRecord)
            .filter(
                and_(
                    WorkRecord.employee_id.in_(employee_ids),
                    WorkRecord.action_type == "like",
                    WorkRecord.status == "success",
                    func.date(WorkRecord.created_at) == today,
                )
            )
            .count()
        )

        today_comments = (
            self.db.query(WorkRecord)
            .filter(
                and_(
                    WorkRecord.employee_id.in_(employee_ids),
                    WorkRecord.action_type == "comment",
                    WorkRecord.status == "success",
                    func.date(WorkRecord.created_at) == today,
                )
            )
            .count()
        )

        # 成功率
        total_attempts = (
            self.db.query(WorkRecord)
            .filter(WorkRecord.employee_id.in_(employee_ids))
            .count()
        )

        successful_attempts = (
            self.db.query(WorkRecord)
            .filter(
                and_(
                    WorkRecord.employee_id.in_(employee_ids),
                    WorkRecord.status == "success",
                )
            )
            .count()
        )

        success_rate = (
            (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
        )

        # 平台统计
        platform_stats = {}
        platforms = ["xiaohongshu", "douyin"]
        for platform in platforms:
            platform_count = (
                self.db.query(WorkRecord)
                .filter(
                    and_(
                        WorkRecord.employee_id.in_(employee_ids),
                        WorkRecord.platform == platform,
                        WorkRecord.status == "success",
                    )
                )
                .count()
            )
            platform_stats[platform] = platform_count

        # 员工统计
        employee_stats = []
        employees = self.db.query(User).filter(User.parent_id == user_admin_id).all()
        for employee in employees:
            emp_total = (
                self.db.query(WorkRecord)
                .filter(
                    and_(
                        WorkRecord.employee_id == employee.id,
                        WorkRecord.status == "success",
                    )
                )
                .count()
            )

            emp_today = (
                self.db.query(WorkRecord)
                .filter(
                    and_(
                        WorkRecord.employee_id == employee.id,
                        WorkRecord.status == "success",
                        func.date(WorkRecord.created_at) == today,
                    )
                )
                .count()
            )

            employee_stats.append(
                {
                    "employee_id": employee.id,
                    "username": employee.username,
                    "full_name": employee.full_name,
                    "total_work_count": emp_total,
                    "today_work_count": emp_today,
                }
            )

        return {
            "total_follows": total_follows,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "today_follows": today_follows,
            "today_likes": today_likes,
            "today_comments": today_comments,
            "success_rate": round(success_rate, 2),
            "platform_stats": platform_stats,
            "employee_stats": employee_stats,
        }

    def export_work_records_to_excel(self, export_request: ExportRequest) -> str:
        """导出工作记录到Excel文件"""
        # 构建查询
        query = self.db.query(WorkRecord).join(User)

        if export_request.user_admin_id:
            query = query.filter(User.parent_id == export_request.user_admin_id)

        if export_request.employee_id:
            query = query.filter(WorkRecord.employee_id == export_request.employee_id)

        if export_request.platform:
            query = query.filter(WorkRecord.platform == export_request.platform)

        if export_request.action_type:
            query = query.filter(WorkRecord.action_type == export_request.action_type)

        if export_request.start_date:
            query = query.filter(WorkRecord.created_at >= export_request.start_date)

        if export_request.end_date:
            query = query.filter(WorkRecord.created_at <= export_request.end_date)

        # 获取数据
        records = query.order_by(desc(WorkRecord.created_at)).all()

        # 转换为DataFrame
        data = []
        for record in records:
            data.append(
                {
                    "ID": record.id,
                    "员工用户名": record.employee.username,
                    "员工姓名": record.employee.full_name or "",
                    "平台": record.platform,
                    "操作类型": record.action_type,
                    "目标用户名": record.target_username or "",
                    "目标用户ID": record.target_user_id or "",
                    "目标链接": record.target_url or "",
                    "设备ID": record.device_id or "",
                    "设备名称": record.device_name or "",
                    "状态": record.status,
                    "错误信息": record.error_message or "",
                    "创建时间": record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "执行时间": (
                        record.executed_at.strftime("%Y-%m-%d %H:%M:%S")
                        if record.executed_at
                        else ""
                    ),
                }
            )

        if not data:
            raise HTTPException(status_code=404, detail="没有找到符合条件的数据")

        df = pd.DataFrame(data)

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"work_records_{timestamp}.xlsx"

        # 确保导出目录存在
        export_dir = Path("exports")
        export_dir.mkdir(exist_ok=True)

        filepath = export_dir / filename

        # 导出到Excel
        with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="工作记录", index=False)

            # 设置列宽
            worksheet = writer.sheets["工作记录"]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

        return str(filepath)

    def delete_work_record(self, record_id: int) -> bool:
        """删除工作记录"""
        record = self.db.query(WorkRecord).filter(WorkRecord.id == record_id).first()
        if not record:
            return False

        self.db.delete(record)
        self.db.commit()
        return True

    def get_work_record_count(
        self,
        employee_id: Optional[int] = None,
        platform: Optional[str] = None,
        action_type: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        """获取工作记录总数"""
        query = self.db.query(WorkRecord)

        if employee_id:
            query = query.filter(WorkRecord.employee_id == employee_id)

        if platform:
            query = query.filter(WorkRecord.platform == platform)

        if action_type:
            query = query.filter(WorkRecord.action_type == action_type)

        if status:
            query = query.filter(WorkRecord.status == status)

        if start_date:
            query = query.filter(WorkRecord.created_at >= start_date)

        if end_date:
            query = query.filter(WorkRecord.created_at <= end_date)

        return query.count()
