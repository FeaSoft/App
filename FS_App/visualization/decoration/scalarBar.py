from typing import Literal
from visualization.decoration.colormaps import Colormaps
from vtkmodules.vtkCommonCore import vtkLookupTable
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor
from vtkmodules.vtkRenderingCore import vtkRenderer, vtkColorTransferFunction

class ScalarBar:
    '''
    Viewport scalar bar.
    '''

    @property
    def lookupTable(self) -> vtkLookupTable:
        '''The scalar bar lookup table.'''
        return self._lookupTable

    # attribute slots
    __slots__ = ('_lookupTable', '_scalarBarActor', '_decimalPlaces', '_numberFormat')

    def __init__(
        self,
        decimalPlaces: int,
        numberFormat: Literal['Scientific', 'Fixed'],
        textColor: tuple[float, float, float],
        fontSize: int
    ) -> None:
        '''Scalar bar constructor.'''
        # decimal places
        self._decimalPlaces: int = decimalPlaces
        self._numberFormat: Literal['Scientific', 'Fixed'] = numberFormat
        # lookup table
        self._lookupTable: vtkLookupTable = vtkLookupTable()
        # scalar bar actor
        self._scalarBarActor: vtkScalarBarActor = vtkScalarBarActor()
        self._scalarBarActor.UnconstrainedFontSizeOn()
        self._scalarBarActor.GetLabelTextProperty().SetFontSize(fontSize)    # type: ignore
        self._scalarBarActor.GetLabelTextProperty().SetFontFamilyToCourier() # type: ignore
        self._scalarBarActor.GetLabelTextProperty().ItalicOff()              # type: ignore
        self._scalarBarActor.GetLabelTextProperty().ShadowOn()               # type: ignore
        self._scalarBarActor.GetLabelTextProperty().BoldOff()                # type: ignore
        self._scalarBarActor.SetLookupTable(self._lookupTable)               # type: ignore
        self._scalarBarActor.SetPosition(0.025, 0.5)
        self._scalarBarActor.SetWidth(0.1)
        self._scalarBarActor.SetHeight(0.45)
        self.setTextColor(textColor)
        # initialize colormap
        self.setColormap(Colormaps.Jet)
        # initialize labels
        self.setNumberFormat(numberFormat)

    def initialize(self, renderer: vtkRenderer) -> None:
        '''Sets the renderer.'''
        renderer.AddActor2D(self._scalarBarActor)

    def visible(self) -> bool:
        '''Sets the visibility of the actor.'''
        return bool(self._scalarBarActor.GetVisibility())

    def setVisible(self, value: bool) -> None:
        '''Sets the visibility of the actor.'''
        self._scalarBarActor.SetVisibility(value)

    def setTextColor(self, color: tuple[float, float, float]) -> None:
        '''Sets the text color.'''
        self._scalarBarActor.GetLabelTextProperty().SetColor(color) # type: ignore

    def setFontSize(self, size: int) -> None:
        '''Sets the font size.'''
        self._scalarBarActor.GetLabelTextProperty().SetFontSize(size) # type: ignore

    def setNumberFormat(self, format: Literal['Scientific', 'Fixed']) -> None:
        '''Sets the number format.'''
        self._numberFormat = format
        match self._numberFormat:
            case 'Scientific': self._scalarBarActor.SetLabelFormat(f'%+0.{self._decimalPlaces}e')
            case 'Fixed': self._scalarBarActor.SetLabelFormat(f'%+0.{self._decimalPlaces}f')

    def setDecimalPlaces(self, decimalPlaces: int) -> None:
        '''Sets the number format.'''
        self._decimalPlaces = decimalPlaces
        match self._numberFormat:
            case 'Scientific': self._scalarBarActor.SetLabelFormat(f'%+0.{self._decimalPlaces}e')
            case 'Fixed': self._scalarBarActor.SetLabelFormat(f'%+0.{self._decimalPlaces}f')

    def setColormap(self, colormap: Colormaps, numberOfColors: int = 12, reverse: bool = False) -> None:
        '''Sets the current colormap.'''
        match colormap:
            case Colormaps.Jet:
                colors: tuple[tuple[float, float, float], ...] = (
                    (0.0, 0.0, 1.0),
                    (0.0, 1.0, 1.0),
                    (0.0, 1.0, 0.0),
                    (1.0, 1.0, 0.0),
                    (1.0, 0.0, 0.0),
                )
            case Colormaps.Rainbow:
                colors: tuple[tuple[float, float, float], ...] = (
                    (0.5, 0.0, 1.0),
                    (0.0, 0.0, 1.0),
                    (0.0, 1.0, 1.0),
                    (0.0, 1.0, 0.0),
                    (1.0, 1.0, 0.0),
                    (1.0, 0.5, 0.0),
                    (1.0, 0.0, 0.0),
                )
            case Colormaps.Cyclic:
                colors: tuple[tuple[float, float, float], ...] = (
                    (1.0, 0.0, 0.0),
                    (1.0, 0.0, 1.0),
                    (0.0, 0.0, 1.0),
                    (0.0, 1.0, 1.0),
                    (0.0, 1.0, 0.0),
                    (1.0, 1.0, 0.0),
                    (1.0, 0.0, 0.0),
                )
            case Colormaps.Parula:
                colors: tuple[tuple[float, float, float], ...] = (
                    (0.2422, 0.1504, 0.6603),
                    (0.2580, 0.1823, 0.7526),
                    (0.2710, 0.2159, 0.8388),
                    (0.2786, 0.2580, 0.9015),
                    (0.2814, 0.3035, 0.9437),
                    (0.2790, 0.3482, 0.9737),
                    (0.2684, 0.3936, 0.9916),
                    (0.2392, 0.4412, 0.9994),
                    (0.1912, 0.4908, 0.9871),
                    (0.1778, 0.5351, 0.9640),
                    (0.1639, 0.5768, 0.9314),
                    (0.1438, 0.6157, 0.9036),
                    (0.1195, 0.6528, 0.8842),
                    (0.0859, 0.6863, 0.8516),
                    (0.0145, 0.7138, 0.8054),
                    (0.0197, 0.7361, 0.7532),
                    (0.1209, 0.7544, 0.6977),
                    (0.1844, 0.7717, 0.6391),
                    (0.2323, 0.7888, 0.5719),
                    (0.3212, 0.7996, 0.4946),
                    (0.4255, 0.8029, 0.4066),
                    (0.5434, 0.7960, 0.3187),
                    (0.6563, 0.7819, 0.2332),
                    (0.7613, 0.7624, 0.1706),
                    (0.8539, 0.7426, 0.1574),
                    (0.9327, 0.7293, 0.2030),
                    (0.9940, 0.7402, 0.2399),
                    (0.9956, 0.7862, 0.2049),
                    (0.9798, 0.8362, 0.1777),
                    (0.9613, 0.8874, 0.1543),
                    (0.9627, 0.9366, 0.1271),
                    (0.9769, 0.9839, 0.0805),
                )
            case Colormaps.Viridis:
                colors: tuple[tuple[float, float, float], ...] = (
                    (0.2670, 0.0049, 0.3294),
                    (0.2770, 0.0503, 0.3757),
                    (0.2823, 0.0950, 0.4173),
                    (0.2829, 0.1359, 0.4534),
                    (0.2780, 0.1804, 0.4867),
                    (0.2693, 0.2188, 0.5096),
                    (0.2573, 0.2561, 0.5266),
                    (0.2431, 0.2921, 0.5385),
                    (0.2259, 0.3308, 0.5473),
                    (0.2105, 0.3637, 0.5522),
                    (0.1959, 0.3954, 0.5553),
                    (0.1823, 0.4262, 0.5571),
                    (0.1681, 0.4600, 0.5581),
                    (0.1563, 0.4896, 0.5579),
                    (0.1448, 0.5191, 0.5566),
                    (0.1337, 0.5485, 0.5535),
                    (0.1235, 0.5817, 0.5474),
                    (0.1194, 0.6111, 0.5390),
                    (0.1248, 0.6405, 0.5271),
                    (0.1433, 0.6695, 0.5112),
                    (0.1807, 0.7014, 0.4882),
                    (0.2264, 0.7289, 0.4628),
                    (0.2815, 0.7552, 0.4326),
                    (0.3441, 0.7800, 0.3974),
                    (0.4219, 0.8058, 0.3519),
                    (0.4966, 0.8264, 0.3064),
                    (0.5756, 0.8446, 0.2564),
                    (0.6576, 0.8602, 0.2031),
                    (0.7519, 0.8750, 0.1432),
                    (0.8353, 0.8860, 0.1026),
                    (0.9162, 0.8961, 0.1007),
                    (0.9932, 0.9062, 0.1439),
                )
            case Colormaps.Plasma:
                colors: tuple[tuple[float, float, float], ...] = (
                    (0.0504, 0.0298, 0.5280),
                    (0.1324, 0.0223, 0.5632),
                    (0.1934, 0.0184, 0.5903),
                    (0.2480, 0.0144, 0.6129),
                    (0.3062, 0.0089, 0.6337),
                    (0.3564, 0.0038, 0.6478),
                    (0.4055, 0.0007, 0.6570),
                    (0.4537, 0.0028, 0.6603),
                    (0.5065, 0.0163, 0.6562),
                    (0.5517, 0.0431, 0.6453),
                    (0.5950, 0.0772, 0.6279),
                    (0.6360, 0.1121, 0.6052),
                    (0.6792, 0.1518, 0.5752),
                    (0.7149, 0.1873, 0.5463),
                    (0.7483, 0.2227, 0.5168),
                    (0.7796, 0.2581, 0.4875),
                    (0.8126, 0.2979, 0.4553),
                    (0.8402, 0.3336, 0.4275),
                    (0.8661, 0.3697, 0.4001),
                    (0.8903, 0.4064, 0.3731),
                    (0.9155, 0.4488, 0.3429),
                    (0.9356, 0.4877, 0.3160),
                    (0.9534, 0.5280, 0.2889),
                    (0.9685, 0.5697, 0.2617),
                    (0.9818, 0.6186, 0.2313),
                    (0.9899, 0.6638, 0.2049),
                    (0.9941, 0.7107, 0.1801),
                    (0.9939, 0.7593, 0.1591),
                    (0.9876, 0.8160, 0.1444),
                    (0.9763, 0.8680, 0.1434),
                    (0.9593, 0.9214, 0.1516),
                    (0.9400, 0.9752, 0.1313),
                )
            case Colormaps.Marc:
                colors: tuple[tuple[float, float, float], ...] = (
                    (0.0, 0.0, 1.0),
                    (1.0, 0.0, 0.0),
                    (1.0, 1.0, 0.0),
                )
            case Colormaps.Linear:
                colors: tuple[tuple[float, float, float], ...] = (
                    (0.0, 0.0, 1.0),
                    (1.0, 0.0, 0.0),
                )
            case Colormaps.Diverging:
                colors: tuple[tuple[float, float, float], ...] = (
                    (0.0, 0.0, 1.0),
                    (1.0, 1.0, 1.0),
                    (1.0, 0.0, 0.0),
                )
            case Colormaps.Grayscale:
                colors: tuple[tuple[float, float, float], ...] = (
                    (0.0, 0.0, 0.0),
                    (1.0, 1.0, 1.0),
                )
        # color transfer function
        colorFunction: vtkColorTransferFunction = vtkColorTransferFunction()
        for i, color in enumerate(colors):
            colorFunction.AddRGBPoint(i, *color)
        # weights
        n: int = len(colors) - 1
        a: int = n if reverse else 0
        b: int = 0 if reverse else n
        weights: tuple[float, ...] = tuple(a + i*(b - a)/(numberOfColors - 1) for i in range(numberOfColors))
        # update lookup table
        self._lookupTable.SetNumberOfColors(numberOfColors)
        self._lookupTable.SetNumberOfTableValues(numberOfColors)
        for i, weight in enumerate(weights):
            self._lookupTable.SetTableValue(i, *colorFunction.GetColor(weight))
        self._lookupTable.Build()
        self._lookupTable.Modified()
        # update actor
        self._scalarBarActor.SetNumberOfLabels(numberOfColors + 1)
        self._scalarBarActor.Modified()
