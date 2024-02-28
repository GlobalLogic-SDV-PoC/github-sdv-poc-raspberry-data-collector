from src.enums.run_modes import RunModes
from src.config.run_modes.modes.strict_run_mode import StrictRunMode
from src.config.run_modes.modes.debug_run_mode import DebugRunMode


class ModesProvider:
    MAPPER = {
        RunModes.STRICT: StrictRunMode, 
        RunModes.DEBUG: DebugRunMode
    }

    @classmethod
    def get_mode(cls, mode):

        _mode = cls.MAPPER.get(mode)
        if _mode is None:
            raise NotImplementedError(f"Run Mode '{mode}' is not registered")

        return _mode