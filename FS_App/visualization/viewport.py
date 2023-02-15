import vtkmodules.vtkRenderingContextOpenGL2 # type: ignore (initialize VTK)
import visualization.utility as vu
from typing import Literal, Any, cast
from collections.abc import Callable, Sequence
from dataModel import (
    Mesh, NodeSet, ElementSet, ConcentratedLoad, BoundaryCondition, ModelDatabase, BodyLoad, SurfaceSet, Pressure,
    SurfaceTraction, DataObject
)
from visualization.decoration import Triad, Info, ScalarBar, PointLabel, Colormaps
from visualization.rendering import (
    RenderObject, GridRenderObject, PointsRenderObject, CellsRenderObject, ArrowsRenderObject, GroupRenderObject
)
from visualization.interaction import (
    Views, InteractionStyles, InteractionStyle, RotateInteractionStyle, PanInteractionStyle, ZoomInteractionStyle,
    PickSingleInteractionStyle, PickMultipleInteractionStyle, ProbeInteractionStyle, RulerInteractionStyle
)
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor # type: ignore
from vtkmodules.vtkCommonCore import vtkObject
from vtkmodules.vtkCommonDataModel import vtkCell
from vtkmodules.vtkIOImage import vtkPNGWriter
from vtkmodules.vtkRenderingCore import vtkRenderer, vtkRenderWindow, vtkRenderWindowInteractor, vtkWindowToImageFilter

