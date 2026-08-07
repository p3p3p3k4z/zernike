"""
gui/components
==============
Paquete de componentes GUI independientes y reutilizables.
"""

from gui.components.parameter_panel import ParameterInputPanel
from gui.components.summary_tables import SummaryTablesWidget
from gui.components.menu_bar import AppMenuBar
from gui.components.control_bar_3d import ControlBar3D
from gui.components.base_3d_dialog import Base3DPlotDialog
from gui.components.preset_manager import PresetManagerDialog, PresetStorage

__all__ = [
    "ParameterInputPanel",
    "SummaryTablesWidget",
    "AppMenuBar",
    "ControlBar3D",
    "Base3DPlotDialog",
    "PresetManagerDialog",
    "PresetStorage",
]



