from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.task import Task
from src.models.column import Column
from src.schemas.tasks import TaskCreate, TaskUpdate


def get_task(db: Session, task_id: int) -> Task | None:
    return db.get(Task, task_id)


def get_all_tasks(db: Session, project_id: int | None = None) -> list[Task]:
    q = db.query(Task)
    if project_id:
        q = q.join(Column).filter(Column.project_id == project_id)
    return q.order_by(Task.position.asc()).all()


def create_task(db: Session, data: TaskCreate, user_id: int) -> Task:
    task_data = data.model_dump()
    task_data["created_by"] = user_id
    if task_data.get("assigned_to") is None:
        task_data["assigned_to"] = user_id
    
    # Calculate next position
    max_pos = db.query(func.max(Task.position)).filter(Task.column_id == data.column_id).scalar()
    task_data["position"] = (max_pos if max_pos is not None else -1) + 1

    obj = Task(**task_data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def move_task(db: Session, task_id: int, new_column_id: int, new_position: int) -> Task | None:
    task = get_task(db, task_id)
    if not task:
        return None
    
    old_column_id = task.column_id
    old_position = task.position

    if old_column_id == new_column_id:
        if old_position == new_position:
            return task
        
        if old_position < new_position:
            # Shift items down (decrement index of items in between)
            db.query(Task).filter(
                Task.column_id == old_column_id,
                Task.position > old_position,
                Task.position <= new_position
            ).update({Task.position: Task.position - 1}, synchronize_session=False)
        else:
            # Shift items up (increment index of items in between)
            db.query(Task).filter(
                Task.column_id == old_column_id,
                Task.position >= new_position,
                Task.position < old_position
            ).update({Task.position: Task.position + 1}, synchronize_session=False)
    else:
        # Close gap in old column
        db.query(Task).filter(
            Task.column_id == old_column_id,
            Task.position > old_position
        ).update({Task.position: Task.position - 1}, synchronize_session=False)

        # Make room in new column
        db.query(Task).filter(
            Task.column_id == new_column_id,
            Task.position >= new_position
        ).update({Task.position: Task.position + 1}, synchronize_session=False)

    task.column_id = new_column_id
    task.position = new_position
    db.commit()
    db.refresh(task)
    return task


def update_task(db: Session, task_id: int, data: TaskUpdate) -> Task | None:
    obj = get_task(db, task_id)
    if not obj:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


def delete_task(db: Session, task_id: int) -> Task | None:
    obj = get_task(db, task_id)
    if not obj:
        return None
    db.delete(obj)
    db.commit()
    return obj
