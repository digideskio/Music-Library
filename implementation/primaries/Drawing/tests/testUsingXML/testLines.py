from implementation.primaries.Drawing.tests.testUsingXML.setup import xmlSet, parsePiece
from implementation.primaries.Drawing.classes import MxmlParser
from implementation.primaries.Drawing.classes import Directions, Measure
import os
from implementation.primaries.Drawing.classes.tree_cls.PartNode import PartNode
from implementation.primaries.Drawing.classes.tree_cls.MeasureNode import MeasureNode
from implementation.primaries.Drawing.classes.tree_cls.BaseTree import Search
from implementation.primaries.Drawing.classes.tree_cls.NoteNode import NoteNode, Placeholder
from implementation.primaries.Drawing.classes.tree_cls.OtherNodes import ExpressionNode, DirectionNode

partname = "lines.xml"
folder = "/Users/charlottegodley/PycharmProjects/FYP/implementation/primaries/SampleMusicXML/testcases"
piece = parsePiece(os.path.join(folder, partname))

class testFile(xmlSet):
    def setUp(self):
        xmlSet.setUp(self)
        self.m_num = 15
        self.p_id = "P1"
        self.p_name = "Flute"

    def testParts(self):
        global piece
        self.assertIsInstance(piece.getPart(self.p_id), PartNode)
        self.assertEqual(self.p_name, piece.getPart(self.p_id).GetItem().name)

    def testMeasures(self):
        self.assertIsInstance(piece.getPart(self.p_id).getMeasure(self.m_num, 1), MeasureNode)

class testWedge(xmlSet):
    def setUp(self):
        if hasattr(self, "measure_id"):
            self.measure = piece.getPart(self.p_id).getMeasure(self.measure_id, 1)
        if hasattr(self, "item_id"):
            if hasattr(self, "place_id"):
                note = Search(Placeholder, self.measure, self.place_id)
            else:
                note = Search(NoteNode, self.measure, 1)
            self.item = Search(ExpressionNode, note, self.item_id+1).GetItem()

    def testInstance(self):
        if hasattr(self, "item"):
            self.assertIsInstance(self.item, Directions.Wedge)

    def testType(self):
        if hasattr(self, "type"):
            self.assertEqual(self.type, self.item.type)

    def testPlacement(self):
        if hasattr(self, "placement"):
            self.assertEqual(self.placement, self.item.placement)

class testOctaveShift(xmlSet):
    def setUp(self):
        if hasattr(self, "measure_id"):
            self.measure = piece.getPart(self.p_id).getMeasure(self.measure_id, 1)
        if hasattr(self, "item_id"):
            if hasattr(self, "note_id"):
                note = Search(NoteNode, self.measure, self.note_id)
            else:
                note = Search(NoteNode, self.measure, 1)
            self.item = Search(DirectionNode, note, self.item_id+1).GetItem()

    def testInstance(self):
        if hasattr(self, "item"):
            self.assertIsInstance(self.item, Directions.OctaveShift)

    def testType(self):
        if hasattr(self, "type"):
            self.assertEqual(self.type, self.item.type)

    def testAmount(self):
        if hasattr(self, "amount"):
            self.assertEqual(self.amount, self.item.amount)

    def testFont(self):
        if hasattr(self, "font"):
            self.assertEqual(self.font, self.item.font)

class testPedal(xmlSet):
    def setUp(self):
        if hasattr(self, "measure_id"):
            self.measure = piece.getPart(self.p_id).getMeasure(self.measure_id, 1)
        if hasattr(self, "item_id"):
            note = Search(NoteNode, self.measure, 1)
            self.item = Search(DirectionNode, note, self.item_id+1).GetItem()

    def testInstance(self):
        if hasattr(self, "item"):
            self.assertIsInstance(self.item, Directions.Pedal)

    def testType(self):
        if hasattr(self, "type"):
            self.assertEqual(self.type, self.item.type)

    def testLine(self):
        if hasattr(self, "line"):
            self.assertEqual(self.line, self.item.line)

    def testPlacement(self):
        if hasattr(self, "placement"):
            self.assertEqual(self.placement, self.item.placement)

