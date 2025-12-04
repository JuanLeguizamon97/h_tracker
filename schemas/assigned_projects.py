from pydantic import BaseModel

# Base: lo que tiene realmente la tabla
class AssignedProjectBase(BaseModel):
    project_id: int
    client_id: int
    active: bool = True

# Para creación (POST). Aquí decides si employee_id viene del body o del token
class AssignedProjectCreate(AssignedProjectBase):
    # Si lo asignas automáticamente al empleado logueado, puedes omitirlo aquí
    employee_id: int | None = None  

# Respuesta completa (para administración, por ejemplo)
class AssignedProjectOut(AssignedProjectBase):
    id: int
    employee_id: int

    class Config:
        from_attributes = True

# Versión "ligera" para tu vista de Project Design (solo lo que mostrarás en pantalla)
class ProjectDesignOut(BaseModel):
    project_id: int
    employee_id: int
    active: bool

    class Config:
        from_attributes = True
