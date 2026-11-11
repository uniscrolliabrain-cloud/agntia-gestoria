from .service import Service
from .imports import Imports
from .jobs import Jobs
from .commands import Commands
from .attachments import Attachments


class Adapter(Service,Imports,Jobs,Commands,Attachments):
    """Business operations composed over one scoped registry and one local store."""