class testBracket(xmlSet):
    def setUp(self):
        if hasattr(self, "measure_id"):
            self.measure = piece.getPart(self.p_id).getMeasure(self.measure_id, 1)
        if hasattr(self, "item_id"):
            self.item = self.measure.GetItem().getWrapper(self.item_id)

    def testInstance(self):
        if hasattr(self, "item"):
            self.assertIsInstance(self.item, Directions.Bracket)

    def testType(self):
        if hasattr(self, "type"):
            self.assertEqual(self.type, self.item.type)

    def testNumber(self):
        if hasattr(self, "number"):
            self.assertEqual(self.number, self.item.number)

    def testLineEnd(self):
        if hasattr(self, "lineend"):
            self.assertEqual(self.lineend, self.item.lineEnd)

    def testLineType(self):
        if hasattr(self, "linetype"):
            self.assertEqual(self.linetype, self.item.lineType)

    def testEndLength(self):
        if hasattr(self, "endlength"):
            self.assertEqual(self.endlength, self.item.endLength)

class testMeasure1Item1(testWedge):
    def setUp(self):
        self.placement = "below"
        self.type = "crescendo"
        self.measure_id = 1
        self.item_id = 0
        self.p_id = "P1"
        testWedge.setUp(self)

class testMeasure1Item3(testWedge):
    def setUp(self):
        self.placement = "below"
        self.type = "stop"
        self.measure_id = 1
        self.item_id = 0
        self.p_id = "P1"
        self.place_id = 1
        testWedge.setUp(self)

class testMeasure2Item1(testWedge):
    def setUp(self):
        self.placement = "below"
        self.type = "diminuendo"
        self.measure_id = 2
        self.item_id = 0
        self.p_id = "P1"
        testWedge.setUp(self)

class testMeasure2Item3(testWedge):
    def setUp(self):
        self.placement = "below"
        self.type = "stop"
        self.measure_id = 2
        self.item_id = 0
        self.p_id = "P1"
        self.place_id = 1
        testWedge.setUp(self)

class testEndings(xmlSet):
    def setUp(self):
        xmlSet.setUp(self)
        self.p_id = "P1"
        if hasattr(self, "measure_id"):
            self.measure = piece.getPart(self.p_id).getMeasure(self.measure_id, 1).GetItem()

    def testHasBarline(self):
        if hasattr(self, "measure"):
            self.assertTrue(hasattr(self.measure, "barlines"))

    def testBarlineKeys(self):
        if hasattr(self, "key"):
            self.assertTrue(self.key in self.measure.barlines)

    def testBarlineInstance(self):
        if hasattr(self, "key"):
            self.assertIsInstance(self.measure.barlines[self.key], Measure.Barline)

    def testBarlineEnding(self):
        if hasattr(self, "key"):
            self.assertTrue(hasattr(self.measure.barlines[self.key], "ending"))

    def testBarlineEndingInstance(self):
        if hasattr(self, "key"):
            self.assertIsInstance(self.measure.barlines[self.key].ending, Measure.EndingMark)
    def testBarlineNum(self):
        if hasattr(self, "num"):
            self.assertEqual(self.num, self.measure.barlines[self.key].ending.number)

    def testBarlineType(self):
        if hasattr(self, "type"):
            self.assertEqual(self.type, self.measure.barlines[self.key].ending.type)

class testMeasure3Left(testEndings):
    def setUp(self):
        self.measure_id = 3
        self.key = "left"
        self.num = 1
        self.type = "start"
        testEndings.setUp(self)

class testMeasure3Right(testEndings):
    def setUp(self):
        self.measure_id = 3
        self.key = "right"
        self.num = 1
        self.type = "stop"
        testEndings.setUp(self)

class testMeasure4Left(testEndings):
    def setUp(self):
        self.measure_id = 4
        self.key = "left"
        self.num = 2
        self.type = "start"
        testEndings.setUp(self)

