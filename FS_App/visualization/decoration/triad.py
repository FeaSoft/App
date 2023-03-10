from vtkmodules.vtkRenderingAnnotation import vtkAxesActor, vtkCaptionActor2D
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
from vtkmodules.vtkRenderingCore import vtkRenderWindowInteractor

class Triad:
    '''
    The view triad (global axes).
    '''

    @staticmethod
    def setupCaptionActor2D(captionActor2D: vtkCaptionActor2D, fontSize: int) -> None:
        '''Utility function to setup a vtkCaptionActor2D.'''
        captionActor2D.GetTextActor().SetTextScaleModeToNone()           # type: ignore
        captionActor2D.GetCaptionTextProperty().SetFontSize(fontSize)    # type: ignore
        captionActor2D.GetCaptionTextProperty().SetFontFamilyToCourier() # type: ignore
        captionActor2D.GetCaptionTextProperty().ItalicOff()              # type: ignore
        captionActor2D.GetCaptionTextProperty().ShadowOn()               # type: ignore
        captionActor2D.GetCaptionTextProperty().BoldOff()                # type: ignore

    # attribute slots
    __slots__ = ('_axesActor', '_orientationMarkerWidget')

    def __init__(self, textColor: tuple[float, float, float], fontSize: int) -> None:
        '''Triad constructor.'''
        # axes actor
        self._axesActor: vtkAxesActor = vtkAxesActor()
        self.setupCaptionActor2D(self._axesActor.GetXAxisCaptionActor2D(), fontSize)
        self.setupCaptionActor2D(self._axesActor.GetYAxisCaptionActor2D(), fontSize)
        self.setupCaptionActor2D(self._axesActor.GetZAxisCaptionActor2D(), fontSize)
        self._axesActor.SetTipTypeToCone()
        self._axesActor.SetShaftTypeToCylinder()
        self._axesActor.SetConeResolution(64)
        self._axesActor.SetCylinderResolution(64)
        self._axesActor.SetConeRadius(0.5)
        self._axesActor.SetCylinderRadius(0.08)
        self._axesActor.SetNormalizedTipLength(0.3, 0.3, 0.3)
        self._axesActor.SetNormalizedShaftLength(0.7, 0.7, 0.7)
        self._axesActor.SetNormalizedLabelPosition(1.25, 1.25, 1.25)
        self.setTextColor(textColor)
        # orientation marker widget
        self._orientationMarkerWidget: vtkOrientationMarkerWidget = vtkOrientationMarkerWidget()
        self._orientationMarkerWidget.SetOrientationMarker(self._axesActor) # type: ignore
        self._orientationMarkerWidget.SetViewport(0.75, 0.0, 1.0, 0.25)

    def initialize(self, interactor: vtkRenderWindowInteractor) -> None:
        '''Sets the render window interactor and initializes the orientation marker widget.'''
        self._orientationMarkerWidget.SetInteractor(interactor)
        self._orientationMarkerWidget.EnabledOn()
        self._orientationMarkerWidget.InteractiveOff()

    def setTextColor(self, color: tuple[float, float, float]) -> None:
        '''Sets the text color.'''
        self._axesActor.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetColor(color) # type: ignore
        self._axesActor.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetColor(color) # type: ignore
        self._axesActor.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetColor(color) # type: ignore

    def setFontSize(self, size: int) -> None:
        '''Sets the font size.'''
        self._axesActor.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(size) # type: ignore
        self._axesActor.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(size) # type: ignore
        self._axesActor.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(size) # type: ignore
