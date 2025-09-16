# Import all models to ensure they are registered with SQLAlchemy
from .project import Project
from .fmea import FMEA
from .nonconformance import NonConformance
from .user import User
from .change_control import ChangeControl
from .capa import CAPA

 
__all__ = ["Project", "FMEA", "NonConformance", "User", "ChangeControl", "CAPA"] 