from vtkmodules.vtkRenderingCore import vtkTextActor, vtkRenderer

class Info:
    '''
    Viewport information text.
    '''

    # attribute slots
    __slots__ = ('_text', '_actor')

    def __init__(self, textColor: tuple[float, float, float], fontSize: int) -> None:
        '''Info constructor.'''
        # text storage
        self._text: list[str] = []
        # actor
        self._actor: vtkTextActor = vtkTextActor()
        self._actor.SetTextScaleModeToNone()
        self._actor.GetTextProperty().SetFontSize(fontSize)
        self._actor.GetTextProperty().SetFontFamilyToCourier()
        self._actor.GetTextProperty().ItalicOff()
        self._actor.GetTextProperty().ShadowOn()
        self._actor.GetTextProperty().BoldOff()
        self._actor.GetTextProperty().SetJustificationToLeft()
        self._actor.GetTextProperty().SetVerticalJustificationToBottom()
        self._actor.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
        self._actor.GetPositionCoordinate().SetValue(0.01, 0.01)
        self.setTextColor(textColor)

    def initialize(self, renderer: vtkRenderer) -> None:
        '''Sets the renderer.'''
        renderer.AddActor2D(self._actor)

    def clear(self) -> None:
        '''Clears all text.'''
        self._text.clear()
        self._actor.SetInput('')

    def setText(self, row: int, text: str) -> None:
        '''Sets the text at the specified row/line.'''
        while len(self._text) < row + 1: self._text.append('')
        self._text[row] = text
        self._actor.SetInput('\n'.join(self._text[::-1]))

    def setTextColor(self, color: tuple[float, float, float]) -> None:
        '''Sets the text color.'''
        self._actor.GetTextProperty().SetColor(color)

    def setFontSize(self, size: int) -> None:
        '''Sets the font size.'''
        self._actor.GetTextProperty().SetFontSize(size)
