'''
Visualization preferences.
'''

# private variables
_curveResolution: int = 64
_viewportFontSize: int = 20
_viewportForeground: tuple[float, float, float] = (1.0, 1.0, 1.0)
_viewportBackground1: tuple[float, float, float] = (0.7, 0.8, 0.9)
_viewportBackground2: tuple[float, float, float] = (0.1, 0.2, 0.3)
_meshLineVisibility: bool = True
_meshCellColor: tuple[float, float, float] = (1.0, 1.0, 0.8)
_meshLineColor: tuple[float, float, float] = (0.0, 0.0, 0.0)
_selectionPointSize: int = 8
_selectionLineWidth: int = 2
_nodeSetColor: tuple[float, float, float] = (1.0, 0.0, 0.0)
_elementSetColor: tuple[float, float, float] = (1.0, 0.0, 0.0)

# public getters
def getCurveResolution(): return _curveResolution
def getViewportFontSize(): return _viewportFontSize
def getViewportForeground(): return _viewportForeground
def getViewportBackground1(): return _viewportBackground1
def getViewportBackground2(): return _viewportBackground2
def getMeshLineVisibility(): return _meshLineVisibility
def getMeshCellColor(): return _meshCellColor
def getMeshLineColor(): return _meshLineColor
def getSelectionPointSize(): return _selectionPointSize
def getSelectionLineWidth(): return _selectionLineWidth
def getNodeSetColor(): return _nodeSetColor
def getElementSetColor(): return _elementSetColor
