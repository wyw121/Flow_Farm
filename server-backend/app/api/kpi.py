"""
KPI工作记录相关API路由
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..api.auth import get_current_user, require_user_admin_or_above
from ..database import get_db
from ..models import AuditLog, User
from ..schemas import (
    ExportRequest,
    ExportResponse,
    WorkRecordCreate,
    WorkRecordResponse,
    WorkRecordUpdate,
)
from ..services.work_record_service import WorkRecordService

router = APIRouter()


@router.post("/", response_model=WorkRecordResponse)
async def create_work_record(
    record_data: WorkRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建工作记录"""
    work_service = WorkRecordService(db)

    # 权限检查：只有员工能创建自己的工作记录，或管理员为其员工创建
    if current_user.role == "employee":
        if record_data.employee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="只能创建自己的工作记录"
            )
    elif current_user.role in ["user_admin", "system_admin"]:
        # 管理员可以为下属员工创建记录，这里暂时允许
        pass

    record = work_service.create_work_record(record_data)

    # 记录审计日志
    audit_log = AuditLog(
        user_id=current_user.id,
        action="create_work_record",
        resource_type="work_record",
        resource_id=str(record.id),
        details={
            "employee_id": record.employee_id,
            "platform": record.platform,
            "action_type": record.action_type,
        },
    )
    db.add(audit_log)
    db.commit()

    return WorkRecordResponse.from_orm(record)


@router.get("/", response_model=List[WorkRecordResponse])
async def get_work_records(
    employee_id: Optional[int] = Query(None),
    platform: Optional[str] = Query(None),
    action_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取工作记录列表"""
    work_service = WorkRecordService(db)

    # 权限检查
    if current_user.role == "employee":
        # 员工只能查看自己的记录
        employee_id = current_user.id
        records = work_service.get_work_records(
            employee_id=employee_id,
            platform=platform,
            action_type=action_type,
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=skip,
        )
    elif current_user.role == "user_admin":
        # 用户管理员查看自己下属的记录
        if employee_id:
            # 检查该员工是否属于当前管理员
            from ..services.user_service import UserService

            user_service = UserService(db)
            employee = user_service.get_user_by_id(employee_id)
            if not employee or employee.parent_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无权查看该员工的工作记录",
                )
            records = work_service.get_work_records(
                employee_id=employee_id,
                platform=platform,
                action_type=action_type,
                status=status,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                offset=skip,
            )
        else:
            # 查看所有下属的记录
            records = work_service.get_work_records_by_user_admin(
                user_admin_id=current_user.id,
                platform=platform,
                action_type=action_type,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
                offset=skip,
            )
    else:  # system_admin
        # 系统管理员可以查看所有记录
        records = work_service.get_work_records(
            employee_id=employee_id,
            platform=platform,
            action_type=action_type,
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=skip,
        )

    return [WorkRecordResponse.from_orm(record) for record in records]


@router.put("/{record_id}", response_model=WorkRecordResponse)
async def update_work_record(
    record_id: int,
    record_data: WorkRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新工作记录"""
    work_service = WorkRecordService(db)

    # 获取原记录进行权限检查
    record = work_service.get_work_records(limit=1, offset=0)
    original_record = None
    for r in record:
        if r.id == record_id:
            original_record = r
            break

    if not original_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="工作记录不存在"
        )

    # 权限检查
    if current_user.role == "employee":
        if original_record.employee_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="只能更新自己的工作记录"
            )
    elif current_user.role == "user_admin":
        # 检查该记录的员工是否属于当前管理员
        from ..services.user_service import UserService

        user_service = UserService(db)
        employee = user_service.get_user_by_id(original_record.employee_id)
        if not employee or employee.parent_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="无权更新该工作记录"
            )

    updated_record = work_service.update_work_record(record_id, record_data)
    if not updated_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="工作记录不存在"
        )

    # 记录审计日志
    audit_log = AuditLog(
        user_id=current_user.id,
        action="update_work_record",
        resource_type="work_record",
        resource_id=str(record_id),
        details=record_data.dict(exclude_unset=True),
    )
    db.add(audit_log)
    db.commit()

    return WorkRecordResponse.from_orm(updated_record)


@router.delete("/{record_id}")
async def delete_work_record(
    record_id: int,
    current_user: User = Depends(require_user_admin_or_above),
    db: Session = Depends(get_db),
):
    """删除工作记录（仅管理员）"""
    work_service = WorkRecordService(db)

    success = work_service.delete_work_record(record_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="工作记录不存在"
        )

    # 记录审计日志
    audit_log = AuditLog(
        user_id=current_user.id,
        action="delete_work_record",
        resource_type="work_record",
        resource_id=str(record_id),
    )
    db.add(audit_log)
    db.commit()

    return {"message": "工作记录删除成功"}


@router.get("/statistics/user-admin/{user_admin_id}")
async def get_user_admin_work_statistics(
    user_admin_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户管理员的工作统计"""
    work_service = WorkRecordService(db)

    # 权限检查
    if current_user.role == "user_admin":
        if user_admin_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="无权查看其他管理员的统计"
            )
    elif current_user.role == "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="员工无权查看统计信息"
        )

    stats = work_service.get_work_statistics_by_user_admin(user_admin_id)
    return stats


@router.post("/export", response_model=ExportResponse)
async def export_work_records(
    export_request: ExportRequest,
    current_user: User = Depends(require_user_admin_or_above),
    db: Session = Depends(get_db),
):
    """导出工作记录到Excel"""
    work_service = WorkRecordService(db)

    # 权限检查
    if current_user.role == "user_admin":
        # 用户管理员只能导出自己管理的员工数据
        export_request.user_admin_id = current_user.id

    try:
        filepath = work_service.export_work_records_to_excel(export_request)

        # 记录审计日志
        audit_log = AuditLog(
            user_id=current_user.id,
            action="export_work_records",
            resource_type="work_record",
            details=export_request.dict(exclude_unset=True),
        )
        db.add(audit_log)
        db.commit()

        return ExportResponse(
            download_url=f"/api/v1/kpi/download/{filepath.split('/')[-1]}",
            filename=filepath.split("/")[-1],
            expires_at=datetime.now().replace(hour=23, minute=59, second=59),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导出失败: {str(e)}",
        )


@router.get("/download/{filename}")
async def download_exported_file(
    filename: str, current_user: User = Depends(require_user_admin_or_above)
):
    """下载导出的文件"""
    filepath = f"exports/{filename}"

    try:
        return FileResponse(
            path=filepath,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=filename,
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在或已过期"
        )