class Viewport(QFrame):
    '''
    Visualization viewport based on VTK.
    '''

    # class variables
    _callbacks: dict[int, Callable[[str, Any], None]] = {}
    _viewports: list['Viewport'] = []
    _currentInteractionStyle: InteractionStyles = InteractionStyles.Rotate
    _gridLinesVisible: bool = True
    _gridLineWidth: float = 1.5
    _gridLineColor: tuple[float, float, float] = (0.0, 0.0, 0.0)
    _gridCellRepresentation: Literal['Surface', 'Wireframe'] = 'Surface'
    _gridCellColor: tuple[float, float, float] = (0.0, 0.5, 1.0)
    _pointGlyphScale: float = 0.004
    _arrowGlyphScale: float = 0.020
    _projection: Literal['Perspective', 'Parallel'] = 'Perspective'
    _lighting: Literal['On', 'Off'] = 'On'
    _background1: tuple[float, float, float] = (0.1, 0.2, 0.3)
    _background2: tuple[float, float, float] = (0.6, 0.7, 0.8)
    _foreground: tuple[float, float, float] = (1.0, 1.0, 1.0)
    _fontSize: int = 20
    _deformationScaleFactor: float = 1.0
    _showMaxPointLabel: bool = False
    _showMinPointLabel: bool = False
    _useCustomLimits: bool = False
    _defaultMaxLimit: float = 1.0
    _defaultMinLimit: float = 0.0
    _customMaxLimit: float = 1.0
    _customMinLimit: float = 0.0
    _scalarBarNumberFormat: Literal['Scientific', 'Fixed'] = 'Scientific'
    _scalarBarDecimalPlaces: int = 3
    _colormap: Colormaps = Colormaps.Jet
    _colormapIntervals: int = 12
    _reverseColormap: bool = False

    @classmethod
    def registerCallback(cls, callback: Callable[[str, Any], None]) -> int:
        '''
        Adds the specified callback function to the internal container of callbacks.
        Returns a key used to deregister the callback.
        '''
        key: int = 0
        while key in cls._callbacks: key += 1
        cls._callbacks[key] = callback
        return key

    @classmethod
    def deregisterCallback(cls, key: int) -> None:
        '''Removes the callback function from the internal container of callbacks using its key.'''
        del cls._callbacks[key]

    @classmethod
    def notifyOptionChanged(cls, optionName: str, optionValue: Any) -> None:
        '''This method is called when a viewport option has changed its value.'''
        for callback in cls._callbacks.values(): callback(optionName, optionValue)

    @classmethod
    def setInteractionStyle(cls, interactionStyle: InteractionStyles) -> None:
        '''Sets the viewport interaction style for all viewports.'''
        cls._currentInteractionStyle = interactionStyle
        for viewport in cls._viewports:
            viewport._interactor.SetInteractorStyle(viewport._interactionStyles[cls._currentInteractionStyle].base)
            viewport._interactor.RemoveObservers('CharEvent')
        cls.notifyOptionChanged('InteractionStyle', cls._currentInteractionStyle)

    @classmethod
    def gridLinesVisible(cls) -> bool:
        '''Gets the grid line visibility.'''
        return cls._gridLinesVisible

    @classmethod
    def setGridLinesVisible(cls, value: bool) -> None:
        '''Sets the grid line visibility.'''
        cls._gridLinesVisible = value
        for viewport in cls._viewports:
            if viewport._gridRenderObject:
                viewport._gridRenderObject.setLinesVisible(cls._gridLinesVisible)
            if isinstance(viewport._selectionRenderObject, CellsRenderObject):
                viewport._selectionRenderObject.setLinesVisible(cls._gridLinesVisible)
            viewport.render()
        cls.notifyOptionChanged('GridLinesVisible', cls._gridLinesVisible)

    @classmethod
    def gridLineWidth(cls) -> float:
        '''Gets the grid line width.'''
        return cls._gridLineWidth

    @classmethod
    def setGridLineWidth(cls, value: float) -> None:
        '''Sets the grid line width.'''
        InteractionStyle.setGridLineWidth(value)
        cls._gridLineWidth = value
        for viewport in cls._viewports:
            if viewport._gridRenderObject:
                viewport._gridRenderObject.setLineWidth(cls._gridLineWidth)
            if isinstance(viewport._selectionRenderObject, CellsRenderObject):
                viewport._selectionRenderObject.setLineWidth(cls._gridLineWidth)
            viewport.render()
        cls.notifyOptionChanged('GridLineWidth', cls._gridLineWidth)

    @classmethod
    def gridLineColor(cls) -> tuple[float, float, float]:
        '''Gets the grid line color.'''
        return cls._gridLineColor

    @classmethod
    def setGridLineColor(cls, value: tuple[float, float, float]) -> None:
        '''Sets the grid line color.'''
        cls._gridLineColor = value
        for viewport in cls._viewports:
            if viewport._gridRenderObject:
                viewport._gridRenderObject.setLineColor(cls._gridLineColor)
            if isinstance(viewport._selectionRenderObject, CellsRenderObject):
                viewport._selectionRenderObject.setLineColor(cls._gridLineColor)
            viewport.render()
        cls.notifyOptionChanged('GridLineColor', cls._gridLineColor)

    @classmethod
    def gridCellRepresentation(cls) -> Literal['Surface', 'Wireframe']:
        '''Gets the grid cell representation.'''
        return cls._gridCellRepresentation

    @classmethod
    def setGridCellRepresentation(cls, value: Literal['Surface', 'Wireframe']) -> None:
        '''Sets the grid cell representation.'''
        cls._gridCellRepresentation = value
        for viewport in cls._viewports:
            if viewport._gridRenderObject:
                viewport._gridRenderObject.setCellRepresentation(cls._gridCellRepresentation)
            viewport.render()
        cls.notifyOptionChanged('GridCellRepresentation', cls._gridCellRepresentation)

    @classmethod
    def gridCellColor(cls) -> tuple[float, float, float]:
        '''Gets the grid cell color.'''
        return cls._gridCellColor

    @classmethod
    def setGridCellColor(cls, value: tuple[float, float, float]) -> None:
        '''Sets the grid cell color.'''
        cls._gridCellColor = value
        for viewport in cls._viewports:
            if viewport._gridRenderObject:
                viewport._gridRenderObject.setCellColor(cls._gridCellColor)
            viewport.render()
        cls.notifyOptionChanged('GridCellColor', cls._gridCellColor)

    @classmethod
    def pointGlyphScale(cls) -> float:
        '''Gets the point glyph scale.'''
        return cls._pointGlyphScale

    @classmethod
    def setPointGlyphScale(cls, value: float) -> None:
        '''Sets the point glyph scale.'''
        InteractionStyle.setPointGlyphScale(value)
        cls._pointGlyphScale = value
        for viewport in cls._viewports:
            InteractionStyle.recomputeGlyphSize(viewport._renderer)
        cls.notifyOptionChanged('PointGlyphScale', cls._pointGlyphScale)

    @classmethod
    def arrowGlyphScale(cls) -> float:
        '''Gets the arrow glyph scale.'''
        return cls._arrowGlyphScale

    @classmethod
    def setArrowGlyphScale(cls, value: float) -> None:
        '''Sets the arrow glyph scale.'''
        InteractionStyle.setArrowGlyphScale(value)
        cls._arrowGlyphScale = value
        for viewport in cls._viewports:
            InteractionStyle.recomputeGlyphSize(viewport._renderer)
        cls.notifyOptionChanged('ArrowGlyphScale', cls._arrowGlyphScale)

    @classmethod
    def projection(cls) -> Literal['Perspective', 'Parallel']:
        '''Gets the projection type.'''
        return cls._projection

    @classmethod
    def setProjection(cls, value: Literal['Perspective', 'Parallel']) -> None:
        '''Sets the projection type.'''
        cls._projection = value
        for viewport in cls._viewports:
            viewport._renderer.GetActiveCamera().SetParallelProjection(cls._projection == 'Parallel')
            viewport.render()
        cls.notifyOptionChanged('Projection', cls._projection)

    @classmethod
    def lighting(cls) -> Literal['On', 'Off']:
        '''Gets the lighting flag.'''
        return cls._lighting

    @classmethod
    def setLighting(cls, value: Literal['On', 'Off']) -> None:
        '''Sets the lighting flag.'''
        cls._lighting = value
        for viewport in cls._viewports:
            if viewport._gridRenderObject:
                viewport._gridRenderObject.setLighting(cls._lighting)
            viewport.render()
        cls.notifyOptionChanged('Lighting', cls._lighting)

    @classmethod
    def background1(cls) -> tuple[float, float, float]:
        '''Gets the background 1 (top color).'''
        return cls._background1

    @classmethod
    def setBackground1(cls, value: tuple[float, float, float]) -> None:
        '''Sets the background 1 (top color).'''
        cls._background1 = value
        for viewport in cls._viewports:
            viewport._renderer.SetBackground2(cls._background1)
            viewport.render()
        cls.notifyOptionChanged('Background1', cls._background1)

    @classmethod
    def background2(cls) -> tuple[float, float, float]:
        '''Gets the background 2 (bottom color).'''
        return cls._background2

    @classmethod
    def setBackground2(cls, value: tuple[float, float, float]) -> None:
        '''Sets the background 2 (top color).'''
        cls._background2 = value
        for viewport in cls._viewports:
            viewport._renderer.SetBackground(cls._background2)
            viewport.render()
        cls.notifyOptionChanged('Background2', cls._background2)

    @classmethod
    def foreground(cls) -> tuple[float, float, float]:
        '''Gets the foreground color.'''
        return cls._foreground

    @classmethod
    def setForeground(cls, value: tuple[float, float, float]) -> None:
        '''Sets the foreground color.'''
        InteractionStyle.setForeground(value)
        cls._foreground = value
        for viewport in cls._viewports:
            viewport._triad.setTextColor(cls._foreground)
            viewport._info.setTextColor(cls._foreground)
            viewport._scalarBar.setTextColor(cls._foreground)
            viewport._maxPointLabel.setColor(cls._foreground)
            viewport._minPointLabel.setColor(cls._foreground)
            viewport.render()
        cls.notifyOptionChanged('Foreground', cls._foreground)

    @classmethod
    def fontSize(cls) -> int:
        '''Gets the font size.'''
        return cls._fontSize

    @classmethod
    def setFontSize(cls, value: int) -> None:
        '''Sets the font size.'''
        cls._fontSize = value
        for viewport in cls._viewports:
            viewport._triad.setFontSize(cls._fontSize)
            viewport._info.setFontSize(cls._fontSize)
            viewport._scalarBar.setFontSize(cls._fontSize)
            viewport._maxPointLabel.setFontSize(cls._fontSize)
            viewport._minPointLabel.setFontSize(cls._fontSize)
            viewport.render()
        cls.notifyOptionChanged('FontSize', cls._fontSize)

    @classmethod
    def deformationScaleFactor(cls) -> float:
        '''Gets the deformation scale factor.'''
        return cls._deformationScaleFactor

    @classmethod
    def setDeformationScaleFactor(cls, value: float) -> None:
        '''Sets the deformation scale factor.'''
        cls._deformationScaleFactor = value
        for viewport in cls._viewports:
            if viewport._gridRenderObject:
                gridRenderObject: GridRenderObject = viewport._gridRenderObject
                gridRenderObject.setPointDisplacements(None, cls._deformationScaleFactor)
                viewport._maxPointLabel.setPosition(gridRenderObject.dataSet.GetPoint(viewport._maxPointIndex))
                viewport._minPointLabel.setPosition(gridRenderObject.dataSet.GetPoint(viewport._minPointIndex))
            viewport.render()
        cls.notifyOptionChanged('DeformationScaleFactor', cls._deformationScaleFactor)

    @classmethod
    def showMaxPointLabel(cls) -> bool:
        '''Gets the show max point label flag.'''
        return cls._showMaxPointLabel

    @classmethod
    def setShowMaxPointLabel(cls, value: bool) -> None:
        '''Sets the show max point label flag.'''
        cls._showMaxPointLabel = value
        for viewport in cls._viewports:
            viewport._maxPointLabel.setVisible(viewport._scalarBar.visible() and cls._showMaxPointLabel)
            viewport.render()
        cls.notifyOptionChanged('ShowMaxPointLabel', cls._showMaxPointLabel)

    @classmethod
    def showMinPointLabel(cls) -> bool:
        '''Gets the show min point label flag.'''
        return cls._showMinPointLabel

    @classmethod
    def setShowMinPointLabel(cls, value: bool) -> None:
        '''Sets the show min point label flag.'''
        cls._showMinPointLabel = value
        for viewport in cls._viewports:
            viewport._minPointLabel.setVisible(viewport._scalarBar.visible() and cls._showMinPointLabel)
            viewport.render()
        cls.notifyOptionChanged('ShowMinPointLabel', cls._showMinPointLabel)

    @classmethod
    def useCustomLimits(cls) -> bool:
        '''Gets the use custom limits flag.'''
        return cls._useCustomLimits

    @classmethod
    def setUseCustomLimits(cls, value: bool) -> None:
        '''Sets the use custom limits flag.'''
        cls._useCustomLimits = value
        for viewport in cls._viewports:
            if viewport._gridRenderObject:
                max = cls._customMaxLimit if cls._useCustomLimits else cls._defaultMaxLimit
                min = cls._customMinLimit if cls._useCustomLimits else cls._defaultMinLimit
                viewport._gridRenderObject.setNodalScalarFieldRange(min, max)
            viewport.render()
        if not cls._useCustomLimits:
            Viewport.setCustomMaxLimit(cls._defaultMaxLimit)
            Viewport.setCustomMinLimit(cls._defaultMinLimit)
        cls.notifyOptionChanged('UseCustomLimits', cls._useCustomLimits)

    @classmethod
    def customMaxLimit(cls) -> float:
        '''Gets the custom max limit.'''
        return cls._customMaxLimit

    @classmethod
    def setCustomMaxLimit(cls, value: float) -> None:
        '''Sets the custom max limit.'''
        if value < cls._customMinLimit: cls.setCustomMinLimit(value) # raise ValueError('bad range')
        cls._customMaxLimit = value
        if cls._useCustomLimits:
            for viewport in cls._viewports:
                if viewport._gridRenderObject:
                    viewport._gridRenderObject.setNodalScalarFieldRange(cls._customMinLimit, cls._customMaxLimit)
                viewport.render()
        cls.notifyOptionChanged('CustomMaxLimit', cls._customMaxLimit)

    @classmethod
    def customMinLimit(cls) -> float:
        '''Gets the custom min limit.'''
        return cls._customMinLimit

    @classmethod
    def setCustomMinLimit(cls, value: float) -> None:
        '''Sets the custom min limit.'''
        if value > cls._customMaxLimit: cls.setCustomMaxLimit(value) # raise ValueError('bad range')
        cls._customMinLimit = value
        if cls._useCustomLimits:
            for viewport in cls._viewports:
                if viewport._gridRenderObject:
                    viewport._gridRenderObject.setNodalScalarFieldRange(cls._customMinLimit, cls._customMaxLimit)
                viewport.render()
        cls.notifyOptionChanged('CustomMinLimit', cls._customMinLimit)

    @classmethod
    def scalarBarNumberFormat(cls) -> Literal['Scientific', 'Fixed']:
        '''Gets the scalar bar number format.'''
        return cls._scalarBarNumberFormat

    @classmethod
    def setScalarBarNumberFormat(cls, value: Literal['Scientific', 'Fixed']) -> None:
        '''Gets the scalar bar number format.'''
        cls._scalarBarNumberFormat = value
        for viewport in cls._viewports:
            viewport._scalarBar.setNumberFormat(cls._scalarBarNumberFormat)
            viewport.render()
        cls.notifyOptionChanged('ScalarBarNumberFormat', cls._scalarBarNumberFormat)

    @classmethod
    def scalarBarDecimalPlaces(cls) -> int:
        '''Gets the scalar bar decimal places.'''
        return cls._scalarBarDecimalPlaces

    @classmethod
    def setScalarBarDecimalPlaces(cls, value: int) -> None:
        '''Gets the scalar bar decimal places.'''
        cls._scalarBarDecimalPlaces = value
        for viewport in cls._viewports:
            viewport._scalarBar.setDecimalPlaces(cls._scalarBarDecimalPlaces)
            viewport.render()
        cls.notifyOptionChanged('ScalarBarDecimalPlaces', cls._scalarBarDecimalPlaces)

    @classmethod
    def colormap(cls) -> Colormaps:
        '''Gets the current colormap.'''
        return cls._colormap

    @classmethod
    def setColormap(cls, value: Colormaps | str) -> None:
        '''Sets the current colormap.'''
        if isinstance(value, str): value = Colormaps[value]
        cls._colormap = value
        for viewport in cls._viewports:
            viewport._scalarBar.setColormap(cls._colormap, cls._colormapIntervals, cls._reverseColormap)
            viewport.render()
        cls.notifyOptionChanged('Colormap', cls._colormap)

    @classmethod
    def colormapIntervals(cls) -> int:
        '''Gets the number of colormap colors.'''
        return cls._colormapIntervals

    @classmethod
    def setColormapIntervals(cls, value: int) -> None:
        '''Sets the number of colormap colors.'''
        cls._colormapIntervals = value
        for viewport in cls._viewports:
            viewport._scalarBar.setColormap(cls._colormap, cls._colormapIntervals, cls._reverseColormap)
            viewport.render()
        cls.notifyOptionChanged('ColormapIntervals', cls._colormapIntervals)

    @classmethod
    def reverseColormap(cls) -> bool:
        '''Gets the reverse colormap flag.'''
        return cls._reverseColormap

    @classmethod
    def setReverseColormap(cls, value: bool) -> None:
        '''Sets the reverse colormap flag.'''
        cls._reverseColormap = value
        for viewport in cls._viewports:
            viewport._scalarBar.setColormap(cls._colormap, cls._colormapIntervals, cls._reverseColormap)
            viewport.render()
        cls.notifyOptionChanged('ReverseColormap', cls._reverseColormap)

    @classmethod
    def setPickAction(
        cls,
        onPicked: Callable[[Sequence[int], bool], None] | None,
        pickTarget: Literal['Points', 'Cells'] | None
    ) -> None:
        '''Sets the pick action on the current interaction style.'''
        for viewport in cls._viewports:
            viewport._interactionStyles[cls._currentInteractionStyle].setPickAction(onPicked, pickTarget)

    @property
    def info(self) -> Info:
        '''The viewport information object.'''
        return self._info

    # attribute slots
    __slots__ = (
        '_layout', '_vtkWidget', '_renderer', '_renderWindow', '_interactor', '_interactionStyles', '_triad', '_info',
        '_scalarBar', '_gridRenderObject', '_selectionRenderObject', '_maxPointIndex', '_minPointIndex',
        '_maxPointLabel', '_minPointLabel'
    )

    def __init__(self, parent: QWidget | None = None) -> None:
        '''Viewport constructor.'''
        super().__init__(parent)
        vtkObject.GlobalWarningDisplayOn()
        # self (frame)
        self.setStyleSheet('border: 1px solid rgb(185,185,185);')
        # layout
        self._layout: QVBoxLayout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self.setLayout(self._layout)
        # VTK widget
        self._vtkWidget: QVTKRenderWindowInteractor = QVTKRenderWindowInteractor(self)
        self._layout.addWidget(self._vtkWidget)
        # register viewport
        self._viewports.append(self)
        # renderer
        self._renderer: vtkRenderer = vtkRenderer()
        self._renderer.GradientBackgroundOn()
        # render window
        self._renderWindow: vtkRenderWindow = cast(vtkRenderWindow, self._vtkWidget.GetRenderWindow())
        self._renderWindow.AddRenderer(self._renderer)
        # interactor
        self._interactor: vtkRenderWindowInteractor = self._renderWindow.GetInteractor()
        # interactor styles
        self._interactionStyles: dict[InteractionStyles, InteractionStyle] = {
            InteractionStyles.Rotate       : RotateInteractionStyle(),
            InteractionStyles.Pan          : PanInteractionStyle(),
            InteractionStyles.Zoom         : ZoomInteractionStyle(),
            InteractionStyles.PickSingle   : PickSingleInteractionStyle(),
            InteractionStyles.PickMultiple : PickMultipleInteractionStyle(),
            InteractionStyles.Probe        : ProbeInteractionStyle(),
            InteractionStyles.Ruler        : RulerInteractionStyle()
        }
        # triad & info % scalar bar & max/min point labels
        self._triad: Triad = Triad(self._foreground, self._fontSize)
        self._info: Info = Info(self._foreground, self._fontSize)
        self._scalarBar: ScalarBar = ScalarBar(
            self._scalarBarDecimalPlaces,
            self._scalarBarNumberFormat,
            self._foreground,
            self._fontSize
        )
        self._maxPointLabel: PointLabel = PointLabel(self._foreground, self._fontSize)
        self._minPointLabel: PointLabel = PointLabel(self._foreground, self._fontSize)
        self._maxPointLabel.setText('Max')
        self._minPointLabel.setText('Min')
        self._maxPointIndex: int = 0
        self._minPointIndex: int = 0
        # render objects
        self._gridRenderObject: GridRenderObject | None = None
        self._selectionRenderObject: RenderObject | None = None

    def initialize(self) -> None:
        '''Initializes the viewport.'''
        self._renderer.GetActiveCamera().SetParallelProjection(self._projection == 'Parallel')
        self._renderer.SetBackground2(self._background1)
        self._renderer.SetBackground(self._background2)
        self._interactor.Initialize()
        self._triad.initialize(self._interactor)
        self._info.initialize(self._renderer)
        self._scalarBar.initialize(self._renderer)
        self._scalarBar.setVisible(False)
        self._maxPointLabel.initialize(self._renderer)
        self._minPointLabel.initialize(self._renderer)
        self._maxPointLabel.setVisible(False)
        self._minPointLabel.setVisible(False)
        self.setInteractionStyle(self._currentInteractionStyle)

    def finalize(self) -> None:
        '''Finalizes the viewport.'''
        self._vtkWidget.Finalize()

    def print(self, file: str) -> None:
        '''Prints the viewport scene to a file.'''
        # save current background and foreground colors
        background1: tuple[float, float, float] = Viewport.background1()
        background2: tuple[float, float, float] = Viewport.background2()
        foreground: tuple[float, float, float] = Viewport.foreground()
        # set white background and black foreground
        Viewport.setBackground1((1.0, 1.0, 1.0))
        Viewport.setBackground2((1.0, 1.0, 1.0))
        Viewport.setForeground((0.0, 0.0, 0.0))
        # create filter
        filter: vtkWindowToImageFilter = vtkWindowToImageFilter()
        filter.SetInput(self._renderWindow) # type: ignore
        filter.SetInputBufferTypeToRGBA()
        filter.Update() # type: ignore
        # create writer
        writer: vtkPNGWriter = vtkPNGWriter()
        writer.SetInputConnection(filter.GetOutputPort())
        writer.SetFileName(file)
        writer.Update() # type: ignore
        # write
        writer.Write()
        # reset background and foreground colors
        Viewport.setBackground1(background1)
        Viewport.setBackground2(background2)
        Viewport.setForeground(foreground)

    def render(self) -> None:
        '''Renders the current scene.'''
        self._renderWindow.Render()

    def add(self, renderObject: RenderObject, render: bool = True) -> None:
        '''Adds the renderable visualization object to the scene.'''
        for actor in renderObject.actors(): self._renderer.AddActor(actor)
        if isinstance(renderObject, PointsRenderObject):
            InteractionStyle.recomputeGlyphSize(self._renderer, render=False)
        if render: self.render()

    def remove(self, renderObject: RenderObject, render: bool = True) -> None:
        '''Removes the renderable visualization object from the scene.'''
        for actor in renderObject.actors(): self._renderer.RemoveActor(actor)
        if render: self.render()

    def setView(self, view: Views, render: bool = True) -> None:
        '''Sets the camera view.'''
        focalPoint: tuple[float, float, float]
        position:   tuple[float, float, float]
        viewUp:     tuple[float, float, float]
        match view:
            case Views.Front:
                focalPoint = (+0.0, +0.0, +0.0)
                position   = (+0.0, +0.0, +1.0)
                viewUp     = (+0.0, +1.0, +0.0)
            case Views.Back:
                focalPoint = (+0.0, +0.0, +0.0)
                position   = (+0.0, +0.0, -1.0)
                viewUp     = (+0.0, +1.0, +0.0)
            case Views.Top:
                focalPoint = (+0.0, +0.0, +0.0)
                position   = (+0.0, +1.0, +0.0)
                viewUp     = (+0.0, +0.0, -1.0)
            case Views.Bottom:
                focalPoint = (+0.0, +0.0, +0.0)
                position   = (+0.0, -1.0, +0.0)
                viewUp     = (+0.0, +0.0, +1.0)
            case Views.Left:
                focalPoint = (+0.0, +0.0, +0.0)
                position   = (-1.0, +0.0, +0.0)
                viewUp     = (+0.0, +1.0, +0.0)
            case Views.Right:
                focalPoint = (+0.0, +0.0, +0.0)
                position   = (+1.0, +0.0, +0.0)
                viewUp     = (+0.0, +1.0, +0.0)
            case Views.Isometric:
                focalPoint = (+0.0, +0.0, +0.0)
                position   = (+1.0, +1.0, +1.0)
                viewUp     = (+0.0, +1.0, +0.0)
        self._renderer.GetActiveCamera().SetFocalPoint(focalPoint)
        self._renderer.GetActiveCamera().SetPosition(position)
        self._renderer.GetActiveCamera().SetViewUp(viewUp)
        self._renderer.ResetCamera()
        InteractionStyle.recomputeGlyphSize(self._renderer, render=False)
        if render: self.render()

    def setGridRenderObject(self, mesh: Mesh | None, isDeformable: bool, render: bool = True) -> None:
        '''Renders the specified grid.'''
        self._scalarBar.setVisible(False)
        self._maxPointLabel.setVisible(False)
        self._minPointLabel.setVisible(False)
        if self._selectionRenderObject: self.remove(self._selectionRenderObject, render=False)
        if self._gridRenderObject: self.remove(self._gridRenderObject, render=False)
        self._gridRenderObject = GridRenderObject(
            mesh,
            isDeformable,
            self._scalarBar.lookupTable,
            self._gridLinesVisible,
            self._gridLineWidth,
            self._gridLineColor,
            self._gridCellRepresentation,
            self._gridCellColor,
            self._lighting
        ) if mesh else None
        if self._gridRenderObject: self.add(self._gridRenderObject, render=False)
        if render: self.render()

    def setGridDeformation(
        self,
        nodalDisplacements: tuple[tuple[float, float, float], ...] | None,
        render: bool = True
    ) -> None:
        '''Sets the deformation on the currently drawn grid.'''
        if not self._gridRenderObject: return
        if not nodalDisplacements:
            nodalDisplacements = tuple(
                (0.0, 0.0, 0.0) for _ in range(self._gridRenderObject.dataSet.GetNumberOfPoints())
            )
        self._gridRenderObject.setPointDisplacements(nodalDisplacements, self._deformationScaleFactor)
        # update max/min labels position
        self._maxPointLabel.setPosition(self._gridRenderObject.dataSet.GetPoint(self._maxPointIndex))
        self._minPointLabel.setPosition(self._gridRenderObject.dataSet.GetPoint(self._minPointIndex))
        if render: self.render()

    def setSelectionRenderObject(
        self,
        dataObject: DataObject | None,
        color: tuple[float, float, float] | None = None,
        modelDatabase: ModelDatabase | None = None,
        render: bool = True
    ) -> None:
        '''Renders the specified selection.'''
        if self._selectionRenderObject: self.remove(self._selectionRenderObject, render=False)
        if not self._gridRenderObject: return
        match dataObject:
            case NodeSet():
                self._selectionRenderObject = PointsRenderObject(
                    self._gridRenderObject.dataSet, dataObject.indices(), color
                )
            case ElementSet():
                self._selectionRenderObject = CellsRenderObject(
                    self._gridRenderObject.dataSet,
                    dataObject.indices(),
                    self._gridLinesVisible,
                    self._gridLineWidth,
                    self._gridLineColor,
                    color
                )
            case SurfaceSet():
                centroids: list[tuple[float, float, float]] = []
                normals: list[tuple[float, float, float]] = []
                for surface in dataObject.surfaces():
                    elementIndex, connectivity = surface
                    cell: vtkCell = self._gridRenderObject.dataSet.GetCell(elementIndex)
                    centroids.append(vu.surfaceCentroid(cell, connectivity))
                    normals.append(vu.surfaceNormal(cell, connectivity))
                self._selectionRenderObject = ArrowsRenderObject(centroids, normals, 'Normal', color)
            case ConcentratedLoad():
                if not modelDatabase: raise ValueError("missing optional argument: 'modelDatabase'")
                if sum(abs(x) for x in dataObject.components()) == 0.0:
                    self._selectionRenderObject = None
                else:
                    nodeSet: NodeSet = cast(NodeSet, modelDatabase.nodeSets[dataObject.nodeSetName])
                    origins: tuple[tuple[float, float, float], ...] = tuple(
                        modelDatabase.mesh.nodes[k].coordinates for k in nodeSet.indices()
                    )
                    self._selectionRenderObject = GroupRenderObject()
                    for i in range(3):
                        if dataObject.components()[i] == 0.0: continue
                        a: float = +1.0 if dataObject.components()[i] >= 0.0 else -1.0
                        directions: tuple[tuple[float, float, float], ...] = (
                            tuple(a if k == i else 0.0 for k in range(3)),
                        )*nodeSet.count
                        self._selectionRenderObject.add(ArrowsRenderObject(origins, directions, 'Normal', color))
            case Pressure():
                if not modelDatabase: raise ValueError("missing optional argument: 'modelDatabase'")
                if dataObject.magnitude == 0.0:
                    self._selectionRenderObject = None
                else:
                    surfaceSet: SurfaceSet = cast(SurfaceSet, modelDatabase.surfaceSets[dataObject.surfaceSetName])
                    centroids: list[tuple[float, float, float]] = []
                    normals: list[tuple[float, float, float]] = []
                    for surface in surfaceSet.surfaces():
                        elementIndex, connectivity = surface
                        cell: vtkCell = self._gridRenderObject.dataSet.GetCell(elementIndex)
                        centroids.append(vu.surfaceCentroid(cell, connectivity))
                        normals.append(vu.surfaceNormal(cell, connectivity))
                    arrowType = 'Normal' if dataObject.magnitude < 0.0 else 'Flipped'
                    self._selectionRenderObject = ArrowsRenderObject(centroids, normals, arrowType, color)
            case SurfaceTraction():
                if not modelDatabase: raise ValueError("missing optional argument: 'modelDatabase'")
                if sum(abs(x) for x in dataObject.components()) == 0.0:
                    self._selectionRenderObject = None
                else:
                    surfaceSet: SurfaceSet = cast(SurfaceSet, modelDatabase.surfaceSets[dataObject.surfaceSetName])
                    origins: tuple[tuple[float, float, float], ...] = tuple(
                        vu.surfaceCentroid(
                            self._gridRenderObject.dataSet.GetCell(elementIndex),
                            connectivity
                        ) for elementIndex, connectivity in surfaceSet.surfaces()
                    )
                    self._selectionRenderObject = GroupRenderObject()
                    for i in range(3):
                        if dataObject.components()[i] == 0.0: continue
                        a: float = +1.0 if dataObject.components()[i] >= 0.0 else -1.0
                        directions: tuple[tuple[float, float, float], ...] = (
                            tuple(a if k == i else 0.0 for k in range(3)),
                        )*surfaceSet.count
                        self._selectionRenderObject.add(ArrowsRenderObject(origins, directions, 'Normal', color))
            case BodyLoad():
                if not modelDatabase: raise ValueError("missing optional argument: 'modelDatabase'")
                if sum(abs(x) for x in dataObject.components()) == 0.0:
                    self._selectionRenderObject = None
                else:
                    elementSet: ElementSet = cast(ElementSet, modelDatabase.elementSets[dataObject.elementSetName])
                    origins: tuple[tuple[float, float, float], ...] = tuple(
                        vu.cellCentroid(self._gridRenderObject.dataSet.GetCell(k)) for k in elementSet.indices()
                    )
                    self._selectionRenderObject = GroupRenderObject()
                    for i in range(3):
                        if dataObject.components()[i] == 0.0: continue
                        a: float = +1.0 if dataObject.components()[i] >= 0.0 else -1.0
                        directions: tuple[tuple[float, float, float], ...] = (
                            tuple(a if k == i else 0.0 for k in range(3)),
                        )*elementSet.count
                        self._selectionRenderObject.add(ArrowsRenderObject(origins, directions, 'Normal', color))
            case BoundaryCondition():
                if not modelDatabase: raise ValueError("missing optional argument: 'modelDatabase'")
                if True not in dataObject.activeDOFs():
                    self._selectionRenderObject = None
                else:
                    nodeSet: NodeSet = cast(NodeSet, modelDatabase.nodeSets[dataObject.nodeSetName])
                    origins: tuple[tuple[float, float, float], ...] = tuple(
                        modelDatabase.mesh.nodes[k].coordinates for k in nodeSet.indices()
                    )
                    self._selectionRenderObject = GroupRenderObject()
                    for i in range(3):
                        if not dataObject.activeDOFs()[i]: continue
                        a: float = +1.0 if dataObject.components()[i] >= 0.0 else -1.0
                        directions: tuple[tuple[float, float, float], ...] = (
                            tuple(a if k == i else 0.0 for k in range(3)),
                        )*nodeSet.count
                        arrowType: str = 'Normal' if dataObject.components()[i] != 0.0 else 'NoShaft'
                        self._selectionRenderObject.add(ArrowsRenderObject(origins, directions, arrowType, color))
            case _:
                self._selectionRenderObject = None
        if self._selectionRenderObject:
            self.add(self._selectionRenderObject, render=False)
            InteractionStyle.recomputeGlyphSize(self._renderer, render=False)
        if render: self.render()

    def plotNodalScalarField(self, nodalScalarField: tuple[float, ...] | None, render: bool = True) -> None:
        '''Plots the given nodal scalar field on the current mesh.'''
        if not self._gridRenderObject:
            self._scalarBar.setVisible(False)
            self._maxPointLabel.setVisible(False)
            self._minPointLabel.setVisible(False)
        else:
            # update visibility of scalar bar and max/min labels
            self._scalarBar.setVisible(nodalScalarField is not None)
            self._maxPointLabel.setVisible(nodalScalarField is not None and self._showMaxPointLabel)
            self._minPointLabel.setVisible(nodalScalarField is not None and self._showMinPointLabel)
            # update max/min
            if nodalScalarField:
                Viewport._defaultMaxLimit = max(nodalScalarField)
                Viewport._defaultMinLimit = min(nodalScalarField)
                if not self._useCustomLimits:
                    self.setCustomMaxLimit(self._defaultMaxLimit)
                    self.setCustomMinLimit(self._defaultMinLimit)
                self._maxPointIndex = nodalScalarField.index(self._defaultMaxLimit)
                self._minPointIndex = nodalScalarField.index(self._defaultMinLimit)
                self._maxPointLabel.setPosition(self._gridRenderObject.dataSet.GetPoint(self._maxPointIndex))
                self._minPointLabel.setPosition(self._gridRenderObject.dataSet.GetPoint(self._minPointIndex))
            # plot contour
            self._gridRenderObject.setNodalScalarField(nodalScalarField)
            if self._useCustomLimits:
                self._gridRenderObject.setNodalScalarFieldRange(self._customMinLimit, self._customMaxLimit)
            else:
                self._gridRenderObject.setNodalScalarFieldRange(self._defaultMinLimit, self._defaultMaxLimit)
        if render: self.render()