class testMeasure4Right(testEndings):
    def setUp(self):
        self.measure_id = 4
        self.key = "right"
        self.num = 2
        self.type = "stop"
        testEndings.setUp(self)

class testMeasure5Left(testEndings):
    def setUp(self):
        self.measure_id = 5
        self.key = "left"
        self.num = 3
        self.type = "start"
        testEndings.setUp(self)

class testMeasure5Right(testEndings):
    def setUp(self):
        self.measure_id = 5
        self.key = "right"
        self.num = 3
        self.type = "stop"
        testEndings.setUp(self)

class testMeasure6Item1(testOctaveShift):
    def setUp(self):
        self.placement = "above"
        self.amount = 8
        self.type = "down"
        self.measure_id = 6
        self.item_id = 0
        self.p_id = "P1"
        testOctaveShift.setUp(self)

class testMeasure6Item3(testOctaveShift):
    def setUp(self):
        self.placement = "above"
        self.amount = 8
        self.type = "stop"
        self.measure_id = 6
        self.item_id = 1
        self.p_id = "P1"
        testOctaveShift.setUp(self)

class testMeasure7Item1(testOctaveShift):
    def setUp(self):
        self.placement = "above"
        self.amount = 15
        self.type = "down"
        self.measure_id = 7
        self.item_id = 0
        self.p_id = "P1"
        testOctaveShift.setUp(self)

class testMeasure7Item3(testOctaveShift):
    def setUp(self):
        self.placement = "above"
        self.amount = 15
        self.type = "stop"
        self.measure_id = 7
        self.item_id = 1
        self.p_id = "P1"
        testOctaveShift.setUp(self)

class testMeasure8Item1(testOctaveShift):
    def setUp(self):
        self.placement = "below"
        self.amount = 8
        self.type = "up"
        self.measure_id = 8
        self.item_id = 0
        self.p_id = "P1"
        testOctaveShift.setUp(self)

class testMeasure8Item3(testOctaveShift):
    def setUp(self):
        self.placement = "below"
        self.amount = 8
        self.type = "stop"
        self.measure_id = 8
        self.item_id = 1
        self.p_id = "P1"
        testOctaveShift.setUp(self)

class testMeasure9Item1(testOctaveShift):
    def setUp(self):
        self.placement = "below"
        self.amount = 15
        self.type = "up"
        self.measure_id = 9
        self.item_id = 0
        self.p_id = "P1"
        testOctaveShift.setUp(self)

class testMeasure9Item3(testOctaveShift):
    def setUp(self):
        self.placement = "below"
        self.amount = 15
        self.type = "stop"
        self.measure_id = 9
        self.item_id = 1
        self.p_id = "P1"
        testOctaveShift.setUp(self)

class testMeasure12Item1(testPedal):
    def setUp(self):
        self.type = "start"
        self.line = True
        self.measure_id = 12
        self.item_id = 0
        self.p_id = "P1"
        testPedal.setUp(self)

class testMeasure12Item3(testPedal):
    def setUp(self):
        self.type = "stop"
        self.line = True
        self.measure_id = 12
        self.item_id = 1
        self.p_id = "P1"
        testPedal.setUp(self)

class testMeasure13Item1(testPedal):
    def setUp(self):
        self.type = "start"
        self.line = True
        self.measure_id = 13
        self.item_id = 0
        self.p_id = "P1"
        testPedal.setUp(self)

class testMeasure13Item3(testPedal):
    def setUp(self):
        self.type = "stop"
        self.line = True
        self.measure_id = 13
        self.item_id = 1
        self.p_id = "P1"
        testPedal.setUp(self)

class testMeasure14Item2(testBracket):
    def setUp(self):
        self.type = "start"
        self.number = 1
        self.lineend = "none"
        self.measure_id = 14
        self.item_id = 0
        self.p_id = "P1"
        testBracket.setUp(self)

class testMeasure14Item4(testBracket):
    def setUp(self):
        self.type = "stop"
        self.number = 1
        self.lineend = "down"
        self.endlength = 15
        self.measure_id = 14
        self.item_id = 1
        self.p_id = "P1"
        testBracket.setUp(self)